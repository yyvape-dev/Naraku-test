"""Check temporal continuity and avoid the alpha/luminance dip of double fades."""
from pathlib import Path
import argparse,json
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--base-url',default='http://127.0.0.1:8005');parser.add_argument('--out',default='dev/reports/fox-gust/continuity.json');args=parser.parse_args()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pg=b.new_page();pg.set_default_timeout(120000);pg.set_default_navigation_timeout(120000);pg.goto(args.base_url+'/index.html?foxfirefx=gust');pg.wait_for_function('window.NARAKU_READY&&NARAKU.foxSkillReady()')
 result=pg.evaluate('''async()=>{
  const c=document.createElement('canvas');c.width=c.height=256;const g=c.getContext('2d',{willReadFrequently:true});
  function snap(t){g.clearRect(0,0,256,256);drawFoxSkill(g,{layer:'air',x:95,y:115,angle:0,w:106,t});return g.getImageData(0,0,256,256).data}
  function delta(a,b){let d=0;for(let i=0;i<a.length;i++)d+=Math.abs(a[i]-b[i]);return d}
  const newDelta=delta(snap(.105),snap(.11));
  const timeline=FOX_SKILL.times.slice();
  const original=VT.foxgust_air,flat=document.createElement('canvas');flat.width=1792;flat.height=2016;const f=flat.getContext('2d');f.fillStyle='rgba(230,100,30,.5)';f.fillRect(0,0,1792,2016);
  const im=new Image();im.src=flat.toDataURL();await im.decode();VT.foxgust_air=im;
  const start=Array.from(snap(0).slice((100*256+95)*4,(100*256+95)*4+4));
  const mid=Array.from(snap(1/120).slice((100*256+95)*4,(100*256+95)*4+4));
  VT.foxgust_air=original;
  const last=Array.from(snap(1.399));const endAlpha=last.filter((_,i)=>i%4===3).reduce((a,b)=>a+b,0);
  return {newInterpolatedFrameDelta:newDelta,constantFlameStart:start,constantFlameMidpoint:mid,frameCount:timeline.length,maxInitialStep:Math.max(...timeline.slice(1,18).map((t,i)=>t-timeline[i])),endAlpha};
 }''')
 assert result['newInterpolatedFrameDelta']>0,result
 assert all(abs(a-b)<=1 for a,b in zip(result['constantFlameStart'],result['constantFlameMidpoint'])),result
 assert result['frameCount']==57 and result['maxInitialStep']<.016667,result
 assert result['endAlpha']==0,result
 b.close()
out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2));print(json.dumps(result))
