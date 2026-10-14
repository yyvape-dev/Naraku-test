"""Verify visual-only fox hit candidate against a served legacy/baseline build."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--base-url',default='http://127.0.0.1:8000');parser.add_argument('--baseline-url');parser.add_argument('--out',default='dev/reports/godot-fox');args=parser.parse_args()
base=args.base_url.rstrip('/');out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
script='''()=>{const N=NARAKU,results=[];for(const seed of [1,77,4242]){N.start(['fox','sword','mage'],seed);N.sim(12);N.B.slots[0].card=N.CARDS.find(c=>c.id==='fox_fire');N.useCard(0,180,200);N.sim(18);const B=N.B;results.push({seed,t:B.t,kills:B.kills,life:B.life,gold:B.gold,hp:B.allies.map(a=>a.hp),stat:B.stat,enemies:B.enemies.map(e=>[e.idx,e.hp,e.x,e.y]),slots:B.slots.map(s=>[s.card?.id,s.refill])})}return results}'''
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);errors=[];states=[]
 for url in [args.baseline_url or base+'/index.html?hitfx=legacy',base+'/index.html'+'?hitfx=godot']:
  pg=b.new_page();pg.on('pageerror',lambda e:errors.append(str(e)));pg.goto(url);pg.wait_for_function('window.NARAKU_READY');pg.wait_for_timeout(500);states.append(pg.evaluate(script));pg.close()
 assert states[0]==states[1],'combat changed'
 pg=b.new_page(viewport={'width':860,'height':900},device_scale_factor=1);pg.on('pageerror',lambda e:errors.append(str(e)))
 pg.goto(base+'/dev/mock/fox_hit_demo.html');pg.wait_for_function("document.querySelector('#status').textContent==='候補比較'");pg.click('#pause')
 for enemy in ['knight','skel','ogre','scorp']:
  pg.select_option('#enemy',enemy)
  for t in [.025,.075,.15,.55]:
   pg.locator('#scrub').evaluate('(e,t)=>{e.value=t;e.dispatchEvent(new Event("input"))}',t);pg.wait_for_timeout(70);pg.screenshot(path=str(out/f'{enemy}-{t}.png'))
 pg.select_option('#enemy','knight');pg.check('#rapid');pg.click('#pause');pg.wait_for_timeout(1500);pg.screenshot(path=str(out/'rapid.png'))
 counts=pg.evaluate("[...document.querySelectorAll('iframe')].map(f=>f.contentWindow.NARAKU.FX.sh.length)")
 pg.click('#pause');pg.uncheck('#rapid');pg.locator('#scrub').evaluate('(e)=>{e.value=.8;e.dispatchEvent(new Event("input"))}');pg.wait_for_timeout(100)
 remaining=pg.evaluate("[...document.querySelectorAll('iframe')].map(f=>f.contentWindow.NARAKU.FX.sh.filter(s=>s.k==='foximpact'||s.k==='hitreaction').length)")
 assert remaining==[0,0],remaining
 for w,h in [(375,667),(393,852)]:
  q=b.new_page(viewport={'width':w,'height':h});q.on('pageerror',lambda e:errors.append(str(e)));q.goto(base+'/index.html'+'?hitfx=godot');q.wait_for_function('window.NARAKU_READY');q.wait_for_timeout(300)
  q.evaluate("NARAKU.start(['fox','sword','mage'],4242);NARAKU.sim(12);document.querySelector('#btnPause').click();NARAKU.QUAKE_VFX.preview=true;const e=NARAKU.B.enemies.find(e=>!e.dead);e.hp=1000;NARAKU.foxPreviewHit(e);NARAKU.vfx.tick(.075)");q.wait_for_timeout(100);q.screenshot(path=str(out/f'game-{w}x{h}.png'));q.close()
 assert not errors,errors
 result={'combatEqual':True,'seeds':[1,77,4242],'durationSeconds':30,'errors':errors,'expiredEffects':remaining,'rapidEffectCounts':counts,'phoneViewports':[[375,667],[393,852]]};(out/'checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));b.close()
