import sys,numpy as np,json
from scipy.spatial.transform import Rotation
from build_v17 import Actor,NAMES,ROOT

def quality(a,t):
 f=a.data['indices'].reshape(-1,3)[a.upper_body_face_start:]
 weights=a.expression(t)
 rest=a.data['POSITION'].copy()
 for w,nm in zip(weights,NAMES):rest+=w*a.morphs[nm]
 p=a.deform(t);ref=np.cross(rest[f[:,1]]-rest[f[:,0]],rest[f[:,2]]-rest[f[:,0]])
 out=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]])
 matrices=a.posed_matrices(t)
 id=a.data['JOINTS_0'];wg=a.data['WEIGHTS_0']
 rot=np.zeros((len(rest),3,3),dtype=float)
 for j in range(4):rot+=wg[:,j,None,None]*matrices[id[:,j],:3,:3]
 meanrot=(rot[f[:,0]]+rot[f[:,1]]+rot[f[:,2]])/3
 exp=np.einsum('nij,nj->ni',meanrot,ref)
 ar=np.linalg.norm(ref,axis=1);ao=np.linalg.norm(out,axis=1)
 cos=np.sum(exp*out,axis=1)/(np.linalg.norm(exp,axis=1)*ao+1e-12)
 return {'inversion_count':int(np.sum(cos<-.1)), 'compression_faces_under_25pct':int(np.sum(ao/ar<.25)), 'min_area_ratio':float(np.min(ao/ar)), 'p1_area_ratio':float(np.percentile(ao/ar,1)), 'median_ratio':float(np.median(ao/ar))}

def delta(a,amplitude,kind):
 elbow=a.rest['elbow_R' if a.key=='ava' else 'elbow_L'];sign=1 if a.key=='ava' else -1
 xyz=a.data['POSITION']; s=a.upper_body_vertex_start; x=xyz[s:];v=x-elbow
 envelope=np.exp(-((v[:,1])/.05)**2)*np.exp(-((v[:,0])/.09)**2)
 move=np.zeros_like(x)
 if kind=='radial':
  rad=v[:,[0,2]].copy();norm=np.linalg.norm(rad,axis=1)+1e-7; rad/=norm[:,None]
  move[:,0]=rad[:,0]*envelope*amplitude
  move[:,2]=rad[:,1]*envelope*amplitude
 if kind=='side':move[:,0]=sign*envelope*amplitude
 if kind=='front':move[:,2]=envelope*amplitude
 if kind=='long':move[:,1]=(-np.sign(v[:,1]))*envelope*amplitude
 if kind=='spread':move[:,1]=np.sign(v[:,1])*envelope*amplitude
 if kind=='corner':move[:,0]=sign*envelope*amplitude;move[:,2]=envelope*amplitude/2
 return move

rows=[]
for name in ('ava','noor'):
 a=Actor(name)
 baseline=quality(a,3.4)
 rows.append({'key':name,'kind':'baseline','amp':0,**baseline})
 saved=a.morphs['cloth_reach'].copy()
 for kind in ['radial','side','front','long','spread','corner']:
  for amp in [.005,.012,.020]:
   a.morphs['cloth_reach']=saved.copy()
   a.morphs['cloth_reach'][a.upper_body_vertex_start:]+=delta(a,amp,kind)
   res=quality(a,3.4)
   rows.append({'key':name,'kind':kind,'amp':amp,**res})
   print(name,kind,amp,res['inversion_count'],res['compression_faces_under_25pct'],flush=True)
 a.morphs['cloth_reach']=saved
(ROOT/'qa'/'ELBOW_CORRECTIVE_EXPERIMENTS.json').write_text(json.dumps(rows,indent=2))
for k in ('ava','noor'):
 print(k,'TOP OPTIONS',sorted([r for r in rows if r['key']==k],key=lambda r:(r['inversion_count'],r['compression_faces_under_25pct']))[:5])
