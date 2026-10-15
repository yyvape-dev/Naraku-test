"""Compare real game-loop CPU timings against b4ea389; not a mobile/GPU benchmark."""
from playwright.sync_api import sync_playwright
import json,statistics,subprocess
from pathlib import Path
out=Path('dev/reports/fox-finish-v3');out.mkdir(parents=True,exist_ok=True);rows=[]
before=out/'before.html';before.write_bytes(subprocess.check_output(['git','show','b4ea389:index.html']))
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for repeat in range(3):
   for version,url in [('before','dev/reports/fox-finish-v3/before.html'),('after','index.html')]:
    q=b.new_page(viewport={'width':393,'height':852},device_scale_factor=2);errors=[];q.on('pageerror',lambda e:errors.append(str(e)));q.goto('http://127.0.0.1:8008/'+url,timeout=120000);q.wait_for_function('NARAKU_READY&&NARAKU.foxSkillReady()&&FOX_GUST_EMBERS.size===2',timeout=120000)
    for rank in [0,4]:
     data=q.evaluate('''rank=>new Promise(resolve=>{
      const N=NARAKU;N.start(['fox','sword','mage'],4242);N.sim(12);N.B.need=1e9;N.B.up.s_r=rank;recalc();clearFX();N.B.combo=null;N.B.slots[0].card=N.CARDS.find(c=>c.id==='fox_fire');N.useCard(0,190,245);
      const original=render,rows=[];render=function(t){const active=N.FX.sh.some(s=>s.k==='foxskill'),start=performance.now();original(t);rows.push({time:start,cpu:performance.now()-start,active})};
      setTimeout(()=>{render=original;resolve({rows,mode:N.mode,canvas:[cv.width,cv.height],battleTime:N.B.t})},2300);
     })''',rank)
     samples=data.pop('rows');active=[s['cpu'] for s in samples if s['active']];intervals=[b['time']-a['time'] for a,b in zip(samples,samples[1:]) if a['active'] and b['active']]
     def stats(a):
      a=sorted(a);return {'count':len(a),'median':statistics.median(a),'p95':a[int((len(a)-1)*.95)],'max':max(a)} if a else None
     rows.append({'repeat':repeat,'version':version,'rank':rank,'renderMs':stats(active),'frameIntervalMs':stats(intervals),'over25ms':sum(t>25 for t in intervals),'errors':errors.copy(),**data})
    q.close()
  b.close()
 (out/'runtime-performance.json').write_text(json.dumps({'environment':'headless Chromium, cloud CPU; 393x852 DPR2; actual game requestAnimationFrame; one natural mixed cast at seed4242 t12 per case; level dialog suppressed; 3 repeats; timing excludes deferred GPU completion','cases':rows},indent=2));print(json.dumps(rows))
finally:
 before.unlink(missing_ok=True)
