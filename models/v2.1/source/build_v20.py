#!/usr/bin/env python3
"""VillaVerse v2.0: one continuous skinned surface from shoulders through wrists into fingers."""
import pathlib,json,struct
import trimesh
from build_v19 import Actor as V19, MODELS, QA
from build_v16 import read_glb
from wrist_bridge_v20 import bridge
class Actor(V19):
    def __init__(self,key):
        super().__init__(key)
        self.wrist_weld_metadata=bridge(self)
    def export_v20(self):
        meta=super().export_v19()
        old=MODELS/f'{self.key}_CONTINUOUS_HANDS_v1_9.glb'
        dst=MODELS/f'{self.key}_WRIST_WELDED_v2_0.glb';old.rename(dst)
        gltf,blob=read_glb(dst)
        gltf['asset']['generator']='VillaVerse v2.0 welded forearm-to-hand anatomy'
        gltf['meshes'][0]['name']=f'{self.key}_continuous_shoulder_elbow_wrist_fingers_v20'
        gltf['skins'][0]['name']=f'{self.key}_43bone_welded_wrist_v20'
        gltf['scenes'][0]['name']=f'{self.key}_v20'
        gltf['animations'][0]['name']='reach_contact_hold_v20'
        j=json.dumps(gltf,separators=(',',':'),ensure_ascii=False).encode();j+=b' '*(-len(j)%4)
        blob+=b'\0'*(-len(blob)%4)
        dst.write_bytes(b'glTF'+struct.pack('<II',2,12+8+len(j)+8+len(blob))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(blob),b'BIN\0')+blob)
        meta['version']='2.0';meta['glb']=dst.name;meta['wrist_weld']=self.wrist_weld_metadata
        meta['open_issues']=['Godot native editor/animation import not tested here',
            'Genuine interlocking handhold and inside-finger self-collisions require visual/mesh inspection',
            'Simplified face/hair/garments remain below final lookdev standard']
        (MODELS/f'{self.key}_v19_manifest.json').unlink(missing_ok=True)
        (MODELS/f'{self.key}_v20_manifest.json').write_text(json.dumps(meta,indent=2))
        return meta
if __name__=='__main__':
    result={}
    for key in ('ava','noor'):
        a=Actor(key);result[key]=a.export_v20()
        print(key,'wrist weld',a.wrist_weld_metadata,flush=True)
    (QA/'build_report_v20.json').write_text(json.dumps(result,indent=2))
