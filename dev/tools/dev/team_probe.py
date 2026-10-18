"""7人から3人を選ぶ全35編成×2シードを、ボット操縦・強化ランダムで1戦ずつ回し、キャラ別の与ダメージ（通常DPS・スキルDPS・合計・編成内シェア）と札の使用回数を出す。
   使い方: python3 dev/tools/dev/team_probe.py http://127.0.0.1:8765/index.html   （約10分。ばらつきは±20程度）
   atk_probe.py（5編成）の全編成版。シオウ・リンネ・ユズナミキの強さ比べと、大きな調整のあとの回帰確認に使う。"""
import sys, os, json
import itertools
from playwright.sync_api import sync_playwright
html=sys.argv[1] if sys.argv[1].startswith("http") else os.path.abspath(sys.argv[1]); ov=json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
JS=r"""([ids,seed,ov])=>{
  for(const k in ov)Object.assign(NARAKU.CHARS[k],ov[k]);
  if(!window._w){window._w=1;window.PS={};const h0=window.hitFrom,a0=window.allyHit;
    window.allyHit=function(a,tg,rep){const s=PS[a.d.id]||(PS[a.d.id]={n:0,hits:0,raw:0});s.n++;return a0(a,tg,rep)};
    window.hitFrom=function(a,e,k){const s=PS[a.d.id]||(PS[a.d.id]={n:0,hits:0,raw:0});s.hits++;s.raw+=a.d.dmg*k;return h0(a,e,k)}}
  window.PS={};window.CU={};
  const BOT=(B)=>{const al=B.allies.filter(a=>a.alive);
    B.slots.forEach((s,i)=>{const c=s.card;if(!c)return;
      if(c.kind==='instant'){if(c.band){if(B.enemies.filter(e=>e.y>B.lineY-c.band).length>=4)(CU[c.id]=(CU[c.id]||0)+1,NARAKU.useCard(i,0,0))}
        else if(al.some(a=>a.hp<a.max*0.55))(CU[c.id]=(CU[c.id]||0)+1,NARAKU.useCard(i,0,0));return}
      if(c.shape==='col'){let bx=0,bn=0;for(let x=30;x<=330;x+=20){let n=0;for(const e of B.enemies){if(e.y<B.lineY&&Math.abs(e.x-x)<c.hw)n++}if(n>bn){bn=n;bx=x}}if(bn>=3)(CU[c.id]=(CU[c.id]||0)+1,NARAKU.useCard(i,bx,B.lineY*0.5));return}
      if(c.shape==='row'){let bb=null,bn=0;for(const e of B.enemies){let n=0;for(const o of B.enemies){if(Math.abs(o.y-e.y)<c.hh)n++}if(n>bn){bn=n;bb=e}}if(bb&&bn>=4)(CU[c.id]=(CU[c.id]||0)+1,NARAKU.useCard(i,180,bb.y-16));return}
      let best=null,bc=0;for(const e of B.enemies){if(e.y<20)continue;let n=0;for(const o of B.enemies){const dx=o.x-e.x,dy=o.y-e.y;if(dx*dx+dy*dy<c.r*c.r)n++}if(n>bc){bc=n;best=e}}
      if(best&&bc>=4)(CU[c.id]=(CU[c.id]||0)+1,NARAKU.useCard(i,best.x,best.y-16))})};
  let rs=seed*7919+13;const rnd=()=>{rs=(rs*1103515245+12345)&0x7fffffff;return rs/0x7fffffff};
  const pick=(o,B)=>{const c=o.map((u,i)=>i).filter(i=>o[i].fam!=='taboo');return c[Math.floor(rnd()*c.length)]};
  NARAKU.start(ids,seed);const dead={};let m='battle';
  for(let t=0;t<NARAKU.CFG.dur+1&&(m==='battle'||m==='levelup');t++){m=NARAKU.sim(1,BOT,pick);NARAKU.B.allies.forEach(a=>{if(!a.alive&&dead[a.d.id]==null)dead[a.d.id]=NARAKU.B.t})}
  const B=NARAKU.B,t=B.t;
  return {cu:CU,win:m==='victory',rows:B.allies.map(a=>{const s=B.stat[a.d.id],q=PS[a.d.id]||{n:0,hits:0,raw:0};return [a.d.id,s.atk/t,s.skill/t,q.n,q.hits,q.raw,s.atk,dead[a.d.id]==null?t:dead[a.d.id],s.taken]})}}"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':390,'height':844})
    errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto(html if html.startswith("http") else "file://"+html); pg.wait_for_function("window.NARAKU_READY",timeout=120000)
    agg={}; wins=0; n=0; cu={}; share={}
    ids=['fox','sword','sister','mage','blue','ninja','samurai']
    for party in itertools.combinations(ids,3):
        for seed in (1,2):
            r=pg.evaluate(JS,[list(party),seed,ov]); n+=1; wins+=r['win']
            for k,v in r['cu'].items(): cu[k]=cu.get(k,0)+v
            tot=sum(x[1]+x[2] for x in r['rows']) or 1
            for x in r['rows']:
                a=agg.setdefault(x[0],[0]*9); a[0]+=1
                for i in range(1,9): a[i]+=x[i]
                share.setdefault(x[0],[]).append((x[1]+x[2])/tot)
    print(f'勝率 {wins}/{n}（各キャラ {agg["fox"][0]} 戦ずつ）')
    print('キャラ   通常DPS スキルDPS  合計DPS  編成内シェア  生存秒 被ダメ')
    for k,a in sorted(agg.items(),key=lambda kv:-(kv[1][1]+kv[1][2])/kv[1][0]):
        c=a[0]; print(f'{k:7} {a[1]/c:7.0f} {a[2]/c:8.0f} {(a[1]+a[2])/c:8.0f} {sum(share[k])/len(share[k])*100:9.0f}% {a[7]/c:7.0f} {a[8]/c:6.0f}')
    print('札の使用回数（全戦合計）',{k:cu[k] for k in sorted(cu)})
    b.close(); print('errs',errs)
