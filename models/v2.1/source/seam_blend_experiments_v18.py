"""Measured parameter probes on actual skinned ring mesh. Not visual iterations."""
import json,numpy as np
from build_v18 import Actor,ROOT
from probe_elbow_quality_v18 import check
out={}
for key,side in [('ava','R'),('noor','L')]:
 a=Actor(key)
 f=a.data['indices'].reshape(-1,3)[a.upper_body_face_start:]
 E=np.unique(np.sort(np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[0,2]]]),axis=1),axis=0)
 V=a.data['POSITION'];r=np.linalg.norm(V[E[:,0]]-V[E[:,1]],axis=1)
 arr=[]
 for fade in [.015,.02,.025,.03,.035,.045,.055,.063]:
  Actor.SEAM_FADE=fade
  j,w=a.body_weights(a.new_mesh_vertices)
  a.data['JOINTS_0'][a.upper_body_vertex_start:]=j
  a.data['WEIGHTS_0'][a.upper_body_vertex_start:]=w
  m=check(a,3.4,side)
  P=a.deform(3.4);d=np.linalg.norm(P[E[:,0]]-P[E[:,1]],axis=1)/(r+1e-10)
  m.update({'seam_fade_m':fade,'max_edge_stretch':float(d.max()),'num_edges_over_2_5':int(np.sum(d>2.5))})
  print(key,'seam',fade,'bad normal',m['suspicious_normal_count'],'compress',round(m['severely_compressed_area_fraction'],3),'maxstretch',round(m['max_edge_stretch'],2),'bad edges',m['num_edges_over_2_5'],flush=True)
  arr.append(m)
 out[key]=arr
(ROOT/'qa'/'SEAM_WEIGHT_EXPERIMENTS.json').write_text(json.dumps(out,indent=2))
