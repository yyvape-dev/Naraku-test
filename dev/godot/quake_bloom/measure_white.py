"""炸裂コマの白さ・赤さを数える（調整を数字で確かめる）。
usage: python3 measure_white.py <air atlas.webp> [frames=1-5]
暗い灰色(0.12)の上に重ねて、RGBすべて>0.85を白、R>0.5かつG<0.3を赤として数える。"""
import sys
import numpy as np
from PIL import Image
at = Image.open(sys.argv[1]).convert('RGBA'); t = at.width // 6
a, b = (int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else '1-5').split('-'))
white = red = 0
for f in range(a, b + 1):
    px = np.asarray(at.crop((f % 6 * t, f // 6 * t, f % 6 * t + t, f // 6 * t + t)), np.float32) / 255
    rgb = px[:, :, :3] * px[:, :, 3:] + 0.12 * (1 - px[:, :, 3:])
    white += int((rgb > 0.85).all(axis=2).sum()); red += int(((rgb[:, :, 0] > 0.5) & (rgb[:, :, 1] < 0.3)).sum())
print('white px', white, 'red px', red)
