"""Join v1.9 palm shells to v1.8 forearm topology with an actual indexed vertex bridge.

No floating cuff and no arbitrary hand scaling. The forearm ring is cut at a
supported elbow-retopology row; the hand shell is clipped by a plane. Four
intermediate support loops blend forearm/wrist/hand skinning in rest pose.
"""
import numpy as np
import trimesh
from collections import defaultdict
from elbow_retopo_v18 import loops_from_boundary

FIELDS=('POSITION','COLOR_0','JOINTS_0','WEIGHTS_0')

def polar(loop,xyz):
    ids=np.array(loop,dtype=np.int64)
    q=xyz[ids];c=q[:,[0,2]].mean(0)
    angle=np.arctan2(q[:,2]-c[1],q[:,0]-c[0])
    return list(ids[np.argsort(angle)]), np.sort(angle)

def dense_skin(idx,wei,nb):
    x=np.zeros(nb,np.float64)
    np.add.at(x,idx.astype(int),wei)
    return x

def simplify_skin(v):
    ix=np.argsort(v)[-4:][::-1]
    w=v[ix].astype(np.float32); w=w / max(float(w.sum()),1e-12)
    return ix.astype('<u2'),w.astype('<f4')

def bridge(actor):
    d=actor.data; originals=len(d['POSITION']); xyz=d['POSITION']; fs=d['indices'].reshape(-1,3)
    morphs=['MORPH_'+name for name in actor.morphs]
    vertex_attrs={k:list(d[k].copy()) for k in list(FIELDS)+morphs}
    # Normals regenerated from welded triangles, not interpolated from cut edges.
    cut_face_arrays=[];discarded={};new_vertices=[]; bridged={}; metadata={}
    nb=len(actor.names); scale=actor.rest['shoulder_R'][0]/.178
    seam_data={}
    for side,sgn in [('L',-1),('R',1)]:
        wrist_y=float(actor.rest['wrist_'+side][1]);
        # Existing forearm support row 70mm above wrist, nearest hand shell trimmed 8mm above wrist.
        bc=wrist_y+.070*scale; hc=wrist_y+.008*scale
        seam_data[side]={'body_y':bc,'hand_y':hc, 'hand_range':actor.ranges[f'{side}_CONTINUOUS_ANATOMICAL_HAND_v19']}
    old_body_start=actor.upper_body_vertex_start
    def add_vertex(a,b,t):
        idx=len(vertex_attrs['POSITION']); t=float(t)
        pos=(1-t)*xyz[a]+t*xyz[b]
        vertex_attrs['POSITION'].append(pos.astype('<f4'))
        for name in morphs:
            vertex_attrs[name].append(((1-t)*d[name][a]+t*d[name][b]).astype('<f4'))
        co=(1-t)*d['COLOR_0'][a].astype(float)+t*d['COLOR_0'][b].astype(float)
        vertex_attrs['COLOR_0'].append(np.clip(co,0,255).astype(np.uint8))
        sk=(1-t)*dense_skin(d['JOINTS_0'][a],d['WEIGHTS_0'][a],nb)+t*dense_skin(d['JOINTS_0'][b],d['WEIGHTS_0'][b],nb)
        ids,ws=simplify_skin(sk)
        vertex_attrs['JOINTS_0'].append(ids);vertex_attrs['WEIGHTS_0'].append(ws)
        return idx
    retained=[];hand_faces={'L':[],'R':[]};body_faces=[];removed_counts={'L':0,'R':0}
    hand_edges={'L':{},'R':{}}
    # Keep original triangles except the removed forearm caps and cropped hand tops.
    for f in fs:
        f=[int(v) for v in f]
        hand_side=None
        for side in ('L','R'):
            lo,hi=seam_data[side]['hand_range']
            if all(lo<=v<hi for v in f):hand_side=side;break
        if hand_side is not None:
            side=hand_side;plane=seam_data[side]['hand_y'];cache=hand_edges[side]
            yy=xyz[f,1]; inside=yy<=plane+1e-8
            if not any(inside):removed_counts[side]+=1;continue
            if all(inside):
                retained.append(f);hand_faces[side].append(f);continue
            # Clip each original triangle against the hand plane, reusing edge seam vertices.
            out=[]
            def xpoint(a,b):
                key=tuple(sorted((a,b)))
                if key not in cache:
                    t=(plane-xyz[a,1])/(xyz[b,1]-xyz[a,1])
                    cache[key]=add_vertex(a,b,t)
                return cache[key]
            prev=f[-1]; previn=xyz[prev,1]<=plane+1e-8
            for curr in f:
                cin=xyz[curr,1]<=plane+1e-8
                if previn!=cin:out.append(xpoint(prev,curr))
                if cin:out.append(curr)
                prev=curr;previn=cin
            for k in range(1,len(out)-1):
                tri=[out[0],out[k],out[k+1]];retained.append(tri);hand_faces[side].append(tri)
            continue
        if all(v>=old_body_start for v in f):
            drop=False
            for side,sgn in [('L',-1),('R',1)]:
                below=(xyz[f,1]<seam_data[side]['body_y']-1e-5)
                distal=(sgn*xyz[f,0]>.190*scale)
                if np.any(below & distal):
                    drop=True;removed_counts[side]+=1;break
            if drop:continue
            retained.append(f);body_faces.append(f)
        else:retained.append(f)
    # Extract the 4 anatomical boundary curves. Separate body and hands means
    # no crossing into unrelated clothing meshes during the weld operation.
    for side,sgn in [('L',-1),('R',1)]:
        bc,hc=seam_data[side]['body_y'],seam_data[side]['hand_y']
        body_options=[]
        for loop in loops_from_boundary(body_faces):
            ids=loop[:-1];q=np.array([vertex_attrs['POSITION'][i] for i in ids]);
            if len(ids)>16 and np.mean(sgn*q[:,0])>.20*scale and abs(np.mean(q[:,1])-bc)<.001*scale:
                body_options.append(ids)
        hand_options=[]
        for loop in loops_from_boundary(hand_faces[side]):
            ids=loop[:-1];q=np.array([vertex_attrs['POSITION'][i] for i in ids]);
            if len(ids)>16 and abs(np.mean(q[:,1])-hc)<.001*scale:hand_options.append(ids)
        if len(body_options)!=1 or len(hand_options)!=1:
            raise RuntimeError(f'{side} loops body={list(map(len,body_options))}, hand={list(map(len,hand_options))}')
        verts=np.array(vertex_attrs['POSITION'])
        body,_=polar(body_options[0],verts);hand,_=polar(hand_options[0],verts)
        # Angular zipper bridges loops of different polygon counts without duplicate seams.
        hb=np.array(hand);qb=verts[hb]; cb=qb[:,[0,2]].mean(axis=0)
        ah=np.arctan2(qb[:,2]-cb[1],qb[:,0]-cb[0]);ah=np.unwrap(ah)
        # atan2 sorted sequence (wrapped into [-pi,pi]), pad endpoints for periodic interpolation.
        aa=np.r_[ah[-1]-2*np.pi,ah,ah[0]+2*np.pi]
        qpad=np.vstack([qb[-1],qb,qb[0]])
        bxy=verts[np.array(body)];center=bxy[:,[0,2]].mean(0)
        theta=np.arctan2(bxy[:,2]-center[1],bxy[:,0]-center[0]);theta=np.unwrap(theta)
        # hand seam features sampled by polar direction, not naive vertex indices.
        sample=np.column_stack([np.interp(theta,aa,qpad[:,k]) for k in range(3)])
        body_skin=np.array([dense_skin(d['JOINTS_0'][i],d['WEIGHTS_0'][i],nb) for i in body])
        hand_skin=np.array([dense_skin(vertex_attrs['JOINTS_0'][i],vertex_attrs['WEIGHTS_0'][i],nb) for i in hb])
        hs=np.vstack([hand_skin[-1],hand_skin,hand_skin[0]])
        hs_res=np.column_stack([np.interp(theta,aa,hs[:,k]) for k in range(nb)])
        rows=[body]
        for j in range(1,5):
            t=j/5.;ease=t*t*(3-2*t);newrow=[]
            for k,vid in enumerate(body):
                p=(1-t)*bxy[k]+t*sample[k];p[1]=(1-t)*bc+t*hc
                idx=len(vertex_attrs['POSITION']);vertex_attrs['POSITION'].append(p.astype('<f4'))
                for name in morphs:vertex_attrs[name].append(np.zeros(3,dtype='<f4'))
                color=(1-t)*d['COLOR_0'][vid].astype(float)+t*vertex_attrs['COLOR_0'][hb[np.argmin(np.abs(ah-theta[k]))]].astype(float)
                vertex_attrs['COLOR_0'].append(np.clip(color,0,255).astype(np.uint8))
                sk=(1-ease)*body_skin[k]+ease*hs_res[k];ii,ww=simplify_skin(sk)
                vertex_attrs['JOINTS_0'].append(ii);vertex_attrs['WEIGHTS_0'].append(ww)
                newrow.append(idx)
            rows.append(newrow)
        # Connect rings of equal count.
        patches=[]
        for ra,rb in zip(rows[:-1],rows[1:]):
            for i in range(len(ra)):
                nxt=(i+1)%len(ra)
                patches.extend([[ra[i],ra[nxt],rb[i]],[ra[nxt],rb[nxt],rb[i]]])
        # last-row -> clipped hand seam with unequal counts, advancing by angle.
        row=rows[-1];n=len(row);m=len(hand)
        ar=np.arctan2(verts[np.array(body),2]-center[1],verts[np.array(body),0]-center[0]);ar=np.unwrap(ar)
        # orient from [-pi,pi] with same phase as hand, round-trip one revolution.
        i=j=0
        while i<n or j<m:
            tA=ar[i+1] if i+1<n else ar[0]+2*np.pi
            tB=ah[j+1] if j+1<m else ah[0]+2*np.pi
            if i==n:takeA=False
            elif j==m:takeA=True
            else:takeA=tA<=tB
            if takeA:
                patches.append([row[i%n],row[(i+1)%n],hand[j%m]]);i+=1
            else:
                patches.append([row[i%n],hand[(j+1)%m],hand[j%m]]);j+=1
        retained.extend(patches)
        bridged[side]={'forearm_boundary_vertices':len(body),'hand_boundary_vertices':len(hand),'support_loops':4,
                       'wrist_transition_m':float(bc-hc),'skin_weights':'dense 43-bone linear blend, top-4 normalized',
                       'new_faces':len(patches),'crop_removed_faces':removed_counts[side]}
    # Repair a pre-v2.0 rigging fault: nearest-finger assignment abruptly switched
    # neighboring surface vertices between unrelated tip bones. Blend digit influence
    # smoothly across knuckle width while retaining distinct moving fingers.
    digit_reweights={}
    for side in ('L','R'):
        lo,hi=seam_data[side]['hand_range']; cx,hy,hz=actor.rest['hand_'+side]
        sign=1 if side=='R' else -1
        centers=np.array([actor.rest[f'{side}_finger{i}_base'][0] for i in range(4)])
        root_y=np.mean([actor.rest[f'{side}_finger{i}_base'][1] for i in range(4)])
        tip_y=np.mean([actor.rest[f'{side}_finger{i}_tip'][1] for i in range(4)])
        affected=0
        for idx in range(lo,hi):
            x,y,z=vertex_attrs['POSITION'][idx]
            # Continuous thumb-to-index web influence; the old binary thumb mask
            # caused neighboring 1mm edges to follow unrelated bones.
            u=float(np.clip((root_y+.009*scale-y)/(.033*scale),0,1))
            u=u*u*(3-2*u)
            v=float(np.clip((tip_y+.010*scale-y)/(.021*scale),0,1));v=v*v*(3-2*v)
            # Gaussian bands smoothly bridge finger webs without making fingers rigid.
            sigma=.0068*scale
            g=np.exp(-.5*((x-centers)/sigma)**2);g/=max(float(g.sum()),1e-10)
            dense=np.zeros(nb,np.float64)
            dense[actor.names.index('hand_'+side)]=1-u
            for finger in range(4):
                dense[actor.names.index(f'{side}_finger{finger}_base')]+=u*(1-v)*g[finger]
                dense[actor.names.index(f'{side}_finger{finger}_tip')]+=u*v*g[finger]
            xt=sign*(x-cx)
            alpha=np.clip((xt-.019*scale)/(.022*scale),0,1);alpha=alpha*alpha*(3-2*alpha)
            low=np.clip((y-(hy-.077*scale)) /(.024*scale),0,1);low=low*low*(3-2*low)
            high=np.clip(((hy+.026*scale)-y)/(.014*scale),0,1);high=high*high*(3-2*high)
            alpha*=low*high
            # Thumb proximal/tip phalanges rotate independently, with webbed palm influence.
            thumb_u=float(np.clip((xt-.015*scale)/(.025*scale),0,1));thumb_u=thumb_u*thumb_u*(3-2*thumb_u)
            thumb_v=float(np.clip((xt-.036*scale)/(.020*scale),0,1));thumb_v=thumb_v*thumb_v*(3-2*thumb_v)
            thumb=np.zeros(nb,np.float64)
            thumb[actor.names.index('hand_'+side)]=1-thumb_u
            thumb[actor.names.index(f'{side}_thumb_prox')]=thumb_u*(1-thumb_v)
            thumb[actor.names.index(f'{side}_thumb_tip')]=thumb_u*thumb_v
            dense=(1-alpha)*dense+alpha*thumb
            jj,ww=simplify_skin(dense)
            vertex_attrs['JOINTS_0'][idx]=jj;vertex_attrs['WEIGHTS_0'][idx]=ww;affected+=1
        digit_reweights[side]=affected
    attrs={k:np.asarray(v,dtype=d[k].dtype) for k,v in vertex_attrs.items()}
    f=np.array(retained,dtype=np.uint32)
    # Determine winding consistency on the full indexed mesh and repair if needed;
    # do not silently accept inverse-facing strips.
    mesh=trimesh.Trimesh(vertices=attrs['POSITION'],faces=f,process=False)
    wind_before=bool(mesh.is_winding_consistent)
    if not wind_before:
        trimesh.repair.fix_winding(mesh)
        f=mesh.faces.astype('<u4')
    wind_after=bool(mesh.is_winding_consistent)
    # Vertex normals computed from finalized triangle orientation.
    attrs['NORMAL']=mesh.vertex_normals.astype('<f4')
    attrs['indices']=f.reshape(-1)
    if not mesh.is_watertight or not wind_after:
        boundary=loops_from_boundary(f)
        raise RuntimeError(f'wrist weld not watertight or winding inconsistent: watertight={mesh.is_watertight} wind={wind_after} loops={[len(b) for b in boundary]}')
    for k in morphs:actor.morphs[k[6:]]=attrs[k]
    actor.data=attrs
    actor.wrist_weld_metadata={'sides':bridged,'watertight':bool(mesh.is_watertight),
                               'winding_consistent':wind_after,'winding_before_repair':wind_before,
                               'smooth_digit_weight_vertices':digit_reweights,
                               'vertices':len(attrs['POSITION']),'faces':len(f),
                               'limitations':['Skinning is procedural, not manually sculpted','Mesh union does not prove that fingers wrap the other hand correctly']}
    actor.mesh_health['wrist_weld']=actor.wrist_weld_metadata
    return actor.wrist_weld_metadata
