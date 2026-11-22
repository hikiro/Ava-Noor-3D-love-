"""Check that each actual hand surface shares vertices/edges with the torso.
Warn: other outfit/face elements remain independent shells, by design.
"""
import json
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
import trimesh
from build_v20 import Actor,MODELS
from build_v19 import ROOT
out={}
for key in ('ava','noor'):
 a=Actor(key);d=a.data;V=d['POSITION'];F=d['indices'].reshape(-1,3)
 pairs=np.concatenate([F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]]);n=len(V)
 g=coo_matrix((np.ones(2*len(pairs),np.uint8),(np.r_[pairs[:,0],pairs[:,1]],np.r_[pairs[:,1],pairs[:,0]])),shape=(n,n)).tocsr()
 num,labels=connected_components(g,directed=False)
 body_label=labels[a.upper_body_vertex_start];used=np.unique(F)
 component_vertices=used[labels[used]==body_label]
 info={'body_label':int(body_label),'surface_vertices':int(len(component_vertices)),'hands':{},'used_components_total':int(len(np.unique(labels[used])))}
 for side in ('L','R'):
  lo,hi=a.ranges[f'{side}_CONTINUOUS_ANATOMICAL_HAND_v19']
  indices=used[(used>=lo)&(used<hi)]
  linked=bool(len(indices)>1000 and np.all(labels[indices]==body_label))
  info['hands'][side]={'used_vertices':len(indices),'body_welded':linked}
  assert linked,(key,side)
 selected=F[np.all(labels[F]==body_label,axis=1)]
 uniq,inv=np.unique(selected,return_inverse=True)
 mesh=trimesh.Trimesh(vertices=V[uniq],faces=inv.reshape(-1,3),process=False)
 info['merged_body_watertight']=bool(mesh.is_watertight)
 assert mesh.is_watertight
 p=MODELS/f'{key}_BODY_ARMS_HANDS_WELDED_rest_v20.ply';mesh.export(p)
 info['rest_mesh_export']=p.name
 out[key]=info
 print(key,info,flush=True)
(ROOT/'qa'/'CONTINUITY_AUDIT.json').write_text(json.dumps(out,indent=2))
