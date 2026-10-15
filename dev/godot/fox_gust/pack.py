"""Pack native-resolution, alpha-trimmed frames without stretching a fixed grid."""
from pathlib import Path
from PIL import Image
import json
import numpy as np
root=Path(__file__).resolve().parent
assets=root.parents[1]/'assets'
timeline=json.loads((root/'timeline.json').read_text())
native=timeline['native'];pad=3

def layout(items,width):
 # Height-sorted shelves pack small opaque tiles without a giant frame box.
 rows=[];placed={};height=0
 for i,w,h in sorted(items,key=lambda q:(q[2],q[1]),reverse=True):
  if w>width:return None
  choices=[(width-row[1]-w,j) for j,row in enumerate(rows) if h<=row[2] and row[1]+w<=width]
  if choices:
   _,j=min(choices);row=rows[j];placed[i]=(row[1],row[0]);row[1]+=w
  else:
   if height+h>4096:return None
   placed[i]=(0,height);rows.append([height,w,h]);height+=h
 height=(height+3)//4*4
 return width*height,width,height,placed

meta={'native':native,'anchor':timeline['anchor'],'life':timeline['life'],'times':timeline['times'],'particles':json.loads((root/'particles.json').read_text()),'layers':{}}
report={'timeline':timeline,'alphaTrimThreshold':1,'tilePartition':192,'layers':{}}
for layer in ['floor','air']:
 crops={};offsets={};by_frame=[[] for _ in range(timeline['frames'])]
 for i in range(timeline['frames']):
  im=Image.open(root/'frames'/f'{layer}_{i:02}.png').convert('RGBA')
  assert im.size==(native,native)
  rgba=np.asarray(im,dtype=np.float32).copy();alpha=rgba[:,:,3:4]
  # Discard only <=1/255 alpha, so invisible haze cannot reserve whole frames.
  rgba[:,:,3][rgba[:,:,3]<=1]=0
  rgba[:,:,:3]=np.minimum(255,rgba[:,:,:3]*255/np.maximum(alpha,1))
  image=Image.fromarray(np.rint(rgba).astype('uint8'),'RGBA')
  # Tile the silhouette before trimming: empty space between separate flame
  # lobes must not reserve texture memory. Stamps are reconstructed at 1:1.
  for y in range(0,native,192):
   for x in range(0,native,192):
    cell=image.crop((x,y,min(native,x+192),min(native,y+192)))
    box=cell.getchannel('A').getbbox()
    if not box:continue
    key=len(crops);crops[key]=cell.crop(box);offsets[key]=(x+box[0],y+box[1]);by_frame[i].append(key)
 items=[(i,im.width+pad*2,im.height+pad*2) for i,im in crops.items()]
 options=[r for width in [1024,1280,1536,1792,2048,2560,3072,3584,4096] if (r:=layout(items,width))]
 assert options,'Native frames do not fit a 4096px atlas; split layers instead of silently downscaling'
 _,w,h,placed=min(options,key=lambda q:q[0])
 atlas=Image.new('RGBA',(w,h));rects=[[] for _ in range(timeline['frames'])];locations={}
 for i,im in crops.items():
  x,y=placed[i];x+=pad;y+=pad;atlas.paste(im,(x,y));ox,oy=offsets[i]
  locations[i]=[x,y,im.width,im.height,ox,oy]
 for i,keys in enumerate(by_frame):rects[i]=[locations[key] for key in keys]
 path=assets/f'vfx_foxgust_{layer}.webp';atlas.save(path,quality=94,method=4)
 meta['layers'][layer]={'size':[w,h],'rects':rects}
 report['layers'][layer]={'size':[w,h],'bytes':path.stat().st_size,'decodedBytes':w*h*4,'occupiedPixels':sum(im.width*im.height for im in crops.values())}
(root/'atlas.json').write_text(json.dumps(report,indent=2))
mp=assets/'vfx_meta.json';all_meta=json.loads(mp.read_text()) if mp.exists() else {};all_meta['foxgust']=meta;mp.write_text(json.dumps(all_meta,separators=(',',':')))
# Individual burning fragments retain their own pixel density when range grows.
for suffix in ['a','b']:
 Image.open(root/'art'/f'fragment_{suffix}.png').save(assets/f'vfx_foxsakura_{suffix}.webp',quality=95,method=4)
print(json.dumps(report))
