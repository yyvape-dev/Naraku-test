"""攻撃速度の倍率（×1〜×8）を変えたときの、攻撃回数・命中数・無駄弾（飛行中に標的が倒れて消えた弾）・与ダメージを測る（敵は毎秒5体追加）。
   使い方: python3 dev/tools/dev/speed_probe.py http://127.0.0.1:8765/index.html fox,sister"""
import sys,json
from playwright.sync_api import sync_playwright
url=sys.argv[1]
JS=r"""([id,seed,m,secs])=>{
  const N=NARAKU;
  if(!window._w){window._w=1;const a0=window.allyHit,h0=window.hitFrom;window.allyHit=function(a,tg,rep,so){window.CNT.att++;return a0(a,tg,rep,so)};window.hitFrom=function(a,e,k){window.CNT.hit++;return h0(a,e,k)}}
  window.CNT={att:0,hit:0};
  N.start([id],seed);const B=N.B;B.need=1e12;B.life=1e9;
  const a=B.allies[0];a.max=a.hp=1e9;a.M.spd=m;
  for(let t=0;t<secs;t++){for(let k=0;k<5;k++)N.spawn('skel');N.sim(1)}
  const s=B.stat[id];
  return {m,att:CNT.att/secs,hit:CNT.hit/secs,dps:s.atk/secs,kills:B.kills,cd:+(a.d.cd/m).toFixed(3)}}"""
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':844});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(url);pg.wait_for_function("window.NARAKU_READY",timeout=120000)
    for id in sys.argv[2].split(','):
        print(id)
        for m in (1,1.5,2,3,4,6,8):
            rs=[pg.evaluate(JS,[id,seed,m,60]) for seed in (1,2,3)]
            av=lambda k:sum(r[k] for r in rs)/3
            print(f"  速度×{m:<4} 間隔{rs[0]['cd']:.2f}s 攻撃/秒 {av('att'):5.2f} 命中/秒 {av('hit'):5.2f} 無駄弾 {(1-av('hit')/max(av('att'),1e-9))*100:4.0f}% 与ダメ/秒 {av('dps'):6.1f} 撃破 {av('kills'):5.0f}")
    print('errs',errs);b.close()
