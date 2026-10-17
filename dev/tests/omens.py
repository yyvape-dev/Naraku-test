"""Explore omen persistence, migration, damage paths, rewards, map weights and UI.
Usage: python dev/tests/omens.py http://127.0.0.1:8950/index.html [report-dir]
"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

out=Path(sys.argv[2] if len(sys.argv)>2 else '/tmp/omen-checks')
out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch()
    page=b.new_page(viewport={'width':375,'height':812})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(sys.argv[1]);page.wait_for_function('window.NARAKU_READY')
    initial=page.evaluate('({omen:NARAKU.S.omen,seed:NARAKU.S.omenSeed})')
    page.reload();page.wait_for_function('window.NARAKU_READY')
    assert page.evaluate('({omen:NARAKU.S.omen,seed:NARAKU.S.omenSeed})')==initial
    result=page.evaluate("""()=>{
      const N=NARAKU,O=N.omens,out={},check=(k,v)=>out[k]=!!v;
      const ready=(anomaly='none')=>{
        N.start(['sword','mage','fox'],42,{anomaly});N.B.enemies.length=0;N.spawn('skel');
        const e=N.B.enemies[0];e.x=180;e.y=160;e.hp=e.max=100000;
        N.B.allies.forEach(a=>{a.M.crit=0;a.M.burn=0;a.M.chill=0;a.M.knock=0});return e;
      };
      // Normal attacks, skills, ult-style cloned cards, burn ticks and zones all use hurt.
      const atk=(a,id)=>{const e=ready(a),unit=N.B.allies.find(q=>q.d.id===id);const hp=e.hp;O.hitFrom(unit,e,1);return hp-e.hp};
      check('physical_normal_30pct',Math.abs(atk('steel','sword')/atk('none','sword')-.7)<1e-8);
      check('magic_normal_30pct',Math.abs(atk('seal','mage')/atk('none','mage')-.7)<1e-8);
      check('opposite_attribute_unchanged',atk('steel','mage')===atk('none','mage')&&atk('seal','sword')===atk('none','sword'));
      const skill=(a,id,ult=false)=>{const e=ready(a),c={...N.CARDS.find(c=>c.id===id)};delete c.zone;
        if(ult){c.ult=c.owner;c.dmg=140}const hp=e.hp;O.impact(c,e.x,e.y-16,1);return hp-e.hp};
      check('physical_skills_and_ult',Math.abs(skill('steel','sw_quake')/skill('none','sw_quake')-.7)<1e-8&&Math.abs(skill('steel','sw_rift',true)/skill('none','sw_rift',true)-.7)<1e-8);
      check('skills_use_caster_attribute',Math.abs(skill('seal','mg_inferno')/skill('none','mg_inferno')-.7)<1e-8&&Math.abs(skill('steel','fox_fire')/skill('none','fox_fire')-.7)<1e-8&&skill('seal','fox_fire')===skill('none','fox_fire')&&Math.abs(skill('steel','fox_bind')/skill('none','fox_bind')-.7)<1e-8&&Math.abs(skill('steel','fox_fire',true)/skill('none','fox_fire',true)-.7)<1e-8);
      const ticks=(anomaly,zone)=>{const e=ready(anomaly);N.B.allies.forEach(a=>a.cdT=999);e.spd=0;
        if(zone)N.B.zones.push({x:e.x,hw:100,t:3,life:3,tick:.001,dps:40,c:N.CARDS.find(c=>c.id==='sw_rift')});
        else{e.burnT=3;e.burnTick=.001;e.burnDps=40;e.burnBy='sword'}
        const hp=e.hp;N.sim(1/60);return hp-e.hp};
      check('burn_uses_caster_attribute_once',Math.abs(ticks('steel',false)/ticks('none',false)-.7)<1e-8&&ticks('seal',false)===ticks('none',false));
      check('zone_physical_once',Math.abs(ticks('steel',true)/ticks('none',true)-.7)<1e-8);
      let e=ready('whispers');N.B.allies[0].m.madness=80;const hp=e.hp;O.hurt(e,100,'#fff',false,true,'sword','atk');
      check('madness_bonus',Math.abs(hp-e.hp-140)<1e-8);
      e=ready('undead');e.hp=e.max=100;const before=[N.B.soul,N.B.gold,N.B.kills,N.B.loot.length];
      O.hurt(e,9999,'#fff',false,true,'sword','atk');check('revive_once_no_reward',!e.dead&&e.hp===35&&e.revived&&JSON.stringify(before)===JSON.stringify([N.B.soul,N.B.gold,N.B.kills,N.B.loot.length]));
      O.hurt(e,9999,'#fff',false,true,'sword','atk');check('final_kill_one_reward',e.dead&&N.B.kills===1&&N.B.soul>0);
      const after=N.B.soul;O.hurt(e,9999,'#fff',false,true,'sword','atk');check('no_duplicate_reward',N.B.soul===after&&N.B.kills===1);
      const spawn=(anomaly,type='skel')=>{N.start(['sword'],10,{anomaly});N.spawn(type);const e=N.B.enemies[0];return [e.max,e.d.dmg]};
      const base=spawn('none'),swarm=spawn('swarm'),giant=spawn('giants');
      check('normal_enemy_modifiers',swarm[0]===base[0]*.75&&giant[0]===base[0]*1.5&&giant[1]===base[1]*1.25&&N.ENEMIES.skel.dmg===base[1]);
      check('boss_and_elite_unchanged',JSON.stringify(spawn('none','ogre'))===JSON.stringify(spawn('giants','ogre'))&&JSON.stringify(spawn('none','scorp'))===JSON.stringify(spawn('swarm','scorp')));
      const count=anomaly=>{N.start(['sword'],10,{anomaly});N.B.allies[0].cdT=999;N.sim(15);return N.B.idx};
      const counts=[count('giants'),count('none'),count('swarm')];check('spawn_counts',counts[0]<counts[1]&&counts[1]<counts[2]);out.spawnCounts=counts;
      const maps={none:{chest:0,elite:0},treasure:{chest:0,elite:0}};
      for(const kind of Object.keys(maps))for(let seed=0;seed<200;seed++){const m=N.genMap(seed,kind);for(const n of m.nodes)if(n.type in maps[kind])maps[kind][n.type]++}
      check('treasure_map_weights',maps.treasure.chest>maps.none.chest&&maps.treasure.elite>maps.none.elite);out.mapCounts=maps;
      let s=N.fresh();s.omen='steel';s.floorMax=2;const announced=s.omen;N.town.floor(1);N.town.pick('fox');N.town.pick('fox');check('town_choices_keep_omen',s.omen===announced);
      N.sortie(123);check('run_snapshot',N.R.anomaly==='steel'&&s.run.anomaly==='steel');
      const serialized=JSON.parse(N.saveText()),fixed=N.fixSave(serialized);check('save_snapshot',fixed.omen==='steel'&&fixed.run.anomaly==='steel');
      const old=JSON.parse(N.saveText());delete old.omen;delete old.omenSeed;delete old.run.anomaly;const legacy=N.fixSave(old);check('legacy_active_run_is_normal',legacy.omen==='none'&&legacy.run.anomaly==='none');
      const invalid=JSON.parse(N.saveText());invalid.omen='<script>';invalid.run.anomaly='constructor';const clean=N.fixSave(invalid);check('invalid_keys_sanitized',clean.omen==='none'&&clean.run.anomaly==='none');
      N.S.omen='seal';const bt=N.R.map.nodes[0].next.find(k=>N.R.map.nodes[k].type==='battle');N.go(bt);
      check('battle_uses_frozen_omen',N.B.anomaly==='steel');N.startRewind();N.updRewind(1);N.updRewind(.8);check('rewind_preserves_omen',N.B.anomaly==='steel');
      N.startRun(['fox','sword','mage'],123,1,'seal');const runOmen=N.R.anomaly;N.retreat();const next=N.S.omen;
      check('return_rolls_next',next===O.roll(N.S.omenSeed,N.S.runs,runOmen)&&next!==runOmen&&N.S.run===null);
      check('all_outcomes_drawable',new Set(Array.from({length:500},(_,i)=>O.roll(i,0))).size===Object.keys(O.table).length);
      // Actual reload with an active treasure map; keep the production save switch off.
      N.startRun(['fox','sword','mage'],9876,1,'treasure');
      localStorage.setItem('naraku_save_v1',N.saveText());out.resumeMap=JSON.stringify(N.R.map);
      return out;
    }""")
    expected=result.pop('resumeMap')
    assert all(v for v in result.values() if isinstance(v,bool)),result
    page.reload();page.wait_for_function('window.NARAKU_READY');page.click('[data-act=resume]')
    assert page.evaluate('NARAKU.R.anomaly')=='treasure'
    assert page.evaluate('JSON.stringify(NARAKU.R.map)')==expected
    # New upcoming rumor and its direct party link are usable on small screens.
    page.evaluate("NARAKU.fresh();NARAKU.S.omen='steel';NARAKU.town.show()")
    for width,height in [(375,812),(390,844)]:
        page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(150)
        assert page.locator('#hubDive').is_visible()
        page.screenshot(path=str(out/f'town-{width}.png'))
    page.locator('.omen-notice summary').click();page.wait_for_timeout(150)
    page.screenshot(path=str(out/'rumor-open.png'))
    page.locator('.omen-notice [data-go=party]').click()
    assert page.locator('#fac').is_visible()
    assert not errors,errors
    result['reload_resume_map_exact']=True;result['errors']=errors
    (out/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
    b.close()
