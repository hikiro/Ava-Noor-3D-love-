#!/usr/bin/env python3
"""Independent numerical/topology/video and selected-frame collision checks for Villa Verse 2.0.
These do NOT establish native Godot playback or artistic fidelity.
"""
import json,hashlib,pathlib,subprocess,sys
import numpy as np, cv2,trimesh
from scipy.spatial import cKDTree
from build_v21 import Actor,MODELS
from build_v19 import ROOT
from build_v16 import read_glb
from arm_collision_v20 import measure as arm_measure
from contact_sweep_v20 import measures as hand_measure
checks=[]; actors={};metrics={};failures=[]
def test(name,result,detail=None):
  p=bool(result);checks.append({'check':name,'pass':p,'detail':detail});
  if not p:failures.append(name);print('FAIL',name,detail,flush=True)
  return p
for key in ('ava','noor'):
  a=Actor(key);actors[key]=a;d=a.data;glb=MODELS/f'{key}_MOUTH_GRIP_v2_1.glb'
  j,bin=read_glb(glb)
  third=trimesh.load(glb,force='scene',process=False)
  test(key+' independent GLB parser',len(third.geometry)==1,len(third.geometry))
  test(key+' original 43 bone armature',len(j['skins'][0]['joints'])==43 and len(a.names)==43)
  test(key+' eight facial/clothing morph targets',len(j['meshes'][0]['primitives'][0]['targets'])==8)
  test(key+' preserved animated rotation channels',sum(c['target']['path']=='rotation' for c in j['animations'][0]['channels'])==25)
  test(key+' neck to head parenting',a.parents['head']=='neck_top' and a.parents['neck_top']=='neck_base')
  test(key+' finite vertex values',np.isfinite(d['POSITION']).all() and np.isfinite(d['WEIGHTS_0']).all())
  test(key+' normalized skin weights',np.allclose(d['WEIGHTS_0'].sum(1),1.,atol=1e-5))
  test(key+' all skin joint indices valid',d['JOINTS_0'].max()<43)
  f=d['indices'].reshape(-1,3);v=d['POSITION']
  m=trimesh.Trimesh(vertices=v,faces=f,process=False)
  test(key+' all skinned surfaces watertight',m.is_watertight)
  test(key+' consistent face winding',m.is_winding_consistent)
  weld=a.wrist_weld_metadata
  test(key+' both wrist bridges present',set(weld['sides'])=={'L','R'} and all(x['support_loops']==4 for x in weld['sides'].values()))
  test(key+' topology has no external old cap geometry',weld['watertight'] and weld['winding_consistent'])
  edges=np.unique(np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]],axis=0),axis=1),axis=0)
  lens=np.linalg.norm(v[edges[:,0]]-v[edges[:,1]],axis=1)
  # New wrist support loops + newly clipped hand vertices appended after v1.9.
  from build_v19 import Actor as Old
  previous_count=len(Old(key).data['POSITION']);sw=np.any(edges>=previous_count,axis=1)
  root_shoe=[n for n in a.ranges if ('shoe' in n or 'sole' in n)]
  shoe_idx=np.hstack([np.arange(*a.ranges[n]) for n in root_shoe]);rest_shoe=a.deform(0)[shoe_idx]
  foot_errors=[];bone_errors=[];wrist_stretch=[];global_stretch=[];nonfinite=[]
  for frame in range(125):
    t=frame/24;posed=a.deform(t)
    nonfinite.append(not np.isfinite(posed).all());foot_errors.append(float(np.linalg.norm(posed[shoe_idx]-rest_shoe,axis=1).max()))
    transformed=a.posed_matrices(t)
    world={name: transformed[i,:3,:3]@a.rest[name]+transformed[i,:3,3] for i,name in enumerate(a.names)}
    bone_errors.append(max(abs(np.linalg.norm(world[n]-world[p])-np.linalg.norm(a.rest[n]-a.rest[p])) for n,p in a.parents.items() if p))
    l2=np.linalg.norm(posed[edges[:,0]]-posed[edges[:,1]],axis=1)
    r=l2/np.maximum(lens,1e-7)
    wrist_stretch.append(float(r[sw].max()));global_stretch.append(float(r.max()))
  test(key+' finite skinning all 125 frames',not any(nonfinite))
  test(key+' planted feet stay under 1mm drift all 125 frames',max(foot_errors)<.001,max(foot_errors))
  test(key+' parent-child lengths preserved all 125 frames',max(bone_errors)<1e-5,max(bone_errors))
  test(key+' new wrist support edges never stretch beyond 2.5x',max(wrist_stretch)<2.5,max(wrist_stretch))
  # Global edge stretch includes fingertips, clothing and face; report as-is.
  print('GLOBAL EDGE STRETCH',key,max(global_stretch),flush=True)
  metrics[key]={'mesh_vertices':len(v),'triangles':len(f),'mesh_components':len(m.split(only_watertight=False)),
    'wrist_support_edges':int(sw.sum()),'wrist_support_max_edge_stretch':max(wrist_stretch),
    'global_max_edge_stretch':max(global_stretch),'foot_drift_max_m':max(foot_errors),
    'bone_length_error_m':max(bone_errors),'finger_vertices_reweighted':weld['smooth_digit_weight_vertices'],
    'previous_v19_vertices':previous_count,'wrist_metadata':weld}
  print(key,'structural checks complete',flush=True)
# Check every encoded frame for opposing palm/finger triangle intersections.
handline=[]
for frame in sorted(set(range(0,125,5))|{124}):
   r=hand_measure(actors['ava'],actors['noor'],frame/24,z=.039);r['frame']=frame
   handline.append(r)
   if frame%25==0:print('palm contact frame',frame,'hits',r['triangle_intersections'],flush=True)
test('no opposing finger/palm collision at 26 encoded frame samples',all(r['triangle_intersections']==0 for r in handline),[(r['frame'],r['triangle_intersections']) for r in handline if r['triangle_intersections']])
test('last encoded frame fingers within 4mm',handline[-1]['nearest_vertices_m']<.004,handline[-1]['nearest_vertices_m'])
# Independent expanded geometry sampling also includes new wrist bridges and forearms.
frame_ids=[0,50,81,114,124]
armlist=[]
for frame in frame_ids:
   r=arm_measure(actors['ava'],actors['noor'],frame/24,z=.039);r['frame']=frame
   armlist.append(r)
   print('full distal arm frame',frame,'hits',r['hits'],flush=True)
test('no collisions including wrist bridges and forearms at sampled frames',all(r['hits']==0 for r in armlist),[(r['frame'],r['hits']) for r in armlist if r['hits']])
metrics['contact']={'palm_samples':26,'distal_arm_samples':len(armlist),'noor_depth_offset_m':.039,
    'min_gap_final_m':handline[-1]['nearest_vertices_m'],
    'gap_at_3_4_s_m':hand_measure(actors['ava'],actors['noor'],3.4,z=.039)['nearest_vertices_m'],
    'palm_timeline':handline,'arm_timeline':armlist}
mouth=json.loads((ROOT/'qa'/'mouth_comparison_v21.json').read_text())
for key in ('ava','noor'):
    old=mouth[key]['v20']['mouth_cavity_v16']['worst_stretch_x']
    new=mouth[key]['v21']['mouth_cavity_v16']['worst_stretch_x']
    test(key+' revised mouth cavity max stretch under 2.5x across 125 frames',new<2.5,{'old':old,'new':new})
    test(key+' improved mouth cavity over v2.0',new<old,{'old':old,'new':new})
metrics['mouth_morph_comparison']=mouth
full_hand=json.loads((ROOT/'qa'/'ALL_125_HAND_COLLISION_v21.json').read_text())
test('all 125 encoded frames opposing hand surface triangle intersections',
    full_hand['frames_checked']==125 and full_hand['zero_opposing_triangle_intersections'] is True,
    {'frames_checked':full_hand['frames_checked'],'scope':'opposing hands only'})
metrics['full_hand_collision_frames']=full_hand['frames_checked']
cap=cv2.VideoCapture(str(ROOT/'previews'/'Ava_Noor_v21_MOUTH_REPAIR_GRIP.mp4'))
first=None;middle=None;last=None;count=0
while True:
  okay,im=cap.read()
  if not okay:break
  if first is None:first=im.copy()
  if count==62:middle=im.copy()
  last=im;count+=1
cap.release()
test('MP4 125 fully decoded frames',count==125,count)
test('MP4 vertical 540x960',first is not None and first.shape[:2]==(960,540))
test('MP4 frames show actual scene changes',middle is not None and float(np.mean(cv2.absdiff(first,middle)))>2.)
metrics['video_frames']=count
report={'version':'2.1','checks':checks,'pass_count':sum(int(x['pass']) for x in checks),'total_count':len(checks),
  'failures':failures,'measured':metrics,
  'engine_tested':False,
  'limitations':['No Godot executable: Godot project/animation import NOT tested',
  'Unresolved: contact remains mostly a touch/high-five, not verified as natural finger wrapping',
  'Facial cavity mouth morph has reduced measured stretch but simplified lips still lack true mouth-corner anatomical topology',
  'Opposing hand triangle collision covered all 125 encoded frames; wider distal arms sampled 5 frames; self-collision, clothing intersections and pressure grip not verified',
  'Numerical triangle stretching does not establish beautiful animation, facial performance, or realistic anatomy'],
  'actual_design_iterations':{'wrist_topology_rebuilds':0,'mouth_morph_redesign_passes':2,'finger_curl_profiles_rendered':4,'wrist_orientation_variants_rendered':5,'rendered_full_v21_clips':1}}
(ROOT/'qa'/'validation_v21.json').write_text(json.dumps(report,indent=2))
print('VALIDATION',report['pass_count'],'/',report['total_count'],'failures',failures,flush=True)
if failures:sys.exit(1)
