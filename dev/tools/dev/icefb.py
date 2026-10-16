"""シェリ「凍てつく虚無」（mg_void）の原画6枚（黒背景）→ RIFE でコマを増やした連番アトラス。
   順番：1_circle 魔法陣 → 2_swirl 冷気の渦 → 3_spikes 氷柱が伸びる → 4_max 氷原（最大）→ 5_shatter 砕ける → 6_dust 残る煌めき。
   使い方：
     python3 tools/dev/icefb.py prep <空のフォルダ>     … 魔法陣の中心をマスの高さ0.75に揃えた640pxの連番 001〜006.png を書く
     （RIFE：VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json ./rife-ncnn-vulkan -i <prep> -o <out> -m rife-v4.6 -n 26 -f %03d.png。手順は Skill naraku-vfx の「8.」）
     python3 tools/dev/icefb.py bake <RIFEの出力フォルダ> … 26コマを透過にして assets/vfx_mage_void.webp（256px・6列）へ
   黒地の光の絵なので「RGBの最大値＝不透明度、色は割り戻し」で透過にする（白い氷は不透明に近く、暗い所は透ける）。鍵のコマ＝0,5,10,15,20,25"""
import sys,glob,numpy as np
from PIL import Image
D='vfx/src_mage_void/';CY=0.75;T=256;COLS=6
SRC=[('1_circle',800),('2_swirl',800),('3_spikes',960),('4_max',985),('5_shatter',980),('6_dust',750)]
if sys.argv[1]=='prep':
    for i,(n,cy) in enumerate(SRC):
        a=np.asarray(Image.open(D+n+'.png').convert('RGB'));h=a.shape[0];sh=int(h*CY-cy);b=np.zeros_like(a)
        if sh>=0:b[sh:]=a[:h-sh]
        else:b[:h+sh]=a[-sh:]
        Image.fromarray(b).resize((640,640),Image.LANCZOS).save(f'{sys.argv[2]}/{i+1:03d}.png')
    sys.exit()
fs=sorted(glob.glob(sys.argv[2]+'/*.png'));n=len(fs);rows=(n+COLS-1)//COLS
at=Image.new('RGBA',(COLS*T,rows*T))
for j,f in enumerate(fs):
    b=np.asarray(Image.open(f).convert('RGB').resize((T,T),Image.LANCZOS)).astype(np.float32)/255
    m=b.max(-1);al=np.clip((m-0.04)/0.7,0,1)
    c=np.where(al[...,None]>0.01,b/np.maximum(m[...,None],1e-3),0)*np.clip(m/0.7,0,1)[...,None]**0.25
    at.paste(Image.fromarray((np.dstack([np.clip(c,0,1),al])*255).astype(np.uint8),'RGBA'),((j%COLS)*T,(j//COLS)*T))
at.save('assets/vfx_mage_void.webp',quality=84,method=6);print('コマ',n)
