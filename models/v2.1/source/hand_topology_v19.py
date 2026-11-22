"""Produce one skinnable, contiguous anatomical hand surface per side.

This is procedural reference geometry, NOT a Blender-sculpted hand.
Reference landmarks come from the existing measured rig; all dimensions in meters.
"""
import numpy as np
import trimesh
from skimage.measure import marching_cubes
from scipy.ndimage import gaussian_filter
from build_v17 import smooth_min, smoothstep

def ellipsoid(X,Y,Z,center,radius):
    d=np.sqrt(((X-center[0])/radius[0])**2+((Y-center[1])/radius[1])**2+((Z-center[2])/radius[2])**2)-1
    return d*min(radius)

def tapered_capsule(X,Y,Z,a,b,ra,rb):
    a=np.asarray(a);b=np.asarray(b);D=b-a
    t=np.clip(((X-a[0])*D[0]+(Y-a[1])*D[1]+(Z-a[2])*D[2])/(D@D),0,1)
    dist=np.sqrt((X-a[0]-t*D[0])**2+(Y-a[1]-t*D[1])**2+(Z-a[2]-t*D[2])**2)
    return dist-(ra*(1-t)+rb*t)

def generate(a,side,spacing=.0022):
    s=a.rest['shoulder_R'][0]/.178
    sign=1 if side=='R' else -1
    H=a.rest['hand_'+side];cx,hy,hz=H
    # Anatomical relations: palm narrower at wrist, distinct knuckles, four tapered
    # fingers with graduated lengths and an opposable angled thumb.
    x=np.arange(cx-.064*s,cx+.065*s,spacing*s,dtype=np.float32)
    y=np.arange(hy-.110*s,hy+.110*s,spacing*s,dtype=np.float32)
    z=np.arange(hz-.043*s,hz+.070*s,spacing*s,dtype=np.float32)
    X=x[:,None,None];Y=y[None,:,None];Z=z[None,None,:]
    field=ellipsoid(X,Y,Z,[cx,hy+.003*s,hz],[.026*s,.038*s,.0175*s])
    wrist=tapered_capsule(X,Y,Z,[cx,hy+.056*s,hz-.004*s],[cx,hy+.009*s,hz],.022*s,.024*s)
    field=smooth_min(field,wrist,.009*s)
    knuckle=tapered_capsule(X,Y,Z,[cx-.018*s,hy-.027*s,hz+.005*s],
                             [cx+.018*s,hy-.027*s,hz+.005*s],.016*s,.014*s)
    field=smooth_min(field,knuckle,.006*s)
    finger_info=[]
    for i in range(4):
        base=a.rest[f'{side}_finger{i}_base'];second=a.rest[f'{side}_finger{i}_tip']
        xx=base[0]; yy=base[1]+.009*s
        # Keep each digit attached to its knuckle; longer middle/ring than pinky.
        length=[.049,.060,.057,.045][i]*s
        P0=np.array([xx,yy,hz+.012*s]);P1=np.array([xx,yy-.54*length,hz+.022*s]);P2=np.array([xx,yy-length,hz+.027*s])
        field=smooth_min(field,tapered_capsule(X,Y,Z,P0,P1,.0083*s,.0068*s),.0033*s)
        field=smooth_min(field,tapered_capsule(X,Y,Z,P1,P2,.0068*s,.0046*s),.0024*s)
        finger_info.append({'index':i,'root':P0.tolist(),'knuckle':P1.tolist(),'tip':P2.tolist(),
                            'bone_base_y':float(base[1]),'bone_tip_y':float(second[1])})
    # The thumb extends diagonally across the hand, as its existing rig specifies.
    tx=cx+sign*.020*s
    T0=np.array([tx,hy+.005*s,hz+.004*s]);T1=np.array([cx+sign*.043*s,hy-.013*s,hz+.015*s]);T2=np.array([cx+sign*.052*s,hy-.037*s,hz+.024*s])
    field=smooth_min(field,tapered_capsule(X,Y,Z,T0,T1,.011*s,.0085*s),.007*s)
    field=smooth_min(field,tapered_capsule(X,Y,Z,T1,T2,.0085*s,.006*s),.003*s)
    field=gaussian_filter(field,.47)
    verts,faces,_,_=marching_cubes(field,0,spacing=(spacing*s,)*3)
    verts=verts+np.array([x[0],y[0],z[0]])
    m=trimesh.Trimesh(vertices=verts,faces=faces,process=False)
    if m.volume<0:faces=faces[:,::-1].copy();m=trimesh.Trimesh(vertices=verts,faces=faces,process=False)
    assert m.is_watertight and len(m.split(only_watertight=False))==1,(side,m.is_watertight)
    assert m.volume>0
    names=a.names;bone=lambda name:names.index(name)
    weights=np.zeros((len(verts),len(names)),dtype=np.float32)
    xx,yy,zz=verts.T
    # Connected palms inherit the hand bone; digits smoothly blend into two phalange bones.
    thumb_mask=(sign*(xx-cx)>.028*s)&(yy<hy+.008*s)&(yy>hy-.064*s)
    others=~thumb_mask
    centers=np.array([a.rest[f'{side}_finger{i}_base'][0] for i in range(4)])
    fi=np.argmin(np.abs(xx[others,None]-centers[None,:]),axis=1)
    remaining_idx=np.where(others)[0]
    for i in range(4):
        idx=remaining_idx[fi==i]
        base=a.rest[f'{side}_finger{i}_base'];second=a.rest[f'{side}_finger{i}_tip']
        u=1-smoothstep(base[1]-.018*s,base[1]+.008*s,yy[idx]);v=1-smoothstep(second[1]-.012*s,second[1]+.012*s,yy[idx])
        weights[idx,bone('hand_'+side)]=1-u
        weights[idx,bone(f'{side}_finger{i}_base')]=u*(1-v)
        weights[idx,bone(f'{side}_finger{i}_tip')]=u*v
    idx=np.where(thumb_mask)[0];u=smoothstep(.027*s,.052*s,sign*(xx[idx]-cx));v=smoothstep(.035*s,.060*s,sign*(xx[idx]-cx))
    weights[idx,bone('hand_'+side)]=1-u
    weights[idx,bone(f'{side}_thumb_prox')]=u*(1-v)
    weights[idx,bone(f'{side}_thumb_tip')]=u*v
    # Explicitly limit influences to four glTF-weight slots and normalize.
    order=np.argsort(weights,axis=1)[:,-4:][:,::-1]
    vals=np.take_along_axis(weights,order,axis=1)
    vals=vals/np.maximum(vals.sum(axis=1,keepdims=True),1e-7)
    col=np.zeros((len(verts),4),np.uint8)
    pl=a.ranges[f'{side}_hand_palm_v14'];col[:]=np.median(a.data['COLOR_0'][pl[0]:pl[1]],axis=0).astype(np.uint8)
    col[:,3]=255
    mesh=trimesh.Trimesh(vertices=verts,faces=faces,process=False)
    metadata={'watertight':bool(mesh.is_watertight),'components':len(mesh.split(only_watertight=False)),
              'volume_m3':float(mesh.volume),'vertices':int(len(verts)),'triangles':int(len(faces)),
              'voxel_m':float(spacing*s),'finger_info':finger_info,
              'boundary':'Hand is one watertight connected surface, attached visually at wrist, not welded to the upper body',
              'limitation':'Procedural approximated hand with existing two-phalange finger bones, not sculpted anatomy.'}
    return {'POSITION':verts.astype('<f4'),'NORMAL':mesh.vertex_normals.astype('<f4'),
            'COLOR_0':col,'JOINTS_0':order.astype('<u2'),'WEIGHTS_0':vals.astype('<f4'),
            'faces':faces.astype('<u4'),'metadata':metadata}
