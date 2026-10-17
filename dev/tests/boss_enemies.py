"""Boss/elite classification, scheduled spawns, eight-frame combat and fallback."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765/index.html'
OUT=Path(__file__).resolve().parents[1]/'reports/bosses';OUT.mkdir(parents=True,exist_ok=True)
IDS=['violet_knight','frill_dragon','sixarm_minotaur','crimson_succubus','blue_cyclops']
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':393,'height':852});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('response',lambda r:errors.append(str(r.status)+' '+r.url) if r.status>=400 else None)
 page.route('**/favicon.ico',lambda r:r.fulfill(status=204))
 page.goto(URL);page.wait_for_function('window.NARAKU_READY===true',timeout=60000)
 result=page.evaluate('''ids=>{
 const N=NARAKU,assert=(c,m)=>{if(!c)throw Error(m)},frames={};
 N.start(['fox','sword','mage'],777);
 for(const id of ids){const d=N.ENEMIES[id],s=N.SPR.enemy[id];
  assert(s.real&&s.frames.length===8&&s.refH>=400,id+' atlas');
  assert(id==='crimson_succubus'?d.elite&&!d.boss:!!d.boss&&!d.elite,id+' class');
  const e={d,type:id,motionT:0,animT:-1,ph:0,st:'walk'},w=new Set(),a=new Set();
  for(let i=0;i<100;i++){e.motionT=i*.03;w.add(N.enemyFrame(e));a.add(N.enemyAttackFrame(id,i/100))}
  assert([...w].sort().join()==='0,1,2,3'&&[...a].sort().join()==='4,5,6,7',id+' phases');
  assert(N.enemyAttackFrame(id,.5)===5,id+' hit frame');
  const base=N.ENEMIES[d.boss?'scorp':'ogre'];
  for(const k of ['hp','spd','dmg','cd','life','soul'])assert(d[k]===base[k],id+' '+k);
  const h=d.h*(N.TUNE[id]?.s||100)/100,bh=base.h*(N.TUNE[d.boss?'scorp':'ogre']?.s||100)/100;
  assert(h>bh&&h<bh*1.2,id+' display scale');
  frames[id]={class:d.boss?'boss':'elite',walk:[...w],attack:[...a],refH:s.refH,height:h};
 }
 assert(!N.ENCOUNTERS.boss.includes('crimson_succubus')&&N.ENCOUNTERS.elite.includes('crimson_succubus'),'succubus pool');
 const counts={boss:{},elite:{}};
 for(const kind of ['boss','elite'])for(let seed=1;seed<=50;seed++){
  N.start(['fox','sword','mage'],seed);const B=N.B;B.enemies.length=0;B.acc=-9999;B.nextWave=9999;B.allies.forEach(a=>a.cdT=9999);
  const time=kind==='boss'?N.CFG.bossAt:B.nextElite,index=0,expected=N.encounterType(kind,index);
  if(kind==='boss')B.nextElite=9999;else B.hasBoss=false;
  B.t=time/B.ts-.1;N.sim(.05);assert(B.enemies.length===0,kind+' early');
  B.t=time/B.ts;N.sim(1/60);assert(B.enemies.length===1&&B.enemies[0].type===expected,kind+' scheduled');
  N.sim(.1);assert(B.enemies.length===1,kind+' duplicate');counts[kind][expected]=(counts[kind][expected]||0)+1;
  const once=expected;N.start(['fox','sword','mage'],seed);assert(once===N.encounterType(kind,index),'deterministic '+kind);
 }
 assert(Object.keys(counts.boss).length===5&&Object.keys(counts.elite).length===2,'all variants reachable');
 N.start(['fox','sword','mage'],1);
 for(let i=0;i<100;i++){const t=N.pickType(90);assert(!ids.includes(t),'special in normal pool');N.spawn(t)}
 for(const id of ids.filter(id=>id!=='crimson_succubus')){
  N.start(['fox','sword','mage'],3);const B=N.B;B.enemies.length=0;B.acc=-9999;B.nextWave=B.nextElite=9999;B.hasBoss=false;B.allies.forEach(a=>a.cdT=9999);
  N.spawn(id);const e=B.enemies[0],t=B.allies[0];e.x=t.x;e.y=B.lineY+e.stopOff;e.st='engage';e.tg=t;e.atkT=0;
  const hp=t.hp;N.sim(.2);assert(t.hp===hp,id+' early damage');N.sim(.1);assert(t.hp<hp,id+' hit');
  const fr=N.enemyFrame(e),clock=e.motionT,anim=e.animT;e.frzT=1;N.sim(.2);assert(N.enemyFrame(e)===fr&&e.motionT===clock&&e.animT===anim,id+' frozen');
  const drop=N.dropFor(1,0,true,0,true);assert(drop.gear&&drop.gear.r>=2,id+' boss reward');
 }
 N.start(['fox','sword','mage'],4);const B=N.B;B.enemies.length=0;B.acc=-9999;B.nextWave=B.nextElite=9999;B.hasBoss=false;B.allies.forEach(a=>a.cdT=9999);
 N.spawn('crimson_succubus');const e=B.enemies[0];e.y=B.lineY+e.stopOff;e.atkT=0;
 N.sim(.2);assert(e.castTarget&&B.shots.length===0,'succubus windup');N.sim(.1);assert(!e.castTarget&&B.shots.some(s=>s.from===0),'succubus spell');
 assert(e.elite&&!e.d.boss&&e.d.life===3&&e.d.soul===10,'succubus elite rewards');
 return {frames,scheduledSpawns:counts,meleeHits:true,freeze:true,succubusCast:true,deterministic:true};
 }''',IDS)
 for id in ['scorp',*IDS]:
  page.evaluate('''id=>{const N=NARAKU;N.start(['fox','sword','mage'],777);const B=N.B;B.enemies.length=0;N.FX.banner=null;N.QUAKE_VFX.preview=true;N.spawn(id);const e=B.enemies[0];e.x=180;e.y=B.lineY-130;e.hp=e.max*.85;}''',id)
  page.click('#btnPause')
  for w,h in [(393,852),(375,667)]:
   page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(100);page.screenshot(path=str(OUT/f'{id}-{w}.png'))
  if id=='crimson_succubus':
   for i,t in enumerate([0,.25,.32,.45]):
    page.evaluate('t=>NARAKU.B.enemies[0].animT=t',t);page.wait_for_timeout(80);page.screenshot(path=str(OUT/f'succubus-attack-{i+1}.png'))
 fallback=b.new_page();fallback.route('**/violet_knight.webp*',lambda r:r.abort());fallback.goto(URL);fallback.wait_for_function('window.NARAKU_READY===true',timeout=60000)
 assert fallback.evaluate("()=>{const N=NARAKU;N.start(['fox','sword','mage'],1);N.spawn('violet_knight');N.sim(1);return !N.SPR.enemy.violet_knight.real&&[0,.25,.5,.99].every(t=>N.enemyAttackFrame('violet_knight',t)<6)}")
 result['fallback']=True;result['errors']=errors;assert not errors,errors
 (OUT/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False));b.close()
