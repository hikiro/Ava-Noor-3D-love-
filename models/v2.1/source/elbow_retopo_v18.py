"""Replace implicit-mesh elbows and forearms with connected circumferential quad rings.

Operates on the single watertight v1.7 upper-body mesh, cutting each free arm at
Y=1.117*(per-character scale) and sewing a ruled ring mesh onto that actual boundary.
No floating tubes or caps are added on top of the old surface. Returns one closed mesh.
"""
import numpy as np
import trimesh
from collections import defaultdict, Counter
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

def loops_from_boundary(faces):
    uses=defaultdict(list)
    for fi,(a,b,c) in enumerate(faces):
        for u,v in [(a,b),(b,c),(c,a)]:uses[tuple(sorted((int(u),int(v))))].append((int(u),int(v)))
    directed=[x[0] for x in uses.values() if len(x)==1]
    nxt=defaultdict(list)
    for a,b in directed:nxt[a].append(b)
    loops=[];visited=set()
    for a,b in directed:
        if (a,b) in visited:continue
        start=a;u=a;v=b;loop=[u]
        for j in range(len(directed)+3):
            visited.add((u,v));loop.append(v)
            if v==start:break
            opts=[z for z in nxt[v] if (v,z) not in visited]
            if not opts:break
            u,v=v,opts[0]
        loops.append(loop)
    return loops

def retopo(v,f,rest,scale=1.):
    points=[p.astype(float).tolist() for p in np.asarray(v)]
    faces=[tuple(map(int,ff)) for ff in np.asarray(f)]
    seam_meta={}
    for side,sgn in [('L',-1),('R',1)]:
        cut=1.117*scale
        # At cut height, trunk surface x<.155*scale and isolated arm surface x>.167*scale.
        # All triangles in the arm below the cut are retained nowhere else.
        # Component flood *below* the cut; arm + torso are disjoint there,
        # even though all are one surface above at the shoulder.
        xyz=np.array(points)
        ff=np.asarray(faces,dtype=np.int64)
        below=xyz[:,1]<cut-1e-8
        e=np.concatenate([ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]],axis=0)
        e=e[below[e[:,0]] & below[e[:,1]]]
        nodes=np.where(below)[0]
        remap=np.full(len(points),-1,int);remap[nodes]=np.arange(len(nodes))
        ei=remap[e]
        g=coo_matrix((np.ones(len(ei)*2,dtype=np.int8),
             (np.r_[ei[:,0],ei[:,1]],np.r_[ei[:,1],ei[:,0]])),
             shape=(len(nodes),len(nodes))).tocsr()
        ncomp,labels=connected_components(g,directed=False)
        wrist=np.array(rest[f'wrist_{side}'])
        guess=nodes[np.argmin(np.linalg.norm(xyz[nodes]-wrist,axis=1))]
        arm_comp=labels[remap[guess]]
        is_arm=np.zeros(len(points),bool);is_arm[nodes[labels==arm_comp]]=True
        # A separate arm component should include most of the distal surface.
        if np.sum(is_arm)<100 or np.mean(sgn*xyz[is_arm,0])<.18*scale:
            raise RuntimeError(f'Arm component not separated: side={side}, size={np.sum(is_arm)}, components={ncomp}')
        face_out=[];isect_cache={}
        def intersect(a,b):
            key=tuple(sorted([a,b]))
            if key not in isect_cache:
                A=np.array(points[a]);B=np.array(points[b]);ratio=(cut-A[1])/(B[1]-A[1])
                q=A+ratio*(B-A);q[1]=cut
                isect_cache[key]=len(points);points.append(q.tolist())
            return isect_cache[key]
        touched=0
        for face in faces:
            coords=np.array([points[i] for i in face]);
            # Isolated free-arm region; never modify any chest/armpit triangles.
            target=bool(np.any(is_arm[np.asarray(face)]))
            if not target:
                face_out.append(face);continue
            touched+=1
            if np.max(coords[:,1])<=cut:continue
            # Keep only region y>=cut. Maintain source face winding.
            out=[];prev=face[-1];pin=points[prev][1]>=cut
            for cur in face:
                cin=points[cur][1]>=cut
                if pin!=cin:out.append(intersect(prev,cur))
                if cin:out.append(cur)
                prev=cur;pin=cin
            for k in range(1,len(out)-1):face_out.append((out[0],out[k],out[k+1]))
        faces=face_out
        # Extract the open arm seam(s) after clipping; if anything else opens, fail explicitly.
        all_loops=loops_from_boundary(faces)
        candidates=[]
        for loop in all_loops:
            q=np.array([points[i] for i in loop[:-1]])
            if len(q)>10 and np.mean(sgn*q[:,0])>.18*scale and abs(np.mean(q[:,1])-cut)<.002*scale:
                candidates.append(loop)
        if len(candidates)!=1:
            raise RuntimeError(f'{side}: expected 1 clean arm seam, got {len(candidates)}; all loops {[len(l) for l in all_loops]}')
        seam=candidates[0][:-1]
        q=np.array([points[i] for i in seam]);
        elbow=np.array(rest[f'elbow_{side}']); wrist=np.array(rest[f'wrist_{side}']);shoulder=np.array(rest[f'shoulder_{side}'])
        # Follow the proximal arm and then distal forearm; avoid straight-angle elbow notch.
        def center(y):
            if y>=elbow[1]:
                t=np.clip((cut-y)/(cut-elbow[1]),0,1);return shoulder+(elbow-shoulder)*np.clip((shoulder[1]-y)/(shoulder[1]-elbow[1]),0,1)
            return elbow+(wrist-elbow)*np.clip((elbow[1]-y)/(elbow[1]-wrist[1]),0,1)
        orig_center=np.array([np.mean(q[:,0]),cut,np.mean(q[:,2])])
        theta=np.arctan2(q[:,2]-orig_center[2],q[:,0]-orig_center[0])
        # Multiple supporting loops within 6cm of bend, not one pivot-straddling strip.
        ylevels=np.array([cut-.006*scale, elbow[1]+.026*scale, elbow[1]+.019*scale,
                 elbow[1]+.018*scale,elbow[1]+.008*scale,elbow[1],
                 elbow[1]-.009*scale, elbow[1]-.019*scale,elbow[1]-.036*scale,
                 elbow[1]-.056*scale, wrist[1]+.11*scale,wrist[1]+.07*scale,
                 wrist[1]+.03*scale,wrist[1]-.008*scale,wrist[1]-.030*scale])
        ylevels=sorted(set([round(float(y),8) for y in ylevels]),reverse=True)
        rows=[seam]
        for ridx,y in enumerate(ylevels):
            # Axis-centred oval sections approximate elbow/forearm anatomy, preserve volume.
            if y>elbow[1]+.025*scale:rx,rz=.044,.042
            elif y>elbow[1]-.035*scale:rx,rz=.046,.042
            else:
                fdist=np.clip((elbow[1]-y)/(elbow[1]-wrist[1]+.03*scale),0,1)
                rx=.046*(1-fdist)+.026*fdist;rz=.042*(1-fdist)+.027*fdist
            if ridx==len(ylevels)-1:rx,rz=.019,.020
            mid=center(y)
            # First row is nearly seam-size; subsequent rings blend gradually to sculpted ellipse.
            verts=[]
            # Conform the first support rings to the *actual* seam contours.
            # Abrupt radius changes caused a visible horizontal shelf in pass 1.
            fade=np.clip((cut-y)/(.048*scale),0,1)
            fade=fade*fade*(3-2*fade)
            for vi,t in enumerate(theta):
                target=np.array([mid[0]+rx*scale*np.cos(t),y,mid[2]+rz*scale*np.sin(t)])
                seam_cont=np.array([q[vi,0],y,q[vi,2]])
                p=(1-fade)*seam_cont+fade*target
                verts.append(len(points));points.append(p.tolist())
            rows.append(verts)
            a,b=rows[-2],rows[-1]
            for i in range(len(a)):
                j=(i+1)%len(a)
                # Reverse boundary orientation (b->a) at the seam.
                faces.append((a[j],a[i],b[i]));faces.append((a[j],b[i],b[j]))
        # Apex is the end-cap, overlapping the separately skinned wrist/hand meshes.
        last=rows[-1];tail=center(ylevels[-1]-.007*scale)
        apex=len(points);points.append([float(tail[0]),float(tail[1]),float(tail[2])])
        for i in range(len(last)):faces.append((last[(i+1)%len(last)],last[i],apex))
        seam_meta[side]={'cut_height_m':cut,'seam_vertex_count':len(seam),'ring_count':len(rows),
                        'clipped_source_faces':touched,'retopo_triangles':2*len(seam)*len(ylevels)+len(seam),
                        'elbow_position_m':elbow.tolist(),'wrist_position_m':wrist.tolist(),
                        'support_loops_near_joint':7}
    verts=np.array(points,np.float32)
    tri=np.array(faces,np.uint32)
    # Remove unreferenced old distal-arm vertices. Manifold checks rely on indexed adjacency.
    used,inv=np.unique(tri,return_inverse=True)
    verts=verts[used];tri=inv.reshape(-1,3).astype('<u4')
    mesh=trimesh.Trimesh(vertices=verts,faces=tri,process=False)
    if mesh.volume < 0:
        tri=tri[:,[0,2,1]].copy();mesh=trimesh.Trimesh(vertices=verts,faces=tri,process=False)
    if not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1:
        boundary=loops_from_boundary(tri)
        raise RuntimeError(f'Retopo not manifold: watertight={mesh.is_watertight} loops={[len(l) for l in boundary]} components={len(mesh.split(only_watertight=False))}')
    return verts,tri,mesh.vertex_normals.astype('<f4'),seam_meta
