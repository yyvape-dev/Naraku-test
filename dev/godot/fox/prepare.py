"""Crop the generated source sheet into independent production layers."""
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent/'art'
im=Image.open(root/'source_sheet.png')
for name,box in {'flame':(0,0,725,681),'fragments':(725,0,1254,681),'smoke':(0,681,760,1254),'embers':(760,700,1254,1254)}.items():
 im.crop(box).save(root/(name+'.png'))
