#!/usr/bin/env python3
"""Independent v1.9 validation with exact opposing-hand triangle intersection checks.

Geometry checks and CPU renders are NOT Godot import proof or an artistic pass.
"""
import pathlib,sys,json,hashlib, subprocess
import numpy as np,cv2,trimesh
from build_v19 import Actor, ROOT
from build_v16 import read_glb,NAMES
from contact_sweep_v19 import measures
from scipy.spatial import cKDTree
QA=ROOT/'qa';QA.mkdir(exist_ok=True)
checks=[];metrics={};warnings=[]
def check(n,ok,value=None):
    ok=bool(ok);checks.append({'name':n,'passed':ok,'measurement':value})
    if not ok: print('FAIL',n,value,flush=True)
    return ok
actors={k:Actor(k) for k in ('ava','noor')}
times=np.linspace(0,5.19,25)
for key,actor in actors.items():
    j,b=read_glb(ROOT/'models'/f'{key}_CONTINUOUS_HANDS_v1_9.glb')
    parsed=trimesh.load(ROOT/'models'/f'{key}_CONTINUOUS_HANDS_v1_9.glb',force='scene',process=False)
    check(key+' third-party GLB parse',len(parsed.geometry)==1,len(parsed.geometry))
    check(key+' 43-bone skeleton',len(j['skins'][0]['joints'])==43 and len(actor.names)==43)
    check(key+' 8 morph targets',len(j['meshes'][0]['primitives'][0]['targets'])==8)
    check(key+' preserved speech and finger rotation tracks',sum(c['target']['path']=='rotation' for c in j['animations'][0]['channels'])==25)
    check(key+' all weights normalized',np.allclose(actor.data['WEIGHTS_0'].sum(1),1,atol=1e-5))
    check(key+' bone ids valid',actor.data['JOINTS_0'].max()<43)
    check(key+' head-neck hierarchy',actor.parents['head']=='neck_top' and actor.parents['neck_top']=='neck_base')
    check(key+' no deleted finger capsule range left',all(not n.endswith(('_prox_v14','_dist_v14','_nail_v14')) for n in actor.ranges))
    for side in ('L','R'):
        hand=actor.hand_geometry[side]
        check(f'{key}/{side} one continuous watertight hand surface',hand.is_watertight and len(hand.split(only_watertight=False))==1)
        check(f'{key}/{side} positive hand volume',hand.volume>0)
        check(f'{key}/{side} finite hand coordinates',np.isfinite(hand.vertices).all())
        check(f'{key}/{side} hand topology > 1000 triangles',len(hand.faces)>1000,len(hand.faces))
    check(key+' upperbody remains watertight',trimesh.load(ROOT/'models'/f'{key}_continuous_upperbody_RETOPO_v19.ply',process=False).is_watertight)
    footnames=[n for n in actor.ranges if ('shoe' in n or 'sole' in n)]
    foot=np.hstack([np.arange(*actor.ranges[n]) for n in footnames]);origin=actor.deform(0)[foot]
    drift=[];boneerr=[];finite=[]
    for t in times:
        posed=actor.deform(float(t));finite.append(bool(np.isfinite(posed).all()))
        drift.append(float(np.linalg.norm(posed[foot]-origin,axis=1).max()))
        M=actor.posed_matrices(float(t))
        xyz={n:M[i,:3,:3]@actor.rest[n]+M[i,:3,3] for i,n in enumerate(actor.names)}
        boneerr.append(float(max(abs(np.linalg.norm(xyz[n]-xyz[p])-np.linalg.norm(actor.rest[n]-actor.rest[p])) for n,p in actor.parents.items() if p is not None)))
    check(key+' finite skinning 25 samples',all(finite))
    check(key+' planted foot max drift <1mm',max(drift)<.001,max(drift))
    check(key+' 43-bone hierarchy lengths preserved',max(boneerr)<1e-5,max(boneerr))
    metrics[key]={'vertices':int(len(actor.data['POSITION'])),'triangles':int(len(actor.data['indices'])//3),
                  'rest_hand_triangles':{s:int(len(actor.hand_geometry[s].faces)) for s in ['L','R']},
                  'max_foot_drift_m':max(drift),'max_bone_length_error_m':max(boneerr)}
# Contact validation uses VTK triangle-triangle tests, rather than closest vertex alone.
results=[]
for i,t in enumerate(times):
    r=measures(actors['ava'],actors['noor'],float(t),z=.038)
    r['sample']=i+1;results.append(r)
    print('contact',i+1,'/',len(times),'t',round(float(t),2),'intersections',r['triangle_intersections'],flush=True)
check('all 25 sampled times have zero opposing-hand triangle intersections',all(r['triangle_intersections']==0 for r in results),[x for x in results if x['triangle_intersections']])
check('at final handhold geometry distance below 4mm',results[-1]['nearest_vertices_m']<.004,round(results[-1]['nearest_vertices_m'],5))
metrics['contact']={'noor_z_offset_m':.038,'tested_times':25,'timeline':results,
  'min_gap_last_sample_m':results[-1]['nearest_vertices_m'],
  'gap_at_3_4_s_m':measures(actors['ava'],actors['noor'],3.4,z=.038)['nearest_vertices_m']}
# Rest topology and sampled collision are necessary but do not establish natural grasp.
video=ROOT/'previews'/'Ava_Noor_v19_CONTINUOUS_HANDS.mp4'
cap=cv2.VideoCapture(str(video));count=0;first=None;middle=None;last=None
while True:
 ok,im=cap.read()
 if not ok:break
 if first is None:first=im.copy()
 if count==62:middle=im.copy()
 last=im;count+=1
cap.release()
check('MP4 exactly 125 decoded frames',count==125,count)
check('MP4 dimensions 540x960',first is not None and first.shape[:2]==(960,540))
check('encoded motion changes across shot',middle is not None and float(np.mean(cv2.absdiff(first,middle)))>2)
metrics['video_frames']=count
warnings=[
  'Godot is not installed in this environment: real editor import and playback not executed.',
  'Opposing-hand collision tests were run at 25 samples; not every rendered subframe.',
  'Mid-hold surface gap at 3.4s remains ~10mm; late contact is close, but the gesture does not read as a natural finger grasp at all angles.',
  'Hands form separate watertight meshes and overlap the forearm at the wrist; they are not welded to the torso/arm surface.',
  'Finger phalanges are only two per finger; sculpted knuckles, realistic nail beds and physical skin contact are unfinished.',
  'Production Sims-like facial and clothing fidelity still not achieved.',
  '25 timeline collision samples are not 25 independent artistic redesigns or research sample annotations.'
]
report={'version':'1.9','result':{'passed':sum(c['passed'] for c in checks),'total':len(checks)},
 'checks':checks,'metrics':metrics,'unresolved':warnings,'godot_engine_tested':False,
 'iteration_count':{'geometry_rebuilds':2,'fixed_staging_candidates':13,'timeline_collision_samples':25,'independent_artistic_redesigns':1}}
(QA/'validation_v19.json').write_text(json.dumps(report,indent=2))
print('VALIDATION',report['result']['passed'],'/',report['result']['total'])
if report['result']['passed']!=report['result']['total']:sys.exit(1)
