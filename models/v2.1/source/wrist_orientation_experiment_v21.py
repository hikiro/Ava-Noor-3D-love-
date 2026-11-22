"""Real triangle-mesh renders with controlled wrist yaw; comparisons, not approvals."""
import numpy as np,json
from scipy.spatial.transform import Rotation
from PIL import Image
from build_v21 import Actor
from render_lookdev_v21 import image_of,label
from build_v19 import ROOT
from contact_sweep_v20 import measures
from pathlib import Path
OUT=ROOT/'previews';QA=ROOT/'qa'
settings=[-.30,-.16,0.,.16,.30]
imgs=[];reports=[]
for bias in settings:
 A,N=Actor('ava'),Actor('noor')
 for actor,bone,sgn in [(A,'wrist_R',1),(N,'wrist_L',-1)]:
  original=actor.local_rotations
  def modified(t,original=original,bone=bone,sgn=sgn):
   d=original(t);u=np.clip((t-2.3)/.9,0,1);u=u*u*(3-2*u)
   d[bone]=d[bone]*Rotation.from_rotvec([0,0,sgn*bias*u])
   return d
  actor.local_rotations=modified
 for angle in [25,55]:
  im=image_of([(A,(-.48,0,0),3.4),(N,(.48,0,.039),3.4)],'hand',angle,size=(600,410))
  imgs.append(label(im,f'wrist bias {bias:+.2f} rad / {angle} deg'))
 # geometric nearest vertices, no collision claim from point proximity
 av=A.deform(3.4);no=N.deform(3.4)
 al,ah=A.ranges['R_CONTINUOUS_ANATOMICAL_HAND_v19'];nl,nh=N.ranges['L_CONTINUOUS_ANATOMICAL_HAND_v19']
 from scipy.spatial import cKDTree
 gap=float(cKDTree(av[al:ah]+[-.48,0,0]).query(no[nl:nh]+[.48,0,.039])[0].min())
 reports.append({'wrist_bias_rad':bias,'contact_nearest_vertices_m':gap})
 print('wrist',bias,'min gap',gap,flush=True)
canvas=Image.new('RGB',(1200,len(settings)*410),'white')
for i,im in enumerate(imgs):canvas.paste(im,((i%2)*600,(i//2)*410))
canvas.save(OUT/'WRIST_ORIENTATION_VARIANTS_v21.png')
(QA/'WRIST_ORIENTATION_EXPERIMENT_v21.json').write_text(json.dumps({'candidates':reports,'evaluated_pose_time_s':3.4,'collision_test':'not run in this experiment; proximity is NOT collision-free proof'},indent=2))
