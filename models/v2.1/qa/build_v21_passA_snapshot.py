#!/usr/bin/env python3
"""Villa Verse v2.1: repair speech morphs; controlled per-finger grasp experiments.
No claims of native Godot execution. Builds from complete frozen v2.0 source.
"""
import pathlib, json, struct
import numpy as np
from scipy.spatial.transform import Rotation
from build_v20 import Actor as ActorV20, MODELS, QA
from build_v16 import read_glb, NAMES

class Actor(ActorV20):
    def __init__(self,key,grip='staggered'):
        super().__init__(key)
        self.grip=grip
        self.mouth_metadata=self.rebuild_mouth_targets()

    def rebuild_mouth_targets(self):
        """Replace v1.6 exaggerated membrane-only scaling with bounded lip/cavity movements.
        The mouth membrane remains the v1.6 mesh; this is a deformation fix,
        NOT full facial retopology or a final lip-sync system.
        """
        p=self.data['POSITION']; d=self.morphs
        names=['upper_lip_contour_v15','lower_lip_contour_v15','mouth_cavity_v16']
        bounds={n:self.ranges[n] for n in names}
        lo,hi=bounds['mouth_cavity_v16']
        mid=float((p[lo:hi,1].min()+p[lo:hi,1].max())/2)
        for name in ['jaw_open','viseme_O','viseme_EE']:
            for r in names:
                lo,hi=bounds[r]
                d[name][lo:hi]=0.
        # Lip movements stay anatomically small and are coordinated with the cavity.
        u0,u1=bounds['upper_lip_contour_v15'];l0,l1=bounds['lower_lip_contour_v15']
        d['jaw_open'][u0:u1,1]=.0018
        d['jaw_open'][l0:l1,1]=-.0080
        d['viseme_O'][u0:u1,1]=.0029
        d['viseme_O'][l0:l1,1]=-.0050
        d['viseme_EE'][u0:u1,1]=.00065
        d['viseme_EE'][l0:l1,1]=-.0013
        # Preserve vowel distinction by moving lips radially rather than stretching cavity aggressively.
        for r in ['upper_lip_contour_v15','lower_lip_contour_v15']:
            lo,hi=bounds[r];x=p[lo:hi,0]
            d['viseme_O'][lo:hi,0]=-x*.26
            d['viseme_EE'][lo:hi,0]=x*.16
        lo,hi=bounds['mouth_cavity_v16'];c=p[lo:hi];dy=c[:,1]-mid
        # Uniform, bounded iris-like cavity aperture; rest membrane has ~5mm depth.
        d['jaw_open'][lo:hi,1]=dy*1.28
        d['jaw_open'][lo:hi,2]=.00045
        d['viseme_O'][lo:hi,1]=dy*.43
        d['viseme_O'][lo:hi,0]=-c[:,0]*.30
        d['viseme_EE'][lo:hi,1]=-dy*.12
        d['viseme_EE'][lo:hi,0]=c[:,0]*.24
        for n in NAMES:
            self.data['MORPH_'+n]=d[n].astype('<f4')
        return {'previous':'v1.6 cavity vertical dilation 4.6x jaw, 3.3x O plus lower-lip 19mm displacement',
                'new':'jaw cavity dilation 1.28x, O 0.43x; lower lip jaw 8mm at full morph weight; no unbounded scaling',
                'target_limit_local_mouth_edge_stretch':'<=2.5x at 125 encoded frames',
                'note':'Not speech-synchronized to audio; sampled two-syllable animation only'}

    def finger_rotation(self,name,t):
        if self.grip=='baseline':
            return super().finger_rotation(name,t)
        u=float(np.clip((t-2.58)/.8,0,1));u=u*u*(3-2*u)
        u*=1-.10*np.clip((t-4.40)/.8,0,1)
        side='R' if self.key=='ava' else 'L'
        if not name.startswith(side+'_'):return Rotation.identity()
        # Anatomical variation: index stabilizes, middle/ring curl further, pinky is relaxed.
        base_amplitudes=[.24,.38,.46,.32]
        tip_amplitudes=[.30,.47,.52,.41]
        if self.grip=='gentle':
            mult=.82
        elif self.grip=='strong':
            mult=1.25
        else:
            mult=1.0
        if 'thumb' in name:
            is_tip=name.endswith('_tip')
            return Rotation.from_euler('xz',[-(.27 if is_tip else .21)*u*mult,
                (.15 if side=='R' else -.15)*u])
        finger_idx=int(name.split('finger')[1][0])
        is_tip=name.endswith('_tip')
        amp=(tip_amplitudes if is_tip else base_amplitudes)[finger_idx]
        z=(.05 if side=='R' else -.05)*u*(finger_idx-1.5)/1.5
        return Rotation.from_euler('xz',[-amp*u*mult,z])

    def export_v21(self):
        meta=super().export_v20()
        old=MODELS/f'{self.key}_WRIST_WELDED_v2_0.glb'
        target=MODELS/f'{self.key}_MOUTH_GRIP_v2_1.glb'
        old.rename(target)
        gltf,bb=read_glb(target)
        gltf['asset']['generator']='Villa Verse v2.1 bounded visemes and staggered digit flexion'
        gltf['meshes'][0]['name']=f'{self.key}_continuous_anatomy_corrected_mouth_v21'
        gltf['animations'][0]['name']='reach_contact_speech_corrected_v21'
        gltf['scenes'][0]['name']=f'{self.key}_v21'
        j=json.dumps(gltf,separators=(',',':'),ensure_ascii=False).encode();j+=b' '*(-len(j)%4)
        bb+=b'\0'*(-len(bb)%4)
        target.write_bytes(b'glTF'+struct.pack('<II',2,12+8+len(j)+8+len(bb))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(bb),b'BIN\0')+bb)
        meta['version']='2.1';meta['glb']=target.name;meta['mouth_corrective']=self.mouth_metadata
        meta['grip_profile']=self.grip
        meta['caveats']=['No native Godot import/playback verified', 'No final artistic approval',
                        'Digit flexion remains procedural; no true interlocked grasp or force model',
                        'Mouth cavity not rebuilt topologically; no audio-driven phoneme synchronization']
        (MODELS/f'{self.key}_v20_manifest.json').unlink(missing_ok=True)
        (MODELS/f'{self.key}_v21_manifest.json').write_text(json.dumps(meta,indent=2))
        return meta

if __name__=='__main__':
    out={}
    for k in ['ava','noor']:
        a=Actor(k);out[k]=a.export_v21()
        print(k, 'v2.1 vertices',len(a.data['POSITION']),'morphs',len(NAMES),'grip',a.grip,flush=True)
    (QA/'build_report_v21.json').write_text(json.dumps(out,indent=2))
