"""黒背景の原画（数枚・始動→収束）→ RIFE でコマを増やした透過アトラス。スキルごとの設定は CFG。
   使い方：
     python3 tools/dev/keyfb.py <名前> prep <空のフォルダ>   … 中心を揃えた640pxの連番 001.png〜 を書く
     （RIFE：VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json ./rife-ncnn-vulkan -i <prep> -o <out> -m rife-v4.6 -n <コマ数> -f %03d.png）
     python3 tools/dev/keyfb.py <名前> bake <RIFEの出力>     … assets/vfx_<名前>.webp（256px・6列）
   透過：「RGBの最大値＝不透明度、色は割り戻し」。さらに楕円のふち（vig）で外側を溶かし、四角い・塊のシルエットを崩す。
   dust_ring（物理の技の砂煙の輪。光ではないので普通に重ねる）。mage_void（シェリ 凍てつく虚無）は tools/dev/icefb.py と同じ並び・中心。"""
import sys,glob,numpy as np
from PIL import Image
CFG={
 'fox_fire':dict(d='vfx/src_fox_fire/',cy=0.6,n=21,keys=[('1_fall',1050,635),('2_bloom',700,630),('3_max',640,640),('4_scatter',640,630),('5_ember',740,640)],vig=(0.36,0.5)),
 'dust_ring':dict(d='vfx/src_dust_ring/',cy=0.5,n=21,sc=0.88,cmul=0.82,keys=[('1_burst',658,630),('2_thick',655,628),('3_spread',641,616),('4_thin',632,612),('5_faint',653,594)],vig=(0.44,0.52)),
 'mage_void':dict(d='vfx/src_mage_void/',cy=0.75,n=26,keys=[('1_circle',800,627),('2_swirl',800,627),('3_spikes',960,627),('4_max',985,627),('5_shatter',980,627),('6_dust',750,627)],vig=(0.4,0.5)),
}
name,mode=sys.argv[1],sys.argv[2];C=CFG[name];T=256;COLS=6
if mode=='prep':
    for i,(n,cy,cx) in enumerate(C['keys']):
        a=np.asarray(Image.open(C['d']+n+'.png').convert('RGB'));h,w=a.shape[:2];b=np.zeros_like(a)
        dy=int(h*C['cy']-cy);dx=int(w*0.5-cx)
        ys=slice(max(0,dy),min(h,h+dy));yd=slice(max(0,-dy),min(h,h-dy));xs=slice(max(0,dx),min(w,w+dx));xd=slice(max(0,-dx),min(w,w-dx))
        b[ys,xs]=a[yd,xd];im=Image.fromarray(b);sc=C.get('sc',1)
        if sc!=1:  # 中心（cx, cy の位置）を保ったまま縮める
            z=im.resize((int(w*sc),int(h*sc)),Image.LANCZOS);im=Image.new('RGB',(w,h));im.paste(z,(int(w*0.5*(1-sc)),int(h*C['cy']*(1-sc))))
        im.resize((640,640),Image.LANCZOS).save(f'{sys.argv[3]}/{i+1:03d}.png')
    sys.exit()
fs=sorted(glob.glob(sys.argv[3]+'/*.png'));n=len(fs);rows=(n+COLS-1)//COLS
yy,xx=np.mgrid[0:T,0:T]/(T-1);r=np.hypot(xx-0.5,(yy-C['cy'])*0.5/max(C['cy'],1-C['cy']))  # 中心から上下の端まで0.5になる楕円
v0,v1=C['vig'];vig=np.clip((v1-r)/(v1-v0),0,1);vig=vig*vig*(3-2*vig)
at=Image.new('RGBA',(COLS*T,rows*T))
for j,f in enumerate(fs):
    b=np.asarray(Image.open(f).convert('RGB').resize((T,T),Image.LANCZOS)).astype(np.float32)/255
    m=b.max(-1);al=np.clip((m-0.04)/0.7,0,1)*vig
    c=np.where(al[...,None]>0.01,b/np.maximum(m[...,None],1e-3),0)*np.clip(m/0.7,0,1)[...,None]**0.25*C.get('cmul',1)  # cmul：砂煙など光でない絵は色を落とす
    at.paste(Image.fromarray((np.dstack([np.clip(c,0,1),al])*255).astype(np.uint8),'RGBA'),((j%COLS)*T,(j//COLS)*T))
at.save(f'assets/vfx_{name}.webp',quality=84,method=6);print(name,'コマ',n)
b=Image.new('RGBA',at.size,(40,36,44,255));b.alpha_composite(at);b.convert('RGB').resize((at.width//2,at.height//2)).save(f'/tmp/claude-0/nv/{name}_sheet.png')
