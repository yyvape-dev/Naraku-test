"""マゼンタ背景のエフェクト原画 → 透過・発光の焼き込み・コマ補間した連番アトラス（4列）。
   使い方: python3 tools/dev/slashfb.py ninja|samurai"""
import sys,numpy as np
from PIL import Image,ImageFilter
from scipy import ndimage as ndi
name=sys.argv[1];D=f'vfx/src_{name}/';T=256
def key(p):
    a=np.asarray(Image.open(p).convert('RGB')).astype(np.float32)
    bg=np.median(np.concatenate([a[:6].reshape(-1,3),a[-6:].reshape(-1,3)]),0)
    d=np.sqrt(((a-bg)**2).sum(-1));al=np.clip((d-45)/120,0,1)
    c=np.clip(np.where(al[...,None]>0.02,(a-bg*(1-al[...,None]))/np.maximum(al[...,None],0.02),0),0,255)
    h,w=al.shape;s=min(h,w);y0=(h-s)//2;x0=(w-s)//2
    im=Image.fromarray(np.dstack([c,al*255]).astype(np.uint8)[y0:y0+s,x0:x0+s],'RGBA').resize((T,T),Image.LANCZOS)
    return np.asarray(im).astype(np.float32)/255
def ink(f):  # シオウ：赤い飛沫を黒い墨へ（少し赤みを残す）
    r,g,b=f[...,0],f[...,1],f[...,2];m=np.clip((r-np.maximum(g,b))*3-0.15,0,1)*(g<0.45)
    gray=0.25*(r+g+b)/3;f[...,0]=r*(1-m)+(gray+0.06)*m;f[...,1]=g*(1-m)+gray*m;f[...,2]=b*(1-m)+gray*m;return f
def glow(f,col):  # 明るい所から色つきのにじみを作り、下に敷く（赤黒／緑）
    lum=f[...,:3].max(-1)*f[...,3];src=np.clip((lum-0.55)/0.45,0,1)
    g=ndi.gaussian_filter(src,6)*1.6+ndi.gaussian_filter(src,16)*1.2;g=np.clip(g,0,0.85)
    a=f[...,3];oa=a+g*(1-a)
    oc=np.where(oa[...,None]>1e-3,(f[...,:3]*a[...,None]+np.array(col)*g[...,None]*(1-a[...,None]))/np.maximum(oa[...,None],1e-3),0)
    return np.dstack([oc,oa])
flip=lambda f:f[:,::-1].copy()
if name=='ninja':
    src=[key(f'{D}{i}.png') for i in range(1,6)]
    # 一閃→返し（1の反転）→三本爪→最大→裂け残り（3と反転）→残滓（5と反転）
    keys=[src[0],flip(src[0]),src[1],src[3],src[2],flip(src[2]),src[4],flip(src[4])];col=(0.55,0.02,0.02)
    steps=[1,1,1,2,1,2,2,2]  # 次の絵までの補間コマ数
else:
    src=[ink(key(f'{D}{i}.png')) for i in range(1,7)];keys=src;col=(0.1,0.85,0.35);steps=[2,2,2,2,2,2]
frames=[]
for i,k in enumerate(keys):
    nxt=keys[i+1] if i+1<len(keys) else None
    for s in range(steps[i]):
        t=s/steps[i]
        if nxt is None: f=k.copy();f[...,3]*=1-t*0.9
        else: f=k*(1-t)+nxt*t
        frames.append(f)
fin=frames[-1].copy();fin[...,3]*=0.25;frames.append(fin)
n=len(frames);cols=4;rows=(n+cols-1)//cols
at=Image.new('RGBA',(cols*T,rows*T))
for j,f in enumerate(frames):
    g=glow(f.copy(),col);at.paste(Image.fromarray((np.clip(g,0,1)*255).astype(np.uint8),'RGBA'),((j%cols)*T,(j//cols)*T))
at.save(f'assets/vfx_{name}_fb.webp',quality=90,method=6);print(name,'コマ',n)
b=Image.new('RGBA',at.size,(28,24,30,255));b.alpha_composite(at);b.convert('RGB').resize((at.width//2,at.height//2)).save(f'/tmp/claude-0/nv/fb_{name}.png')
