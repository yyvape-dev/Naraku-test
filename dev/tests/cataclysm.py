"""大異変の確認。使い方: python3 dev/tests/cataclysm.py <http の配布版URL> [seeds=1,2,3]
   1マスの地図／9分戦・主は3・6・9分／強敵は2体ずつ／最後の主を倒すまで終わらない／超必殺が1分半ごとに戻る／踏破で伝説確定／抽選は約8%で他の異変の結果は不変"""
import sys, json
from playwright.sync_api import sync_playwright
url=sys.argv[1]; seeds=[int(x) for x in (sys.argv[2].split('=')[1] if len(sys.argv)>2 else '1,2,3').split(',')]
BOT=r"""(B)=>{const al=B.allies.filter(a=>a.alive);
  B.slots.forEach((s,i)=>{const c=s.card;if(!c)return;
    if(c.kind==='instant'){if(c.band){if(B.enemies.filter(e=>e.y>B.lineY-c.band).length>=4)NARAKU.useCard(i,0,0)}else if(al.some(a=>a.hp<a.max*0.55))NARAKU.useCard(i,0,0);return}
    if(c.shape==='col'){let bx=0,bn=0;for(let x=30;x<=330;x+=20){let n=0;for(const e of B.enemies){if(e.y<B.lineY&&Math.abs(e.x-x)<c.hw)n++}if(n>bn){bn=n;bx=x}}if(bn>=3)NARAKU.useCard(i,bx,B.lineY*0.5);return}
    if(c.shape==='row'){let bb=null,bn=0;for(const e of B.enemies){let n=0;for(const o of B.enemies){if(Math.abs(o.y-e.y)<c.hh)n++}if(n>bn){bn=n;bb=e}}if(bb&&bn>=4)NARAKU.useCard(i,180,bb.y-16);return}
    let best=null,bc=0;for(const e of B.enemies){if(e.y<20)continue;let n=0;for(const o of B.enemies){const dx=o.x-e.x,dy=o.y-e.y;if(dx*dx+dy*dy<c.r*c.r)n++}if(n>bc){bc=n;best=e}}
    if(best&&bc>=4)NARAKU.useCard(i,best.x,best.y-16)})}"""
JS="""([seed,pid])=>{const N=NARAKU,out={};const bot="""+BOT+""";
  N.startRun(pid,seed,1,'cata');const R=N.R;out.map=[R.map.steps,R.map.nodes.length,R.map.nodes[1].type].join();
  N.go(1);const B=N.B;out.kind=B.kind;out.dur=B.dur;
  const bossT=[],eliteT={},ultReset=[];let prevUlt=0;let m='battle',guard=0;
  const pick=(o)=>{const c=o.map((u,i)=>i).filter(i=>o[i].fam!=='taboo');return c[(seed*7+guard)%c.length]};
  while((m==='battle'||m==='levelup')&&guard<4000){
    const nb=N.B.enemies.filter(e=>e.d.boss).length,ne=N.B.enemies.length;
    const had=Object.keys(N.B.ultUsed).length;m=N.sim(0.25,bot,pick);guard++;
    if(had&&!Object.keys(N.B.ultUsed).length)ultReset.push(Math.round(N.B.t));
    for(const e of N.B.enemies){if(e.d.boss&&!e._seen){e._seen=1;bossT.push(Math.round(N.B.t))}if(e.elite&&!e.d.boss&&!e._seen){e._seen=1;const k=Math.round(N.B.t);eliteT[k]=(eliteT[k]||0)+1}}

    if(N.B.t>=540&&!out.at540){out.at540=[m,N.B.cata.n,N.B.cata.last&&N.B.cata.last.dead]}
  }
  const b=N.B;out.end=m;out.t=Math.round(b.t);out.bossT=bossT;out.eliteTwo=Object.values(eliteT).filter(v=>v>=2).length;out.lv=b.lv;out.kills=b.kills;out.ultReset=ultReset;
  if(m==='victory'){out.rew=[b.reward&&b.reward.r,b.rewardGold];out.cleared=N.R.cleared}
  return out}"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
    pg.goto(url); pg.wait_for_function('window.NARAKU_READY',timeout=120000)
    lot=pg.evaluate("""(()=>{let c=0,n=4000,diff=0;for(let i=0;i<n;i++){const s=(i*2654435761)>>>0,k=NARAKU.omens.roll(s,i,'none');if(k==='cata')c++}return c/n})()""")
    print('大異変の抽選率',lot); assert 0.06<lot<0.10
    res=[]
    for sd in seeds:
        for pid in (['fox','sword','mage'],['blue','sister','mage']):
            r=pg.evaluate(JS,[sd,pid]); res.append(r); print(sd,pid,json.dumps(r,ensure_ascii=False))
    print('errs',errs[:3])
    ok=all(r['map']=='1,2,boss' and r['kind']=='cata' and r['dur']==540 for r in res)
    ok=ok and all(r['bossT'][:3]==[180,360,540] or r['end']=='defeat' for r in res)
    ok=ok and all(r['end']!='victory' or (r['t']>=540 and r['rew'][0]==3 and r['cleared']) for r in res)
    ok=ok and all(all(t%90<=1 for t in r['ultReset']) and len(r['ultReset'])>=1 for r in res) and all(r['eliteTwo']>=1 or r['t']<120 for r in res) and not errs
    assert ok,'NG'
    b.close()
print('OK')
