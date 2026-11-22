"""Pose-space elbow volume correction approximating dual-quaternion skinning at t=3.4.
Uses original 43-bone LBS skeleton/glTF and drives corrective through cloth_reach morph.
This is a single target-pose correction, NOT a general DQS Godot runtime shader.
"""
import numpy as np
from scipy.spatial.transform import Rotation
from build_v16 import NAMES

def qmul(a,b):
    # Scalar-last quaternions: [x,y,z,w].
    v1,w1=a[...,:3],a[...,3:];v2,w2=b[...,:3],b[...,3:]
    return np.concatenate([w1*v2+w2*v1+np.cross(v1,v2),w1*w2-np.sum(v1*v2,axis=-1,keepdims=True)],axis=-1)

def compute(a, t=3.4):
    side='R' if a.key=='ava' else 'L';sgn=1 if side=='R' else -1
    pos=a.data['POSITION'];ey=a.rest['elbow_'+side][1]
    # Restrict target to deforming mesh elbow band; no head/hand offsets.
    i=np.arange(len(pos));inside=(i>=a.upper_body_vertex_start)&(np.abs(pos[:,1]-ey)<.085)&(sgn*pos[:,0]>.17)
    ix=np.where(inside)[0]
    w_expr=a.expression(t);cloth=w_expr[NAMES.index('cloth_reach')]
    posed=pos[ix].copy()
    for ww,n in zip(w_expr,NAMES):posed+=ww*a.morphs[n][ix]
    M=a.posed_matrices(t);r=Rotation.from_matrix(M[:,:3,:3]).as_quat()
    tq=np.column_stack([M[:,:3,3],np.zeros(len(M))]);dual=.5*qmul(tq,r)
    bone=a.data['JOINTS_0'][ix];w=a.data['WEIGHTS_0'][ix]
    ref=r[bone[np.arange(len(ix)),np.argmax(w,axis=1)]]
    s=np.where((r[bone]*ref[:,None,:]).sum(axis=-1)<0,-1,1)
    qr=np.einsum('ni,nij->nj',w*s,r[bone]);qd=np.einsum('ni,nij->nj',w*s,dual[bone])
    norm=np.linalg.norm(qr,axis=-1,keepdims=True);qr=qr/norm;qd=qd/norm
    qd=qd-(qd*qr).sum(axis=-1,keepdims=True)*qr
    conjugate=np.concatenate([-qr[:,:3],qr[:,3:]],axis=-1)
    transl=2*qmul(qd,conjugate)[:,:3]
    target=Rotation.from_quat(qr).apply(posed)+transl
    matrices=M[bone];rot=matrices[:,:,:3,:3]
    A=(w[:,:,None,None]*rot).sum(axis=1)
    src=np.einsum('nij,nj->ni',A,posed)+(w[:,:,None]*matrices[:,:,:3,3]).sum(axis=1)
    desired=target-src
    delta=np.linalg.solve(A,desired[...,None])[...,0]
    envelope=np.exp(-((pos[ix,1]-ey)/.052)**4)
    # Scale by the morph's actual weight at the 3.4s reference pose.
    delta=delta*envelope[:,None]/max(float(cloth),.01)
    out=np.zeros_like(pos);out[ix]=delta
    return out,{'affected_vertices':len(ix),'max_offset_m':float(np.max(np.linalg.norm(delta,axis=1))),
                'mean_offset_m':float(np.mean(np.linalg.norm(delta,axis=1))),'target_time_s':t}
