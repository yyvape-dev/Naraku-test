"""Measure real maximum-range pixel density at DPR 2, using the actual renderer."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
out=Path('dev/reports/fox-sakura');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);q=b.new_page(viewport={'width':393,'height':852},device_scale_factor=2);q.set_default_timeout(120000);q.set_default_navigation_timeout(120000);errors=[];q.on('pageerror',lambda e:errors.append(str(e)));q.goto('http://127.0.0.1:8006/index.html?foxfirefx=gust');q.wait_for_function('NARAKU_READY&&NARAKU.foxSkillReady()');results=[]
 for width,height in [(375,667),(393,852),(520,900)]:
  q.set_viewport_size({'width':width,'height':height})
  for rank in [0,1,2,3,4]:
   item=q.evaluate('''rank=>{const N=NARAKU;N.start(['fox','sword','mage'],4242);N.sim(12);document.querySelector('#btnPause').click();N.QUAKE_VFX.preview=true;N.B.up.s_r=rank;recalc();N.B.slots[0].card=N.CARDS.find(c=>c.id==='fox_fire');N.useCard(0,190,245);N.sim(10/60);N.FX.cut=null;N.vfx.tick(.13);render(12);const s=N.FX.sh.find(s=>s.k==='foxskill');const need=s.w*Math.max(VSx,VSy);return {rank,scale:N.B.M.skR,radius:72*N.B.M.skR,logicalWidth:s.w,canvasPixels:[cv.width,cv.height],screenScale:[VSx,VSy],requiredPixels:need,sourcePixels:FOX_GUST_PACKED.native,scratchPixels:FOX_SKILL_MIX.width,upscale:need/FOX_GUST_PACKED.native,decodedAtlases:Object.keys(VT).filter(k=>/^(foxgust|foxsakura)/.test(k))}}''',rank)
   assert abs(item['scale']-1.25**rank)<1e-10 and item['scratchPixels']==1280,item
   if width<=393:assert item['requiredPixels']<=item['sourcePixels'],item
   assert not any('gust1' in k for k in item['decodedAtlases']),item
   item['viewport']=[width,height];results.append(item)
   if rank in [0,4]:q.screenshot(path=str(out/f'dpr2-{width}-rank{rank}.png'))
 q.close();assert not errors,errors;b.close()
result={'DPR':2,'cases':results,'errors':errors,'realPhonePerformance':'unverified'};(out/'resolution.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
