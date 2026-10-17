"""聖母の加護（マリアンヌの超必殺・15秒の聖域）の確認。
使い方: python3 dev/tests/sister_sanct.py http://127.0.0.1:8765/index.html [撮影の保存先フォルダ]
確認：入りの10%回復／発動中だけ 攻撃速度1.4倍・攻撃回数+1・射程1.25倍・継続回復・敵の移動0.6倍／15秒で元に戻る／
      再発動で延長／逆転の右手（作り直し）で消える／聖域の絵が読み込まれている／エラーなし。保存先を渡すと 入り・発動中・戻り を撮る。
"""
import sys, os
from playwright.sync_api import sync_playwright

url=sys.argv[1];out=sys.argv[2] if len(sys.argv)>2 else None
with sync_playwright() as p:
    b=p.chromium.launch();page=b.new_page(viewport={'width':390,'height':844})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(url);page.wait_for_function('window.NARAKU && NARAKU.SPR && NARAKU.SPR.bg && NARAKU.SPR.bg.sanctuary')
    r=page.evaluate("""()=>{
      const N=NARAKU,out={};N.start(['sword','sister','mage'],4242);const B=()=>N.B,si=()=>N.B.allies.find(a=>a.d.id==='sister');
      const snap=()=>N.B.allies.map(a=>[a.M.spd,a.M.multi,a.rg]);
      const base=snap();
      for(const a of N.B.allies)a.hp=a.max*0.5;
      N.ULT_DEF.sister.fire(si());
      out.heal0=N.B.allies.map(a=>+(a.hp/a.max).toFixed(3));
      const on=snap();
      out.ratio=on.map((v,i)=>[+(v[0]/base[i][0]).toFixed(3),v[1]-base[i][1],+(v[2]/base[i][2]).toFixed(3)]);
      // 敵の移動：同じ敵を聖域あり・なしで1秒歩かせる
      N.spawn('skel');const e=N.B.enemies[N.B.enemies.length-1];e.y=60;const y0=e.y,sp=e.spd;N.B.sanct.t=1;
      for(let i=0;i<60;i++){N.B.enemies.forEach(o=>{if(o!==e){o.dead=true}});N.sim(1/60)}
      out.walk=+((e.y-y0)/sp).toFixed(3);
      out.regenHp=+(si().hp/si().max).toFixed(3);
      // 再発動で延長
      N.B.sanct.t=12;N.ULT_DEF.sister.fire(si());out.extend=+N.B.sanct.t.toFixed(2);
      // 15秒で戻る
      N.B.sanct.t=14.9;N.sim(0.2);out.after=snap().map((v,i)=>[+(v[0]/base[i][0]).toFixed(3),v[1]-base[i][1],+(v[2]/base[i][2]).toFixed(3)]);
      N.sim(1);out.cleared=!N.B.sanct;
      // 作り直し（逆転の右手と同じく B を作り直す）で消える
      N.ULT_DEF.sister.fire(si());N.start(['sword','sister','mage'],4242);out.reset=!N.B.sanct;
      return out}""")
    print(r)
    assert all(abs(h-0.6)<0.002 for h in r['heal0']),r['heal0']
    assert all(v==[1.4,1,1.25] for v in r['ratio']),r['ratio']
    assert 0.55<=r['walk']<=0.65,r['walk']
    assert r['regenHp']>0.6,r['regenHp']
    assert r['extend']==0.7,r['extend']
    assert all(v==[1.0,0,1.0] for v in r['after']),r['after']
    assert r['cleared'] and r['reset']
    if out:
        os.makedirs(out,exist_ok=True)
        page.evaluate("()=>{const N=NARAKU;N.start(['sword','sister','mage'],4242);N.sim(20)}")
        page.wait_for_timeout(300)
        page.evaluate("()=>{const N=NARAKU;N.ULT_DEF.sister.fire(N.B.allies[1]);N.sim(0.35)}");page.wait_for_timeout(120);page.screenshot(path=out+'/1_in.png')
        page.evaluate("()=>NARAKU.sim(3)");page.wait_for_timeout(120);page.screenshot(path=out+'/2_on.png')
        page.evaluate("()=>{NARAKU.B.sanct.t=15.3;NARAKU.sim(0.05)}");page.wait_for_timeout(120);page.screenshot(path=out+'/3_out.png')
    assert not errors,errors
    print('RESULT OK')
    b.close()
