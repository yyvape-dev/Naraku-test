"""ユズナミキの後ろ姿12コマを、体型・アルファを保って色白に補正。
使い方: python fox_fair.py <補正前fox.webp> <出力fox.webp>
補正前画像: git show ff5cedd:dev/assets/fox.webp > /tmp/fox-original.webp
補間・2倍拡大は行わない。12コマはそのまま。
"""
import sys,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,minimum_filter
CW,CH,COUNT=251,269,12
source=Image.open(sys.argv[1]).convert('RGBA')
assert source.size==(3012,269)
assert hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest() == '63b6e9b60f1ba00bdbe42fee6ee8f831c2a3de9f0e2b2a6b775464c2770a7f15', '補正前の原本を指定してください（重ねがけ防止）'
frames, improved, checks = [], [], []
for i in range(COUNT):
    frame = source.crop((i*CW, 0, (i+1)*CW, CH))
    a = np.asarray(frame).copy()
    rgb = a[:,:,:3].astype(np.float32)
    # Work only inside the opaque figure. Never sharpen alpha or translucent edges.
    mask = minimum_filter(a[:,:,3], size=5) == 255
    luminance = rgb @ np.array([0.2126,0.7152,0.0722], dtype=np.float32)
    detail = luminance - gaussian_filter(luminance, sigma=0.65)
    correction = np.clip(detail * 0.38, -5, 5)
    correction[np.abs(detail) < 1.5] = 0
    correction *= mask
    sharp = rgb + correction[:,:,None]
    r,g,b = rgb.transpose(2,0,1)
    # Same colour transfer in all frames. Per-frame exclusion protects the hair.
    skin = np.clip((r-110)/50,0,1)*np.clip((g-75)/55,0,1)
    skin *= np.clip((68-(r-g))/18,0,1)*np.clip((76-(g-b))/22,0,1)
    skin *= np.clip((r-b-8)/18,0,1)
    hair_boxes = [(88,0,151,59),(88,0,153,65),(70,83,138,147),
                  (70,83,138,146),(82,72,147,124),(78,77,145,130),
                  (65,87,135,149),(65,87,135,149),(65,87,135,149),
                  (77,60,146,122),(80,15,153,78),(88,0,151,59)]
    x0,y0,x1,y1=hair_boxes[i]
    skin[y0:y1,x0:x1]=0
    # Smooth the colour selection, not the image or its silhouette.
    skin=gaussian_filter(skin,0.65)
    skin *= a[:,:,3]>0
    # Lift skin while removing the yellow cast; retain existing light and shadow.
    skin_target = sharp + np.array([-3,5,27],dtype=np.float32)
    skin_target += (255-skin_target)*0.13
    neutral = sharp + np.array([-0.5,0,4],dtype=np.float32)*np.clip((luminance-65)/140,0,1)[:,:,None]
    a[:,:,:3] = np.rint(np.clip(neutral*(1-skin[:,:,None])+skin_target*skin[:,:,None],0,255)).astype('uint8')
    a[a[:,:,3]==0,:3]=np.asarray(frame)[a[:,:,3]==0,:3]
    result = Image.fromarray(a)
    assert np.array_equal(a[:,:,3], np.asarray(frame)[:,:,3])
    assert result.getbbox() == frame.getbbox()
    frames.append(frame)
    improved.append(result)
    checks.append({'frame':i+1,'alpha_identical':True,'bounds_identical':True,
                   'maximum_rgb_change':int(np.abs(a[:,:,:3].astype(int)-rgb).max()),
                   'mean_rgb_change':round(float(np.abs(a[:,:,:3].astype(int)-rgb).mean()),4)})

def sheet(fs):
    w,h = fs[0].size
    image = Image.new('RGBA',(w*len(fs),h))
    for i,f in enumerate(fs): image.paste(f,(i*w,0))
    return image

native = sheet(improved)
native.save(sys.argv[2],lossless=True,exact=True)
print('12 frames; alpha and bounds unchanged')
