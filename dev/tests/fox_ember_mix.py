"""Check premultiplied ember interpolation against a single source-over composite."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--base-url',default='http://127.0.0.1:8008');parser.add_argument('--out',default='dev/reports/fox-finish-v3/ember-mix.json');args=parser.parse_args()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);q=b.new_page();errors=[];q.on('pageerror',lambda e:errors.append(str(e)));q.goto(args.base_url+'/index.html',timeout=120000);q.wait_for_function('NARAKU_READY&&NARAKU.foxSkillReady()&&FOX_GUST_EMBERS.size===2',timeout=120000)
 result=q.evaluate('''()=>{
 const c=document.createElement('canvas');c.width=c.height=16;const g=c.getContext('2d');
 const source=(color)=>{const c=document.createElement('canvas');c.width=c.height=16;const g=c.getContext('2d');g.fillStyle=color;g.fillRect(0,0,16,16);return c};
 const a=source('rgba(230,100,30,.5)'),b=source('rgba(100,20,0,.25)'),same=[a,a],different=[a,b],results=[];
 for(const bg of ['#000000','#604830','#ffffff'])for(const alpha of [1,.4]){
  const snap=im=>{g.globalAlpha=1;g.fillStyle=bg;g.fillRect(0,0,16,16);g.globalAlpha=alpha;g.drawImage(im,0,0);return [...g.getImageData(8,8,1,1).data]};
  const expected=snap(a),samples=[0,.25,.5,.75,1].map(t=>snap(foxEmberMix(same,t)));
  const actual=snap(foxEmberMix(different,.5));
  // Independent straight-alpha prediction, allowing byte quantization.
  const da=a.getContext('2d').getImageData(0,0,1,1).data,db=b.getContext('2d').getImageData(0,0,1,1).data;
  g.globalAlpha=1;g.fillStyle=bg;g.fillRect(0,0,16,16);const base=g.getImageData(8,8,1,1).data;
  const opacity=(da[3]+db[3])/510*alpha;
  const predicted=[0,1,2].map(k=>Math.round(base[k]*(1-opacity)+alpha*(da[k]*da[3]+db[k]*db[3])/510));
  results.push({bg,alpha,expected,samples,actual,predicted});
 }
 const caches=[...FOX_GUST_EMBERS.values()].map(frames=>{
  const samples=[0,.1,.5,.95,1].map(t=>{const c=foxEmberMix(frames,t),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let alpha=0;for(let i=3;i<d.length;i+=4)alpha+=d[i];return alpha});
  const first=foxEmberMix(frames,.2),reused=first===foxEmberMix(frames,.3);return {samples,reused,bytes:first.width*first.height*4};
 });
 const atlas=foxSkillAtlas('air');FOX_GUST_PRIMED.delete(atlas);
 const waitsForPrime=!foxSkillReady();const fallback=!fxFoxSkill(190,245,72);
 FOX_GUST_PRIMED.add(atlas);const readyAfterPrime=foxSkillReady();
 return {results,caches,waitsForPrime,fallback,readyAfterPrime};
 }''')
 for r in result['results']:
  assert all(all(abs(a-b)<=1 for a,b in zip(s,r['expected'])) for s in r['samples']),r
  assert all(abs(a-b)<=2 for a,b in zip(r['actual'][:3],r['predicted'])),r
 for c in result['caches']:
  assert c['reused'] and c['samples'][-1]==0 and all(a+c['bytes']/4>=b for a,b in zip(c['samples'],c['samples'][1:])),c
 assert result['waitsForPrime'] and result['fallback'] and result['readyAfterPrime'],result
 assert not errors,errors
 result['errors']=errors;b.close()
 out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2));print(json.dumps(result))
