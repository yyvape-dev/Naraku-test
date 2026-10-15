"""Verify fox-fire skill timing, range, echoes, fallback, and visual-only changes."""
from pathlib import Path
import argparse,json
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--base-url',default='http://127.0.0.1:8006');parser.add_argument('--out',default='dev/reports/fox-sakura');args=parser.parse_args();base=args.base_url.rstrip('/');out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
combat="""()=>{const N=NARAKU,res=[];for(const seed of [1,77,4242]){N.start(['fox','sword','mage'],seed);N.sim(12);N.B.slots[0].card=N.CARDS.find(c=>c.id==='fox_fire');N.useCard(0,190,245);N.sim(18);const B=N.B;res.push({seed,t:B.t,kills:B.kills,life:B.life,gold:B.gold,hp:B.allies.map(a=>a.hp),stat:B.stat,enemies:B.enemies.map(e=>[e.idx,e.hp,e.x,e.y]),slots:B.slots.map(s=>[s.card?.id,s.refill])})}return res}"""
isolated="""()=>{const N=NARAKU,res=[];for(const echo of [0,1]){N.start(['fox','sword','mage'],4242);N.sim(12);const sample=N.B.enemies.find(e=>!e.dead);N.B.enemies=[190,277.9,278.1].map((x,i)=>({...sample,idx:900+i,type:'knight',d:N.ENEMIES.knight,x,y:261,hp:1000,max:1000,sc:1,elite:false,dead:false,spd:0,pend:0,tg:null,st:'walk',atkT:99}));for(const a of N.B.allies){a.cdT=99;a.pend=null;a.sk=1}N.B.shots.length=0;N.B.M.skR=1;N.B.M.skDmg=1;N.B.M.echo=echo;N.B.combo=null;N.FX.sh.length=0;N.B.slots[0].card=N.CARDS.find(c=>c.id==='fox_fire');N.useCard(0,190,245);const reload=N.B.slots[0].max;N.sim(9/60);const before=N.B.enemies.slice(0,3).map(e=>e.hp);const pending=N.B.impacts.length;N.sim(1/60);const hit=N.B.enemies.slice(0,3).map(e=>e.hp),layers=N.FX.sh.filter(s=>s.k==='foxskill').length;N.sim(.45);const afterEcho=N.B.enemies.slice(0,3).map(e=>e.hp);N.sim(2);N.vfx.tick(2);const remaining=N.FX.sh.filter(s=>s.k==='foxskill').length;res.push({echo,before,pending,hit,afterEcho,layers,reload,remaining})}return res}"""
range_combat=combat.replace("N.sim(12);N.B.slots", "N.sim(12);N.B.up.s_r=4;recalc();N.B.slots")
range_isolated=isolated.replace('[190,277.9,278.1]', '[190,190+72*Math.pow(1.25,4)+15.9,190+72*Math.pow(1.25,4)+16.1]').replace('N.B.M.skR=1;', 'N.B.M.skR=Math.pow(1.25,4);')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);errors=[];states=[];cases=[];range_states=[];range_cases=[]
 for mode in ['legacy','gust']:
  q=b.new_page();q.on('pageerror',lambda e:errors.append(str(e)));q.set_default_timeout(120000);q.set_default_navigation_timeout(120000);q.goto(base+'/index.html?hitfx=godot&foxfirefx='+mode);q.wait_for_function('window.NARAKU_READY');
  if mode=='gust':q.wait_for_function('NARAKU.foxSkillReady()')
  else:assert q.evaluate("!VT.foxgust_air&&!VT.foxgust_floor&&!VT.foxskill_air&&!VT.foxbloom_air"),'default loaded candidate textures'
  if mode=='gust':assert q.evaluate("!VT.foxskill_air&&!VT.foxskill_floor&&!VT.foxbloom_air&&!VT.foxbloom_floor&&!VT.foxgust1_air&&!VT.foxgust1_floor"),'unused candidate atlases decoded' 
  states.append(q.evaluate(combat));cases.append(q.evaluate(isolated));range_states.append(q.evaluate(range_combat));range_cases.append(q.evaluate(range_isolated));q.close()
 assert states[0]==states[1],'combat state changed'
 assert range_states[0]==range_states[1],'max-range combat state changed'
 for i in [0,1]:
  a=dict(range_cases[0][i]);c=dict(range_cases[1][i]);a.pop('layers');c.pop('layers');assert a==c,(a,c)
  assert c['hit']==[945,945,1000] and c['remaining']==0,c
 for i in [0,1]:
  a=dict(cases[0][i]);c=dict(cases[1][i]);a.pop('layers');c.pop('layers');assert a==c,(a,c)
  assert c['before']==[1000]*3 and c['hit']==[945,945,1000],c
  assert c['afterEcho']==([912,912,1000] if i else [945,945,1000]),c
  assert c['remaining']==0 and cases[1][i]['layers']==2,c
 q=b.new_page(viewport={'width':860,'height':900});q.on('pageerror',lambda e:errors.append(str(e)));q.set_default_timeout(120000);q.set_default_navigation_timeout(120000);q.goto(base+'/dev/mock/fox_sakura_demo.html');q.wait_for_function("document.querySelector('#status').textContent==='候補比較'");q.click('#pause')
 previewHP=q.evaluate("engines.map(N=>N.B.enemies.map(e=>e.hp))");assert previewHP==[[945]*3,[945]*3],previewHP
 for enemy in ['knight','ogre','scorp']:
  q.select_option('#enemy',enemy)
  for t in ([.035,.10,.18,.30,.48,.72,1.1,1.38] if enemy=='knight' else [.15]):
   q.locator('#scrub').evaluate('(e,t)=>{e.value=t;e.dispatchEvent(new Event("input"))}',t);q.wait_for_timeout(70);q.screenshot(path=str(out/f'{enemy}-{t}.png'))
 q.uncheck('#air');q.locator('#scrub').evaluate('(e)=>{e.value=.85;e.dispatchEvent(new Event("input"))}');q.wait_for_timeout(60);q.screenshot(path=str(out/'floor-only.png'));q.check('#air');q.uncheck('#floor');q.locator('#scrub').evaluate('(e)=>{e.value=.20;e.dispatchEvent(new Event("input"))}');q.wait_for_timeout(60);q.screenshot(path=str(out/'air-only.png'))
 q.close()
 q=b.new_page();q.on('pageerror',lambda e:errors.append(str(e)));q.set_default_timeout(120000);q.set_default_navigation_timeout(120000);q.goto(base+'/index.html?foxfirefx=gust');q.wait_for_function('window.NARAKU_READY&&NARAKU.foxSkillReady()')
 extras=q.evaluate("""()=>{const N=NARAKU;N.start(['fox','sword','mage'],4242);N.sim(12);const c=N.CARDS.find(c=>c.id==='fox_fire');N.FX.sh.length=0;impact({...c,ult:'fox'},190,245,1);const ultimateExcluded=!N.FX.sh.some(s=>s.k==='foxskill');const image=VT.foxgust_air;delete VT.foxgust_air;N.FX.sh.length=0;impact(c,190,245,1);const fallback=N.FX.sh.some(s=>s.n==='burst')&&!N.FX.sh.some(s=>s.k==='foxskill');VT.foxgust_air=image;return {ultimateExcluded,fallback,timeline:FOX_SKILL.times,frames:FOX_SKILL.frames,cols:FOX_SKILL.cols,life:FOX_SKILL.life}}""")
 assert extras['ultimateExcluded'] and extras['fallback'],extras
 meta=json.loads(Path('dev/godot/fox_gust/timeline.json').read_text());assert len(extras['timeline'])==meta['frames']==extras['frames'];assert max(abs(a-b) for a,b in zip(extras['timeline'],meta['times']))<1e-12
 q.close()
 for w,h in [(375,667),(393,852)]:
  q=b.new_page(viewport={'width':w,'height':h});q.on('pageerror',lambda e:errors.append(str(e)));q.set_default_timeout(120000);q.set_default_navigation_timeout(120000);q.goto(base+'/index.html?hitfx=godot&foxfirefx=gust');q.wait_for_function('window.NARAKU_READY&&NARAKU.foxSkillReady()');q.evaluate("NARAKU.start(['fox','sword','mage'],4242);NARAKU.sim(12);document.querySelector('#btnPause').click();NARAKU.QUAKE_VFX.preview=true;NARAKU.B.slots[0].card=NARAKU.CARDS.find(c=>c.id==='fox_fire');NARAKU.useCard(0,190,245);NARAKU.sim(10/60);NARAKU.FX.cut=null;NARAKU.vfx.tick(.10)");q.wait_for_timeout(80);q.screenshot(path=str(out/f'game-{w}x{h}.png'));q.close()
 assert not errors,errors
 result={'combatEqual':True,'maxRangeCombatEqual':True,'maxRangeIsolatedCases':range_cases[1],'seeds':[1,77,4242],'durationSeconds':30,'isolatedCases':cases[1],'previewHP':previewHP,'ultimateExcluded':extras['ultimateExcluded'],'missingAtlasFallback':extras['fallback'],'metadataMatches':True,'legacyDoesNotDecodeSkillAtlases':True,'errors':errors,'phoneViewports':[[375,667],[393,852]]};(out/'checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));b.close()
