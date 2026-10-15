"""Pack Godot renders into the game's atlas format (6x6, floor 192px / air 256px, 36 frames, 40 fps).
light pass: opaque RGB on black (additive) -> alpha = max channel, colour un-premultiplied.
matte pass: Godot transparent readback is premultiplied -> un-premultiply.
result = light OVER matte, straight alpha (what the game's source-over drawImage expects)."""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parent
out = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'out'
out.mkdir(parents=True, exist_ok=True)
report = {}
for layer, tile in [('floor', 192), ('air', 320)]:
    atlas = Image.new('RGBA', (tile * 6, tile * 6))
    for i in range(36):
        L = np.asarray(Image.open(root / f'frames/{layer}_light_{i:02}.png').convert('RGB'), np.float32) / 255
        M = np.asarray(Image.open(root / f'frames/{layer}_matte_{i:02}.png').convert('RGBA'), np.float32) / 255
        la = np.clip(L.max(axis=2, keepdims=True), 0, 1)
        lc = np.where(la > 1e-4, L / np.maximum(la, 1e-4), 0)
        ma = M[:, :, 3:4]
        mc = np.where(ma > 1e-4, M[:, :, :3] / np.maximum(ma, 1e-4), 0)
        oa = la + ma * (1 - la)
        oc = np.where(oa > 1e-4, (lc * la + mc * ma * (1 - la)) / np.maximum(oa, 1e-4), 0)
        rgba = np.concatenate([np.clip(oc, 0, 1), np.clip(oa, 0, 1)], axis=2)
        im = Image.fromarray(np.rint(rgba * 255).astype(np.uint8), 'RGBA')
        atlas.paste(im.resize((tile, tile), Image.Resampling.LANCZOS), (i % 6 * tile, i // 6 * tile))
    p = out / f'foxfire_{layer}.webp'
    atlas.save(p, quality=94, method=6)
    report[layer] = {'tile': tile, 'bytes': p.stat().st_size, 'decodedBytes': atlas.width * atlas.height * 4}
print(json.dumps(report))
