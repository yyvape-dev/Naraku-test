"""フィリシア（phyllis）の背面スプライト：ユーザーの16コマ（2064×1392・マゼンタ背景）→ assets/phyllis.webp
   使い方:
     python3 -I tools/dev/phyllis_sprite.py crop <作業フォルダ>          # 共通の画角で切った不透明のコマ（RIFE の入力）を書く
     python3 -I tools/dev/phyllis_sprite.py pack <作業フォルダ> [mid]    # 抜いて1枚のシートに。mid＝作業フォルダ/mid の補間コマを間に挟む
   全コマ同じ切り抜き・同じ倍率（足元は元画像で y=1175・x≈1048 に揃っているので、動かさない）。
   左右の中心は足元。反転して描いても足元が動かない。"""
import sys, json, glob
from pathlib import Path
import numpy as np
from PIL import Image

mode, work = sys.argv[1], Path(sys.argv[2])
root = Path(__file__).resolve().parents[2]
src = sorted((root/'cardart'/'src_phyllis_motion').glob('key_*.png'))
assert len(src) == 16, len(src)
FOOT_X, FOOT_Y, TOP = 1048, 1175, 204
BOX = (FOOT_X-520, 60, FOOT_X+520, 1200)       # 1040×1140。花びらが左へ散る分と、頭上へ舞う分を含む
K = 0.28   # 2026-10-18 0.36→0.28（iPhone のメモリ対策。表示の身長に対して十分）
SIZE = (round(1040*K), round(1140*K))           # 291×319

def keyed(im):
    rgb = np.asarray(im.convert('RGB'), dtype=np.float32)
    bg = np.median(np.concatenate([rgb[:6].reshape(-1,3), rgb[-6:].reshape(-1,3)]), axis=0)
    delta = np.max(np.abs(rgb-bg), axis=2)
    alpha = np.clip((delta-40)/110, 0, 1)
    color = (rgb-bg*(1-alpha[:,:,None]))/np.maximum(alpha[:,:,None], .001)
    r, g, b = color[...,0], color[...,1], color[...,2]
    # マゼンタのにじみ：赤い花びらの縁は桃色、茨の縁は紫になる。この絵に青・紫の部分は無いので寄せて消す
    pink = (b > g+25) & (r > 120)
    color[...,2] = np.where(pink, g+(b-g)*0.15, b)
    purple = (color[...,2] > g+15) & (r > g+15)
    y = 0.3*r+0.59*g+0.11*color[...,2]
    for c, k in ((0,1.15),(1,0.95),(2,0.85)):
        color[...,c] = np.where(purple, y*k, color[...,c])
    out = np.dstack([np.clip(color,0,255), alpha*255]).astype('uint8')
    out[alpha == 0] = 0
    return Image.fromarray(out, 'RGBA')

if mode == 'crop':
    work.mkdir(parents=True, exist_ok=True)
    for i, p in enumerate(src):
        Image.open(p).convert('RGB').crop(BOX).resize(SIZE, Image.Resampling.LANCZOS).save(work/f'{i:08}.png')
    print('crop', SIZE, len(src))
else:
    frames = [keyed(Image.open(work/f'{i:08}.png')) for i in range(16)]
    if 'mid' in sys.argv[3:]:
        mids = sorted((work/'mid').glob('*.png'))
        assert len(mids) == 15, len(mids)
        seq = []
        for i, f in enumerate(frames):
            seq.append(f)
            if i < 15: seq.append(keyed(Image.open(mids[i])))
    else:
        seq = frames
    # 本体から離れた小さな欠片（抜き残りの点）を消すのはしない：花びらが散る演出なので、離れた点も絵の一部
    sheet = Image.new('RGBA', (SIZE[0]*len(seq), SIZE[1]))
    for i, f in enumerate(seq): sheet.paste(f, (i*SIZE[0], 0))
    sheet.save(root/'assets'/'phyllis.webp', lossless=True, exact=True)
    meta = dict(cols=len(seq), cw=SIZE[0], ch=SIZE[1], ax=SIZE[0]/2, ay=round((FOOT_Y-BOX[1])*K), refH=round((FOOT_Y-TOP)*K), target='ally')
    (root/'assets'/'phyllis.json').write_text(json.dumps(meta)+'\n')
    print('pack', meta, round((root/'assets'/'phyllis.webp').stat().st_size/1024), 'KB')
