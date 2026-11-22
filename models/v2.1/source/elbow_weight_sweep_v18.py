"""20 numeric skin-weight candidates on retopo; NOT 20 full artistic iterations."""
import json,numpy as np
from build_v18 import Actor,ROOT,smoothstep
from probe_elbow_quality_v18 import check

def set_weights(a,side,band, wrist_zone,base_i,base_w):
    a.data['JOINTS_0'][:]=base_i;a.data['WEIGHTS_0'][:]=base_w
    p=a.data['POSITION'];scale=a.rest['shoulder_R'][0]/.178
    cut=a.retopo_meta[side]['cut_height_m'];sign=1 if side=='R' else -1
    y_el=a.rest['elbow_'+side][1];y_wr=a.rest['wrist_'+side][1]
    mask=(sign*p[:,0]>.155*scale)&(p[:,1]<cut+2e-5)&(p[:,1]>y_wr-.05*scale)
    loc=np.where(mask)[0];y=p[loc,1]
    lower=1-smoothstep(y_el-band*scale,y_el+band*scale,y)
    distal=1-smoothstep(y_wr+.012*scale,y_wr+wrist_zone*scale,y)
    ww=np.stack([1-lower,lower*(1-distal),lower*distal],axis=1)
    ww/=ww.sum(axis=1,keepdims=True)
    a.data['JOINTS_0'][loc,:]=0;a.data['WEIGHTS_0'][loc,:]=0
    a.data['JOINTS_0'][loc,:3]=[a.names.index('shoulder_'+side),a.names.index('elbow_'+side),a.names.index('wrist_'+side)]
    a.data['WEIGHTS_0'][loc,:3]=ww

def run():
    out={}
    for key,side in [('ava','R'),('noor','L')]:
        a=Actor(key);base_i=a.data['JOINTS_0'].copy();base_w=a.data['WEIGHTS_0'].copy();rows=[]
        for band in [.035,.045,.055,.065,.075]:
            for zone in [.075,.100,.125,.150]:
                set_weights(a,side,band,zone,base_i,base_w)
                m=check(a,3.4,side)
                m['band_m']=band;m['wrist_zone_m']=zone
                # Reject elbow folding and over expansion. Inversion risk priority, but compression is not ignored.
                m['score']=(3*m['suspicious_normal_fraction']+2*m['severely_compressed_area_fraction']+
                    .5*m['overexpanded_area_fraction']+max(0,.25-m['p1_area_ratio'])*.1)
                rows.append(m)
        rows.sort(key=lambda x:x['score'])
        out[key]={'best':rows[0],'all':rows}
        print(key,'BEST',rows[0],flush=True)
    (ROOT/'qa'/'20_WEIGHT_CANDIDATES_PER_ACTOR.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':run()
