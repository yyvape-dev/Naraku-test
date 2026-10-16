"""Sherry candidate vs legacy: combat, timestamps, cleanup and fallback."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,sys
url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765/dev/mock/blackhole_player.html'
out=Path('dev/reports/blackhole');out.mkdir(parents=True,exist_ok=True)
script='''()=>{const N=NARAKU,out=[];for(const seed of [1,77,4242])for(const levels of [0,4]){
 N.start(['sword','fox','mage'],seed);N.sim(8);for(let j=0;j<levels;j++)N.grant('s_r');
 N.ULT_DEF.mage.fire(N.B.allies.find(a=>a.d.id==='mage'));
 const pending=N.B.impacts.map(i=>[i.t,i.c.dmg,i.c.freeze||0,i.c.hh*N.B.M.skR]);
 for(let i=0;i<180;i++){N.sim(1/60);N.vfx.tick(1/60)}
 const B=N.B;out.push({seed,levels,pending,state:{t:B.t,life:B.life,kills:B.kills,stat:B.stat,hp:B.allies.map(a=>a.hp),enemies:B.enemies.map(e=>[e.idx,e.hp,e.x,e.y,e.frzT]),slots:B.slots.map(s=>[s.card?.id,s.refill])}});
 }return out}'''
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);results=[];errors=[]
 for variant in ['legacy','godot']:
  pg=b.new_page();pg.on('pageerror',lambda e:errors.append(str(e)));pg.goto(url+'?blackholefx='+variant)
  pg.wait_for_function('window.NARAKU_READY&&NARAKU.vfx.blackholeReady()');results.append(pg.evaluate(script));pg.close()
 assert results[0]==results[1],'combat changed'
 pg=b.new_page();pg.on('pageerror',lambda e:errors.append(str(e)));pg.goto(url+'?blackholefx=godot');pg.wait_for_function('window.NARAKU_READY&&NARAKU.vfx.blackholeReady()')
 detail=pg.evaluate('''()=>{const N=NARAKU;N.start(['sword','fox','mage'],42);N.sim(8);
 N.B.allies.forEach(a=>{a.cdT=999;a.pend=null});N.B.shots=[];N.B.impacts=[];N.B.echoes=[];
 const e=N.B.enemies.find(e=>!e.dead);Object.assign(e,{hp:10000,max:10000,x:180,y:240,spd:0,st:'walk',pend:0,atkT:999,frzT:0});N.B.enemies=[e];
 N.ULT_DEF.mage.fire(N.B.allies.find(a=>a.d.id==='mage'));const hp=e.hp;
 N.sim(2/60);if(e.hp!==hp)throw Error('early first hit');
 N.sim(2/60);if(e.hp>=hp||e.frzT<2.9)throw Error('first hit or freeze');const h=e.hp;
 N.sim(2.3);if(e.hp!==h)throw Error('early final hit');
 N.sim(.05);if(e.hp>=h)throw Error('no final hit');
 N.vfx.tick(3.19);if(N.FX.sh.filter(s=>s.k==='blackhole').length!==2)throw Error('ended early');
 N.vfx.tick(.02);if(N.FX.sh.some(s=>s.k==='blackhole'))throw Error('leaked');
 N.start(['sword','fox','mage'],42);N.ULT_DEF.mage.fire(N.B.allies[2]);N.start(['sword','fox','mage'],42);if(N.FX.sh.some(s=>s.k==='blackhole'))throw Error('reset leak');
 const img=VT.blackhole_air;delete VT.blackhole_air;N.ULT_DEF.mage.fire(N.B.allies[2]);N.sim(.1);VT.blackhole_air=img;
 if(N.FX.sh.some(s=>s.k==='blackhole')||!N.FX.sh.some(s=>s.k==='flash'))throw Error('fallback');
 N.start(['sword','fox','mage'],42);N.B.slots[0].card=N.CARDS.find(c=>c.id==='mg_void');N.useCard(0,180,240);N.sim(.2);
 if(N.FX.sh.some(s=>s.k==='blackhole'))throw Error('ordinary card changed');
 return {firstHit:.05,freeze:3,finalHit:2.4,visualLife:3.2,cleanup:true,reset:true,fallback:true,ordinaryUnchanged:true};}''')
 assert not errors,errors
 report={'sameCombat':True,'seeds':[1,77,4242],'rangeLevels':[0,4],'details':detail,'errors':errors}
 (out/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT OK',json.dumps(report));b.close()
