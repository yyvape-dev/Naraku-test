"""乾坤一擲（ラナ・縦一列）の原画 → 透過・発光の焼き込み・コマ補間した縦長の連番アトラス。
   原画は vfx/src_rift/（マゼンタ背景）：slash＝一閃の光（別の絵）、e1→e2＝地面から伸びる隆起（下端が防衛線）、
   peak→peak2＝最大（列いっぱいの岩と赤い光）、scar＝残る裂け目（3秒、床の層）。
   マスは 192×576（1:3）。下端＝防衛線、上端＝戦場の上端。使い方: python3 tools/dev/riftfb.py"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
D='vfx/src_rift/';CW,CH=192,576;COL=(0.55,0.02,0.02)
def key(p):
    a=np.asarray(Image.open(p).convert('RGB')).astype(np.float32)
    bg=np.median(np.concatenate([a[:6].reshape(-1,3),a[:,:6].reshape(-1,3),a[:,-6:].reshape(-1,3)]),0)
    d=np.sqrt(((a-bg)**2).sum(-1));al=np.clip((d-45)/120,0,1)
    c=np.clip(np.where(al[...,None]>0.02,(a-bg*(1-al[...,None]))/np.maximum(al[...,None],0.02),0),0,255)/255
    # 半透明の煙に残る桃色（マゼンタの混じり）を赤へ寄せる：青が緑より強い所の青を落とす
    r,g,b=c[...,0],c[...,1],c[...,2];c[...,2]=np.minimum(b,np.maximum(g,b*0.35))
    return np.dstack([c,al])
def place(f,hf,maxw=0.98):  # 中身の外接矩形を、下端に揃えて高さ hf（マスの割合）に。幅が溢れるときは横だけ縮める
    ys,xs=np.where(f[...,3]>0.06);f=f[ys.min():ys.max()+1,xs.min():xs.max()+1]
    h=int(CH*hf);w=int(f.shape[1]*h/f.shape[0]);w=min(w,int(CW*maxw))
    im=Image.fromarray((f*255).astype(np.uint8),'RGBA').resize((w,h),Image.LANCZOS)
    out=Image.new('RGBA',(CW,CH));out.paste(im,((CW-w)//2,CH-h));return np.asarray(out).astype(np.float32)/255
def glow(f):
    lum=f[...,:3].max(-1)*f[...,3];src=np.clip((lum-0.55)/0.45,0,1)
    g=ndi.gaussian_filter(src,5)*1.5+ndi.gaussian_filter(src,13)*1.1;g=np.clip(g,0,0.8);a=f[...,3];oa=a+g*(1-a)
    oc=np.where(oa[...,None]>1e-3,(f[...,:3]*a[...,None]+np.array(COL)*g[...,None]*(1-a[...,None]))/np.maximum(oa[...,None],1e-3),0)
    return np.dstack([oc,oa])
def pm_mix(a,b,t):  # 不透明度つきで混ぜる（色は不透明度で重みづけ）
    al=a[...,3]*(1-t)+b[...,3]*t;c=(a[...,:3]*a[...,3:]*(1-t)+b[...,:3]*b[...,3:]*t)/np.maximum(al[...,None],1e-4)
    return np.dstack([c,al])
keys=[place(key(D+'e1.png'),0.40),place(key(D+'e2.png'),0.70),place(key(D+'peak.png'),1.0),place(key(D+'peak2.png'),1.0),place(key(D+'scar.png'),0.97,0.8)]
steps=[2,2,2,3]
frames=[]
for i in range(len(keys)-1):
    for s in range(steps[i]):frames.append(pm_mix(keys[i],keys[i+1],s/steps[i]))
frames.append(keys[-1])
n=len(frames);cols=5;rows=(n+cols-1)//cols
at=Image.new('RGBA',(cols*CW,rows*CH))
for j,f in enumerate(frames):at.paste(Image.fromarray((np.clip(glow(f),0,1)*255).astype(np.uint8),'RGBA'),((j%cols)*CW,(j//cols)*CH))
at.save('assets/vfx_rift_fb.webp',quality=88,method=6)
# 発光だけの絵（黒地・半分の大きさ）：赤く光る所だけを加算で脈打たせる（岩の灰色は明るくしない）
em=Image.new('RGB',(cols*CW//2,rows*CH//2))
for j,f in enumerate(frames):
    g=glow(f);c=g[...,:3]*g[...,3:];r,gg,b=c[...,0],c[...,1],c[...,2]
    m=np.clip((r-np.maximum(gg,b)*1.15-0.12)*3,0,1);e=c*m[...,None]
    em.paste(Image.fromarray((np.clip(e,0,1)*255).astype(np.uint8),'RGB').resize((CW//2,CH//2),Image.LANCZOS),((j%cols)*CW//2,(j//cols)*CH//2))
em.save('assets/vfx_rift_em.webp',quality=80,method=6)
sl=place(key(D+'slash.png'),1.0,0.6);Image.fromarray((np.clip(glow(sl),0,1)*255).astype(np.uint8),'RGBA').save('assets/vfx_rift_slash.webp',quality=88,method=6)
print('コマ',n)
b=Image.new('RGBA',at.size,(28,24,30,255));b.alpha_composite(at);b.convert('RGB').resize((at.width//2,at.height//2)).save('/tmp/claude-0/nv/rift_fb.png')
