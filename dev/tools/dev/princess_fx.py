"""ラナの衣装「姫騎士」用：赤黒のエフェクトを白金（聖なる光）に焼き直す。元の素材は変えず <名前>_p／別名で出す。
   使い方（dev/ で）: python3 -I tools/dev/princess_fx.py [seq|tex|sprite|all]
   色替えの式：v＝RGBの最大（明るさ）、w＝最小÷最大（白さ）。出力＝v×（金→淡い金を v で補間 → 白へ w で補間）。
     色相に関係なく効くので、赤（ラナ）も緑（シオウの斬撃）も同じ式で白金になる。灰色の岩（w≈1）はほぼそのまま。
   seq   ：seq_lanaU_NN・seq_lanaU24_NN（光・黒地）→ seq_lanaPU_NN・seq_lanaPU24_NN。抜き（…m_NN）は共有（コードの SEQ_MT）。
   tex   ：vfx_rift_fb/em/slash・vfx_quakeC_floor/air → vfx_*_p、vfx_samurai_fb → vfx_princess_fb（墨の黒は薄い琥珀に寄せて半透明に）。
   sprite：sword_princess(.webp/_smooth) の原画に焼き込まれた赤い斬撃だけを金へ（赤の強い画素だけ。肌・髪・ブーツは対象外）。
     元に戻すときは git の元版（または tools/dev/lana_princess.py --pack）へ戻してから、このスクリプトの sprite を再実行する（重ねがけ防止のため
     cardart/src_lana_princess/.sprite_gold に印を残し、印があれば何もしない）。"""
import sys, os, glob, numpy as np
from PIL import Image
AMBER=np.array([255,150,34],np.float32); PALE=np.array([255,224,150],np.float32); WHITE=np.array([255,255,255],np.float32)

def holy(rgb, boost=1.08):
    a=rgb.astype(np.float32); v=a.max(-1); mn=a.min(-1)
    w=np.where(v>1,mn/np.maximum(v,1),1.0)[...,None]; t=(v/255)[...,None]
    col=AMBER*(1-t)+PALE*t; col=col*(1-w)+WHITE*w
    return np.clip(col*(v[...,None]/255)*boost,0,255)

def save(arr,mode,path,**kw):
    Image.fromarray(arr.astype(np.uint8),mode).save(path,**kw)

def do_seq():
    for src,dst in (('lanaU','lanaPU'),('lanaU24','lanaPU24')):
        fs=sorted(glob.glob(f'assets/seq_{src}_[0-9][0-9].webp'))
        for f in fs:
            n=f[-7:-5]; a=np.asarray(Image.open(f).convert('RGB'))
            save(holy(a,1.3),'RGB',f'assets/seq_{dst}_{n}.webp',quality=82,method=6)
        print(dst,len(fs),'コマ')

def do_tex():
    for n in ('rift_fb','rift_slash','rift_em'):
        im=Image.open(f'assets/vfx_{n}.webp'); a=np.asarray(im.convert('RGBA')).astype(np.float32)
        a[...,:3]=holy(a[...,:3])
        out=a if im.mode=='RGBA' else a[...,:3]
        save(out,im.mode if im.mode in('RGBA','RGB') else 'RGBA',f'assets/vfx_{n}_p.webp',**({'quality':92} if n in ('rift_fb','rift_em') else {'lossless':True}),method=6)
    for n in ('quakeC_floor','quakeC_air'):   # 大地割り（Godot C案）の赤橙の発光も白金へ。大きいので非可逆
        a=np.asarray(Image.open(f'assets/vfx_{n}.webp').convert('RGBA')).astype(np.float32)
        a[...,:3]=holy(a[...,:3]); save(a,'RGBA',f'assets/vfx_{n}_p.webp',quality=90,method=6)
    a=np.asarray(Image.open('assets/vfx_samurai_fb.webp').convert('RGBA')).astype(np.float32)
    v=a[...,:3].max(-1)
    ink=np.clip((70-v)/50,0,1)                     # 墨の黒（暗い所）
    rgb=holy(a[...,:3],1.15)
    rgb=rgb*(1-ink[...,None])+np.array([150,104,40],np.float32)*ink[...,None]   # 墨→琥珀
    a[...,3]=a[...,3]*(1-0.55*ink)
    a[...,:3]=rgb; save(a,'RGBA','assets/vfx_princess_fb.webp',quality=92,method=6)
    print('tex ok')

def do_sprite():
    mark='cardart/src_lana_princess/.sprite_gold'
    if os.path.exists(mark): print('sprite: 印あり（済み）'); return
    for n in ('sword_princess','sword_princess_smooth'):
        a=np.asarray(Image.open(f'assets/{n}.webp').convert('RGBA')).astype(np.float32)
        r,g,b=a[...,0],a[...,1],a[...,2]
        red=np.clip((r-110)/40,0,1)*np.clip((0.7-np.maximum(g,b)/np.maximum(r,1))/0.15,0,1)*(a[...,3]>0)
        a[...,:3]=a[...,:3]*(1-red[...,None])+holy(a[...,:3],1.2)*red[...,None]
        save(a,'RGBA',f'assets/{n}.webp',lossless=True,exact=True,method=6)
        print(n,'赤→金',int((red>0.5).sum()),'画素')
    open(mark,'w').write('sword_princess*.webp の赤い斬撃を金へ焼き済み（princess_fx.py sprite）\n')

if __name__=='__main__':
    k=sys.argv[1] if len(sys.argv)>1 else 'all'
    if k in('seq','all'):do_seq()
    if k in('tex','all'):do_tex()
    if k in('sprite','all'):do_sprite()
