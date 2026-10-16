"""Measure real Godot Glow on/off captures; particles are hidden for this probe."""
from pathlib import Path
from PIL import Image
import numpy as np,json
root=Path(__file__).resolve().parents[2]/'reports/blackhole';result={}
for version in ['before','after']:
 rows=[]
 for p in sorted((root/f'glow-{version}').glob('*_on.png')):
  on=np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
  off=np.asarray(Image.open(str(p).replace('_on.png','_off.png')).convert('RGB'),dtype=np.int16)
  d=np.abs(on-off);affected=np.max(d,axis=2)>0
  rows.append({'time':float(p.name.split('_')[0]),'changedPixels':int(affected.sum()),'maxChannelDifference':int(d.max()),'totalChannelDifference':int(d.sum()),'haloPixelsBeyondUnlitCore':int(((on.max(axis=2)>2)&(off.max(axis=2)<=2)).sum()),'whitePixels':int((on.min(axis=2)>=235).sum())})
 result[version]=rows
(root/'glow-measure.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
