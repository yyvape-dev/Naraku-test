"""Check baked alpha borders, end state, and packed atlas geometry."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]/'godot/fox_gust'
meta=json.loads((root/'timeline.json').read_text());results={}
for layer in ['floor','air']:
 sums=[];edge=0
 for i in range(meta['frames']):
  im=Image.open(root/'frames'/f'{layer}_{i:02}.png').convert('RGBA')
  assert im.size==(400,400)
  a=np.asarray(im)[:,:,3]
  edge=max(edge,int(max(a[:2,:].max(),a[-2:,:].max(),a[:,:2].max(),a[:,-2:].max())))
  sums.append(int(a.sum()))
 assert edge==0 and sums[-1]==0,(layer,edge,sums[-1])
 atlas=Image.open(root.parents[1]/'assets'/f'vfx_foxgust_{layer}.webp')
 assert atlas.size==(224*meta['cols'],224*((meta['frames']+meta['cols']-1)//meta['cols']))
 results[layer]={'borderAlphaMax':edge,'finalAlphaSum':sums[-1],'peakFrame':int(np.argmax(sums)),'peakSeconds':meta['times'][int(np.argmax(sums))],'atlasSize':list(atlas.size)}
out=root.parents[1]/'reports/fox-gust/frame-checks.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(results,indent=2));print(json.dumps(results))
