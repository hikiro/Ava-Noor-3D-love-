#!/usr/bin/env python3
"""Villa Verse v1.8 actual arm-ring retopology and normalized elbow skinning.

Inherits 43-bone skin, glTF animation, expression and cloth morphs from v1.7.
Elbow/forearm are removed from the implicit surface, reconstructed as shared-edge
support-loop meshes and skinned with broadened elbow transition. NO Blender or
Godot claims: local CPU skinning is mechanically checked separately.
"""
import json, pathlib, struct
import numpy as np
import trimesh
from build_v17 import Actor as ActorV17, ROOT, MODELS, QA, smoothstep
from build_v16 import read_glb
from elbow_retopo_v18 import retopo

class Actor(ActorV17):
    def shape(self):
        implicit=super().shape()
        verts,faces,normals,self.retopo_meta=retopo(implicit[0],implicit[1],self.rest,self.rest['shoulder_R'][0]/.178)
        self.elbow_loops_added=sum(v['retopo_triangles'] for v in self.retopo_meta.values())
        return verts,faces,normals

    def body_weights(self,p):
        indices,w=super().body_weights(p)
        # For retopo regions below clean cut, spread influence continuously across
        # elbow rather than stacking two near-binary changes within 2 cm.
        scale=self.rest['shoulder_R'][0]/.178
        for side,sign in (('L',-1),('R',1)):
            y_elbow=self.rest['elbow_'+side][1]
            y_wrist=self.rest['wrist_'+side][1]
            center=self.rest['elbow_'+side][0]
            cut=self.retopo_meta[side]['cut_height_m']
            mask=(sign*p[:,0]>.155*scale)&(p[:,1]<cut-1e-6) & (p[:,1]>y_wrist-.05*scale)
            loc=np.where(mask)[0]
            if not len(loc):continue
            y=p[loc,1]
            # 0 elbow under upper arm; 1 elbow for forearm. At pivot upper=lower=.5
            lower=1-smoothstep(y_elbow-.075*scale,y_elbow+.075*scale,y)
            # Wrist gradually takes over distal 12cm; prevents skin discontinuity.
            distal=1-smoothstep(y_wrist+.012*scale,y_wrist+.075*scale,y)
            shoulder_w=1-lower; elbow_w=lower*(1-distal); wrist_w=lower*distal
            tot=shoulder_w+elbow_w+wrist_w
            target=np.stack([shoulder_w,elbow_w,wrist_w],axis=1)/tot[:,None]
            # Blend to original v1.7 shoulder/chest weights near the sewn seam.
            # In pass 1, forcing shoulder/elbow-only weights *at* the seam
            # caused adjacent triangles to stretch >100x during reach.
            blend=smoothstep(.003*scale,float(getattr(self,"SEAM_FADE",.045))*scale,cut-y)
            dense=np.zeros((len(loc),len(self.names)),np.float32)
            for k in range(4):
                dense[np.arange(len(loc)),indices[loc,k]]+=w[loc,k]*(1-blend)
            for k,name in enumerate(['shoulder_'+side,'elbow_'+side,'wrist_'+side]):
                dense[:,self.names.index(name)]+=blend*target[:,k]
            order=np.argsort(dense,axis=1)[:,-4:][:,::-1]
            vals=np.take_along_axis(dense,order,axis=1)
            vals/=np.maximum(vals.sum(axis=1,keepdims=True),1e-8)
            indices[loc,:]=order;w[loc,:]=vals
        return indices.astype('<u2'),w.astype('<f4')

    def export_v18(self):
        meta=super().export_v17()
        old=MODELS/f'{self.key}_CONTINUOUS_SHOULDER_v1_7.glb'
        dst=MODELS/f'{self.key}_ELBOW_RETOPO_v1_8.glb';old.rename(dst)
        gltf,blob=read_glb(dst)
        gltf['asset']['generator']='VillaVerse v1.8 contiguous elbow edge-loop retopology'
        gltf['meshes'][0]['name']=f'{self.key}_upperbody_contiguous_elbow_loops_v18'
        gltf['animations'][0]['name']='reach_organic_elbows_dialogue_v18'
        gltf['skins'][0]['name']=f'{self.key}_43bone_retopo_v18'
        gltf['scenes'][0]['name']=f'{self.key}_v18'
        for node in gltf['nodes']:
            if node.get('name')==f'{self.key}_actor_v17':node['name']=f'{self.key}_actor_v18'
        j=json.dumps(gltf,separators=(',',':'),ensure_ascii=False).encode();j+=b' '*(-len(j)%4)
        blob+=b'\x00'*(-len(blob)%4)
        dst.write_bytes(b'glTF'+struct.pack('<II',2,12+8+len(j)+8+len(blob))+
            struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(blob),b'BIN\x00')+blob)
        (MODELS/f'{self.key}_v17_runtime.npz').rename(MODELS/f'{self.key}_v18_runtime.npz')
        (MODELS/f'{self.key}_continuous_upperbody_v17.ply').rename(MODELS/f'{self.key}_continuous_upperbody_RETOPO_v18.ply')
        (MODELS/f'{self.key}_v17_manifest.json').unlink()
        meta['version']='1.8';meta['glb']=dst.name;meta['elbow_retopology']=self.retopo_meta
        meta['modeling_limit']='Procedural ring topology, not sculpted/manual anatomical elbow or production skin weights'
        (MODELS/f'{self.key}_v18_manifest.json').write_text(json.dumps(meta,indent=2))
        return meta

def main():
    out={}
    for key in ['ava','noor']:
        a=Actor(key)
        out[key]=a.export_v18()
        print(key,'new vertices',a.mesh_health['new_upperbody_vertices'],'rings',a.retopo_meta['R']['ring_count'],flush=True)
    (QA/'build_report_v18.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':main()
