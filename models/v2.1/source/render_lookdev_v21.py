"""Render actual deformed triangle meshes: full/half expression and finger-pose comparisons."""
import vtk, numpy as np
from PIL import Image,ImageDraw,ImageFont
from vtk.util.numpy_support import numpy_to_vtk,vtk_to_numpy
from build_v21 import Actor
from render_motion_v20 import meshactor
from build_v19 import ROOT
OUT=ROOT/'previews';OUT.mkdir(exist_ok=True)
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=ImageFont.truetype(BOLD,22)

def image_of(poses,look,angle=0,size=(560,500)):
    r=vtk.vtkRenderer();r.SetBackground(.94,.91,.85)
    for actor,pos,t in poses:
        d=dict(actor.data);d['POSITION']=actor.deform(t).astype('float32')
        mesh,_,_=meshactor(d);mesh.SetPosition(*pos);r.AddActor(mesh)
    for xyz,color,power in [((-2,3,5),(1,.94,.89),1.4),((2,3,0),(.84,.91,1),.8)]:
        light=vtk.vtkLight();light.SetPosition(*xyz);light.SetIntensity(power);light.SetColor(*color);r.AddLight(light)
    cam=r.GetActiveCamera()
    if look=='face':
        cy=1.52;cz=.05
        cam.SetPosition(0,cy+.08,2.3);cam.SetFocalPoint(0,cy,cz);cam.SetViewUp(0,1,0)
        par=.21
    else:
        cy=1.15;ang=np.deg2rad(angle)
        cam.SetPosition(1.5*np.sin(ang),cy+.2,1.5*np.cos(ang));cam.SetFocalPoint(0,cy,0);cam.SetViewUp(0,1,0)
        par=.18
    cam.ParallelProjectionOn();cam.SetParallelScale(par)
    w,h=size;win=vtk.vtkRenderWindow();win.SetOffScreenRendering(True);win.AddRenderer(r);win.SetSize(w,h);win.SetMultiSamples(0)
    filt=vtk.vtkWindowToImageFilter();filt.SetInput(win);filt.ReadFrontBufferOff()
    win.Render();filt.Update();v=vtk_to_numpy(filt.GetOutput().GetPointData().GetScalars()).reshape((h,w,-1));return Image.fromarray(np.flipud(v[:,:,:3]).copy())

def label(img,head):
    d=ImageDraw.Draw(img);w,h=img.size
    d.rectangle((0,0,w,42),fill=(17,37,40));d.text((12,9),head,font=font,fill=(250,236,206));return img

def facial():
    for who in ['ava','noor']:
        actor=Actor(who);old=actor.expression
        cells=[]
        states=[('neutral',[0,0,0]),('JAW',[.95,0,0]),('O',[0,.85,0]),('EE',[0,0,.85]),('jaw+O',[.52,.5,0]),('jaw+EE',[.5,0,.45])]
        for title,values in states:
            arr=np.zeros(8,dtype=np.float32);arr[3:6]=values
            actor.expression=lambda t, v=arr:v
            im=image_of([(actor,(0,0,0),0)],'face',size=(430,430))
            cells.append(label(im,who.upper()+'  |  '+title))
        canvas=Image.new('RGB',(430*3,430*2),'white')
        for k,im in enumerate(cells):canvas.paste(im,((k%3)*430,(k//3)*430))
        canvas.save(OUT/f'{who}_FACIAL_CONTROL_STATES_v21.png')
        actor.expression=old
    print('facial boards rendered',flush=True)

def grips():
    variants=['baseline','gentle','staggered','strong']
    tiles=[]
    for gr in variants:
        A=Actor('ava',grip=gr);N=Actor('noor',grip=gr)
        for angle in [25,55]:
            im=image_of([(A,(-.48,0,0),3.4),(N,(.48,0,.039),3.4)],'hand',angle,size=(600,450))
            tiles.append(label(im,f'{gr}  /  {angle} deg'))
        print('rendered',gr,flush=True)
    sheet=Image.new('RGB',(1200,1800),'white')
    for i,im in enumerate(tiles):sheet.paste(im,((i%2)*600,(i//2)*450))
    sheet.save(OUT/'GRIP_VARIANTS_v21.png')

if __name__=='__main__':
    facial();grips()
