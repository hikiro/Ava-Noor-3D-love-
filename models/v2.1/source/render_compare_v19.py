"""Identical cameras and staging for v1.8/v1.9 contact topology comparison."""
import numpy as np,vtk
from PIL import Image,ImageDraw,ImageFont
from vtk.util.numpy_support import vtk_to_numpy
from build_v18 import Actor as Old
from build_v19 import Actor as New,ROOT
from render_motion_v19 import meshactor
OUT=ROOT/'previews';OUT.mkdir(exist_ok=True)
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',24)

def render(c,t,angle):
 r=vtk.vtkRenderer();r.SetBackground(.94,.91,.85)
 for a,off in [(c['ava'],(-.48,0,0)),(c['noor'],(.48,0,.038))]:
  d=a.data.copy();d['POSITION']=a.deform(t).astype('float32')
  act,_,_=meshactor(d);act.SetPosition(*off);r.AddActor(act)
 light=vtk.vtkLight();light.SetPosition(0,3,3);light.SetIntensity(1.12);r.AddLight(light)
 cam=r.GetActiveCamera();ang=np.deg2rad(angle);cam.SetPosition(1.4*np.sin(ang),1.48,1.4*np.cos(ang));cam.SetFocalPoint(0,1.13,0);cam.SetViewUp(0,1,0);cam.ParallelProjectionOn();cam.SetParallelScale(.185)
 win=vtk.vtkRenderWindow();win.SetOffScreenRendering(True);win.AddRenderer(r);win.SetSize(660,540);win.SetMultiSamples(0)
 w=vtk.vtkWindowToImageFilter();w.SetInput(win);win.Render();w.Update();raw=vtk_to_numpy(w.GetOutput().GetPointData().GetScalars()).reshape((540,660,-1));return Image.fromarray(np.flipud(raw[:,:,:3]))

old={n:Old(n) for n in ['ava','noor']};new={n:New(n) for n in ['ava','noor']}
sheet=Image.new('RGB',(1320,1160),'#e9e5dd');d=ImageDraw.Draw(sheet)
for k,angle in enumerate([0,45]):
 for j,(who,actors) in enumerate([('v1.8 — segmented hands',old),('v1.9 — unified hands',new)]):
  im=render(actors,3.4,angle)
  sheet.paste(im,(k*660,40+j*575));d.text((k*660+16,14+j*575),f'{who}   |   camera {angle}deg',font=FONT,fill='#1f2b31')
sheet.save(OUT/'HANDS_BEFORE_AFTER_V18_V19.png')
print('saved compare')
