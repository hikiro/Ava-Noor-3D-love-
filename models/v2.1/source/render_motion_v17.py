#!/usr/bin/env python3
"""Headless VTK render of evaluated CPU skinning for VillaVerse v1.4.
This renders *actual triangles* post linear blend skinning, never an image simulation.
"""
import vtk,numpy as np,math,sys,subprocess,os,io,time
from vtk.util.numpy_support import numpy_to_vtk,vtk_to_numpy
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from build_v17 import ROOT as HERE,Actor
OUT=HERE/'previews';OUT.mkdir(exist_ok=True)
W,H=540,960
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def meshactor(d):
    poly=vtk.vtkPolyData();pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(d['POSITION'].astype(np.float32),deep=True));poly.SetPoints(pts)
    ntri=len(d['indices'])//3
    conn=np.column_stack([np.full(ntri,3,dtype=np.int64),d['indices'].reshape((-1,3))]).ravel()
    ca=vtk.vtkCellArray();ca.SetCells(ntri,numpy_to_vtk(conn,deep=True,array_type=vtk.VTK_ID_TYPE));poly.SetPolys(ca)
    cols=numpy_to_vtk(d['COLOR_0'][:,:3].copy(),deep=True,array_type=vtk.VTK_UNSIGNED_CHAR);cols.SetNumberOfComponents(3);poly.GetPointData().SetScalars(cols)
    norms=numpy_to_vtk(d['NORMAL'].astype(np.float32),deep=True);norms.SetNumberOfComponents(3);poly.GetPointData().SetNormals(norms)
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly);mapper.ScalarVisibilityOn()
    actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetInterpolationToPhong()
    actor.GetProperty().SetAmbient(.29);actor.GetProperty().SetDiffuse(.64);actor.GetProperty().SetSpecular(.10);actor.GetProperty().SetSpecularPower(14)
    return actor,pts,poly

def cube(renderer,center,ext,color,rough=.25):
    src=vtk.vtkCubeSource();src.SetXLength(ext[0]);src.SetYLength(ext[1]);src.SetZLength(ext[2]);src.SetCenter(*center)
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(src.GetOutputPort())
    act=vtk.vtkActor();act.SetMapper(mapper);act.GetProperty().SetColor(*color);act.GetProperty().SetAmbient(rough)
    renderer.AddActor(act)

def ball(renderer,center,radii,color):
    src=vtk.vtkSphereSource();src.SetThetaResolution(12);src.SetPhiResolution(10);src.SetRadius(1)
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(src.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(mapper);a.SetPosition(*center);a.SetScale(*radii);a.GetProperty().SetColor(*color);a.GetProperty().SetAmbient(.26)
    renderer.AddActor(a)

def scene_bg(renderer):
    # warm villa garden: architectural forms + dark floor and a framed movie-night alcove
    cube(renderer,(0,-.052,-.1),(12,.06,8),(.55,.52,.40))
    cube(renderer,(0,1.8,-1.25),(6.0,3.6,.15),(.83,.77,.66))
    cube(renderer,(0,2.8,-1.16),(4.0,1.1,.08),(.41,.68,.66))
    cube(renderer,(-1.50,1.9,-1.07),(.19,2.9,.20),(.96,.88,.74))
    cube(renderer,(1.50,1.9,-1.07),(.19,2.9,.20),(.96,.88,.74))
    cube(renderer,(0,3.27,-1.07),(3.25,.14,.21),(.97,.88,.74))
    cube(renderer,(0,.06,-.55),(5.5,.13,1.7),(.87,.74,.60))
    for x in (-2.0,-1.65,1.65,2.0):
      for z in (-.50,.70):
       ball(renderer,(x,.39,z),(.18,.26,.25),(.25,.41,.31))
       ball(renderer,(x+.10,.55,z),(.17,.20,.17),(.41,.56,.31))
    cube(renderer,(-1.97,.56,-.70),(.45,.65,.43),(.39,.43,.32))
    cube(renderer,(1.97,.56,-.70),(.45,.65,.43),(.39,.43,.32))
    for x in np.arange(-2,2.1,.6):
     cube(renderer,(float(x),.001,.25),(.43,.012,.40),(.75,.70,.61))
    # shadows under feet, diffuse oval disks
    for x in [-.48,.48]:
      ball(renderer,(x,.004,.10),(.23,.006,.13),(.38,.35,.30))

def run(N=125, fps=24,small=False):
  keys=['ava','noor'];v16={key:Actor(key) for key in keys};data={key:v16[key].data for key in keys}
  renderer=vtk.vtkRenderer();renderer.SetBackground(.77,.83,.79)
  renderer.SetBackground2(.97,.88,.73);renderer.GradientBackgroundOn()
  scene_bg(renderer)
  actors={}
  for key,offset in [('ava',-.48),('noor',.48)]:
     a,p,poly=meshactor(data[key]);a.SetPosition(offset,0,0);renderer.AddActor(a);actors[key]=(a,p,poly)
  def light(pos,intensity,color):
     l=vtk.vtkLight();l.SetLightTypeToSceneLight();l.SetPosition(*pos);l.SetFocalPoint(0,1,0)
     l.SetIntensity(intensity);l.SetColor(*color);renderer.AddLight(l)
  light((-3,5,5),1.1,(1,.92,.83));light((3,2,3),.55,(.81,.88,1));light((0,4,-2),.35,(1,.84,.70))
  cam=renderer.GetActiveCamera();cam.SetPosition(0,2.00,5.6);cam.SetFocalPoint(0,1.12,0);cam.SetViewUp(0,1,0)
  cam.ParallelProjectionOn();cam.SetParallelScale(1.53)
  win=vtk.vtkRenderWindow();win.SetOffScreenRendering(True);win.AddRenderer(renderer);win.SetSize(W,H);win.SetMultiSamples(0)
  filt=vtk.vtkWindowToImageFilter();filt.SetInput(win);filt.ReadFrontBufferOff()
  font_big=ImageFont.truetype(BOLD,27);font_small=ImageFont.truetype(FONT,14);font_mid=ImageFont.truetype(BOLD,18)
  encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','19','-movflags','+faststart',str(OUT/'Ava_Noor_v17_CONTINUOUS_SHOULDERS.mp4')],stdin=subprocess.PIPE)
  frames=[]
  for i in range(N):
     t=i/fps
     for key in keys:
        a,pts,poly=actors[key];v=v16[key].deform(t)
        pts.SetData(numpy_to_vtk(v.astype(np.float32),deep=True));pts.Modified();poly.Modified()
     win.Render();filt.Modified();filt.Update()
     img=filt.GetOutput();v=vtk_to_numpy(img.GetPointData().GetScalars()).reshape((H,W,-1))
     frame=Image.fromarray(np.flipud(v[:,:,:3]).copy())
     d=ImageDraw.Draw(frame)
     d.rectangle((0,0,W,88),fill=(17,36,38))
     d.text((20,13),'VILLA VERSE',font=font_big,fill=(248,239,214))
     d.text((20,52),'AVA + NOOR    /    V1.7 CONTINUOUS SHOULDERS + SPEECH',font=font_small,fill=(204,210,199))
     d.rectangle((0,H-99,W,H),fill=(17,36,38))
     subtitle=('Noor, listen...' if t<1.0 else 'Ava reaches for Noor.' if t<2.6 else 'Their fingers curl.' if t<4.4 else 'Hold the connection.')
     bbox=d.textbbox((0,0),subtitle,font=font_mid)
     d.text(((W-(bbox[2]-bbox[0]))/2,H-75),subtitle,font=font_mid,fill=(246,230,196))
     d.text((22,H-38),f'{t:04.2f}s  |  24 fps  |  CPU skinning',font=font_small,fill=(191,207,201))
     if i in [0,24,60,80,104,124]:frames.append((i,frame.copy()))
     encoder.stdin.write(frame.tobytes())
     if i%24==0:print('rendered',i,'of',N,flush=True)
  encoder.stdin.close();rc=encoder.wait();assert rc==0
  # 6 annotated images as contact-sheet
  cw,ch=360,630; sheet=Image.new('RGB',(cw*3,ch*2),'#F8F1E6')
  for k,(i,f) in enumerate(frames):sheet.paste(f.resize((cw,ch)),((k%3)*cw,(k//3)*ch))
  sheet.save(OUT/'SIX_POSE_V17_INSPECTION.png')
  Image.open(OUT/'SIX_POSE_V17_INSPECTION.png').save(OUT/'SIX_POSE_V17_INSPECTION.png')
  frames[3][1].save(OUT/'CONTACT_V17_DETAIL.png')
  print('VIDEO OK',rc,flush=True)

if __name__=='__main__':run()
