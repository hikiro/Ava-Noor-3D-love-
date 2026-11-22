#!/usr/bin/env python3
"""Villa Verse v1.9: continuous skinned hand topology + explicit collision-aware staged contact.

Retains original v1.8 arm/elbow topology and rig, removes separated palm,
knuckle, finger and nail primitives and replaces each hand with one watertight
signed-distance meshed surface. Does not claim actual Godot verification.
"""
import pathlib, json, struct
import numpy as np
import trimesh
from build_v18 import Actor as ActorV18, MODELS,QA,ROOT
from build_v16 import read_glb, NAMES
from hand_topology_v19 import generate

class Actor(ActorV18):
    def __init__(self,key):
        super().__init__(key)
        self.replace_hands()
    def replace_hands(self):
        d=self.data
        old_faces=d['indices'].reshape(-1,3)
        old_body_start=self.upper_body_vertex_start
        old_body_face_start=self.upper_body_face_start
        exclude=[nm for nm in self.ranges if nm.startswith(('L_','R_')) and any(t in nm for t in ('hand_palm','hand_knuckle','finger','thumb'))]
        mask=np.zeros(old_body_start,bool)
        for nm in exclude:
            lo,hi=self.ranges[nm]
            assert hi<=old_body_start,(nm,hi,old_body_start)
            mask[lo:hi]=True
        preserved_triangles=old_faces[:old_body_face_start]
        crossing=np.any(mask[preserved_triangles],axis=1) & ~np.all(mask[preserved_triangles],axis=1)
        assert not crossing.any(),'Unexpected hand-to-body source triangles; requires weld-aware split'
        keep_faces=preserved_triangles[~np.any(mask[preserved_triangles],axis=1)]
        keep_indices=np.arange(old_body_start)[~mask]
        remap=np.full(len(d['POSITION']),-1,dtype=np.int64)
        remap[keep_indices]=np.arange(len(keep_indices))
        keep_faces=remap[keep_faces].astype('<u4')
        hands={side:generate(self,side) for side in ('L','R')}
        all_d={k:[d[k][keep_indices]] for k in ['POSITION','NORMAL','COLOR_0','JOINTS_0','WEIGHTS_0']}
        for side in ('L','R'):
            for k in all_d:all_d[k].append(hands[side][k])
        body_idx=np.arange(old_body_start,len(d['POSITION']))
        for k in all_d:all_d[k].append(d[k][body_idx])
        for k in all_d:all_d[k]=np.concatenate(all_d[k],axis=0)
        old_cnt=len(keep_indices);hand_counts={s:len(hands[s]['POSITION']) for s in ('L','R')}
        new_body_start=old_cnt+sum(hand_counts.values())
        body_tri=old_faces[old_body_face_start:]-old_body_start+new_body_start
        faces=[keep_faces];start=old_cnt;handranges={}
        for side in ('L','R'):
            h=hands[side];faces.append(h['faces']+start)
            handranges[f'{side}_CONTINUOUS_ANATOMICAL_HAND_v19']=[start,start+len(h['POSITION'])]
            start+=len(h['POSITION'])
        new_body_face_start=sum(map(len,faces))
        faces.append(body_tri.astype('<u4'))
        all_d['indices']=np.concatenate(faces,axis=0).astype('<u4').reshape(-1)
        newranges={}
        for nm,(lo,hi) in self.ranges.items():
            if nm in exclude or nm=='CONTINUOUS_UPPER_BODY_SHOULDERS_ELBOWS_v17':continue
            surviving=remap[lo:hi]
            surviving=surviving[surviving>=0]
            if len(surviving):newranges[nm]=[int(surviving.min()),int(surviving.max()+1)]
        newranges.update(handranges)
        newranges['CONTINUOUS_UPPER_BODY_SHOULDERS_ELBOWS_v17']=[new_body_start,len(all_d['POSITION'])]
        for morph in NAMES:
            arr=np.concatenate([self.morphs[morph][keep_indices],
                np.zeros((sum(hand_counts.values()),3),dtype='<f4'),self.morphs[morph][body_idx]])
            self.morphs[morph]=arr.astype('<f4')
            all_d['MORPH_'+morph]=self.morphs[morph]
        self.ranges=newranges;self.data=all_d
        self.upper_body_vertex_start=new_body_start
        self.upper_body_face_start=new_body_face_start
        self.hands_metadata={s:hands[s]['metadata'] for s in hands}
        self.hand_geometry={s:trimesh.Trimesh(vertices=hands[s]['POSITION'],faces=hands[s]['faces'],process=False) for s in hands}
        self.mesh_health['total_vertices']=len(all_d['POSITION'])
        self.mesh_health['total_triangles']=len(all_d['indices'])//3
        self.mesh_health['continuous_hands']=True
        self.mesh_health['removed_discrete_hand_parts']=exclude
        assert len(all_d['POSITION'])==len(all_d['JOINTS_0'])
        assert all(np.isfinite(v).all() for v in all_d.values())
        assert np.allclose(all_d['WEIGHTS_0'].sum(1),1.,atol=1e-5)
        assert max(all_d['JOINTS_0'].ravel())<len(self.names)
    def export_v19(self):
        meta=super().export_v18()
        old=MODELS/f'{self.key}_ELBOW_RETOPO_v1_8.glb'
        dst=MODELS/f'{self.key}_CONTINUOUS_HANDS_v1_9.glb';old.rename(dst)
        gltf,blob=read_glb(dst)
        gltf['asset']['generator']='VillaVerse v1.9 unified articulated hand topology'
        gltf['meshes'][0]['name']=f'{self.key}_unified_palm_fingers_and_elbow_v19'
        gltf['skins'][0]['name']=f'{self.key}_43bone_connected_hands_v19'
        gltf['scenes'][0]['name']=f'{self.key}_v19'
        gltf['animations'][0]['name']='reach_contact_hold_v19'
        for node in gltf['nodes']:
            if node.get('name')==f'{self.key}_actor_v18':node['name']=f'{self.key}_actor_v19'
        j=json.dumps(gltf,separators=(',',':'),ensure_ascii=False).encode('utf-8');j+=b' '*(-len(j)%4)
        blob+=b'\x00'*(-len(blob)%4)
        dst.write_bytes(b'glTF'+struct.pack('<II',2,12+8+len(j)+8+len(blob))+
              struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(blob),b'BIN\x00')+blob)
        (MODELS/f'{self.key}_v18_runtime.npz').rename(MODELS/f'{self.key}_v19_runtime.npz')
        (MODELS/f'{self.key}_continuous_upperbody_RETOPO_v18.ply').rename(MODELS/f'{self.key}_continuous_upperbody_RETOPO_v19.ply')
        (MODELS/f'{self.key}_v18_manifest.json').unlink(missing_ok=True)
        for side,m in self.hand_geometry.items():m.export(MODELS/f'{self.key}_{side}_unified_hand_v19.ply')
        meta['version']='1.9';meta['glb']=dst.name;meta['hand_geometry']=self.hands_metadata
        meta['collision_aware_scene_offset_m']={'ava':[-.48,0,0],'noor':[.48,0,.038]}
        meta['caveats']=['Godot import has NOT been executed; external validation harness provided',
          'Connected hand surface is not welded to forearm, needs wrist joint evaluation',
          'Surface collision validation is limited to opposing hand triangles and selected time samples']
        (MODELS/f'{self.key}_v19_manifest.json').write_text(json.dumps(meta,indent=2))
        return meta

def main():
    out={}
    for key in ('ava','noor'):
        a=Actor(key);out[key]=a.export_v19()
        print(key,'hands',[(s,m['vertices'],m['triangles']) for s,m in a.hands_metadata.items()],flush=True)
    (QA/'build_report_v19.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':main()
