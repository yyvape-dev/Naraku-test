"""Verify original-pose identity, real in-between motion, and no loop at the end."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json,sys,shutil
url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765/dev/mock/blackhole_player.html?blackholefx=godot'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=shutil.which('chromium'));pg=b.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
 pg.goto(url);pg.wait_for_function('window.NARAKU_READY&&NARAKU.vfx.blackholeSmoothReady()')
 results=pg.evaluate('''()=>{
 const N=NARAKU,canvas=document.createElement('canvas');canvas.width=canvas.height=500;const g=canvas.getContext('2d',{willReadFrequently:true});
 const sample=(layer,t,smooth)=>{g.clearRect(0,0,500,500);N.BLACKHOLE_VFX.smooth=smooth;drawBlackhole(g,{layer,t,life:3.2,x:250,y:250,w:450});return g.getImageData(0,0,500,500).data};
 const difference=(a,b)=>{let n=0,sum=0;for(let i=0;i<a.length;i++){if(a[i]!==b[i])n++;sum+=Math.abs(a[i]-b[i])}return {n,mean:sum/a.length}};
 const out={};
 for(const layer of ['floor','air']){
  const original=[];for(const f of [0,3,20,36,65,72,95]){const d=difference(sample(layer,f/30,false),sample(layer,f/30,true));if(d.n)throw Error('original pose changed '+layer+'/'+f);original.push(f)}
  const mids=[];for(const f of [20,36,65,72]){const d=difference(sample(layer,(f+.5)/30,false),sample(layer,(f+.5)/30,true));if(!d.n)throw Error('midpoint missing '+layer+'/'+f);mids.push({sourceFrame:f,...d})}
  const end=difference(sample(layer,95/30,true),sample(layer,191/60,true));if(end.n)throw Error('end loops or changes');
  const old=VT['blackhole_'+layer+'_mid'];delete VT['blackhole_'+layer+'_mid'];const fallback=difference(sample(layer,36.5/30,false),sample(layer,36.5/30,true));VT['blackhole_'+layer+'_mid']=old;
  if(fallback.n)throw Error('missing mid fallback');
  out[layer]={originalFramesExact:original,midpoints:mids,endHolds:true,missingMidFallsBack:true};
 }
 return out;
 }''')
 assert not errors,errors
 Path('dev/reports/blackhole/rife-checks.json').write_text(json.dumps({'layers':results,'errors':errors},indent=2)+'\n');print('RIFE checks OK',json.dumps(results));b.close()
