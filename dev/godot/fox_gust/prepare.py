"""Extract the reviewed revision-2 flames and reuse the existing contact source."""
from pathlib import Path
from PIL import Image
import runpy
root=Path(__file__).resolve().parent
im=Image.open(root.parents[1]/'design/fox_fire_gust/generated/03_source_materials.png').convert('RGBA')
im.crop((240,421,365,580)).save(root/'art/root.png')
runpy.run_path(str(root/'prepare_revision2.py'),run_name='__main__')
