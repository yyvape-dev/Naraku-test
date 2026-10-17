"""HTTP regression: five new normal enemies, split animation, combat and rewind."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765/index.html'
OUT=Path(__file__).resolve().parents[1]/'reports/enemies';OUT.mkdir(parents=True,exist_ok=True)
IDS=['relic_dead','chain_brute','hook_goblin','twin_orc','veil_ghost']
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':393,'height':852},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:errors.append(f'{r.status} {r.url}') if r.status>=400 else None)
    page.route('**/favicon.ico',lambda r:r.fulfill(status=204))
    page.goto(URL);page.wait_for_function('window.NARAKU && Object.values(NARAKU.SPR.enemy).every(s=>s.real)',timeout=60000)
    result=page.evaluate('''ids=>{
      const N=NARAKU,assert=(ok,msg)=>{if(!ok)throw Error(msg)};
      N.start(['fox','sword','mage'],4242);
      const frames={};
      for(const id of ids){
        const set=N.SPR.enemy[id],d=N.ENEMIES[id];
        assert(set.real&&set.frames.length===8,id+' atlas');
        assert(set.refH>=400&&set.frames[0].c.width===576,id+' native high resolution');
        assert(!d.elite&&!d.boss,id+' normal');
        const e={type:id,d,st:'walk',ph:0,animT:-1,motionT:0};
        const walk=new Set(),attack=new Set();
        for(let i=0;i<100;i++){e.motionT=i*.025;walk.add(N.enemyFrame(e));attack.add(N.enemyAttackFrame(id,i/100))}
        assert([...walk].sort().join()==='0,1,2,3',id+' walk');
        assert([...attack].sort().join()==='4,5,6,7',id+' attack');
        assert(N.enemyAttackFrame(id,.5)===5,id+' strike synchronized');
        e.st='cast';assert(N.enemyFrame(e)===(d.float?Math.floor(e.motionT*d.walkFps)%4:0),id+' idle');
        frames[id]={walk:[...walk],attack:[...attack],height:d.h,refH:set.refH};
      }
      const run=()=>{N.start(['fox','sword','mage'],8181);N.B.enemies.length=0;N.B.allies.forEach(a=>a.cdT=9999);
        for(let i=0;i<400;i++){const type=N.pickType(90);N.spawn(type)}
        return N.B.enemies.map(e=>[e.type,e.x,e.hp])};
      const a=run(),b=run();assert(JSON.stringify(a)===JSON.stringify(b),'deterministic spawns');
      assert(ids.every(id=>a.some(e=>e[0]===id)),'all five naturally selected');
      // Stop spawner and allies, isolate a melee enemy at its attack line.
      N.start(['fox','sword','mage'],4242);const B=N.B;B.enemies.length=0;B.acc=-999;B.nextWave=B.nextElite=9999;B.allies.forEach(a=>a.cdT=9999);
      N.spawn(ids[0]);const e=B.enemies[0],target=B.allies[0];e.x=target.x;e.y=B.lineY+e.stopOff;e.st='engage';e.tg=target;e.atkT=0;
      const hp=target.hp;N.sim(.2);assert(target.hp===hp,'melee does not hit early');N.sim(.1);assert(target.hp<hp,'melee hit');
      e.frzT=1;const before=[e.y,e.motionT,e.animT,N.enemyFrame(e)];N.sim(.2);
      assert(before.every((v,i)=>v===[e.y,e.motionT,e.animT,N.enemyFrame(e)][i]),'frozen animation and position');
      // Floating caster releases its projectile on the attack strike, not anticipation.
      N.start(['fox','sword','mage'],4242);const C=N.B;C.enemies.length=0;C.acc=-999;C.nextWave=C.nextElite=9999;C.allies.forEach(a=>a.cdT=9999);
      N.spawn('veil_ghost');const ghost=C.enemies[0];ghost.x=180;ghost.y=C.lineY+ghost.stopOff;ghost.atkT=0;
      N.sim(.2);assert(ghost.castTarget&&C.shots.length===0,'ghost windup');
      N.sim(.1);assert(!ghost.castTarget&&C.shots.some(s=>s.from===0),'ghost release');
      // Real battlefield, all five and an existing enemy side by side.
      N.start(['fox','sword','mage'],777);const D=N.B;N.QUAKE_VFX.preview=true;N.FX.banner=null;D.enemies.length=0;D.acc=-999;D.nextWave=D.nextElite=9999;
      ['skel',...ids].forEach((id,i)=>{N.spawn(id);const e=D.enemies.at(-1);e.x=64+(i%3)*115;e.y=170+Math.floor(i/3)*140;e.atkT=9999});
      return {frames,spawnCounts:a.reduce((o,e)=>(o[e[0]]=(o[e[0]]||0)+1,o),{}),meleeHit:true,frozen:true,ghostRelease:true};
    }''',IDS)
    page.click('#btnPause')
    for width,height in [(393,852),(375,667)]:
        page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(200)
        page.screenshot(path=str(OUT/f'battle-{width}.png'))
    # Force each of the four attack poses to be drawn in the engine.
    for frame,t in enumerate([0,.25,.32,.45]):
        page.evaluate('(t)=>{NARAKU.B.enemies.forEach(e=>{if(e.d.splitMotion)e.animT=t})}',t)
        page.wait_for_timeout(100);page.screenshot(path=str(OUT/f'attack-{frame+1}.png'))
    # Missing one new atlas must still boot and use the existing six-frame fallback.
    fallback=browser.new_page()
    fallback.route('**/veil_ghost.webp*',lambda r:r.abort())
    fallback.goto(URL);fallback.wait_for_function('window.NARAKU_READY===true',timeout=60000)
    result['fallback']=fallback.evaluate('''()=>{const N=NARAKU;N.start(['fox','sword','mage'],2);N.spawn('veil_ghost');const set=N.SPR.enemy.veil_ghost;const frames=[0,.25,.5,.75,.99].map(u=>N.enemyAttackFrame('veil_ghost',u));N.sim(2);return !set.real&&set.frames.length===6&&frames.every(f=>f>=0&&f<6)}''')
    assert result['fallback']
    fallback.close()
    assert not errors,errors
    result['errors']=errors
    (OUT/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False));browser.close()
