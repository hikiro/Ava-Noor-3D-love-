#!/usr/bin/env python3
"""Independent v1.7 numerical QA. Does NOT grade artistic performance or physics."""
from __future__ import annotations
import json,subprocess,sys,pathlib,zipfile
import numpy as np, cv2, trimesh
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from build_v17 import Actor,ROOT,NAMES
from build_v16 import read_glb,read_accessor
QA=ROOT/'qa';QA.mkdir(exist_ok=True)
report={'version':'1.7','checks':[],'sample_times_s':[],'metrics':{},'unresolved':[],'artistic_iteration_count':0}
def check(name,condition,detail=None):
  report['checks'].append({'check':name,'passed':bool(condition),'detail':detail})
  if not condition: print('FAIL',name,detail,flush=True)
actors={k:Actor(k) for k in ('ava','noor')}
times=np.linspace(0,5.2,20);report['sample_times_s']=[round(float(t),3) for t in times]
for key,a in actors.items():
  j,bin=read_glb(ROOT/'models'/f'{key}_CONTINUOUS_SHOULDER_v1_7.glb')
  parsed=trimesh.load(ROOT/'models'/f'{key}_CONTINUOUS_SHOULDER_v1_7.glb',force='scene',process=False)
  mesh=trimesh.load(ROOT/'models'/f'{key}_continuous_upperbody_v17.ply',process=False)
  check(key+' external GLB import',len(parsed.geometry)==1)
  check(key+' GLB metadata v17',j['asset'].get('generator','').startswith('VillaVerse v1.7'))
  check(key+' GLB contains one skinned mesh',len(j['meshes'])==1 and len(j['skins'])==1)
  check(key+' preserved 43 bones',len(j['skins'][0]['joints'])==43 and len(a.names)==43)
  check(key+' 8 blend shapes',len(j['meshes'][0]['primitives'][0]['targets'])==len(NAMES)==8)
  check(key+' exported morph weight animation',any(c['target']['path']=='weights' for c in j['animations'][0]['channels']))
  check(key+' all 25 keyframed bone tracks retained',sum(c['target']['path']=='rotation' for c in j['animations'][0]['channels'])==len(a.tracks)+(len(a.names)-len(a.old_names)))
  check(key+' one watertight upperbody island',mesh.is_watertight and len(mesh.split(only_watertight=False))==1)
  check(key+' positive surface volume',mesh.volume>0)
  check(key+' consistent triangle winding',mesh.is_winding_consistent)
  check(key+' correct new upperbody vertex count',len(mesh.vertices)==len(a.new_mesh_vertices))
  check(key+' all mesh indices in bounds',int(np.max(a.data['indices']))<len(a.data['POSITION']))
  check(key+' weights normalized',bool(np.allclose(a.data['WEIGHTS_0'].sum(1),1,atol=1e-5)))
  check(key+' bone indices bounded',int(np.max(a.data['JOINTS_0']))<43)
  check(key+' finite morph displacements',all(np.all(np.isfinite(m)) for m in a.morphs.values()))
  check(key+' head attached to neck hierarchy',a.parents['head']=='neck_top' and a.parents['neck_top']=='neck_base')
  for side in ('L','R'):
    check(key+' shoulder-elbow-wrist hierarchy '+side,
          a.parents['elbow_'+side]=='shoulder_'+side and a.parents['wrist_'+side]=='elbow_'+side)
  check(key+' deleted rigid upperbody shells',all(x not in a.ranges for x in a.removed_parts))
  # All source asset triangles remain indexed correctly, while upperbody is a continuous new surface.
  # Test body deformation stretch and foot stability over 20 chronological windows.
  f=a.data['indices'].reshape(-1,3)[a.upper_body_face_start:]
  E=np.unique(np.sort(np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[0,2]]]),axis=1),axis=0)
  V=a.data['POSITION'];r=np.linalg.norm(V[E[:,0]]-V[E[:,1]],axis=1)
  foot_indices=np.hstack([np.arange(*a.ranges[n]) for n in a.ranges if 'shoe' in n or 'sole' in n])
  foot0=a.deform(0)[foot_indices]
  minima=[];maxima=[];feet=[];neckerrs=[]
  for i,t in enumerate(times):
    v=a.deform(float(t));finite=bool(np.isfinite(v).all())
    check(f'{key} finite geometry sample {i+1:02d}/20',finite)
    d=np.linalg.norm(v[E[:,0]]-v[E[:,1]],axis=1)
    ratio=d/(r+1e-10)
    minima.append(float(np.min(ratio)));maxima.append(float(np.max(ratio)))
    feet.append(float(np.max(np.linalg.norm(v[foot_indices]-foot0,axis=1))))
    M=a.posed_matrices(float(t));wp={n:M[ii,:3,:3]@a.rest[n]+M[ii,:3,3] for ii,n in enumerate(a.names)}
    err=max(abs(np.linalg.norm(wp[n]-wp[a.parents[n]])-np.linalg.norm(a.rest[n]-a.rest[a.parents[n]])) for n in a.names if a.parents[n] is not None)
    neckerrs.append(float(err))
    check(f'{key} constant skeleton lengths sample {i+1:02d}/20',err<1e-5,round(float(err),8))
  check(key+' foot fixed 20-sample max <1mm',max(feet)<.001,round(max(feet),7))
  check(key+' no invalid zero-length deformation edges',min(minima)>.05,round(min(minima),3))
  check(key+' no extreme >2.5x stretch edges',max(maxima)<2.5,round(max(maxima),3))
  # Orientation mismatch is a *risk proxy*, not a rigorous self-intersection test.
  t=3.4;w=a.expression(t);rest=V.copy()
  for ww,n in zip(w,NAMES):rest+=ww*a.morphs[n]
  posed=a.deform(t)
  normals_before=np.cross(rest[f[:,1]]-rest[f[:,0]],rest[f[:,2]]-rest[f[:,0]])
  normals_after=np.cross(posed[f[:,1]]-posed[f[:,0]],posed[f[:,2]]-posed[f[:,0]])
  M=a.posed_matrices(t);id=a.data['JOINTS_0'];wg=a.data['WEIGHTS_0'];rot=np.zeros((len(V),3,3))
  for b in range(4):rot+=wg[:,b,None,None]*M[id[:,b],:3,:3]
  meanrot=(rot[f[:,0]]+rot[f[:,1]]+rot[f[:,2]])/3
  expected=np.einsum('nij,nj->ni',meanrot,normals_before)
  cos=(expected*normals_after).sum(1)/(np.linalg.norm(expected,axis=1)*np.linalg.norm(normals_after,axis=1)+1.e-10)
  suspicious=int((cos<-.1).sum())
  report['metrics'][key]={'vertex_count':len(V),'upperbody':a.mesh_health,
     'max_foot_drift_m':max(feet),'min_edge_stretch_ratio':min(minima),'max_edge_stretch_ratio':max(maxima),
     'suspect_elbow_normal_mismatches_at_hold':suspicious,'affected_triangle_fraction':suspicious/len(f),
     'samples':20,'max_bone_length_deviation_m':max(neckerrs)}
  if suspicious>0:report['unresolved'].append(f'{key} elbow bending shows {suspicious} suspicious face orientations in pose-normal proxy; requires manual retopology/pose-space correctives')
  if min(minima)<.4:report['unresolved'].append(f'{key} strong localized elbow compression: min edge stretch {min(minima):.3f}')
# Hand proximity metric only; no claim of interpenetration-free grip.
xyz={}
for name,side,offset in [('ava','R',-.48),('noor','L',.48)]:
 a=actors[name];V=a.deform(3.4)
 ix=np.hstack([np.arange(*a.ranges[n]) for n in a.ranges if n.startswith(side+'_') and any(x in n for x in ('hand_palm','hand_knuckle','finger','thumb'))]);xyz[name]=V[ix]+np.array([offset,0,0])
min_contact=float(cKDTree(xyz['ava']).query(xyz['noor'])[0].min());report['metrics']['hand_min_vertex_gap_m']=min_contact
check('hands nearby at hold (<35mm)',min_contact<.035,round(min_contact,5))
# Full encoded video decode, not a visual-content approval.
video=ROOT/'previews'/'Ava_Noor_v17_CONTINUOUS_SHOULDERS.mp4';cap=cv2.VideoCapture(str(video));frames=[];timeshot=[]
while True:
  ok,im=cap.read()
  if not ok:break
  frames.append(im)
cap.release()
check('MP4 exactly 125 decoded frames',len(frames)==125,len(frames))
check('MP4 540x960',bool(frames and frames[0].shape[:2]==(960,540)))
check('MP4 visible change present',bool(len(frames)>30 and np.mean(cv2.absdiff(frames[0],frames[62]))>1.5))
report['metrics']['video_frames_decoded']=len(frames)
report['metrics']['video_first_middle_mean_abs_difference']=float(np.mean(cv2.absdiff(frames[0],frames[62]))) if len(frames)>62 else 0
report['unresolved'] += ['Physically collision-free finger grasp is NOT established','Model is still simple/procedural rather than production-quality Sims-like character art','Godot editor/runner not available here; GLB import in actual Godot remains unverified','No audio-driven lip-sync, realistic cloth physics or anatomical hand/shoulder twist rig','20 timeline samples and 36 elbow corrective candidates are NOT 20 separate artistic redesign iterations']
report['passed']=sum(c['passed'] for c in report['checks']);report['total']=len(report['checks'])
(QA/'validation_v17.json').write_text(json.dumps(report,indent=2))
print('RESULT',report['passed'],'/',report['total'],'body metrics',[(k,v.get('suspect_elbow_normal_mismatches_at_hold')) for k,v in report['metrics'].items() if isinstance(v,dict)])
assert report['passed']==report['total'],'At least one mechanical check failed'
