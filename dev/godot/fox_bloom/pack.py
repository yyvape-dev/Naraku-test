"""Pack actual Godot render outputs; no procedural image generation here."""
from pathlib import Path
from PIL import Image
import json,sys
import numpy as np
root=Path(__file__).resolve().parent
assets=root.parents[1]/'assets'
name='foxbloom'
frames_dir=root/'frames'
timeline=json.loads((root/'timeline.json').read_text())
count=timeline['frames'];cols=timeline['cols'];rows=(count+cols-1)//cols
report={'timeline':timeline}
for layer,tile in [('floor',224),('air',224)]:
 atlas=Image.new('RGBA',(tile*cols,tile*rows))
 for i in range(count):
  im=Image.open(frames_dir/f'{layer}_{i:02}.png').convert('RGBA')
  assert im.size==(400,400) and im.getpixel((0,0))[3]==0
  # Godot's transparent viewport readback stores premultiplied RGB.
  # PNG/WebP and Canvas expect straight alpha, otherwise glow is darkened twice.
  rgba=np.array(im,dtype=np.float32)
  alpha=rgba[:,:,3:4]
  rgba[:,:,:3]=np.minimum(255,rgba[:,:,:3]*255/np.maximum(alpha,1))
  im=Image.fromarray(np.rint(rgba).astype(np.uint8),'RGBA')
  atlas.paste(im.resize((tile,tile),Image.Resampling.LANCZOS),(i%cols*tile,i//cols*tile))
 path=assets/f'vfx_{name}_{layer}.webp'
 atlas.save(path,quality=94,method=6)
 report[layer]={'tile':tile,'frames':count,'timing':'variable-rate','bytes':path.stat().st_size,'decodedBytes':atlas.width*atlas.height*4}
(root/'atlas.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
