"""Validate native tile reconstruction, alpha continuity, and atlas pixel budget."""
from pathlib import Path
from PIL import Image
import numpy as np,json,argparse
parser=argparse.ArgumentParser();parser.add_argument('--out',default='dev/reports/fox-sakura/frame-checks.json');args=parser.parse_args()
repo=Path(__file__).resolve().parents[2];root=repo/'dev/godot/fox_gust';assets=repo/'dev/assets'
meta=json.loads((assets/'vfx_meta.json').read_text())['foxgust'];result={'native':meta['native'],'layers':{}};total=0
for layer in ['floor','air']:
 atlas=Image.open(assets/f'vfx_foxgust_{layer}.webp').convert('RGBA');assert max(atlas.size)<=4096
 total+=atlas.width*atlas.height*4
 worst=0;edge=0;counts=[]
 for i,rects in enumerate(meta['layers'][layer]['rects']):
  src=np.array(Image.open(root/'frames'/f'{layer}_{i:02}.png').convert('RGBA'))[:,:,3]
  edge=max(edge,int(max(src[:2,:].max(),src[-2:,:].max(),src[:,:2].max(),src[:,-2:].max())))
  target=Image.new('RGBA',(meta['native'],meta['native']))
  for x,y,w,h,ox,oy in rects:target.paste(atlas.crop((x,y,x+w,y+h)),(ox,oy))
  expected=src.copy();expected[expected<=1]=0
  delta=np.abs(np.array(target)[:,:,3].astype(int)-expected.astype(int));worst=max(worst,int(delta.max()))
  counts.append(len(rects))
  if i==len(meta['times'])-1:assert not np.any(expected)
 assert edge==0 and worst==0,(layer,edge,worst)
 result['layers'][layer]={'size':list(atlas.size),'maxAlphaReconstructionError':worst,'borderAlphaMax':edge,'maxTilesPerFrame':max(counts),'decodedBytes':atlas.width*atlas.height*4}
assert total<100*1024**2,('Revisit sprite decomposition before shipping',total)
result['atlasDecodedBytes']=total;result['scratchBytes']=meta['native']**2*4
out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2));print(json.dumps(result))
