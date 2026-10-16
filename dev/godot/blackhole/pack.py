"""Pack Godot's premultiplied matte and black-background HDR/glow captures."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parent
assets=root.parents[1]/'assets'
report={'frames':96,'fps':30,'life':3.2,'cols':12,'rows':8,'anchor':[.5,.5],'sourceSize':[1536,1536]}
for layer,tile in [('floor',192),('air',384)]:
 if '--air-only' in sys.argv and layer=='floor':
  report[layer]=json.loads((root/'atlas.json').read_text())[layer]
  continue
 if '--floor-only' in sys.argv and layer=='air':
  report[layer]=json.loads((root/'atlas.json').read_text())[layer]
  continue
 atlas=Image.new('RGBA',(tile*12,tile*8))
 edge=0
 for i in range(96):
  light=np.asarray(Image.open(root/f'frames/{layer}_light_{i:02}.png').convert('RGB'),dtype=np.float32)/255
  matte=np.asarray(Image.open(root/f'frames/{layer}_matte_{i:02}.png').convert('RGBA'),dtype=np.float32)/255
  la=light.max(axis=2,keepdims=True);ma=matte[:,:,3:4]
  alpha=la+ma*(1-la)
  rgb=np.clip((light+matte[:,:,:3]*(1-la))/np.maximum(alpha,1e-5),0,1)
  rgba=np.concatenate([rgb,alpha],axis=2)
  a=np.rint(np.clip(rgba,0,1)*255).astype('uint8')
  edge=max(edge,int(max(a[0,:,3].max(),a[-1,:,3].max(),a[:,0,3].max(),a[:,-1,3].max())))
  im=Image.fromarray(a).resize((tile,tile),Image.Resampling.LANCZOS)
  atlas.paste(im,(i%12*tile,i//12*tile))
 path=assets/f'vfx_blackhole_{layer}.webp';atlas.save(path,quality=94,method=6)
 report[layer]={'tile':tile,'bytes':path.stat().st_size,'decodedBytes':atlas.width*atlas.height*4,'maxEdgeAlpha':edge}
(root/'atlas.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
