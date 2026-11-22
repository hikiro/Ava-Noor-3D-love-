#!/usr/bin/env python3
"""Villa Verse 1.7: continuous skinned upper-body surface replacing segmented torso/arms.

Preserves the v1.6 skeleton, fingers, facial morphs and source art; builds a
single watertight shoulder-to-wrist upper-body topology and smoothly blends
its influences over 43 existing bones. Removable v1.6 meshes are not drawn.
Validation of geometry and local CPU render DOES NOT imply Godot or Blender verified.
"""
from __future__ import annotations
import json, pathlib, sys, shutil, struct
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.measure import marching_cubes
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
import trimesh
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from build_v16 import Actor as BaseActor, NAMES, read_glb
ROOT=pathlib.Path(__file__).resolve().parents[1]
MODELS=ROOT/'models';QA=ROOT/'qa'

# Angular and shoulder transition geometry is parameterized to facilitate future retopology.
def smoothstep(lo,hi,v):
    t=np.clip((v-lo)/(hi-lo),0,1)
    return t*t*(3-2*t)

def smooth_min(a,b,k):
    h=np.maximum(k-np.abs(a-b),0.)/k
    return np.minimum(a,b)-h*h*k*.25

def ellipsoid(x,y,z,center,radii):
    cx,cy,cz=center;rx,ry,rz=radii
    # Correct approximate SDF (distance in meters), efficient over a dense voxel grid.
    qx=(x-cx)/rx;qy=(y-cy)/ry;qz=(z-cz)/rz
    return (np.sqrt(qx*qx+qy*qy+qz*qz)-1)*min(rx,ry,rz)

def capsule_taper(x,y,z,a,b,r0,r1):
    a=np.array(a);b=np.array(b);vec=b-a;den=np.dot(vec,vec)
    t=np.clip(((x-a[0])*vec[0]+(y-a[1])*vec[1]+(z-a[2])*vec[2])/den,0,1)
    px=a[0]+t*vec[0];py=a[1]+t*vec[1];pz=a[2]+t*vec[2]
    return np.sqrt((x-px)**2+(y-py)**2+(z-pz)**2) - (r0*(1-t)+r1*t)

class Actor(BaseActor):
    def __init__(self,key,voxel=.0075):
        super().__init__(key)
        self.source_vertex_count=len(self.data['POSITION'])
        self.voxel=voxel
        self.build_continuous_upper_body()
    def shape(self):
        # All shapes described in rest-pose meters and scale with each actor's anatomy.
        s=self.rest['shoulder_R'][0]/.178
        C=self.rest['spine_chest'][1]
        # Shape has enough overlap to remove the visible hollow under the armpit.
        dims=np.array([[-.365,.365],[.79,1.44],[-.20,.20]])
        dims[:,0]*=s;dims[:,1]*=s
        x=np.arange(dims[0,0],dims[0,1]+self.voxel/2,self.voxel,dtype=np.float32)
        y=np.arange(dims[1,0],dims[1,1]+self.voxel/2,self.voxel,dtype=np.float32)
        z=np.arange(dims[2,0],dims[2,1]+self.voxel/2,self.voxel,dtype=np.float32)
        X=x[:,None,None];Y=y[None,:,None];Z=z[None,None,:]
        # Chest, tapering waist; more volume around clavicles than waist.
        chest=ellipsoid(X,Y,Z,[0,1.23*s,0],[.170*s,.143*s,.110*s])
        waist=ellipsoid(X,Y,Z,[0,1.095*s,0],[.135*s,.165*s,.092*s])
        field=smooth_min(chest,waist,.082*s)
        for side in ('L','R'):
            shoulder=self.rest['shoulder_'+side]
            elbow=self.rest['elbow_'+side]
            wrist=self.rest['wrist_'+side]
            # Shoulder cap merges into chest, arm tapers to wrist; both elbows attached.
            cap=ellipsoid(X,Y,Z,shoulder,[.058*s,.068*s,.060*s])
            upper=capsule_taper(X,Y,Z,shoulder,elbow,.056*s,.043*s)
            fore=capsule_taper(X,Y,Z,elbow,wrist,.044*s,.029*s)
            field=smooth_min(field,cap,.041*s)
            field=smooth_min(field,upper,.027*s)
            field=smooth_min(field,fore,.016*s)
        # A low-amplitude Gaussian relaxes voxel-grid roughness without destroying silhouette.
        field=gaussian_filter(field,0.58)
        # Extract one connected watertight surface in XYZ space.
        verts,faces,normals,_=marching_cubes(field,level=0,spacing=(self.voxel,)*3)
        verts+=np.array([x[0],y[0],z[0]])
        return verts.astype('<f4'),faces.astype('<u4'),normals.astype('<f4')
    def old_removed_parts(self):
        to_remove=[]
        for name in self.ranges:
            if name.startswith(('L_continuous_deltoid','R_continuous_deltoid','L_armpit_skin','R_armpit_skin',
                                'L_continuous_forearm','R_continuous_forearm','L_subtle_elbow','R_subtle_elbow',
                                'L_wrist_transition','R_wrist_transition',
                                'ZZ_no_fitted_cuff','ZZ_no_sleeve_stitch')):
                to_remove.append(name)
            if name.startswith(('torso_','jacket_back_shell_','inner_top_','white_top_waist_extension_')):
                to_remove.append(name)
        return to_remove
    def body_weights(self,p):
        # Every point has four possible bone influences (total 4 after sorting).
        n=len(p);X=p[:,0];Y=p[:,1];Z=p[:,2]
        influence=np.zeros((n,len(self.names)),np.float32)
        upper=float(self.rest['spine_chest'][1]);lower=float(self.rest['spine_lower'][1])
        sw=smoothstep(lower+.03,upper-.03,Y)
        influence[:,self.names.index('spine_chest')]=sw
        influence[:,self.names.index('spine_lower')]=1-sw
        # Smooth, position-dependent transition from chest skinning to shoulder/arm skinning.
        for side in ('L','R'):
            index=1 if side=='R' else -1
            shoulder=self.rest['shoulder_'+side];elbow=self.rest['elbow_'+side];wrist=self.rest['wrist_'+side]
            axial=(p-shoulder)@(elbow-shoulder)/np.linalg.norm(elbow-shoulder)**2
            axial2=(p-elbow)@(wrist-elbow)/np.linalg.norm(wrist-elbow)**2
            radial=smoothstep(.095,.230,index*X)
            # Avoid influencing other side and keep central chest stationary.
            chest_w=1-radial
            influence[:,self.names.index('spine_chest')]*=chest_w
            influence[:,self.names.index('spine_lower')]*=chest_w
            a=smoothstep(.75,1.08,axial)
            b=smoothstep(.05,.89,axial2)
            # Wrist does not tug the upper torso: downstream weights scale only for distal vertices.
            elbow_phase=smoothstep(.97,1.16,axial)
            shoulder_w=(1-a)*(1-elbow_phase)
            elbow_w=a*(1-elbow_phase)+elbow_phase*(1-b)
            wrist_w=elbow_phase*b
            influence[:,self.names.index('shoulder_'+side)]+=radial*shoulder_w
            influence[:,self.names.index('elbow_'+side)]+=radial*elbow_w
            influence[:,self.names.index('wrist_'+side)]+=radial*wrist_w
            # The other-side pass needs not zero the already accumulated shoulder.
        # normalize and select max 4 influences, even around armpits.
        ix=np.argsort(influence,axis=1)[:,-4:][:,::-1].copy()
        ws=np.take_along_axis(influence,ix,axis=1)
        ws/=np.maximum(ws.sum(axis=1,keepdims=True),1.e-8)
        return ix.astype('<u2'),ws.astype('<f4')
    def classify_colors(self,p):
        # Retain recognizable costume palettes with contiguous, color-coded garment boundaries.
        P=np.zeros((len(p),4),dtype=np.uint8);P[:,3]=255
        s=self.rest['shoulder_R'][0]/.178
        if self.key=='ava':
            # Gold cowl/top and bare upper arms; body skin is warm tan.
            skin=np.array([179,113,78,255],np.uint8)
            gold=np.array([209,151,35,255],np.uint8)
            boundary=.149*s
            # Clean garment edge around armhole, not a detached mesh ring.
            in_top=(np.abs(p[:,0])<boundary) & (p[:,1]>.99*s)
            P[:]=skin;P[in_top]=gold
            # Warmer center front shading for the fabric body.
        else:
            skin=np.array([170,108,76,255],np.uint8)
            teal=np.array([29,109,109,255],np.uint8)
            # Jacket/sleeve section ends around elbow; exposed forearms remain skin.
            trunk=np.abs(p[:,0]) < .142*s
            in_jacket=(p[:,1]>1.112*s) | trunk
            P[:]=skin;P[in_jacket]=teal
            # Inner cream top remains visible between the two open front lapels.
            front=p[:,2]>.052*s
            shirt=front & (np.abs(p[:,0])<.058*s) & (p[:,1]>1.063*s) & (p[:,1]<1.334*s)
            P[shirt]=[232,224,209,255]
        return P
    def build_continuous_upper_body(self):
        d=self.data
        removed=self.old_removed_parts()
        removed_v=np.zeros(len(d['POSITION']),bool)
        for nm in removed:
            lo,hi=self.ranges[nm];removed_v[lo:hi]=True
        triangles=d['indices'].reshape(-1,3)
        # All source component triangles are disconnected: no cross-part triangles expected.
        cross=np.any(removed_v[triangles],axis=1) & ~np.all(removed_v[triangles],axis=1)
        assert not cross.any(),'Unexpected mixed part triangles, requires topology-specific handling'
        kept_faces=triangles[~np.any(removed_v[triangles],axis=1)]
        kept_index=np.unique(kept_faces)
        remap=np.full(len(d['POSITION']),-1,np.int64);remap[kept_index]=np.arange(len(kept_index))
        kept_faces=remap[kept_faces].astype('<u4')
        verts,faces,normals=self.shape()
        n=len(kept_index);self.upper_body_vertex_start=n;self.upper_body_face_start=len(kept_faces)
        self.new_mesh_vertices=verts;self.new_mesh_faces=faces;self.removed_parts=removed
        # Skimage normals may have opposite sign for the chosen gradient sign; enforce outward.
        # Angle-weighted vertex normal from triangle winding has consistent orientation.
        mesh=trimesh.Trimesh(vertices=verts,faces=faces,process=False)
        if mesh.volume<0:
            faces=faces[:,::-1].copy();mesh=trimesh.Trimesh(vertices=verts,faces=faces,process=False)
        normals=np.array(mesh.vertex_normals,dtype='<f4')
        ids,w=self.body_weights(verts)
        colors=self.classify_colors(verts)
        combined={}
        for key in ['POSITION','NORMAL','COLOR_0','JOINTS_0','WEIGHTS_0']:
            comp={'POSITION':verts,'NORMAL':normals,'COLOR_0':colors,'JOINTS_0':ids,'WEIGHTS_0':w}[key]
            combined[key]=np.concatenate([d[key][kept_index],comp],axis=0)
        combined['indices']=np.concatenate([kept_faces.flatten(),(faces+n).flatten()]).astype('<u4')
        for name in NAMES:
            old=self.morphs[name][kept_index]
            new=np.zeros((len(verts),3),np.float32)
            if name=='cloth_reach':
                new[:,2]=.0020*smoothstep(1.14,1.38,verts[:,1])
                # Pose-space elbow corrective after measured collapse at ~90 degree flex.
                # Moved forward (positive Z), localized to the active reach elbow;
                # does not translate the hand, head, torso, or stationary limbs.
                elbow=self.rest['elbow_R' if self.key=='ava' else 'elbow_L']
                dv=verts-elbow
                envelope=np.exp(-(dv[:,1]/.050)**2)*np.exp(-(dv[:,0]/.090)**2)
                new[:,2]+=.020*envelope
            if name=='cloth_breathe':
                upper_body=np.exp(-((verts[:,1]-1.21)/.17)**2)
                new[:,2]=.0011*upper_body
            self.morphs[name]=np.vstack([old,new]).astype('<f4')
            combined['MORPH_'+name]=self.morphs[name]
        # Rebuild ranges for existing parts and append new named unified geometry.
        newranges={}
        for nm,(lo,hi) in self.ranges.items():
            if nm in removed:continue
            part_source_indices=np.arange(lo,hi)
            surviving=remap[part_source_indices]
            v=surviving[surviving>=0]
            if len(v):
                newranges[nm]=[int(v.min()),int(v.max()+1)]
        newranges['CONTINUOUS_UPPER_BODY_SHOULDERS_ELBOWS_v17']=[n,n+len(verts)]
        self.data=combined;self.ranges=newranges
        self.mesh_health={'connected_surface_components':int(len(mesh.split(only_watertight=False))),
                          'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),
                          'volume_m3':float(mesh.volume),'removed_prior_mesh_parts':removed,
                          'retained_source_vertices':int(n),'new_upperbody_vertices':int(len(verts)),
                          'new_upperbody_triangles':int(len(faces)),
                          'total_vertices':int(len(combined['POSITION'])),'total_triangles':int(len(combined['indices'])//3),
                          'max_influences_per_vertex':4}
        assert len(mesh.split(only_watertight=False))==1
        assert mesh.is_watertight and mesh.volume>0
        assert np.allclose(self.data['WEIGHTS_0'].sum(axis=1),1,atol=1e-5)
        assert self.data['JOINTS_0'].max()<len(self.names)
    def export_v17(self):
        meta=super().export()
        src=MODELS/f'{self.key}_RIGGED_SPEECH_HANDS_v1_6.glb'
        dst=MODELS/f'{self.key}_CONTINUOUS_SHOULDER_v1_7.glb'
        src.rename(dst)
        # Update inherited writer metadata without changing accessor, buffer, or joint data.
        gltf,blob=read_glb(dst)
        gltf['asset']['generator']='VillaVerse v1.7 continuous skinned upper body'
        gltf['meshes'][0]['name']=f'{self.key}_continuous_upperbody_face_hands_v17'
        gltf['animations'][0]['name']='reach_continuous_shoulder_dialogue_v17'
        gltf['scenes'][0]['name']=f'{self.key}_v17'
        for node in gltf['nodes']:
            if node.get('name')==f'{self.key}_actor_v16':node['name']=f'{self.key}_actor_v17'
        gltf['skins'][0]['name']=f'{self.key}_43bone_continuous_v17'
        jj=json.dumps(gltf,separators=(',',':'),ensure_ascii=False).encode('utf8'); jj+=b' '*(-len(jj)%4)
        bb=blob+b'\x00'*(-len(blob)%4)
        dst.write_bytes(b'glTF'+struct.pack('<II',2,12+8+len(jj)+8+len(bb))+struct.pack('<I4s',len(jj),b'JSON')+jj+struct.pack('<I4s',len(bb),b'BIN\x00')+bb)
        (MODELS/f'{self.key}_v16_runtime.npz').rename(MODELS/f'{self.key}_v17_runtime.npz')
        # Save rest transformed geometry for DCC inspection and surface continuity tests.
        tri=self.data['indices'].reshape(-1,3)
        newfaces=tri[self.upper_body_face_start:]-self.upper_body_vertex_start
        mesh=trimesh.Trimesh(vertices=self.new_mesh_vertices,faces=newfaces,process=False)
        mesh.export(MODELS/f'{self.key}_continuous_upperbody_v17.ply')
        meta['version']='1.7';meta['mesh_health']=self.mesh_health;meta['source_model_version']='v1.6, unchanged 43-joint rig';meta['glb']=dst.name
        (MODELS/f'{self.key}_v17_manifest.json').write_text(json.dumps(meta,indent=2))
        old=MODELS/f'{self.key}_v16_manifest.json'
        if old.exists(): old.unlink()
        return meta

def main():
    report={}
    for name in ('ava','noor'):
        a=Actor(name);report[name]=a.export_v17()
        print(name,'new verts',a.mesh_health['new_upperbody_vertices'], 'watertight',a.mesh_health['watertight'],flush=True)
    (QA/'build_report_v17.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__': main()
