"""Lossless packing of four bosses and one elite from frontal eight-frame sheets.
First four frames advance, final four attack. No downsampling.
"""
from pathlib import Path
from PIL import Image
import json
import numpy as np
from scipy import ndimage
ROOT = Path(__file__).resolve().parents[2]
IDS = ['violet_knight', 'frill_dragon', 'sixarm_minotaur', 'crimson_succubus', 'blue_cyclops']
CW, CH, AX, AY = 640, 640, 320, 600

def main():
    for name in IDS:
        source = Image.open(ROOT / 'dev/art/bosses' / f'{name}.png').convert('RGBA')
        data = np.array(source)
        labels, count = ndimage.label(data[:, :, 3] > 12, structure=np.ones((3, 3)))
        sizes = np.bincount(labels.ravel()); sizes[0] = 0
        main = sorted(range(1, count+1), key=lambda label: sizes[label], reverse=True)[:8]
        # Each silhouette is isolated in the original, even when an axe crosses
        # a nominal grid line. Extract the complete component, not that grid.
        centers = {label: ndimage.center_of_mass(data[:, :, 3], labels, label) for label in main}
        main.sort(key=lambda label: (int(centers[label][0] // (source.height/2)), centers[label][1]))
        assert len(main) == 8 and all(sizes[label] > 20000 for label in main)
        atlas = Image.new('RGBA', (CW*8, CH))
        heights = []
        for f, label in enumerate(main):
            mask = ndimage.binary_dilation(labels == label, iterations=2)
            bounds = Image.fromarray(mask).getbbox()
            part = data[bounds[1]:bounds[3], bounds[0]:bounds[2]].copy()
            part[~mask[bounds[1]:bounds[3], bounds[0]:bounds[2]]] = 0
            tile = Image.fromarray(part)
            center = (f%4+.5)*source.width/4
            baseline = bounds[3]
            x = AX+round(bounds[0]-center)
            y = AY+round(bounds[1]-baseline)
            assert x >= 0 and x+tile.width < CW and y >= 0 and y+tile.height < CH, (name,f,bounds,x,y)
            atlas.alpha_composite(tile, (f*CW+x, y))
            heights.append(bounds[3]-bounds[1])
        path = ROOT / 'dev/assets' / name
        atlas.save(path.with_suffix('.webp'), lossless=True, method=6)
        meta = dict(cols=8, cw=CW, ch=CH, ax=AX, ay=AY, refH=heights[0], target='enemy')
        path.with_suffix('.json').write_text(json.dumps(meta)+'\n')
        print(name, 'native body height:', heights[0], 'atlas:', atlas.size, 'bytes:', path.with_suffix('.webp').stat().st_size)

if __name__ == '__main__':
    main()
