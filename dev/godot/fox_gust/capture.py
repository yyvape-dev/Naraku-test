from pathlib import Path
import argparse,base64,subprocess
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser()
parser.add_argument('--base-url',default='http://127.0.0.1:8005')
parser.add_argument('--out',default='dev/reports/fox-gust/wind-fire.mp4')
args=parser.parse_args();out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
base=args.base_url.rstrip('/')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);q=b.new_page(viewport={'width':860,'height':900});errors=[];q.on('pageerror',lambda e:errors.append(str(e)));q.set_default_timeout(120000);q.set_default_navigation_timeout(120000);q.goto(base+'/dev/mock/fox_gust_demo.html');q.wait_for_function("document.querySelector('#status').textContent==='候補比較'")
 q.evaluate("replay();playing=false;window.clipCanvas=document.createElement('canvas');clipCanvas.width=786;clipCanvas.height=560")
 for enemy in ['knight','ogre','scorp']:
  q.select_option('#enemy',enemy)
  for t in ([.035,.10,.18,.30,.48,.72,1.1,1.38] if enemy=='knight' else [.15]):
   q.locator('#scrub').evaluate('(e,t)=>{e.value=t;e.dispatchEvent(new Event("input"))}',t);q.wait_for_timeout(50);q.screenshot(path=str(out.parent/f'{enemy}-{t}.png'))
 q.select_option('#enemy','knight');q.uncheck('#air');q.locator('#scrub').evaluate('(e)=>{e.value=.35;e.dispatchEvent(new Event("input"))}');q.wait_for_timeout(50);q.screenshot(path=str(out.parent/'floor-only.png'));q.check('#air');q.uncheck('#floor');q.locator('#scrub').evaluate('(e)=>{e.value=.35;e.dispatchEvent(new Event("input"))}');q.wait_for_timeout(50);q.screenshot(path=str(out.parent/'air-only.png'));q.check('#floor');q.evaluate('replay();playing=false')
 encoder=subprocess.Popen(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','image2pipe','-framerate','60','-i','-','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
 for i in range(144):
  data=q.evaluate('''i=>{if(i>0)advance(1/60);const g=clipCanvas.getContext('2d');g.fillStyle='#130e0b';g.fillRect(0,0,786,560);g.fillStyle='#eee0c8';g.font='16px sans-serif';g.fillText('前候補',12,22);g.fillText('風にほどける狐火・候補',405,22);frames.forEach((f,j)=>{f.contentWindow.eval('render(12)');g.drawImage(f.contentDocument.querySelector('#cv'),j*393,32,393,528)});return clipCanvas.toDataURL('image/jpeg',.97).split(',')[1]}''',i)
  encoder.stdin.write(base64.b64decode(data))
 encoder.stdin.close();assert encoder.wait()==0
 assert not errors,errors
 b.close()
print(out)
