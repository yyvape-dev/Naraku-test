"""Prepare user keyframes with fixed framing; optionally pack RIFE midpoints.
Usage: python lana_princess.py SOURCE_DIR WORK_DIR [--pack]
RIFE operates on the opaque magenta frames before chroma removal.
"""
import csv, json, sys
from pathlib import Path
import numpy as np
from PIL import Image

src, work = map(Path, sys.argv[1:3])
work.mkdir(parents=True, exist_ok=True)
root = Path(__file__).resolve().parents[2]
rows = list(csv.DictReader((src/'frames.csv').open()))
files = sorted(src.glob('key_*.png'))
assert len(files) == len(rows) == 16
# Same crop and scale for every frame: no moving anchors or per-pose resizing.
BOX = (80, 200, 1120, 1840)
SIZE = (352, 560)

def keyed(im):
    rgb = np.asarray(im.convert('RGB'), dtype=np.float32)
    # Estimate each frame's background to avoid compression/exposure flicker.
    bg = np.median(np.concatenate([rgb[:8].reshape(-1,3),rgb[-8:].reshape(-1,3)]),axis=0)
    delta = np.max(np.abs(rgb-bg),axis=2)
    alpha = np.clip((delta-35)/120,0,1)
    # Unmix the background at the soft silhouette, preserving the red slash.
    color = (rgb-bg*(1-alpha[:,:,None]))/np.maximum(alpha[:,:,None],.001)
    # Remove blue spill from the magenta screen on the red/black sword.
    spill=(color[:,:,0]>color[:,:,1]*1.5)&(color[:,:,2]>color[:,:,1]*1.5)
    color[:,:,2]=np.where(spill,np.minimum(color[:,:,2],color[:,:,1]+color[:,:,0]*.12),color[:,:,2])
    out = np.dstack([np.clip(color,0,255),alpha*255]).astype('uint8')
    out[alpha==0] = 0
    return Image.fromarray(out)

if '--pack' not in sys.argv:
    for i,p in enumerate(files):
        Image.open(p).crop(BOX).resize(SIZE,Image.Resampling.LANCZOS).save(work/f'{i:08}.png')
else:
    frames = [keyed(Image.open(work/f'{i:08}.png')) for i in range(16)]
    smooth = []
    for i,f in enumerate(frames):
        smooth.append(f)
        if i<15: smooth.append(keyed(Image.open(work/'mid'/f'{i:08}.png')))
    # Ref height comes from the upright figure, excluding the raised sword/VFX.
    meta = dict(cw=352,ch=560,ax=(624-80)*352/1040,ay=(1523-200)*560/1640,refH=296,target='ally')
    assets=root/'assets'
    for name,fs in [('sword_princess',frames),('sword_princess_smooth',smooth)]:
        sheet=Image.new('RGBA',(SIZE[0]*len(fs),SIZE[1]))
        for i,f in enumerate(fs):sheet.paste(f,(i*SIZE[0],0))
        sheet.save(assets/(name+'.webp'),lossless=True,exact=True)
        (assets/(name+'.json')).write_text(json.dumps(dict(meta,cols=len(fs)))+'\n')
    times=[int(r['source_frame_zero_based']) for r in rows]
    durations=[(b-a)*1000/24 for a,b in zip(times,times[1:])]+[8*1000/24]
    sm=[]
    for d in durations[:-1]:sm.extend([d/2,d/2])
    sm.append(durations[-1])
    record=dict(source='User keyframes_16_upscaled_3x.zip',crop=BOX,size=SIZE,source_frames=times,
                original=dict(ms=durations,hit=7),smooth=dict(ms=sm,hit=14),method='RIFE v4.6 midpoint; original frames retained')
    (root/'cardart'/'lana_princess.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record))
