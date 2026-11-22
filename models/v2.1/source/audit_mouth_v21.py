import numpy as np, json, pathlib
from build_v20 import Actor as Old
from build_v21 import Actor as New
from build_v16 import NAMES
from build_v19 import QA

def test(actor):
    d=actor.data;p=d['POSITION'];faces=d['indices'].reshape(-1,3)
    times=np.arange(125)/24
    result={}
    for part in ['upper_lip_contour_v15','lower_lip_contour_v15','mouth_cavity_v16']:
        lo,hi=actor.ranges[part];tri=faces[np.all((faces>=lo)&(faces<hi),axis=1)]
        edges=np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]],axis=0)
        rest=np.linalg.norm(p[edges[:,0]]-p[edges[:,1]],axis=1)
        stretch=[];compression=[]
        for t in times:
            x=p.copy()
            w=actor.expression(t)
            for i,n in enumerate(NAMES):
                if np.any(actor.morphs[n][lo:hi]):x[lo:hi]+=w[i]*actor.morphs[n][lo:hi]
            length=np.linalg.norm(x[edges[:,0]]-x[edges[:,1]],axis=1)
            ratios=length/np.maximum(rest,1e-8)
            stretch.append(float(np.max(ratios)))
            compression.append(float(np.min(ratios)))
        result[part]={'frames':125,'worst_stretch_x':float(max(stretch)),
            'minimum_edge_ratio_x':float(min(compression)),
            'worst_stretch_frame':int(np.argmax(stretch)), 'rest_min_edge_mm':float(min(rest)*1000)}
    return result
if __name__=='__main__':
    out={}
    for k in ['ava','noor']:
        print('auditing',k,flush=True)
        old=Old(k);new=New(k)
        out[k]={'v20':test(old),'v21':test(new)}
        print(k,'OLD cavity max',out[k]['v20']['mouth_cavity_v16']['worst_stretch_x'],
                    'NEW cavity max',out[k]['v21']['mouth_cavity_v16']['worst_stretch_x'],flush=True)
    (QA/'mouth_comparison_v21.json').write_text(json.dumps(out,indent=2))
