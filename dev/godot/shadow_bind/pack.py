"""Pack Godot's premultiplied matte and black-background HDR/glow captures."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parent
assets=root.parents[1]/'assets'
report={'frames':54,'fps':60,'bakeFps':30,'playbackRate':2,'life':.9,'cols':9,'rows':6,'anchor':[.5,365/512],'widthPerRadius':3.4,'sourceSize':[1254,1254]}
for layer,tile in [('floor',192),('air',512)]:
 atlas=Image.new('RGBA',(tile*9,tile*6))
 edge=0
 for i in range(54):
  light=np.asarray(Image.open(root/f'frames/{layer}_light_{i:02}.png').convert('RGB'),dtype=np.float32)/255
  matte=np.asarray(Image.open(root/f'frames/{layer}_matte_{i:02}.png').convert('RGBA'),dtype=np.float32)/255
  la=light.max(axis=2,keepdims=True);ma=matte[:,:,3:4]
  alpha=la+ma*(1-la)
  rgb=np.clip((light+matte[:,:,:3]*(1-la))/np.maximum(alpha,1e-5),0,1)
  rgba=np.concatenate([rgb,alpha],axis=2)
  a=np.rint(np.clip(rgba,0,1)*255).astype('uint8')
  edge=max(edge,int(max(a[0,:,3].max(),a[-1,:,3].max(),a[:,0,3].max(),a[:,-1,3].max())))
  im=Image.fromarray(a).resize((tile,tile),Image.Resampling.LANCZOS)
  atlas.paste(im,(i%9*tile,i//9*tile))
 path=assets/f'vfx_shadow_{layer}.webp';atlas.save(path,quality=94,method=6)
 report[layer]={'tile':tile,'bytes':path.stat().st_size,'decodedBytes':atlas.width*atlas.height*4,'maxEdgeAlpha':edge}
(root/'atlas.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
# Inspection sheet over a dark backdrop, made from the actual Godot output.
contact=Image.new('RGB',(7*256,280),'#14111c')
for j,i in enumerate([2,6,14,23,31,41,51]):
 cell=Image.new('RGBA',(512,512))
 for layer in ['floor','air']:
  atlas=Image.open(assets/f'vfx_shadow_{layer}.webp');tile=atlas.width//9
  im=atlas.crop((i%9*tile,i//9*tile,(i%9+1)*tile,(i//9+1)*tile)).resize((512,512))
  cell=Image.alpha_composite(cell,im)
 cell.thumbnail((256,256));contact.paste(cell,(j*256,24),cell)
from PIL import ImageDraw
d=ImageDraw.Draw(contact)
for j,i in enumerate([2,6,14,23,31,41,51]):d.text((j*256+10,5),f'{i/60:.2f}s',fill='white')
contact.save('/tmp/shadow-baked-contact.png')
