#!/usr/bin/env python3
"""Reproducible vector blocking boards for Villa Verse Ep 01; no external assets/network."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cairosvg, math, io, shutil
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'frames').mkdir(exist_ok=True); (ROOT/'storyboards').mkdir(exist_ok=True); (ROOT/'assets').mkdir(exist_ok=True)
def resolve_font(bold=False):
    candidates = (
        ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf']
        if bold else ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'C:/Windows/Fonts/arial.ttf']
    )
    for f in candidates:
        if Path(f).exists(): return f
    return None
FONT=resolve_font(False); BOLD=resolve_font(True)
def T(font,size):
    return ImageFont.truetype(font,size) if font else ImageFont.load_default(size=size)

CHAR={
 'ava': {'skin':'#c88d65','hair':'#332121','top':'#e6a829','pants':'#f0e5d6','shoe':'#604238','height':1.0},
 'kai': {'skin':'#7d4837','hair':'#1c2024','top':'#315bb2','pants':'#f0dfc6','shoe':'#eee3d0','height':1.06},
 'noor':{'skin':'#b27659','hair':'#131b24','top':'#147d77','pants':'#873a55','shoe':'#21232b','height':1.03},
 'jules':{'skin':'#d1a382','hair':'#c3c8cf','top':'#252b38','pants':'#252b38','shoe':'#181b24','height':1.02},
 'sloane':{'skin':'#d8a17c','hair':'#8a402d','top':'#373d83','pants':'#373d83','shoe':'#42303a','height':0.97},
 'remy':{'skin':'#d9aa82','hair':'#a65b28','top':'#be5c59','pants':'#29334f','shoe':'#e8e4d8','height':1.0}
}
S='<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280" viewBox="0 0 720 1280">'
DEFS='''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#132d43"/><stop offset="0.52" stop-color="#514459"/><stop offset="1" stop-color="#bf7971"/></linearGradient>
<linearGradient id="terrace" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#66546d"/><stop offset="1" stop-color="#292d43"/></linearGradient>
<linearGradient id="pool" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#94e3e5"/><stop offset="1" stop-color="#2b6b87"/></linearGradient>
<linearGradient id="screen" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#1b4053"/><stop offset="1" stop-color="#102333"/></linearGradient>
<linearGradient id="votered" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#782e41"/><stop offset="1" stop-color="#311e37"/></linearGradient>
<radialGradient id="glow"><stop stop-color="#fde4a0" stop-opacity="0.7"/><stop offset="1" stop-color="#fde4a0" stop-opacity="0"/></radialGradient>
<filter id="soft"><feGaussianBlur stdDeviation="12"/></filter><filter id="shadow"><feDropShadow dx="0" dy="12" stdDeviation="8" flood-opacity=".4"/></filter>
</defs>'''
def rect(x,y,w,h,fill,r=0,stroke=None,sw=1): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>'
def circ(x,y,r,fill,stroke=None,sw=1):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>'
def path(d,fill,stroke=None,sw=1):return f'<path d="{d}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"' if stroke else '')+'/>'
def line(x1,y1,x2,y2,color,width=3):return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>'
def text(x,y,t,size=28,color='#fff8e9',weight='700',anchor='start',spacing=None):
 import html
 return f'<text x="{x}" y="{y}" fill="{color}" font-family="DejaVu Sans, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"'+(f' letter-spacing="{spacing}"' if spacing else '')+f'>{html.escape(t)}</text>'
def star(x,y,scale=1):
 d=f'M{x} {y-9*scale} L{x+2*scale} {y-2*scale} L{x+9*scale} {y} L{x+2*scale} {y+2*scale} L{x} {y+9*scale} L{x-2*scale} {y+2*scale} L{x-9*scale} {y} L{x-2*scale} {y-2*scale} Z'
 return path(d,'#fee6b0')
def sky():
 s=rect(0,0,720,1280,'url(#sky)')
 s+=circ(560,194,64,'#f2cbb5')+circ(560,194,100,'url(#glow)')
 for x,y,r in [(89,122,1),(160,206,2),(307,140,2),(395,242,1),(663,128,1),(120,333,1),(582,350,1)]:s+=circ(x,y,r,'#fbebd5')
 s+=path('M0 525 Q125 460 218 510 T410 503 T720 493 L720 635 L0 635Z','#253846')
 s+=path('M0 576 Q135 536 226 576 T455 548 T720 562 L720 653 L0 653Z','#1c3445')
 return s

def palm(x,y,flip=1,sz=1):
 s=f'<g transform="translate({x} {y}) scale({flip*sz} {sz})">'
 s+=path('M0 0 Q12 -170 20 -340','none','#252d39',15)
 for ex,ey in [(150,-335),(119,-388),(-133,-380),(-90,-438),(26,-454),(-178,-315)]:
  s+=path(f'M20 -340 Q{ex//2} {ey-45} {ex} {ey}','none','#1c4846',16)
  for j in (0.35,0.55,0.75):
   px=20+(ex-20)*j;py=-340+(ey+340)*j
   s+=path(f'M{px} {py} q{20*flip} 14 28 28','none','#336462',5)
 return s+'</g>'
def lookout():
 s='<g opacity=".72">'
 s+=rect(35,430,220,150,'#789ba2',7)
 s+=path('M20 445 L139 348 L279 445 Z','#314957')
 s+=rect(70,469,44,71,'#f6d6ac',8)+rect(165,463,55,80,'#eac6a5',8)
 s+=rect(112,540,85,12,'#d8bba7')
 s+=text(139,602,'LOOKOUT HOUSE',14,'#e7dad3',anchor='middle')
 s+='</g>';return s

def sunhouse():
 s='<g>'
 s+=rect(0,470,533,492,'#e9bc96',9)
 s+=path('M0 475 L105 403 L493 403 L566 470Z','#e4a17d')
 s+=rect(20,493,480,22,'#fbe0b9')
 for x in (52,225,398):
  s+=rect(x,552,104,235,'#885968',53)
  s+=path(f'M{x+9} 783 L{x+9} 611 Q{x+9} 563 {x+52} 563 Q{x+95} 563 {x+95} 611 L{x+95} 783 Z','#354653')
  s+=rect(x+36,655,31,89,'#efb999',5)
 s+=rect(0,792,500,36,'#f4d9bb')
 s+=rect(0,824,500,165,'#d3a180')
 for yy in (846,880,914):s+=line(0,yy,500,yy,'#b78378',3)
 s+=text(242,537,'S U N H O U S E',23,'#7e4d56',anchor='middle')
 s+='</g>';return s

def stringlights():
 s=path('M0 382 Q350 447 720 368','none','#bba5a1',4)
 for x,y in [(40,388),(130,407),(225,418),(323,420),(425,413),(534,396),(640,379)]:
  s+=line(x,y,x,y+17,'#bba5a1',2)+circ(x,y+23,6,'#fee4a0')+circ(x,y+23,19,'url(#glow)')
 return s

def cinema(x=405,y=548,w=275,h=325,content='blank'):
 s=f'<g>{rect(x-9,y-8,w+18,h+20,"#3a3146",10,stroke="#f1b777",sw=7)}'
 s+=rect(x,y,w,h,'url(#votered)' if content=='eviction' else 'url(#screen)',6)
 if content=='blank':s+=text(x+w/2,y+105,'MOVIE',28,'#f3dab9',anchor='middle')+text(x+w/2,y+148,'NIGHT',39,'#f6d5bb',anchor='middle')
 elif content=='private':s+=text(x+w/2,y+92,'TONIGHT',21,'#f7c8b5',anchor='middle')+text(x+w/2,y+147,"KAI'S",38,'#ffe3ae',anchor='middle')+text(x+w/2,y+191,'PRIVATE CLIP',23,'#ffe3ae',anchor='middle')
 elif content=='eviction':s+=text(x+w/2,y+92,'EVICTION',31,'#ffc4c4',anchor='middle')+text(x+w/2,y+145,'ONE OF YOU',25,'#fff3eb',anchor='middle')+text(x+w/2,y+184,'LEAVES',35,'#fff3eb',anchor='middle')+text(x+w/2,y+223,'TONIGHT',34,'#fff3eb',anchor='middle')
 else:s+=text(x+w/2,y+142,content,27,'#fff3eb',anchor='middle')
 return s+'</g>'

def firepit(x=290,y=1110,sz=1):
 s=f'<g transform="translate({x} {y}) scale({sz})">'
 s+=rect(-116,-25,232,62,'#262e3b',29)+rect(-100,-37,200,35,'#77717b',12)
 s+=path('M-12 -35 Q-65 -95 -12 -143 Q-22 -89 14 -118 Q58 -82 6 -34Z','#ffa54e')+path('M-3 -34 Q-27 -72 0 -102 Q34 -65 5 -30Z','#ffe0a0')
 s+=circ(2,-74,80,'url(#glow)')
 return s+'</g>'

def bench(x,y,s=1):return f'<g transform="translate({x} {y}) scale({s})">'+rect(-80,-60,160,27,'#715766',9)+rect(-75,-38,150,30,'#b5857a',9)+rect(-64,-7,13,36,'#464454',2)+rect(51,-7,13,36,'#464454',2)+'</g>'

def scenery(mode='wide',screen='blank'):
 s=sky()+palm(25,765,-1,.82)+palm(693,788,1,.95)
 if mode=='wide':
  s+=lookout()+sunhouse()+stringlights()
  s+=path('M0 995 L720 950 L720 1280 L0 1280Z','url(#terrace)')
  s+=path('M0 1028 L720 974','none','#ca9b8d',5)
  s+=rect(15,1050,168,165,'url(#pool)',22,stroke='#b6ddd9',sw=6)
  for k in (0,1,2):s+=path(f'M26 {1090+k*38}Q78 {1075+k*38} 148 {1094+k*38}','none','#d0ffff',2)
  s+=cinema(394,616,286,298,screen)
  s+=bench(236,1058,.8)+firepit(350,1146,.67)
 elif mode in ['party','vote','garden']:
  s+=sunhouse()+stringlights()
  s+=path('M0 1003 L720 950 L720 1280 L0 1280Z','url(#terrace)')
  if mode=='garden':
   s+=rect(270,471,197,458,'#2b4648',98,stroke='#f0c39c',sw=19)
   s+=path('M367 917 L70 1280 L720 1280Z','#b78a77')
   for xx,yy in [(210,894),(509,818),(167,1010)]:s+=circ(xx,yy,40,'#315c52')+circ(xx+22,yy-15,36,'#4c7b61')
  elif mode=='vote':s+=cinema(226,466,460,403,screen)
  else:s+=cinema(380,551,299,319,screen)
  # firepit kept off-camera in tighter framings to prevent actor/prop overlap
 elif mode=='close':
  s+=sunhouse()+stringlights()+path('M0 1138 L720 1085 L720 1280 L0 1280Z','url(#terrace)')
  s+=circ(595,577,260,'#f5e2a5') if False else ''
 elif mode=='screen':
  s+=sunhouse()+stringlights()+path('M0 1120 L720 1085 L720 1280 L0 1280Z','url(#terrace)')
  s+=cinema(40,394,637,670,'')
 return s

def person(name,x,feet,scale=1,pose='stand',face='right',expression='neutral',dim=False):
 c=CHAR[name];sk=c['skin']; hair=c['hair']; top=c['top'];pants=c['pants'];shoe=c['shoe'];
 flip=-1 if face=='left' else 1; scale*=c['height']; s=f'<g transform="translate({x} {feet}) scale({flip*scale} {scale})" opacity="{0.75 if dim else 1}">'
 seated=pose=='sit';half=pose=='half';walk=pose=='walk'; lean=0  # stance/feet stay grounded; no whole-rig tilt
 hy=50 if seated else (30 if half else 0)
 s+=f'<g transform="translate(0 {hy}) rotate({lean} 0 -125)">'
 # legs
 if seated:
  s+=path('M-26 -112 L-82 -76 L-70 -16 L-53 -16 L-41 -60 L-2 -65 L24 -112Z',pants,'#24283a',3)
  s+=path('M18 -112 L59 -75 L83 -13 L63 -7 L35 -50 L4 -63Z',pants,'#24283a',3)
  s+=rect(-89,-17,44,16,shoe,7)+rect(58,-15,40,15,shoe,7)
 else:
  if walk:
   s+=path('M-25 -112 L-57 -62 L-80 -5 L-57 -3 L-28 -54 L6 -112Z',pants,'#282936',3)
   s+=path('M13 -113 L41 -74 L53 -2 L76 -1 L63 -84 L39 -114Z',pants,'#282936',3)
   s+=rect(-84,-10,44,16,shoe,7)+rect(44,-9,45,15,shoe,7)
  else:
   s+=path('M-35 -114 L-26 -7 L-3 -7 L4 -114Z',pants,'#282936',2.4)
   s+=path('M0 -114 L11 -6 L35 -6 L34 -114Z',pants,'#282936',2.4)
   s+=rect(-31,-12,38,15,shoe,6)+rect(6,-12,39,15,shoe,6)
 # torso
 s+=path('M-48 -207 Q-50 -209 -35 -221 Q0 -240 35 -220 Q55 -215 49 -190 L38 -112 Q0 -99 -37 -112Z',top,'#292c3b',3)
 if name=='ava':
  s+=path('M-14 -226 L-2 -190 L18 -225','#e6ba65')
  s+=path('M-14 -225L1 -199L18 -224','none','#ffe6a4',4)
 if name=='noor':
  s+=path('M-22 -213 L-14 -129 L15 -129 L24 -213','none','#a9e0cb',13)
  s+=rect(-24,-159,48,11,'#f4d8c8',4)
 if name=='kai':
  s+=path('M0 -220 L0 -115','none','#254c99',4)
  for y in (-197,-174,-150):s+=circ(0,y,2.4,'#f9c6a6')
 if name=='jules':
  s+=path('M-28 -222 L-3 -159 L27 -222','none','#eac9a2',6)
  s+=line(-38,-212,-29,-111,'#caa966',5)+line(39,-212,31,-111,'#caa966',5)
 # arms pose
 if pose in ('reach','offer','take'):
  s+=path('M-40 -205 Q-55 -176 -54 -124','none',top,24)
  s+=circ(-54,-124,12,sk)
  s+=path('M40 -204 L84 -187 L145 -173','none',top,22)
  s+=circ(147,-173,13,sk)
 elif pose=='walk':
  s+=path('M-40 -205 L-65 -157 L-36 -127','none',top,23)+circ(-36,-127,11,sk)
  s+=path('M40 -205 L61 -152 L89 -164','none',top,23)+circ(89,-164,11,sk)
 elif pose=='half':
  s+=path('M-42 -200 L-72 -155 L-85 -114','none',top,23)+circ(-85,-114,11,sk)
  s+=path('M42 -202 L83 -167 L110 -147','none',top,23)+circ(110,-147,11,sk)
 else:
  s+=path('M-44 -202 L-53 -149 L-49 -106','none',top,23)+circ(-49,-106,11,sk)
  s+=path('M43 -202 L53 -153 L49 -108','none',top,23)+circ(49,-108,11,sk)
 # neck head hair, placed relative to seated pose
 s+=rect(-11,-251,22,39,sk,9)
 if name=='ava':
  s+=path('M-43 -291 Q-64 -353 -28 -372 Q10 -387 45 -348 Q62 -314 44 -268 Q58 -240 26 -234 Q14 -266 0 -268 L-31 -263 Q-58 -231 -52 -277Z',hair)
  for xx,yy,rr in [(-49,-290,16),(-49,-260,17),(42,-287,16),(48,-261,20),(-31,-353,18),(13,-362,22)]:s+=circ(xx,yy,rr,hair)
 elif name=='noor':
  s+=path('M-40 -300 Q-42 -356 7 -357 Q57 -339 43 -294 L34 -268 L-36 -277Z',hair)
  for i in range(7):s+=circ(-41-i*1.2,-276+i*20,13-i*.35,hair)
  s+=circ(-47,-145,9,'#3f3035')
 elif name=='jules':
  s+=path('M-43 -308 Q-41 -342 6 -348 Q43 -344 44 -309 L24 -326 L-19 -319Z',hair)
 elif name=='sloane':
  s+=path('M-49 -331 Q-12 -368 33 -338 Q49 -324 47 -269 L31 -260 Q35 -302 17 -309 L-26 -306 L-32 -267 L-53 -265Z',hair)
 elif name=='kai':
  for xx,yy in [(-36,-328),(-18,-348),(0,-353),(20,-348),(39,-328),(-29,-341),(32,-343)]:s+=circ(xx,yy,14,hair)
 elif name=='remy':
  for xx,yy in [(-43,-311),(-34,-337),(-16,-352),(9,-355),(32,-344),(48,-316),(-49,-287),(47,-288)]:s+=circ(xx,yy,18,hair)
 s+=f'<ellipse cx="0" cy="-307" rx="36" ry="43" fill="{sk}" stroke="#6b4143" stroke-width="2.4"/>'
 # hair over scalp for all
 if name=='ava':s+=path('M-34 -322 Q-44 -352 -13 -360 Q24 -366 36 -331 Q17 -348 -11 -337 Q-23 -323 -34 -322Z',hair)
 if name=='noor':s+=path('M-33 -327 Q-23 -363 16 -351 Q31 -349 35 -328 Q-3 -337 -33 -327Z',hair)
 if name=='kai':s+=path('M-34 -332 Q-20 -351 8 -348 Q31 -352 37 -331Z',hair)
 if name=='jules':s+=path('M-30 -330 Q0 -351 37 -328 L9 -338 L-20 -320Z',hair)
 if name=='sloane':s+=path('M-36 -327 Q-29 -354 6 -350 Q23 -348 37 -323 L-2 -337Z',hair)
 if name=='remy':s+=circ(-17,-342,17,hair)+circ(12,-347,19,hair)
 # facial features
 for eyex in [-14,14]:
  s+=path(f'M{eyex-7} -311 Q{eyex} {-315 if expression=="hurt" else -321} {eyex+7} -312','none','#29212b',3.6)
  s+=f'<ellipse cx="{eyex}" cy="-302" rx="5.7" ry="6.5" fill="#f7ece4"/>'
  s+=circ(eyex+(2 if expression=='shocked' else 1),-303,3.2,'#23232c')
 s+=path('M0 -297 L-4 -282 L5 -280','none','#8d5b52',2)
 if expression=='shocked':s+=f'<ellipse cx="0" cy="-270" rx="7" ry="10" fill="#542c3a"/>'
 elif expression=='hurt':s+=path('M-10 -269 Q0 -278 11 -269','none','#633845',3.8)
 elif expression=='firm':s+=path('M-12 -268 Q0 -263 11 -268','none','#633845',3)
 elif expression=='smile':s+=path('M-10 -273 Q0 -260 13 -273','none','#633845',3.6)
 else:s+=path('M-9 -270 Q0 -268 10 -269','none','#633845',2.7)
 # character props
 if name=='ava':s+=star(38,-278,.62)
 if name=='noor':s+=circ(39,-292,6,'none','#d7b985',3)
 if name=='jules':s+=rect(-8,-161,40,48,'#59495a',4,stroke='#d0b68e',sw=3)
 s+='</g></g>';return s

def foreground(name):
 s=rect(0,0,720,1280,'#1c2436')+sky()
 s+=path('M0 990 Q360 930 720 1000 L720 1280 L0 1280Z','#343545')
 s+=palm(700,830,1,.75)
 for x,y in [(97,624),(610,551),(190,721)]:s+=circ(x,y,64,'url(#glow)')
 return s

SCENES=[
 ('01','00:00–00:03','THE PRIVATE CLIP','Jules: “Kai. Your secret clip.”'),
 ('02','00:03–00:06.5','THE CONFESSION','Recorded Kai: “I’d pick Noor. Every time.”'),
 ('03','00:06.5–00:10','AVA STANDS','Ava: “You said you chose me.”'),
 ('04','00:10–00:13','KAI REACHES','Kai: “Ava, I was going to tell you.”'),
 ('05','00:13–00:16.5','NOOR INTERRUPTS','Noor: “He forgot one part.”'),
 ('06','00:16.5–00:20','THE QUESTION','Ava: “You said yes?”  Noor: “No.”'),
 ('07','00:20–00:25','THE REVERSAL','Noor: “I didn’t come for Kai. I came for you.”'),
 ('08','00:25–00:30','THE EVICTION','Jules: “And one of you goes home tonight.”')
]

def frame_art(scene,k):
 first=k=='A';
 if scene==1:
  s=scenery('wide','blank' if first else 'private')
  s+=person('ava',180,1100,.55,'sit',expression='neutral')+person('kai',291,1092,.59,'sit')
  s+=person('sloane',100,1034,.36,'sit')+person('remy',360,1040,.33,'sit')
  s+=person('jules',586,1090,.71,'stand',face='left')
  if not first:s+=path('M550 880 L550 929','none','#eed29d',5)
 elif scene==2:
  s=scenery('screen') if first else foreground('ava')
  if first:
   s+=rect(95,448,530,600,'#2b4459',15)
   s+=rect(128,467,464,535,'#405d70',10)
   s+=person('kai',360,1040,1.53,'stand',expression='firm')
   s+=text(137,534,'REC',35,'#fa8a8e')+circ(111,521,9,'#ff565d')
   s+=text(360,959,'KAI / CONFESSIONAL',25,'#f9e5d2',anchor='middle')
  else:
   s+=rect(435,220,236,280,'#364962',12,stroke='#e2b78c',sw=6)
   s+=person('kai',557,480,.57,'stand',expression='firm')
   s+=person('ava',309,1260,2.20,'stand',expression='shocked',face='right')
 elif scene==3:
  s=scenery('party','blank')
  s+=person('sloane',95,1045,.45,'sit',face='right')+person('remy',618,1065,.49,'sit',face='left')
  s+=person('kai',565,1105,.72,'sit',face='left',expression='hurt')
  s+=person('ava',304,1140,1.01,'sit' if first else 'stand',expression='hurt')
  if not first:s+=line(255,1207,388,1207,'#f8ccad',2)
 elif scene==4:
  s=scenery('party','blank')
  s+=person('ava',110,1122,1.08,'stand',face='left',expression='hurt')
  s+=person('kai',380,1115,1.25,'half' if first else 'reach',face='left',expression='hurt')
  s+=person('remy',634,1050,.44,'sit',face='left',expression='shocked')
 elif scene==5:
  s=scenery('garden')
  s+=person('noor',363,1054,.72 if first else 1.21,'walk' if first else 'stand',expression='firm')
  s+=person('kai',612,1089,.66,'stand',face='left',expression='shocked')
  if first:s+=person('jules',125,1050,.56,'stand')
  else:s+=person('ava',76,1087,.66,'stand',expression='shocked')
 elif scene==6:
  s=foreground('ava' if first else 'noor')
  if first:s+=person('ava',342,1328,2.46,'stand',expression='hurt')
  else:s+=person('noor',356,1330,2.42,'stand',expression='firm',face='left')
 elif scene==7:
  s=scenery('party')
  if first:
   s+=person('kai',246,1140,.99,'stand',expression='shocked')
   s+=person('noor',425,1140,1.11,'walk',face='left',expression='firm')
   s+=person('ava',88,1156,.75,'stand',expression='hurt')
  else:
   s+=person('ava',225,1140,1.15,'reach',expression='shocked',face='right')
   s+=person('noor',522,1140,1.15,'reach',expression='smile',face='left')
   s+=line(377,941,377,941,'#f2caa7',12)
   s+=circ(377,941,18,'#c79370')
 elif scene==8:
  s=scenery('vote','blank' if first else 'eviction')
  if first:
   s+=person('ava',230,1142,1.00,'reach',expression='smile')
   s+=person('noor',530,1142,1.00,'reach',face='left',expression='smile')
   s+=circ(375,970,13,'#bc8166')
   s+=person('kai',384,1080,.54,'stand',expression='shocked')
   s+=person('jules',85,1090,.62,'stand')
  else:
   s+=person('kai',178,1196,1.04,'stand',expression='shocked')
   s+=person('ava',485,1184,.74,'reach',expression='shocked')
   s+=person('noor',652,1184,.73,'reach',face='left',expression='firm')
   s+=circ(568,1053,10,'#bf8e72')
 else: s=scenery()
 return s

def strip_and_labels(scene,k):
 nr,ts,title,dialog=SCENES[scene-1]
 s=rect(0,0,720,92,'#111e2c')+rect(0,90,720,3,'#eab182')
 s+=text(34,34,f'SHOT {nr}  •  {"FIRST FRAME" if k=="A" else "LAST FRAME"}',22,'#ffdca7')
 s+=text(34,70,f'{ts}   /   {title}',20,'#e7e0d4')
 s+=rect(0,1150,720,130,'#111e2c')+rect(0,1150,720,4,'#eab182')
 if scene==7:
  s+=text(30,1190,'NOOR: “I didn’t come here for Kai.”',22)
  s+=text(30,1230,'“I came here for you.”',25,'#ffe4bd')
 elif scene==8:
  s+=text(30,1190,'JULES: “One of you goes home tonight.”',21)
  s+=text(30,1234,'CLIFFHANGER / EVICTION',21,'#ffa7a1')
 else:
  if len(dialog)>54:
   split=dialog.find('  ')
   if split!=-1:
    s+=text(30,1190,dialog[:split],21)
    s+=text(30,1231,dialog[split:].strip(),21)
   else:s+=text(30,1210,dialog,19)
  else:s+=text(30,1210,dialog,23)
 return s

def full_svg(scene,k,labels=True):
 s=S+DEFS+frame_art(scene,k)
 if labels:s+=strip_and_labels(scene,k)
 return s+'</svg>'

def convert(svg,filepath):
 filepath.parent.mkdir(parents=True,exist_ok=True)
 cairosvg.svg2png(bytestring=svg.encode('utf-8'),write_to=str(filepath),output_width=720,output_height=1280)

def board(shots):
 # 2 columns x 2 rows, portrait frame pairs, with 28 px margins/gutters and bottom annotations
 w,h=1540,2800
 im=Image.new('RGB',(w,h),'#111d2a')
 dr=ImageDraw.Draw(im)
 f=T(BOLD,37);sf=T(FONT,20)
 dr.text((41,23),'VILLA VERSE  /  THE WRONG CHOICE',font=f,fill='#fff0d4')
 dr.text((43,75),f'SHOTS {shots[0]:02}–{shots[1]:02}   •   FIRST / LAST FRAMES   •   30s REEL',font=sf,fill='#d8b5a1')
 for ridx,scene in enumerate(shots):
  for ci,k in enumerate(('A','B')):
   src=Image.open(ROOT/'frames'/f'S{scene:02}_{k}.png').convert('RGB')
   src=src.resize((715,1271),Image.Resampling.LANCZOS)
   x=40+ci*746;y=145+ridx*1310
   im.paste(src,(x,y))
   dr.rectangle((x-2,y-2,x+716,y+1272),outline='#bd9c81',width=3)
 pathout=ROOT/'storyboards'/f'BOARD_SHOTS_{shots[0]:02}_{shots[1]:02}.png'
 im.save(pathout,optimize=True)

def sheet_chars():
 W,H=2100,1400
 base=Image.new('RGB',(W,H),'#172b3d');dr=ImageDraw.Draw(base)
 font=T(BOLD,43);sm=T(FONT,26)
 dr.text((70,42),'VILLA VERSE  •  CAST AND COSTUMES',font=font,fill='#fceacb')
 for i,(name,c) in enumerate(CHAR.items()):
  xi=i%3;yi=i//3
  x=60+xi*680;y=140+yi*630
  img=Image.new('RGBA',(720,1280),(0,0,0,0))
  svg=S+DEFS+person(name,370,1090,2.04,'stand')+'</svg>'
  # use resolution of 720x1280 and paste scaled
  p=cairosvg.svg2png(bytestring=svg.encode())
  cut=Image.open(io.BytesIO(p)).convert('RGBA')
  alpha=cut.getchannel('A').getbbox()
  if alpha:cut=cut.crop(alpha)
  cut.thumbnail((410,500),Image.Resampling.LANCZOS)
  dr.rounded_rectangle((x,y,x+630,y+578),radius=17,fill='#e9c6a6',outline='#d79d79',width=3)
  base.paste(cut,(x+30+(520-cut.width)//2,y+54),cut)
  dr.text((x+24,y+13),name.upper(),font=font,fill='#2e354a')
  dr.text((x+24,y+530),f'Wardrobe ID: {name.upper()}_01',font=sm,fill='#3c4250')
 base.save(ROOT/'assets'/'character_rig_reference.png',optimize=True)

def build_map():
 W,H=1600,1000
 im=Image.new('RGB',(W,H),'#213742');d=ImageDraw.Draw(im)
 ft=T(BOLD,47);sm=T(FONT,30);tiny=T(BOLD,26)
 d.text((65,33),'VILLA VERSE / WORLD BLOCKING MAP',font=ft,fill='#ffe7cb')
 # paths
 d.line([(210,495),(540,495),(850,595),(1274,595)],fill='#a68b77',width=120,joint='curve')
 d.line([(210,495),(540,495),(850,595),(1274,595)],fill='#d7b395',width=95,joint='curve')
 # house rectangles
 d.rounded_rectangle((95,245,515,520),32,fill='#e9bc96',outline='#ffe0bb',width=13)
 d.text((163,310),'LOOKOUT',font=ft,fill='#5c4c59');d.text((178,368),'HOUSE',font=ft,fill='#5c4c59')
 d.rounded_rectangle((920,290,1515,785),35,fill='#e6ad87',outline='#ffe5bc',width=13)
 d.text((1080,350),'SUNHOUSE',font=ft,fill='#5c4c59')
 d.rounded_rectangle((1020,590,1240,750),15,fill='#3c92a5',outline='#b5f1e7',width=8)
 d.text((1053,656),'POOL',font=sm,fill='#fff')
 d.rounded_rectangle((1290,417,1490,572),14,fill='#294a5d',outline='#efcd9a',width=11)
 d.text((1316,463),'MOVIE',font=sm,fill='#e9e1d0');d.text((1333,507),'SCREEN',font=sm,fill='#e9e1d0')
 d.ellipse((1110,425,1205,520),fill='#ac6752',outline='#ffb867',width=9)
 d.text((1020,540),'FIREPIT',font=sm,fill='#4a3947')
 for name,x,y,col in [('AVA',990,417,'#efae3c'),('KAI',1080,415,'#3c5ca7'),('NOOR',804,585,'#288c79'),('JULES',1350,593,'#ddd3c3')]:
  d.ellipse((x-19,y-19,x+19,y+19),fill=col,outline='white',width=4)
  d.text((x-36,y+20),name,font=tiny,fill='#fff7e9')
 d.text((540,423),'GARDEN PATH',font=sm,fill='#f3dbc9')
 d.text((92,865),'CAMERA AXIS: screen-right / guests-left, maintain across cuts',font=sm,fill='#f7e0c2')
 d.text((92,915),'Continuity: Noor enters from Lookout House path; never teleports.',font=sm,fill='#e7bfa8')
 im.save(ROOT/'assets'/'world_blocking_map.png')

def build_props():
 im=Image.new('RGB',(1520,950),'#172838');d=ImageDraw.Draw(im)
 h=T(BOLD,44);f=T(FONT,26)
 d.text((58,40),'SUNHOUSE / STORY PROPS',font=h,fill='#ffdec4')
 items=[('CINEMA SCREEN','screen / neutral'),('VOTE SCREEN','screen / threat'),('MOVIE REMOTE','Jules prop'),('FIREPIT','motivated light'),('LOUNGE BENCH','sit-to-stand'),('PATHWAY','Noor entrance')]
 for idx,(title,subtitle) in enumerate(items):
  x=60+(idx%3)*490;y=150+(idx//3)*385
  d.rounded_rectangle((x,y,x+430,y+344),24,fill='#e1b5a3',outline='#f5dbba',width=5)
  if idx in [0,1]:
   d.rounded_rectangle((x+65,y+38,x+361,y+236),12,fill='#2a4355' if idx==0 else '#773346',outline='#fff0c9',width=9)
   d.text((x+91,y+125),'MOVIE NIGHT' if idx==0 else 'EVICTION',font=f,fill='#fff0e0')
  elif idx==2:
   d.rounded_rectangle((x+185,y+50,x+260,y+220),22,fill='#222c38',outline='#ffd39c',width=7)
   for yy in (93,142,191):d.ellipse((x+212, y+yy,x+233,y+yy+18),fill='#eb9f7d')
  elif idx==3:
   d.ellipse((x+86,y+133,x+354,y+236),fill='#4c4856',outline='#c4ac9c',width=18)
   d.polygon([(x+206,y+160),(x+167,y+108),(x+215,y+44),(x+248,y+125)],fill='#ffae5a')
  elif idx==4:
   d.rounded_rectangle((x+78,y+84,x+358,y+149),23,fill='#6c5969')
   d.rounded_rectangle((x+60,y+151,x+372,y+198),18,fill='#c49283')
   d.line((x+96,y+194,x+90,y+247),fill='#4c445a',width=12);d.line((x+334,y+194,x+340,y+247),fill='#4c445a',width=12)
  else:
   d.line([(x+35,y+210),(x+199,y+90),(x+406,y+210)],fill='#d6b397',width=70,joint='curve')
   d.line([(x+35,y+210),(x+199,y+90),(x+406,y+210)],fill='#f4d2b2',width=5,joint='curve')
  d.text((x+30,y+264),title,font=h,fill='#353949')
  d.text((x+32,y+304),subtitle,font=f,fill='#5a4859')
 im.save(ROOT/'assets'/'props_and_locations.png')

def export_stage_assets():
    bgs = {
      'sunhouse_wide': scenery('wide','blank'),
      'sunhouse_movie_screen': scenery('wide','private'),
      'sunhouse_close': scenery('party','blank'),
      'garden_path': scenery('garden'),
      'eviction_screen': scenery('vote','eviction'),
      'confessional_stage': scenery('screen')
    }
    for slug,body in bgs.items():
      svg = S + DEFS + body + '</svg>'
      (ROOT/'assets'/f'BG_{slug}.svg').write_text(svg,encoding='utf-8')
      convert(svg,ROOT/'assets'/f'BG_{slug}.png')
    for name in CHAR:
      body = person(name,350,1100,2.12)
      svg = S + DEFS + body + '</svg>'
      (ROOT/'assets'/f'SPRITE_{name}.svg').write_text(svg,encoding='utf-8')
      convert(svg,ROOT/'assets'/f'SPRITE_{name}.png')

def main():
 for i in range(1,9):
  for k in ('A','B'):
   svg=full_svg(i,k)
   (ROOT/'frames'/f'S{i:02}_{k}.svg').write_text(svg,encoding='utf-8')
   convert(svg,ROOT/'frames'/f'S{i:02}_{k}.png')
 for pair in ((1,2),(3,4),(5,6),(7,8)):board(pair)
 sheet_chars();build_map();build_props();export_stage_assets()
 print('Generated',len(list((ROOT/'frames').glob('*.png'))),'PNG frames + 4 boards + 3 asset sheets')
if __name__=='__main__':main()
