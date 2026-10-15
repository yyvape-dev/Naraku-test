"""Capture the full cast in natural combat on contrasting existing backgrounds."""
import argparse,base64,json
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--base-url',default='http://127.0.0.1:8008');parser.add_argument('--out',default='dev/reports/fox-main-v2');args=parser.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);q=b.new_page(viewport={'width':393,'height':852},device_scale_factor=2);errors=[];q.on('pageerror',lambda e:errors.append(str(e)));q.add_init_script('''(()=>{const pending=new Set(),raf=window.requestAnimationFrame.bind(window);window.requestAnimationFrame=fn=>{let id=raf(t=>{pending.delete(id);fn(t)});pending.add(id);return id};window.stopReviewRAF=()=>{for(const id of pending)cancelAnimationFrame(id);pending.clear();window.requestAnimationFrame=()=>0}})()''');q.goto(args.base_url+'/index.html',timeout=120000);q.wait_for_function('NARAKU_READY&&NARAKU.foxSkillReady()',timeout=120000);q.evaluate('stopReviewRAF()');records=[]
 for bg in ['crypt','cavern']:
  for rank in [0,4]:
   setup=q.evaluate('''({bg,rank})=>{const N=NARAKU;if(!N.BG_KEYS.includes(bg))throw Error('Missing background '+bg);N.setBg(bg);N.start(['fox','sword','mage'],4242);N.sim(12);N.B.need=1e9;N.B.up.s_r=rank;recalc();clearFX();N.B.combo=null;const e=N.B.enemies.find(e=>!e.dead),target={x:e.x,y:e.y-12};N.B.slots[0].card=N.CARDS.find(c=>c.id==='fox_fire');N.useCard(0,target.x,target.y);return {background:N.B.bg,target}}''',{'bg':bg,'rank':rank})
   for f in range(95):
    if f:q.evaluate('NARAKU.sim(1/60);NARAKU.vfx.tick(1/60)')
    if f in [5,16,22,34,58,94]:
     data=q.evaluate('''f=>{render(12+f/60);return {image:cv.toDataURL('image/webp',.94).split(',')[1],alive:NARAKU.B.enemies.filter(e=>!e.dead).length}}''',f);(out/f'{bg}-rank{rank}-{f:03}.webp').write_bytes(base64.b64decode(data.pop('image')));records.append({'bg':bg,'rank':rank,'castSeconds':f/60,**setup,**data})
     if f==16:q.screenshot(path=str(out/f'{bg}-rank{rank}-full-ui.webp'),type='png')
 assert not errors,errors;b.close()
 # Playwright screenshot supports PNG/JPEG; convert only the diagnostic screenshot container.
 from PIL import Image
 for path in out.glob('*-full-ui.webp'):
  im=Image.open(path);im.save(path,format='WEBP',quality=90,method=4)
 (out/'art-context.json').write_text(json.dumps({'DPR':2,'ordinaryAttacksRetained':True,'naturalEnemiesRetained':True,'soulDialogSuppressed':True,'fixedStep':True,'cases':records,'errors':errors},indent=2));print('art context captures:',len(records))
