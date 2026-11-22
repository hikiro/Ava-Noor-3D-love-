#!/usr/bin/env python3
"""Villa Verse v1.6: independent finger joints, eight facial/garment morphs, portable glTF export.
Inputs frozen from v1.5; no dependency on Blender, Godot or network, no library-specific meshes.
Source geometry v1.5 preserved. Project-scale directions are not changed.
"""
from __future__ import annotations
import json, struct, pathlib, re, math
import numpy as np
from scipy.spatial.transform import Rotation, Slerp
from scipy.spatial import cKDTree
import trimesh
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=ROOT/'models'; PRE=BASE/'base'; QA=ROOT/'qa'
for p in (BASE,QA):p.mkdir(parents=True,exist_ok=True)
NAMES=['blink','concern','soft_smile','jaw_open','viseme_O','viseme_EE','cloth_reach','cloth_breathe']

def read_glb(path):
    b=path.read_bytes(); assert b[:4]==b'glTF'
    jl=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+jl].decode())
    off=20+jl; bl=struct.unpack_from('<I',b,off)[0];blob=b[off+8:off+8+bl]
    return j,blob

def read_accessor(j,blob,i):
    a=j['accessors'][i];view=j['bufferViews'][a['bufferView']]; start=view.get('byteOffset',0)+a.get('byteOffset',0)
    types={5126:np.float32,5123:np.uint16,5125:np.uint32,5121:np.uint8}
    dim={'SCALAR':1,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    dt=np.dtype(types[a['componentType']]).newbyteorder('<')
    stride=view.get('byteStride',np.dtype(dt).itemsize*dim)
    out=np.ndarray(shape=(a['count'],dim),dtype=dt,buffer=blob,offset=start,strides=(stride,np.dtype(dt).itemsize)).copy()
    return out.reshape(-1) if dim==1 else out

class GLB:
    def __init__(self):
        self.j={'asset':{'version':'2.0','generator':'VillaVerse v1.6 finger skinned + speech morphs'}, 'buffers':[], 'bufferViews':[], 'accessors':[], 'meshes':[], 'nodes':[], 'skins':[], 'scenes':[], 'scene':0,'materials':[],'animations':[]}
        self.bin=bytearray()
    def accessor(self,arr,component,typ,target=None,normalized=False,minmax=False):
        a=np.ascontiguousarray(arr);self.bin.extend(b'\x00'*(-len(self.bin)%4));offset=len(self.bin)
        self.bin.extend(a.tobytes());view={'buffer':0,'byteOffset':offset,'byteLength':a.nbytes}
        if target:view['target']=target
        vi=len(self.j['bufferViews']);self.j['bufferViews'].append(view)
        ac={'bufferView':vi,'componentType':component,'count':int(len(a)),'type':typ}
        if normalized:ac['normalized']=True
        if minmax:
            v=a.reshape(len(a),-1);ac['min']=v.min(axis=0).astype(float).tolist();ac['max']=v.max(axis=0).astype(float).tolist()
        ai=len(self.j['accessors']);self.j['accessors'].append(ac);return ai
    def write(self,path):
        self.j['buffers']=[{'byteLength':len(self.bin)}]
        jj=json.dumps(self.j,separators=(',',':'),ensure_ascii=False).encode();jj+=b' '*(-len(jj)%4)
        bb=bytes(self.bin);bb+=b'\x00'*(-len(bb)%4)
        path.write_bytes(b'glTF'+struct.pack('<II',2,12+8+len(jj)+8+len(bb))+struct.pack('<I4s',len(jj),b'JSON')+jj+struct.pack('<I4s',len(bb),b'BIN\x00')+bb)

class Actor:
    def __init__(self,key):
        self.key=key
        self.source_j,self.source_blob=read_glb(PRE/f'{key}_SKINNED_EXPRESSIVE_v1_5.glb')
        self.data=dict(np.load(PRE/f'{key}_render_data_v15.npz'))
        self.ranges=json.loads((PRE/f'{key}_mesh_ranges_v15.json').read_text())
        j=self.source_j
        self.old_names=[n['name'] for n in j['nodes'] if n.get('name') and n['name'] not in (f'{key}_actor_v15',)]
        self.old_names=self.old_names[:len(j['skins'][0]['joints'])]
        self.parents={name:None for name in self.old_names}
        for i,n in enumerate(j['nodes']):
            for c in n.get('children',[]):
                if c < len(self.old_names):self.parents[self.old_names[c]]=self.old_names[i]
        self.names=list(self.old_names)
        self.local={n:np.array(j['nodes'][i].get('translation',[0,0,0]),float) for i,n in enumerate(self.old_names)}
        self.rest={}
        for n in self.names:
            parent=self.parents[n];self.rest[n]=self.local[n]+(self.rest[parent] if parent else np.zeros(3))
        self.frames,self.tracks=self.read_v15_tracks()
        self.finger_meta=[]
        self.add_finger_bones()
        self.add_mouth_geometry()
        self.make_morphs()
        self.data['JOINTS_0']=self.data['JOINTS_0'].astype('<u2')
        self.data['WEIGHTS_0']=self.data['WEIGHTS_0'].astype('<f4')
        self.reindex_and_check()
    def read_v15_tracks(self):
        jj,bb=self.source_j,self.source_blob;a=jj['animations'][0];frames=None;tracks={}
        for c in a['channels']:
            if c['target']['path']!='rotation':continue
            sampler=a['samplers'][c['sampler']]
            f=read_accessor(jj,bb,sampler['input']).astype(float)
            q=read_accessor(jj,bb,sampler['output']).astype(float)
            name=jj['nodes'][c['target']['node']]['name'];tracks[name]=q
            if frames is None:frames=f
            else:assert np.allclose(frames,f)
        return frames,tracks
    def add_bone(self,name,parent,pos):
        assert parent in self.rest and name not in self.rest
        self.names.append(name);self.parents[name]=parent;self.rest[name]=np.asarray(pos,float)
        self.local[name]=self.rest[name]-self.rest[parent]
    def give_range(self,name,bone):
        if name not in self.ranges:return
        lo,hi=self.ranges[name];self.data['JOINTS_0'][lo:hi,:]=0
        self.data['JOINTS_0'][lo:hi,0]=self.names.index(bone)
        self.data['WEIGHTS_0'][lo:hi,:]=0
        self.data['WEIGHTS_0'][lo:hi,0]=1
    def add_finger_bones(self):
        for side in ('L','R'):
            hand='hand_'+side
            for finger in range(4):
                base=f'{side}_finger{finger}'
                prox,dist=f'{base}_prox_v14',f'{base}_dist_v14'
                coords=self.data['POSITION'];lo,hi=self.ranges[prox];verts=coords[lo:hi]
                orig=np.array([np.mean(verts[:,0]),np.max(verts[:,1])-.004,np.mean(verts[:,2])])
                root=f'{base}_base';self.add_bone(root,hand,orig)
                lo,hi=self.ranges[dist];verts=coords[lo:hi]
                second=np.array([np.mean(verts[:,0]),np.max(verts[:,1])-.002,np.mean(verts[:,2])])
                joint=f'{base}_tip';self.add_bone(joint,root,second)
                self.give_range(prox,root);self.give_range(dist,joint)
                self.give_range(f'{base}_nail_v14',joint)
                self.finger_meta.append((root,joint,side,finger))
            for piece in ('prox','tip'):
                part=f'{side}_thumb_{piece}_v14';lo,hi=self.ranges[part]
                v=self.data['POSITION'][lo:hi];p=np.array([np.mean(v[:,0]),np.max(v[:,1])-.002,np.mean(v[:,2])])
                bn=f'{side}_thumb_{piece}'
                parent=hand if piece=='prox' else f'{side}_thumb_prox'
                self.add_bone(bn,parent,p);self.give_range(part,bn)
            self.finger_meta.append((f'{side}_thumb_prox',f'{side}_thumb_tip',side,'thumb'))
    def add_mouth_geometry(self):
        # Single inner-lip membrane that is nearly closed at rest; follows head bone and jaw/viseme morphs.
        u=trimesh.creation.uv_sphere(count=[17,21]);
        # Disk lies directly behind lips and just in front of face.
        u.vertices*=np.array([.028,.0026,.0015])
        mid=(self.data['POSITION'][self.ranges['upper_lip_contour_v15'][0]:self.ranges['upper_lip_contour_v15'][1],1].mean()+self.data['POSITION'][self.ranges['lower_lip_contour_v15'][0]:self.ranges['lower_lip_contour_v15'][1],1].mean())/2
        u.vertices+=np.array([0,mid,.100])
        # Add triangles to the original skinned combined mesh.
        v=np.asarray(u.vertices,dtype='<f4');faces=np.asarray(u.faces,dtype='<u4')
        off=len(self.data['POSITION']); self.ranges['mouth_cavity_v16']=[off,off+len(v)]
        self.data['POSITION']=np.vstack([self.data['POSITION'],v])
        self.data['NORMAL']=np.vstack([self.data['NORMAL'],u.vertex_normals.astype('<f4')])
        col=np.tile(np.array([66,28,42,255],dtype='u1'),(len(v),1))
        self.data['COLOR_0']=np.vstack([self.data['COLOR_0'],col])
        joint=np.zeros((len(v),4),dtype='<u2');joint[:,0]=self.names.index('head')
        weight=np.zeros((len(v),4),dtype='<f4');weight[:,0]=1
        self.data['JOINTS_0']=np.vstack([self.data['JOINTS_0'],joint]);self.data['WEIGHTS_0']=np.vstack([self.data['WEIGHTS_0'],weight])
        self.data['indices']=np.concatenate([self.data['indices'],faces.reshape(-1)+off]).astype('<u4')
        for nm in ['blink','concern','soft_smile']:
            self.data['MORPH_'+nm]=np.vstack([self.data['MORPH_'+nm],np.zeros_like(v)]).astype('<f4')
    def make_morphs(self):
        v=self.data['POSITION'];m={k:np.zeros_like(v,dtype='<f4') for k in NAMES}
        for n in NAMES[:3]:m[n]=self.data['MORPH_'+n].copy()
        ranges=self.ranges
        ymid=float((v[ranges['upper_lip_contour_v15'][0]:ranges['upper_lip_contour_v15'][1],1].mean()+v[ranges['lower_lip_contour_v15'][0]:ranges['lower_lip_contour_v15'][1],1].mean())/2)
        def V(n):
            a,b=ranges[n];return slice(a,b)
        # Morphs require actual vertex deltas (not merely animation names).
        for n in ('upper_lip_contour_v15','lower_lip_contour_v15','mouth_cavity_v16'):
            s=V(n);p=v[s];lower=n.startswith('lower');cavity=n.startswith('mouth')
            if cavity:
                m['jaw_open'][s,1]=(p[:,1]-ymid)*4.6
                m['jaw_open'][s,2]=.0008
                m['viseme_O'][s,0]=-p[:,0]*.53
                m['viseme_O'][s,1]=(p[:,1]-ymid)*3.3
                m['viseme_EE'][s,0]=p[:,0]*.48
                m['viseme_EE'][s,1]=(p[:,1]-ymid)*1.2
            else:
                m['jaw_open'][s,1]=(-.019 if lower else +.004)
                m['viseme_O'][s,0]=-p[:,0]*.40
                m['viseme_O'][s,1]=(-.009 if lower else +.007)
                m['viseme_EE'][s,0]=p[:,0]*.18
                m['viseme_EE'][s,1]=(-.004 if lower else +.002)
        for name,(lo,hi) in ranges.items():
            vs=v[lo:hi];a=slice(lo,hi)
            side=('L' if name.startswith('L_') else 'R' if name.startswith('R_') else '')
            if any(t in name for t in ('jacket','deltoid','armpit','sleeve','cowl_fold','top_waist')):
                # Small bounded displacement in surface normal and Y near side of contact arm.
                active= (self.key=='ava' and side=='R') or (self.key=='noor' and side=='L')
                if active or not side:
                    m['cloth_reach'][a,2]=np.clip((vs[:,1]-1.07)*.018,0,.006)
                    m['cloth_reach'][a,1]=np.clip((vs[:,0]-.0)*.006,-.004,.004)
            if any(tok in name for tok in ('jacket','top_waist','cowl','shirt','torso')):
                m['cloth_breathe'][a,2]=.0017
        self.morphs=m
    def reindex_and_check(self):
        assert len(self.names)==43,(len(self.names),self.names)
        assert len(self.data['POSITION'])==len(self.data['JOINTS_0'])
        assert self.data['JOINTS_0'].max()<len(self.names)
        assert np.allclose(self.data['WEIGHTS_0'].sum(axis=1),1,atol=1e-5)
        assert len(NAMES)==8
    def finger_rotation(self,name,t):
        # No movement until hands meet, then progressive 2-phalange curl.
        u=np.clip((t-2.57)/.75,0.,1.);u=u*u*(3-2*u)
        u*=1-.10*np.clip((t-4.4)/.8,0,1)
        contact=(self.key=='ava' and name.startswith('R_')) or (self.key=='noor' and name.startswith('L_'))
        if not contact:return Rotation.identity()
        if 'thumb' in name:
            ang=(-.25 if name.endswith('prox') else -.45)*u
            twist=(.22 if 'R_' in name else -.22)*u
            return Rotation.from_euler('xz',[ang,twist])
        ang=(-.40 if name.endswith('_base') else -.54)*u
        return Rotation.from_rotvec([ang,0,0])
    def expression(self,t):
        E=lambda x:np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
        ava=self.key=='ava'
        worry=(.82 if ava else .20)*E((t-.3)/.7)*(1-E((t-3.35)/.65))
        smile=(.6 if ava else .88)*E((t-(3.35 if ava else 2.4))/.8)
        blink=min(1.,np.exp(-((t-(1.61 if ava else 1.15))/.075)**4)+np.exp(-((t-4.65)/.07)**4))
        # Stylized two-syllable dialogue cycle: NOT real phoneme-to-audio lip sync.
        speech=(1-E((t-2.05)/.20)) * E((t-.16)/.20) if ava else E((t-.28)/.15)*(1-E((t-1.8)/.25))
        beat=0.5+.5*np.sin(2*np.pi*(2.4*t+(.1 if ava else .45)))
        jaw=.55*speech*beat
        oh=.65*speech*(0.5+.5*np.sin(2*np.pi*(1.35*t+.24)))
        ee=.58*speech*(0.5+.5*np.sin(2*np.pi*(1.9*t+.80)))
        # Visemes can combine; all shapes remain small relative to the facial geometry.
        cloth=E((t-.78)/1.75)*(1-.20*E((t-4.25)/.7))
        breath=.35+.32*np.sin(2*np.pi*.25*t)
        return np.array([blink,worry,smile,jaw,oh,ee,cloth,breath],dtype='<f4')
    def local_rotations(self,t):
        d={n:Rotation.identity() for n in self.names}
        for n,qs in self.tracks.items():
            q=Slerp(self.frames,Rotation.from_quat(qs))([np.clip(t,self.frames[0],self.frames[-1])])[0]
            d[n]=q
        # Contact-stage wrist correction. Tested visually against eight wrist orientation variants;
        # original v1.5 wrist orientation made both hands meet like a high-five.
        side='R' if self.key=='ava' else 'L';bn='wrist_'+side
        u=np.clip((t-2.3)/.9,0,1);u=u*u*(3-2*u)
        sign=1 if self.key=='ava' else -1
        d[bn]=d[bn]*Rotation.from_rotvec([0,0,sign*(-.80)*u])
        for n in self.names[len(self.old_names):]:d[n]=self.finger_rotation(n,t)
        return d
    def posed_matrices(self,t):
        loc=self.local_rotations(t);world_rot={};world_pos={};out=[]
        for n in self.names:
            p=self.parents[n]
            if p is None: world_rot[n]=loc[n];world_pos[n]=self.local[n]
            else: world_rot[n]=world_rot[p]*loc[n];world_pos[n]=world_pos[p]+world_rot[p].apply(self.local[n])
            mat=np.eye(4);mat[:3,:3]=world_rot[n].as_matrix()
            mat[:3,3]=world_pos[n]-world_rot[n].apply(self.rest[n])
            out.append(mat)
        return np.array(out)
    def deform(self,t):
        v=self.data['POSITION'].copy()
        w=self.expression(t)
        for i,n in enumerate(NAMES):v+=w[i]*self.morphs[n]
        trans=self.posed_matrices(t)
        out=np.zeros_like(v)
        for j in range(4):
            ids=self.data['JOINTS_0'][:,j];weights=self.data['WEIGHTS_0'][:,j]
            if not np.any(weights):continue
            mat=trans[ids];p=np.einsum('nij,nj->ni',mat[:,:3,:3],v)+mat[:,:3,3];out+=p*weights[:,None]
        return out
    def export(self):
        g=GLB();j=g.j;d=self.data
        attrs={}
        for name,comp,typ,norm in [('POSITION',5126,'VEC3',False),('NORMAL',5126,'VEC3',False),('COLOR_0',5121,'VEC4',True),('JOINTS_0',5123,'VEC4',False),('WEIGHTS_0',5126,'VEC4',False)]:
            attrs[name]=g.accessor(d[name],comp,typ,34962,norm,name=='POSITION')
        ii=g.accessor(d['indices'],5125,'SCALAR',34963,minmax=True)
        target=[{'POSITION':g.accessor(self.morphs[n],5126,'VEC3',34962)} for n in NAMES]
        j['materials'].append({'name':self.key+'_vertex_color','pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1], 'metallicFactor':0.0,'roughnessFactor':.84},'doubleSided':True})
        j['meshes']=[{'name':self.key+'_face_hands_cloth_v16','weights':[0]*len(NAMES),'extras':{'targetNames':NAMES},'primitives':[{'attributes':attrs,'indices':ii,'material':0,'targets':target}]}]
        for n in self.names:j['nodes'].append({'name':n,'translation':self.local[n].astype(float).tolist()})
        for n in self.names:
            p=self.parents[n]
            if p is not None:j['nodes'][self.names.index(p)].setdefault('children',[]).append(self.names.index(n))
        meshid=len(j['nodes']);j['nodes'].append({'name':self.key+'_actor_v16','mesh':0,'skin':0})
        inv=[]
        for n in self.names:
            mat=np.eye(4,dtype='<f4');mat[:3,3]=-self.rest[n]
            inv.append(mat.T.reshape(16))
        ib=g.accessor(np.stack(inv).astype('<f4'),5126,'MAT4')
        j['skins']=[{'name':self.key+'_43bone_v16','joints':list(range(len(self.names))),'inverseBindMatrices':ib,'skeleton':0}]
        j['scenes']=[{'name':self.key+'_v16','nodes':[0,meshid]}]
        time=g.accessor(self.frames.astype('<f4'),5126,'SCALAR',minmax=True)
        sm=[];chs=[]
        for name in self.tracks:
            q=self.tracks[name]
            side='R' if self.key=='ava' else 'L';bn='wrist_'+side
            if name==bn:
                def qadj(t,qv):
                    u=np.clip((t-2.3)/.9,0,1);u=u*u*(3-2*u)
                    sign=1 if self.key=='ava' else -1
                    return (Rotation.from_quat(qv)*Rotation.from_rotvec([0,0,sign*(-.80)*u])).as_quat()
                q=np.stack([qadj(float(t),qq) for t,qq in zip(self.frames,q)])
            out=g.accessor(np.array(q,dtype='<f4'),5126,'VEC4');sm.append({'input':time,'output':out,'interpolation':'LINEAR'})
            chs.append({'sampler':len(sm)-1,'target':{'node':self.names.index(name),'path':'rotation'}})
        for name in self.names[len(self.old_names):]:
            rot=np.stack([self.finger_rotation(name,float(t)).as_quat() for t in self.frames]).astype('<f4')
            out=g.accessor(rot,5126,'VEC4');sm.append({'input':time,'output':out,'interpolation':'LINEAR'})
            chs.append({'sampler':len(sm)-1,'target':{'node':self.names.index(name),'path':'rotation'}})
        weights=np.stack([self.expression(float(t)) for t in self.frames]).astype('<f4').reshape(-1)
        out=g.accessor(weights,5126,'SCALAR');sm.append({'input':time,'output':out,'interpolation':'LINEAR'})
        chs.append({'sampler':len(sm)-1,'target':{'node':meshid,'path':'weights'}})
        j['animations']=[{'name':'reach_finger_curl_dialogue_v16','samplers':sm,'channels':chs}]
        target=BASE/f'{self.key}_RIGGED_SPEECH_HANDS_v1_6.glb';g.write(target)
        # Package compact runtime data; original mesh arrays retained in models/base for future authoring.
        np.savez_compressed(BASE/f'{self.key}_v16_runtime.npz',**{**d,**{'MORPH_'+n:self.morphs[n] for n in NAMES}})
        meta={'key':self.key,'old_bones':len(self.old_names),'new_bones':len(self.names),'morphs':NAMES,
              'vertices':len(d['POSITION']),'triangles':len(d['indices'])//3,'duration_s':float(self.frames[-1]),
              'joint_names':self.names,'parents':self.parents,'source_mesh':'v1.5 frozen vertex arrays',
              'max_cloth_reach_delta_m':float(np.linalg.norm(self.morphs['cloth_reach'],axis=1).max()),
              'mouth_neutral': 'shut lips, dark inner membrane', 'status':'experimental, no Blender/Godot runtime verification'}
        (BASE/f'{self.key}_v16_manifest.json').write_text(json.dumps(meta,indent=2))
        return meta

def main():
    results={}
    for key in ('ava','noor'):
        actor=Actor(key);results[key]=actor.export();print(key,results[key]['vertices'],'verts',results[key]['new_bones'],'bones',flush=True)
    (QA/'build_report.json').write_text(json.dumps(results,indent=2))
    return results

if __name__=='__main__':main()
