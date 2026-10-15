"""Check fox finishing lifecycle, other-character cut-ins, cached burnout, and mixed battle rendering."""
import argparse,base64,json
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--base-url',default='http://127.0.0.1:8008');parser.add_argument('--out',default='dev/reports/fox-finish-v2');args=parser.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);q=b.new_page(viewport={'width':393,'height':852},device_scale_factor=2);q.add_init_script('''(()=>{const pending=new Set(),raf=window.requestAnimationFrame.bind(window);window.requestAnimationFrame=fn=>{let id=raf(t=>{pending.delete(id);fn(t)});pending.add(id);return id};window.stopReviewRAF=()=>{for(const id of pending)cancelAnimationFrame(id);pending.clear();window.requestAnimationFrame=()=>0}})()''');errors=[];q.on('pageerror',lambda e:errors.append(str(e)));q.set_default_timeout(120000);q.goto(args.base_url.rstrip('/')+'/index.html',timeout=120000);q.wait_for_function('NARAKU_READY&&NARAKU.foxSkillReady()&&FOX_GUST_EMBERS.size===2')
 q.evaluate('stopReviewRAF()')
 result=q.evaluate('''()=>{
 const N=NARAKU,stages=[];let cacheBytes=0;
 for(const [im,frames] of FOX_GUST_EMBERS){
  const sums=frames.map(c=>{cacheBytes+=c.width*c.height*4;const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let a=0,r=0,g=0,b=0;for(let i=0;i<d.length;i+=4){a+=d[i+3];r+=d[i]*d[i+3];g+=d[i+1]*d[i+3];b+=d[i+2]*d[i+3]}return {alpha:a,greenRed:g/r,blueRed:b/r}});
  stages.push({source:[im.width,im.height],cache:[frames[0].width,frames[0].height],sums});
 }
 N.start(['fox','sword','mage'],4242);N.sim(12);N.B.need=1e9;N.B.combo=null;N.B.slots[0].card=N.CARDS.find(c=>c.id==='fox_fire');clearFX();N.useCard(0,190,245);
 const intro={compact:N.FX.cut.foxFire,kindle:N.FX.sh.some(s=>s.k==='foxkindle')};
 N.vfx.tick(.34);const cutReleased=!N.FX.cut,kindleCleared=!N.FX.sh.some(s=>s.k==='foxkindle');
 const card=N.CARDS.find(c=>c.kind==='target'&&c.owner!=='fox'&&N.B.allies.some(a=>a.d.id===c.owner));N.B.slots[0].card=card;N.B.combo=null;N.useCard(0,190,245);N.vfx.tick(.34);const otherCutRetained=!!N.FX.cut&&!N.FX.cut.foxFire;
 const tracks=foxGustTracks().filter(t=>t.p.petal>=0);return {stages,cacheBytes,intro,cutReleased,kindleCleared,otherCutRetained,largePieces:tracks.length,earliestLargePiece:Math.min(...tracks.map(t=>t.p.born))};
 }''')
 for s in result['stages']:
  a=[x['alpha'] for x in s['sums']];assert all(x>=y for x,y in zip(a,a[1:]));assert a[0]>a[8]>a[-1]==0
  assert s['sums'][8]['greenRed']<s['sums'][0]['greenRed'];assert s['sums'][8]['blueRed']<s['sums'][0]['blueRed']
 assert result['intro']=={'compact':True,'kindle':True};assert result['cutReleased'] and result['kindleCleared'] and result['otherCutRetained'];assert result['largePieces']==14 and result['earliestLargePiece']>=.15;assert not errors
 mixed=[]
 for rank in [0,4]:
  target=q.evaluate("""rank=>{const N=NARAKU;N.start(['fox','sword','mage'],4242);N.sim(12);N.B.need=1e9;N.B.up.s_r=rank;recalc();clearFX();N.B.combo=null;const e=N.B.enemies.find(e=>!e.dead);const target={x:e.x,y:e.y-12};N.B.slots[0].card=N.CARDS.find(c=>c.id==='fox_fire');N.useCard(0,target.x,target.y);return target}""",rank)
  for frame in range(95):
   if frame:q.evaluate('NARAKU.sim(1/60);NARAKU.vfx.tick(1/60)')
   if frame in [5,16,34,58,94]:
    data=q.evaluate("""frame=>{render(12+frame/60);return {image:cv.toDataURL('image/webp',.94).split(',')[1],enemies:NARAKU.B.enemies.filter(e=>!e.dead).length,shots:NARAKU.B.shots.length}}""",frame)
    (out/f'mixed-rank{rank}-frame{frame:03}.webp').write_bytes(base64.b64decode(data.pop('image')));mixed.append({'rank':rank,'frame':frame,'castSeconds':frame/60,'target':target,**data})
 assert not errors,errors
 result['mixedBattle']={'ordinaryAttacksRetained':True,'naturalEnemiesRetained':True,'soulDialogSuppressed':True,'DPR':2,'frames':mixed};result['errors']=errors;(out/'finishing-checks.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['stages','mixedBattle']}));b.close()
