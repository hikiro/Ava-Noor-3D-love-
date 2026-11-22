from PIL import Image
from build_v20 import Actor as Previous
from build_v21 import Actor as Revised
from render_lookdev_v21 import image_of,label
from build_v19 import ROOT
poses=[('ava',1.7),('noor',1.1)]
ims=[]
for who,t in poses:
 for name,clazz in [('v2.0 prior',Previous),('v2.1 corrected',Revised)]:
  a=clazz(who)
  im=image_of([(a,(0,0,0),t)],'face',size=(480,510))
  ims.append(label(im,f'{who.upper()} / {name} / t={t:.1f}s'))
sheet=Image.new('RGB',(960,1020),'white')
for i,im in enumerate(ims):sheet.paste(im,((i%2)*480,(i//2)*510))
sheet.save(ROOT/'previews'/'MOUTH_BEFORE_AFTER_v21.png')
print('saved comparison',flush=True)
