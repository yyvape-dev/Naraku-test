"""Published defaults, lazy midpoints, linked assets, and Claude's revive fix."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json,sys,shutil
url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765/index.html'
out=Path(sys.argv[2] if len(sys.argv)>2 else 'dev/reports/blackhole/deployment-checks.json');out.parent.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=shutil.which('chromium'));pg=b.new_page(viewport={'width':393,'height':852});errors=[];requests=[]
 pg.on('pageerror',lambda e:errors.append(str(e)));pg.on('request',lambda r:requests.append(r.url))
 pg.goto(url);pg.wait_for_function('window.NARAKU_READY&&NARAKU.vfx.blackholeReady()');pg.wait_for_function('!document.querySelector("#ldg")')
 defaults=pg.evaluate('''()=>({enabled:NARAKU.BLACKHOLE_VFX.enabled,smooth:NARAKU.BLACKHOLE_VFX.smooth,midLoaded:!!VT.blackhole_air_mid||!!VT.blackhole_floor_mid,linked:LINKED})''')
 assert defaults=={'enabled':True,'smooth':False,'midLoaded':False,'linked':True},defaults
 assert not any('vfx_blackhole_' in u and '_mid.webp' in u for u in requests),'default downloaded RIFE'
 fixes=pg.evaluate('''()=>{
 const N=NARAKU,setup=()=>{N.startRun(['sword','fox','mage'],3);const node=N.R.map.nodes[0].next.find(k=>N.R.map.nodes[k].type==='battle');N.go(node);if(N.mode!=='battle')throw Error('battle setup');const a=N.B.allies[0];a.m.madness=60;a.alive=false;a.hp=0;a.deadBy='hp';N.B.slots[4].card=N.STRATEGIES.find(c=>c.effect==='revive');const m=a.m;N.useCard(4,0,0);if(m.madness!==60||a.m===m||a.m.madness!==0)throw Error('revive mutated carried state');return {a,m}};
 let {a,m}=setup();N.startRewind();N.updRewind(1);N.updRewind(.8);if(N.P.members[0].madness!==60+N.CFG.rewindCost)throw Error('rewind lost original madness');
 ({a,m}=setup());win();if(m.madness!==0||a.m!==m||a.mP)throw Error('victory did not commit revival');
 ({a,m}=setup());lose('test');if(m.madness!==60)throw Error('defeat committed revival');
 const item=N.mkItem(N.rng(4),1,2);item.n=2;if(!N.itemLines(item)[0].includes('(+'))throw Error('enhancement display reverted');
 return {reviveCopy:true,rewindPreservesOriginal:true,victoryCommits:true,defeatPreservesOriginal:true,enhancementDisplay:true};
 }''')
 for w,h in [(375,667),(393,852)]:
  pg.set_viewport_size({'width':w,'height':h})
  pg.evaluate('''()=>{const N=NARAKU;N.start(['sword','fox','mage'],4242);N.sim(12);const e=N.B.enemies.find(e=>!e.dead);N.start(['sword','fox','mage'],4242);document.querySelector('#btnPause').click();N.B.enemies=[[135,245],[180,278],[225,240],[175,320]].map(([x,y],j)=>({...e,idx:900+j,x,y,hp:1000,max:1000,spd:0,st:'walk',dead:false,pend:0,tg:null,atkT:999,cd:999,flash:0,slowT:0,ph:0}));N.ULT_DEF.mage.fire(N.B.allies.find(a=>a.d.id==='mage'));N.vfx.tick(1.2);N.FX.shake=0}''')
  pg.wait_for_timeout(100);pg.locator('#arena').screenshot(path=str(out.parent/f'deployed-{w}.png'))
  assert pg.evaluate("NARAKU.FX.sh.filter(s=>s.k==='blackhole').length===2")
 assert not errors,errors
 result={'url':url,'defaults':defaults,'noDefaultMidpointRequests':True,'claudeFixes':fixes,'viewports':['375x667','393x852'],'errors':errors}
 out.write_text(json.dumps(result,indent=2)+'\n');print('DEPLOY CHECKS OK',json.dumps(result));b.close()
