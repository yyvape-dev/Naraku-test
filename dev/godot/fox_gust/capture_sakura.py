from pathlib import Path
import argparse,base64,subprocess
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser()
parser.add_argument('--base-url',default='http://127.0.0.1:8006')
parser.add_argument('--out',default='dev/reports/fox-sakura/sakura-fire.mp4')
args=parser.parse_args();out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
base=args.base_url.rstrip('/')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);q=b.new_page(viewport={'width':860,'height':900});errors=[];q.on('pageerror',lambda e:errors.append(str(e)));q.set_default_timeout(120000);q.set_default_navigation_timeout(120000);q.goto(base+'/dev/mock/fox_sakura_demo.html');q.wait_for_function("document.querySelector('#status').textContent==='候補比較'")
 q.evaluate("replay();playing=false;window.clipCanvas=document.createElement('canvas');clipCanvas.width=786;clipCanvas.height=560")
 encoder=subprocess.Popen(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','image2pipe','-framerate','60','-i','-','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
 for rank in [0,4]:
  q.select_option('#rank',str(rank))
  for t in [.10,.18,.30,.55]:
   q.locator('#scrub').evaluate('(e,t)=>{e.value=t;e.dispatchEvent(new Event("input"))}',t);q.wait_for_timeout(70);q.screenshot(path=str(out.parent/f'rank{rank}-{t}.png'))
  q.evaluate('replay();playing=false')
  for i in range(144):
   data=q.evaluate('''({i,rank})=>{if(i>0)advance(1/60);const g=clipCanvas.getContext('2d');g.fillStyle='#130e0b';g.fillRect(0,0,786,560);g.fillStyle='#eee0c8';g.font='15px sans-serif';g.fillText('前候補・'+rank+'段',12,22);g.fillText('桜の燃焼ピーク・'+rank+'段',405,22);frames.forEach((f,j)=>{f.contentWindow.eval('render(12)');g.drawImage(f.contentDocument.querySelector('#cv'),j*393,32,393,528)});return clipCanvas.toDataURL('image/jpeg',.97).split(',')[1]}''',{'i':i,'rank':rank})
   encoder.stdin.write(base64.b64decode(data))
 encoder.stdin.close();assert encoder.wait()==0
 assert not errors,errors
 b.close()
print(out)
