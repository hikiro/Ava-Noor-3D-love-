#!/usr/bin/env python3
"""Identical close-up camera and lighting for v1.6/v1.7 at neutral and reach."""
import pathlib,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import vtk
from vtk.util.numpy_support import vtk_to_numpy,numpy_to_vtk
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from build_v17 import Actor as New, ROOT
from build_v16 import Actor as Old
from render_motion_v17 import meshactor

W,H=470,530
from itertools import product
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
def render(a,t,angle):
    r=vtk.vtkRenderer();r.SetBackground(.94,.88,.78)
    act,p,poly=meshactor(a.data);r.AddActor(act)
    p.SetData(numpy_to_vtk(a.deform(t).astype(np.float32),deep=True));p.Modified();poly.Modified()
    light=vtk.vtkLight();light.SetLightTypeToSceneLight();light.SetPosition(-2,4,5);light.SetIntensity(1.25);r.AddLight(light)
    light2=vtk.vtkLight();light2.SetLightTypeToSceneLight();light2.SetPosition(3,3,-2);light2.SetIntensity(.6);r.AddLight(light2)
    c=r.GetActiveCamera();c.SetPosition(3*np.sin(angle),1.25,3*np.cos(angle));c.SetFocalPoint(0,1.22,0);c.SetViewUp(0,1,0);c.ParallelProjectionOn();c.SetParallelScale(.36)
    w=vtk.vtkRenderWindow();w.SetOffScreenRendering(1);w.SetSize(W,H);w.AddRenderer(r)
    w.Render();grab=vtk.vtkWindowToImageFilter();grab.SetInput(w);grab.SetInputBufferTypeToRGB();grab.ReadFrontBufferOff();grab.Update()
    ar=vtk_to_numpy(grab.GetOutput().GetPointData().GetScalars()).reshape(H,W,3)
    return Image.fromarray(np.flipud(ar).copy())

def main():
    for key in ['ava','noor']:
        before=Old(key);after=New(key)
        sheet=Image.new('RGB',(4*W,2*(H+32)),'#112d30');draw=ImageDraw.Draw(sheet)
        for row,t in enumerate([0.,3.4]):
            for col,(actor,ang,label) in enumerate([(before,0,'V1.6 FRONT'),(after,0,'V1.7 FRONT'),(before,.72,'V1.6 3/4'),(after,.72,'V1.7 3/4')]):
                im=render(actor,t,ang);sheet.paste(im,(col*W,row*(H+32)+32))
                draw.text((col*W+12,row*(H+32)+7),f'{key.upper()} / {label} / t={t:.1f}',font=font,fill='white')
        out=ROOT/'previews'/f'{key}_SHOULDER_COMPARISON.png';sheet.save(out)
        print(out,flush=True)
if __name__=='__main__': main()
