"""Side-by-side v1.7 vs v1.8 skinning proxies, not artistic or collision proof."""
import sys,json,numpy as np
from pathlib import Path
from build_v17 import Actor as Old
from build_v18 import Actor as New,ROOT

def check(a, t, side):
    f=a.data['indices'].reshape(-1,3)[a.upper_body_face_start:]
    V=a.data['POSITION']
    ctr=V[f].mean(axis=1); s=1 if side=='R' else -1;ey=a.rest['elbow_'+side][1]
    ix=(s*ctr[:,0]>.155) & (np.abs(ctr[:,1]-ey)<.105)
    f=f[ix];w=a.expression(t)
    rest=V.copy()
    for ww,n in zip(w,a.morphs):rest+=ww*a.morphs[n]
    posed=a.deform(t)
    n0=np.cross(rest[f[:,1]]-rest[f[:,0]],rest[f[:,2]]-rest[f[:,0]])
    n1=np.cross(posed[f[:,1]]-posed[f[:,0]],posed[f[:,2]]-posed[f[:,0]])
    r=np.linalg.norm(n0,axis=1)+1e-12;d=np.linalg.norm(n1,axis=1)
    ratio=d/r
    M=a.posed_matrices(t);bone_id=a.data['JOINTS_0'];weight=a.data['WEIGHTS_0'];R=np.zeros((len(rest),3,3),np.float64)
    for i in range(4):R+=weight[:,i,None,None]*M[bone_id[:,i],:3,:3]
    er=(R[f[:,0]]+R[f[:,1]]+R[f[:,2]])/3
    expected=np.einsum('nij,nj->ni',er,n0)
    cos=np.sum(expected*n1,axis=1)/(np.linalg.norm(expected,axis=1)*d+1e-12)
    return {'triangles':len(f),'suspicious_normal_count':int(np.sum(cos<-.1)),
       'suspicious_normal_fraction':float(np.mean(cos<-.1)),
       'severely_compressed_area_fraction':float(np.mean(ratio<.25)),
       'p1_area_ratio':float(np.percentile(ratio,1)),'min_area_ratio':float(ratio.min()),
       'overexpanded_area_fraction':float(np.mean(ratio>2.0))}

def main():
    results={}
    for key,side in [('ava','R'),('noor','L')]:
        old=Old(key);new=New(key)
        results[key]={'old':{},'new':{}}
        for label,a in [('old',old),('new',new)]:
            for t in [0,1.5,2.5,3.4,4.33,5.2]:
                res=check(a,t,side)
                results[key][label][str(t)]=res
                print(key,label,t,res,flush=True)
    (ROOT/'qa'/'ELBOW_BEFORE_AFTER_METRICS.json').write_text(json.dumps(results,indent=2))
if __name__=='__main__':main()
