"""Mechanically split the original generated source into its two petal materials."""
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent/'art'
im=Image.open(root/'petal_source.png')
im.crop((0,0,740,1254)).save(root/'petal_wide.png')
im.crop((760,0,1254,1254)).save(root/'petal_curl.png')
