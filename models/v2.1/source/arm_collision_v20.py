"""Collision sampling of continuous wrist+hands and distal forearms (not only cropped palms)."""
import numpy as np, vtk
from vtk.util.numpy_support import numpy_to_vtk
from scipy.spatial import cKDTree
from build_v20 import Actor

def part(actor,side,t):
    P=actor.data['POSITION']; f=actor.data['indices'].reshape(-1,3);s=actor.rest['shoulder_R'][0]/.178
    sign=1 if side=='R' else -1
    mask=(sign*P[:,0]>.162*s)&(P[:,1]<actor.rest['elbow_'+side][1]-.015*s)
    face=f[np.all(mask[f],axis=1)]
    used,rev=np.unique(face,return_inverse=True);tri=rev.reshape(-1,3)
    V=actor.deform(t)[used].astype('float32')
    q=vtk.vtkPolyData();pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(V,deep=True));q.SetPoints(pts)
    c=vtk.vtkCellArray();c.SetCells(len(tri),numpy_to_vtk(np.column_stack([np.full(len(tri),3,dtype=np.int64),tri]).ravel(),deep=True,array_type=vtk.VTK_ID_TYPE));q.SetPolys(c)
    return q,V,len(tri)

def measure(A,N,t,z=.039):
    a,V,n1=part(A,'R',t);b,W,n2=part(N,'L',t)
    m=vtk.vtkCollisionDetectionFilter();m.SetInputData(0,a);m.SetInputData(1,b)
    ta=vtk.vtkTransform();tb=vtk.vtkTransform();ta.Translate(-.48,0,0);tb.Translate(.48,0,z)
    m.SetTransform(0,ta);m.SetTransform(1,tb)
    m.SetCollisionModeToAllContacts();m.SetBoxTolerance(.0001);m.SetCellTolerance(0);m.Update()
    d=float(cKDTree(V+[-.48,0,0]).query(W+[.48,0,z])[0].min())
    return {'time_s':float(t),'hits':int(m.GetNumberOfContacts()),'gap_m':d,'triangles':[n1,n2]}
if __name__=='__main__':
    A=Actor('ava');N=Actor('noor')
    import time
    x=time.time()
    for t in (0,2.1,3.4,4.76,5.15):
        print(measure(A,N,t),time.time()-x,flush=True)
