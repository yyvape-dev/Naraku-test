"""Capture actual cast -> impact -> tail with the skill cut-in retained."""
from pathlib import Path
import argparse,base64,json,subprocess
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--base-url',default='http://127.0.0.1:8008');parser.add_argument('--out',default='dev/reports/fox-finish-review');args=parser.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
selected={0,5,10,16,22,34,58,94};records=[]
setup="""rank=>{const N=NARAKU;N.start(['fox','sword','mage'],4242);N.sim(12);N.B.need=1e9;N.B.up.s_r=rank;recalc();const sample=N.B.enemies.find(e=>!e.dead),d=N.ENEMIES.knight;N.B.enemies=[[142,255],[190,229],[235,263]].map(([x,y],i)=>({...sample,d,type:'knight',idx:900+i,elite:false,sc:1,x,y,hp:1000,max:1000,spd:0,st:'walk',dead:false,animT:-1,flash:0,frzT:0,slowT:0,burnT:0,pend:0,tg:null,atkT:99}));for(const a of N.B.allies){a.cdT=99;a.pend=null;a.animT=-1}N.B.shots.length=0;clearFX();N.B.combo=null;N.B.sel=null;N.B.slots[0].card=N.CARDS.find(c=>c.id==='fox_fire');N.useCard(0,190,245);window.reviewCanvas=document.createElement('canvas');reviewCanvas.width=394;reviewCanvas.height=Math.ceil((cv.height+32)/2)*2;return [reviewCanvas.width,reviewCanvas.height]}"""
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);q=b.new_page(viewport={'width':393,'height':852});q.set_default_timeout(120000);q.set_default_navigation_timeout(120000);errors=[];q.on('pageerror',lambda e:errors.append(str(e)));q.add_init_script('''(()=>{const pending=new Set(),raf=window.requestAnimationFrame.bind(window);window.requestAnimationFrame=fn=>{let id=raf(t=>{pending.delete(id);fn(t)});pending.add(id);return id};window.stopReviewRAF=()=>{for(const id of pending)cancelAnimationFrame(id);pending.clear();window.requestAnimationFrame=()=>0}})()''');q.goto(args.base_url+'/index.html');q.wait_for_function('NARAKU_READY&&NARAKU.foxSkillReady()');q.evaluate('stopReviewRAF()')
 for rank in [0,4]:
  size=q.evaluate(setup,rank)
  encoder=subprocess.Popen(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','image2pipe','-framerate','60','-i','-','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out/f'rank{rank}.mp4')],stdin=subprocess.PIPE)
  for i in range(120):
   data=q.evaluate("""({i,rank})=>{const N=NARAKU;if(i){N.sim(1/60);N.vfx.tick(1/60)}render(12+i/60);const g=reviewCanvas.getContext('2d');g.fillStyle='#130e0b';g.fillRect(0,0,reviewCanvas.width,reviewCanvas.height);g.fillStyle='#eee0c8';g.font='15px sans-serif';g.fillText('発動から '+(i/60).toFixed(3)+'秒 / '+rank+'段',8,22);g.drawImage(cv,0,32,394,reviewCanvas.height-32);return {jpg:reviewCanvas.toDataURL('image/jpeg',.97).split(',')[1],cut:!!N.FX.cut,hp:N.B.enemies.map(e=>e.hp),age:N.FX.sh.find(s=>s.k==='foxskill')?.t??null}}""",{'i':i,'rank':rank})
   raw=base64.b64decode(data.pop('jpg'));encoder.stdin.write(raw)
   if i in selected:
    from PIL import Image
    from io import BytesIO
    Image.open(BytesIO(raw)).save(out/f'rank{rank}-frame{i:03}.webp',quality=95,method=4)
    records.append({'rank':rank,'frame':i,'castSeconds':i/60,**data})
  encoder.stdin.close();assert encoder.wait()==0
 assert not errors,errors;b.close()
(out/'capture.json').write_text(json.dumps({'fps':60,'seconds':2,'ranks':[0,4],'selectedFrames':records,'cutinRetained':True,'pauseOverlay':False,'manualFixedStep':True,'isolatedHealthyTargets':True,'ordinaryAttacksSuppressed':True,'soulDialogSuppressed':True,'errors':errors},indent=2));print(out)
