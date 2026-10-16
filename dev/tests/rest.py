"""HTTP版の焚き火4種・回復・保存再開・スマホ操作を確認する。"""
import json, shutil, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765/index.html'
out=Path(sys.argv[2] if len(sys.argv)>2 else 'dev/reports/rest')
out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=shutil.which('chromium'))
    pg=b.new_page(viewport={'width':393,'height':852},has_touch=True,is_mobile=True)
    errors=[]
    pg.on('pageerror',lambda e:errors.append(str(e)))
    pg.route('**/favicon.ico',lambda r:r.fulfill(status=204))
    pg.goto(url);pg.wait_for_function('window.NARAKU_READY')
    counts=pg.evaluate('''()=>{const c={};for(let seed=0;seed<100000;seed++){const k=restArt({seed});c[k]=(c[k]||0)+1}return c}''')
    for k,v in counts.items():
        assert abs(v/100000-(.05 if 'house' in k else .45))<.005,counts
    cases=pg.evaluate('''()=>{const found={};for(let seed=1;seed<300;seed++){
      const m=NARAKU.genMap(seed,1);for(const n of m.nodes){if(n.type!=='rest')continue;const k=restArt(n);if(!found[k])found[k]={seed,id:n.id}}
      if(Object.keys(found).length===4)break}return found}''')
    assert len(cases)==4,cases
    results=[]
    for w,h in [(375,667),(393,852)]:
        pg.set_viewport_size({'width':w,'height':h})
        for key,c in cases.items():
            rare='house' in key
            pg.evaluate('''c=>{NARAKU.startRun(['sword','fox','mage'],c.seed);R.at=c.id;R.seen[c.id]=true;
              P.members.forEach(m=>{m.hpR=.2;m.madness=73});saveRun();openNode(R.map.nodes[c.id])}''',c)
            pg.wait_for_function('document.querySelector(".bones-art img")?.naturalWidth===1280')
            assert key in pg.locator('.bones-art img').get_attribute('src')
            assert pg.evaluate('P.members.every(m=>m.hpR===1&&m.madness===0)') if rare else pg.evaluate('P.members.every(m=>m.hpR===.2&&m.madness===73)')
            if not rare:
                # 未選択の保存再開でも絵は同じ。選択後も同じ挿絵を維持する。
                pg.evaluate('()=>{const snapshot=saveText();R=null;S=fixSave(JSON.parse(snapshot));resumeRun()}')
                assert key in pg.locator('.bones-art img').get_attribute('src')
                pg.wait_for_timeout(300) # 既存の250ms誤タップ防止
                pg.locator('[data-opt="0"]').tap()
                assert pg.evaluate('P.members.every(m=>Math.abs(m.hpR-.6)<1e-8&&m.madness===73)'), pg.evaluate('({phase:R.node.phase,members:P.members,save:S.run})')
                assert not pg.evaluate('chooseNode(1)'), 'double reward'
            pg.screenshot(path=str(out/f'{key}-{w}.png'))
            pg.wait_for_timeout(300)
            pg.locator('[data-act="leave"]').tap()
            assert pg.evaluate('mode==="map"')
            # 休息済みの再開では回復を繰り返さない。
            pg.evaluate('()=>{P.members[0].hpR=.31;P.members[0].madness=42;saveRun();const snapshot=saveText();R=null;S=fixSave(JSON.parse(snapshot));resumeRun()}')
            assert pg.evaluate('mode==="map"&&P.members[0].hpR===.31&&P.members[0].madness===42')
            results.append({'art':key,'width':w,'effects':True,'resume':True,'touch':True})
    # 通常の「心を鎮める」も従来どおり。
    c=cases['rest_1']
    pg.evaluate('''c=>{NARAKU.startRun(['sword','fox','mage'],c.seed);R.at=c.id;P.members.forEach(m=>{m.hpR=.2;m.madness=73});openNode(R.map.nodes[c.id]);chooseNode(1)}''',c)
    assert pg.evaluate('P.members.every(m=>m.hpR===.2&&m.madness===53)')
    assert not errors,errors
    data={'counts100000':counts,'cases':cases,'checks':results,'errors':errors}
    (out/'checks.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print('REST OK',json.dumps(data,ensure_ascii=False));b.close()
