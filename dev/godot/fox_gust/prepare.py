"""Mechanical extraction of reviewed generated material; not an animation sheet."""
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent
im=Image.open(root.parents[1]/'design/fox_fire_gust/generated/03_source_materials.png').convert('RGBA')
# Visible component bounds; the rear root extends below the sheet midpoint.
for name,box in {'rear':(620,22,1254,665),'front':(35,735,705,1204),'fragment_a':(723,699,992,1130),'fragment_b':(893,824,1237,1221),'root':(240,421,365,580)}.items():
 im.crop(box).save(root/'art'/f'{name}.png')
