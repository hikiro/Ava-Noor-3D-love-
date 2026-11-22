#!/usr/bin/env python3
"""Generate a read-only evidence packet directly from Villa Verse v2.1 artifacts."""
from pathlib import Path
import json, hashlib, os, sys
PROJECT=Path(__file__).resolve().parents[1]
BASE=Path(os.environ.get('VV_BASE','/mnt/data/VillaVerse_Models_v2_1'))

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def main():
 qa=BASE/'qa'; v=json.loads((qa/'validation_v21.json').read_text()); c=json.loads((qa/'ALL_125_HAND_COLLISION_v21.json').read_text()); m=json.loads((qa/'mouth_comparison_v21.json').read_text());
 movie=BASE/'previews/Ava_Noor_v21_MOUTH_REPAIR_GRIP.mp4'
 try:
  import cv2
  cap=cv2.VideoCapture(str(movie)); assert cap.isOpened();frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS);width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT));cap.release()
 except Exception as e:
  raise RuntimeError('Video metadata verification failed: '+str(e))
 assert v['total_count']==len(v['checks']) and v['pass_count']==sum(bool(a['pass']) for a in v['checks']);assert frames==c['frames_checked']==c['frames_expected']
 nearest=[r['nearest_vertices_m']*1000 for r in c['collision_records'] if 75<=r['frame']<=100]
 result={'experiment':'VV_MULTI_AGENT_EXP01','baseline':'Villa Verse v2.1','verified_metrics':{
 'structural_checks':len(v['checks']), 'structural_passed':sum(x['pass'] for x in v['checks']),
 'hand_collision_frames_checked':c['frames_checked'],'hand_intersection_count':sum(x['hits'] for x in c['collision_records']),
 'hold_frames_examined':'75–100','nearest_hand_vertices_median_mm':round(sorted(nearest)[len(nearest)//2],3),
 'mouth_stretch_v21':{k:round(m[k]['v21']['mouth_cavity_v16']['worst_stretch_x'],3) for k in ('ava','noor')},
 'mouth_stretch_v20':{k:round(m[k]['v20']['mouth_cavity_v16']['worst_stretch_x'],3) for k in ('ava','noor')},
 'video_frames':frames,'video_fps':fps,'width':width,'height':height,
 'native_godot_playback_verified':bool(v.get('engine_tested'))},
 'documented_open_visual_issues':['natural interlocking hand grasp not visually approved','simplified finger and facial anatomy','detached-looking lip layers','Godot native playback not tested'],
 'source_checksums':{str(p.relative_to(BASE)):sha(p) for p in [qa/'validation_v21.json',qa/'ALL_125_HAND_COLLISION_v21.json',qa/'mouth_comparison_v21.json',movie]}}
 out=PROJECT/'evidence/v21_evidence.json';out.write_text(json.dumps(result,indent=2)+'\n');os.chmod(out,0o444)
 print(json.dumps({'evidence':str(out),'sha256':sha(out),'source_count':len(result['source_checksums'])}))
if __name__=='__main__':main()
