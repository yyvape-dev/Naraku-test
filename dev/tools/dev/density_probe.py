"""通常攻撃だけ・キャラ単独・速度×1で、敵の密度（毎秒2／6／12体を足す）を変えたときの与ダメージを7人分出す。単体型が群れで伸びない（×1.0）か、範囲型が伸びる（×4）かを見る。
   使い方: python3 dev/tools/dev/density_probe.py http://127.0.0.1:8765/index.html   （約3分）
   注意：単独なので敵が防衛線に溜まり、密度は実戦より高め。傾向を見る道具。"""
import sys
from playwright.sync_api import sync_playwright
url=sys.argv[1]
JS=r"""([id,seed,extra,secs])=>{
  const N=NARAKU;
  if(!window._w){window._w=1;const a0=window.allyHit,h0=window.hitFrom;window.allyHit=function(a,tg,rep,so){window.CNT.att++;return a0(a,tg,rep,so)};window.hitFrom=function(a,e,k){window.CNT.hit++;return h0(a,e,k)}}
  window.CNT={att:0,hit:0};
  N.start([id],seed);const B=N.B;B.need=1e12;B.life=1e9;
  const a=B.allies[0];a.max=a.hp=1e9;
  for(let t=0;t<secs;t++){for(let k=0;k<extra;k++)N.spawn('skel');N.sim(1)}
  const s=B.stat[id];
  return {att:CNT.att/secs,hit:CNT.hit/secs,dps:s.atk/secs,kills:B.kills/secs,alive:B.enemies.filter(e=>!e.dead).length}}"""
ids=['fox','ninja','sister','sword','blue','mage','samurai']
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':844});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(url);pg.wait_for_function("window.NARAKU_READY",timeout=120000)
    print('通常攻撃だけ・単独・速度×1（各3シード×60秒）。DPS＝与ダメ/秒、命中/回＝1回の攻撃で当てた敵の数')
    print('キャラ    型     | 密度小(毎秒2体)  | 密度中(毎秒6体)  | 密度大(毎秒12体)  | 大÷小')
    for id in ids:
        row=[]
        for ex in (2,6,12):
            rs=[pg.evaluate(JS,[id,seed,ex,60]) for seed in (1,2,3)]
            av=lambda k:sum(r[k] for r in rs)/3
            row.append((av('dps'),av('hit')/max(av('att'),1e-9)))
        print(f"{id:8}        | {row[0][0]:5.1f} ({row[0][1]:.1f}/回) | {row[1][0]:5.1f} ({row[1][1]:.1f}/回) | {row[2][0]:5.1f} ({row[2][1]:.1f}/回)  | ×{row[2][0]/row[0][0]:.2f}")
    print('errs',errs);b.close()
