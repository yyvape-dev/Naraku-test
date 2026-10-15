"""Extract four reviewed independent source shapes, not animation frames."""
from pathlib import Path
from PIL import Image
import json
root=Path(__file__).resolve().parent
source=root.parents[1]/'design/fox_fire_gust/revision2/source-02.png'
im=Image.open(source).convert('RGBA')
regions={'rear':(150,0,530,722),'front':(640,310,1245,718),'fragment_a':(170,735,530,1243),'fragment_b':(700,760,1235,1238)}
report={}
for name,box in regions.items():
 c=im.crop(box);bounds=c.getchannel('A').point(lambda a:255 if a>2 else 0).getbbox();assert bounds
 # Preserve transparent edge pixels; the crop itself is not an alpha threshold.
 bounds=(max(0,bounds[0]-6),max(0,bounds[1]-6),min(c.width,bounds[2]+6),min(c.height,bounds[3]+6))
 c=c.crop(bounds);c.save(root/'art'/f'{name}.png');report[name]={'region':box,'trim':bounds,'size':c.size}
(root.parents[1]/'design/fox_fire_gust/revision2/extraction.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
