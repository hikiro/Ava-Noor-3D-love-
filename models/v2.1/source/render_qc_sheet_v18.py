#!/usr/bin/env python3
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
video=ROOT/'previews/Ava_Noor_v18_ELBOW_RETOPO.mp4'
cap=cv2.VideoCapture(str(video));frames=[]
while 1:
 ok,f=cap.read()
 if not ok:break
 frames.append(Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB)))
cap.release()
assert len(frames)==125
T=np.linspace(0,len(frames)-1,20).round().astype(int)
w,h=216,384
sheet=Image.new('RGB',(5*w,4*(h+28)),'#f5e9d7')
fnt=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13)
d=ImageDraw.Draw(sheet)
for i,ix in enumerate(T):
 x=(i%5)*w;y=(i//5)*(h+28)
 sheet.paste(frames[ix].resize((w,h)),(x,y+28))
 d.rectangle((x,y,x+w,y+28),fill=(15,39,40))
 d.text((x+8,y+7),f'Window {i+1:02d}  |  {ix/24:.2f}s',font=fnt,fill='#f2eadb')
sheet.save(ROOT/'qa/20_TIMELINE_SAMPLE_FRAMES.png')
# 12fps accessible GIF, visually a preview not the source master.
import imageio.v2 as imageio
S=[]
for i in range(0,125,2): S.append(np.asarray(frames[i].resize((270,480))))
imageio.mimsave(ROOT/'previews/Ava_Noor_v18_PREVIEW.gif',S,duration=2/24,loop=0)
print('20 sample frames + 12fps GIF written',flush=True)
