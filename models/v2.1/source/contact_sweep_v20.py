"""Quantify actual triangle-triangle intersections in opposing animated hand surfaces (VTK)."""
import numpy as np,json, pathlib,vtk
from vtk.util.numpy_support import numpy_to_vtk
from scipy.spatial import cKDTree
from build_v20 import Actor
from build_v19 import ROOT

def handmesh(actor,side,t,offset=0):
    lo,hi=actor.ranges[f'{side}_CONTINUOUS_ANATOMICAL_HAND_v19']
    tri=actor.data['indices'].reshape(-1,3)
    tri=tri[np.all((tri>=lo)&(tri<hi),axis=1)]-lo
    V=actor.deform(t)[lo:hi].astype('float32')
    p=vtk.vtkPolyData();pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(V,deep=True));p.SetPoints(pts)
    cell=vtk.vtkCellArray();cell.SetCells(len(tri),numpy_to_vtk(np.column_stack([np.full(len(tri),3,dtype=np.int64),tri]).ravel(),deep=True,array_type=vtk.VTK_ID_TYPE))
    p.SetPolys(cell)
    return p,V,len(tri)

def measures(A,N,t,x=.0,z=.035):
    p,v,at=handmesh(A,'R',t);q,w,nt=handmesh(N,'L',t)
    m=vtk.vtkCollisionDetectionFilter();m.SetInputData(0,p);m.SetInputData(1,q)
    a=vtk.vtkTransform();b=vtk.vtkTransform();a.Translate(-.48,0,0);b.Translate(.48+x,0,z)
    m.SetTransform(0,a);m.SetTransform(1,b)
    m.SetCollisionModeToAllContacts();m.SetBoxTolerance(.0001);m.SetCellTolerance(0)
    m.Update()
    gap=float(cKDTree(v+np.array([-.48,0,0])).query(w+np.array([.48+x,0,z]))[0].min())
    return {'time_s':float(t),'noor_dx_m':float(x),'noor_dz_m':float(z),
            'triangle_intersections':int(m.GetNumberOfContacts()),'nearest_vertices_m':gap,
            'triangles_ava':at,'triangles_noor':nt}

if __name__=='__main__':
 A=Actor('ava');N=Actor('noor');coarse=[]
 for dz in [.038,.039,.040,.042,.045]:
  h=measures(A,N,3.4,z=dz);e=measures(A,N,5.15,z=dz)
  coarse.append({'noor_dz_m':dz,'hold':h,'end':e})
  print('candidate',dz,'hold hits',h['triangle_intersections'],'end hits',e['triangle_intersections'],flush=True)
 selected=None
 for c in sorted(coarse,key=lambda a:a['noor_dz_m']):
  if c['hold']['triangle_intersections'] or c['end']['triangle_intersections'] or c['end']['nearest_vertices_m']>.004:
   continue
  times=sorted(set(range(0,125,5))|{124})
  timeline=[measures(A,N,t/24,z=c['noor_dz_m']) for t in times]
  if all(x['triangle_intersections']==0 for x in timeline):
   selected={'choice':c,'timeline':timeline,'frames':times};break
 if selected is None:raise RuntimeError('No zero-collision candidate at sampled frames. Do not release.')
 report={'candidates':coarse,'selected':selected,'method':'VTK triangle collision, sampled encoded frames',
         'not_every_frame':True,'noor_depth_offset_m':selected['choice']['noor_dz_m']}
 (ROOT/'qa'/'CONTACT_SWEEP_V20.json').write_text(json.dumps(report,indent=2))
 print('CHOSEN DEPTH',selected['choice']['noor_dz_m'],'sample count',len(selected['timeline']))
