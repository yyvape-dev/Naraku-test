"""Battle UI interactions, card conservation, strategy effects and combat regression."""
import json, os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

html, before, out = sys.argv[1:4]
Path(out).mkdir(parents=True,exist_ok=True)
results={}
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h in [(390,844),(375,667)]:
        pg=b.new_page(viewport={'width':w,'height':h})
        errors=[]
        pg.on('pageerror',lambda e:errors.append(str(e)))
        pg.goto('file://'+os.path.abspath(html));pg.wait_for_function('window.NARAKU_READY')
        pg.evaluate("NARAKU.start(['sword','fox','mage'],4242);document.querySelector('#btnPause').click()")
        pg.wait_for_timeout(100)
        # Every normal card remains selectable using actual pointer input, including overlapped edges.
        for i in range(5):
            pg.evaluate("""()=>{const N=NARAKU;N.B.slots.forEach(s=>{s.card=N.CARDS.find(c=>c.id==='fox_bind')});N.B.sel=null;document.querySelector('#btnPause').click()}""")
            pg.wait_for_timeout(70)
            pg.locator(f'#hand [data-i="{i}"]').click(position={'x':35,'y':35})
            pg.wait_for_timeout(180)
            assert pg.evaluate('NARAKU.B.sel')==i, ('card blocked',w,i)
            assert pg.evaluate("document.querySelector('#cv').getBoundingClientRect().x")==0, ('field scrolled by selecting',w,i)
            r=pg.locator(f'#hand [data-i="{i}"]').bounding_box()
            assert r['x']>=0 and r['x']+r['width']<=w, ('selected card clipped',w,i,r)
            if i==2:pg.screenshot(path=f'{out}/selected-{w}x{h}.png')
            pg.click('#btnPause')
        assert not pg.locator('#btnRewind').is_visible()
        pg.evaluate("NARAKU.B.sel=null;NARAKU.B.slots[0].card=NARAKU.STRATEGIES[0];NARAKU.B.allies.forEach(a=>a.hp=a.max*.2);NARAKU.P.members.forEach((m,i)=>m.madness=[0,45,85][i]);NARAKU.FX.shake=0")
        pg.wait_for_timeout(100)
        gauges=pg.evaluate("[...document.querySelectorAll('.orb-gauges')].map(e=>[e.querySelector('.hp-ring').style.strokeDasharray,e.querySelector('.mad-ring').style.strokeDasharray])")
        assert gauges==[['20, 100','0, 100'],['20, 100','45, 100'],['20, 100','85, 100']],gauges
        pg.screenshot(path=f'{out}/gauges-{w}x{h}.png')
        heal=pg.evaluate("""()=>{const N=NARAKU,B=N.B;B.M.echo=3;B.allies[2].alive=false;B.allies[2].hp=0;const old=B.allies.map(a=>a.hp);N.useCard(0,0,0);return B.allies.map((a,i)=>a.hp-old[i])}""")
        assert heal==[63,33,0],heal
        mechanics=pg.evaluate("""()=>{
          const N=NARAKU,start=()=>N.start(['sword','fox','mage'],4242);
          const ids=()=>N.B.slots.map(s=>s.card&&s.card.id).concat(N.B.queue.map(c=>c.id)).filter(Boolean).sort().join(',');
          start();const expected=ids(),redraw=N.STRATEGIES.find(c=>c.effect==='redraw');
          const where=N.B.slots.findIndex(s=>s.card&&s.card.id===redraw.id);
          if(where<0){const q=N.B.queue.findIndex(c=>c.id===redraw.id),old=N.B.slots[0].card;N.B.slots[0].card=N.B.queue.splice(q,1)[0];N.B.queue.push(old)}
          const i=where<0?0:where;N.useCard(i,0,0);const conserved=ids()===expected,ownWait=N.B.slots[i].refill===14;
          start();const reset=N.STRATEGIES.find(c=>c.effect==='reset');N.B.slots[0].card=reset;
          const old=N.B.slots[1].card;N.B.queue.push(old);N.B.slots[1].card=null;N.B.slots[1].refill=10;
          const cd=N.B.allies.map(a=>a.cdT);N.useCard(0,0,0);
          const resetOk=!!N.B.slots[1].card&&N.B.slots[1].refill===0&&N.B.slots[0].refill===20&&JSON.stringify(cd)===JSON.stringify(N.B.allies.map(a=>a.cdT));
          const positions=Array.from({length:5},()=>new Set());let mixed=0,valid=true;
          for(let seed=1;seed<=80;seed++){
            N.start(['sword','fox','mage'],seed);
            if(N.B.slots.some(s=>s.card.category==='strategy'))mixed++;
            valid=valid&&N.B.slots.length===5&&new Set(N.B.slots.map(s=>s.card.id).concat(N.B.queue.map(c=>c.id))).size===9;
            N.B.slots.forEach((s,i)=>{if(s.card.category==='strategy')positions[i].add(s.card.id)});
          }
          return {conserved,ownWait,resetOk,mixed,valid,randomPositions:positions.map(s=>s.size)};
        }""")
        assert all(mechanics[k] for k in ['conserved','ownWait','resetOk','valid']),mechanics
        assert all(n==3 for n in mechanics['randomPositions']),mechanics
        assert not errors,errors
        results[f'{w}x{h}']={'selectable':5,'gauges':gauges,'heal':heal,'strategies':mechanics,'errors':errors}
        pg.close()
    # Invariant: unchanged combat / skill / sprite / VFX bodies (except the hand queue update).
    # For numerical comparison force the same hand and actions; hand RNG is independent of combat RNG.
    snapshots=[]
    script="""()=>{
     const N=NARAKU,out=[];
     for(const seed of [1,9,77,4242]){
      N.start(['sword','fox','mage'],seed);document.querySelector('#btnPause').click();
      for(const id of ['fox_bind','sw_rift','mg_void']){N.B.slots[0].card=N.CARDS.find(c=>c.id===id);N.useCard(0,180,240);N.sim(8)}
      N.sim(36);const B=N.B;
      out.push({seed,t:B.t,lineY:B.lineY,life:B.life,gold:B.gold,kills:B.kills,up:B.up,hp:B.allies.map(a=>a.hp),enemies:B.enemies.map(e=>[e.idx,e.x,e.y,e.hp]),stat:B.stat,zones:B.zones.map(z=>[z.x,z.t])});
     }
     return out;
    }"""
    for path in [before,html]:
        pg=b.new_page(viewport={'width':390,'height':844})
        pg.goto('file://'+os.path.abspath(path));pg.wait_for_function('window.NARAKU_READY')
        # Stabilize the legacy hand geometry before comparing subsequent battle starts.
        pg.evaluate("NARAKU.start(['sword','fox','mage'],1);document.querySelector('#btnPause').click()")
        pg.wait_for_timeout(100)
        snapshots.append(pg.evaluate(script));pg.close()
    Path(f'{out}/combat-before.json').write_text(json.dumps(snapshots[0],indent=2))
    Path(f'{out}/combat-after.json').write_text(json.dumps(snapshots[1],indent=2))
    assert snapshots[0]==snapshots[1], 'existing combat changed'
    results['combatRegression']={'seeds':4,'duration':60,'sameSkills':['fox_bind','sw_rift','mg_void'],'equal':True}
    b.close()
Path(f'{out}/checks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print('RESULT OK',json.dumps(results,ensure_ascii=False))
