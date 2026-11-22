"""Render isolated contact closeups at full resolution; not a cosmetic sketch."""
import numpy as np,vtk
from PIL import Image,ImageDraw,ImageFont
from vtk.util.numpy_support import numpy_to_vtk,vtk_to_numpy
from build_v19 import Actor,ROOT
from render_motion_v19 import meshactor
from pathlib import Path
OUT=ROOT/'previews';OUT.mkdir(exist_ok=True)
A=Actor('ava');N=Actor('noor')
for t in [2.1,3.4,4.8]:
 for angle in [0,25,55]:
  r=vtk.vtkRenderer();r.SetBackground(.94,.91,.85)
  for a,off in [(A,(-.48,0,0)),(N,(.48,0,.038))]:
   d=a.data.copy();d['POSITION']=a.deform(t).astype('float32')
   actor,_,_=meshactor(d);actor.SetPosition(*off);r.AddActor(actor)
  light=vtk.vtkLight();light.SetPosition(0,3,3);light.SetIntensity(1.1);r.AddLight(light)
  cam=r.GetActiveCamera();ang=np.deg2rad(angle);cam.SetPosition(1.4*np.sin(ang),1.48,1.4*np.cos(ang));cam.SetFocalPoint(0,1.13,0);cam.SetViewUp(0,1,0);cam.ParallelProjectionOn();cam.SetParallelScale(.185)
  win=vtk.vtkRenderWindow();win.SetOffScreenRendering(True);win.AddRenderer(r);win.SetSize(600,600);win.SetMultiSamples(0)
  w=vtk.vtkWindowToImageFilter();w.SetInput(win);win.Render();w.Update();arr=vtk_to_numpy(w.GetOutput().GetPointData().GetScalars()).reshape((600,600,-1));im=Image.fromarray(np.flipud(arr[:,:,:3]));im.save(OUT/f'CONTACT_{t:.1f}s_{angle:02d}deg_v19.png');print(t,angle,flush=True)
