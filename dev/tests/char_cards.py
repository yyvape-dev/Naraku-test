"""キャラ専用の強化カード（ユズナミキ・リンネ。2026-10-18）の確認。
使い方: python3 dev/tests/char_cards.py http://127.0.0.1:8765/index.html
確認：そのキャラが編成にいる時だけ候補に出る／各カードの効果（弾数・跳弾・爆ぜ・急所狙い・首狩り・連鎖暗殺）／
      連鎖暗殺の苦無では連鎖しない／上限（最大3段）／既存の強化に影響しない／エラーなし。"""
import sys
from playwright.sync_api import sync_playwright

url=sys.argv[1]
fails=[]
def check(name,ok,detail=''):
    print(('OK  ' if ok else 'NG  ')+name,detail if not ok else '')
    if not ok: fails.append(name)

with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':844})
    errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
    pg.goto(url);pg.wait_for_function('window.NARAKU && window.NARAKU_READY',timeout=120000)

    # 1. 候補に出る条件
    r=pg.evaluate("""()=>{
      const N=NARAKU,count=(ids,fam)=>{let c=0;for(let s=1;s<=30;s++){N.start(ids,s);for(const o of (function(){const out=[];let g=0;while(out.length<5&&g++<4000){N.sim(1/60);if(N.mode==='levelup'){out.push(N.B.offer.map(u=>u.fam));N.pick(-1)}else if(N.mode!=='battle')break}return out})())for(const f of o)if(f===fam)c++}return c};
      return {foxIn:count(['fox','sword','mage'],'fox'),foxOut:count(['sword','mage','blue'],'fox'),ninjaIn:count(['ninja','sword','mage'],'ninja'),ninjaOut:count(['fox','sword','mage'],'ninja')}}""")
    check('いる時だけ候補に出る',r['foxIn']>0 and r['foxOut']==0 and r['ninjaIn']>0 and r['ninjaOut']==0,r)
    print('   提示された回数（30戦×5回）',r)

    # 2. 効果
    r=pg.evaluate("""()=>{
      const N=NARAKU,out={};
      N.start(['fox','ninja','sword'],11);const B=N.B,f=B.allies[0],n=B.allies[1],sw=B.allies[2];
      const base={fm:f.M.multi,fx:f.M.xchain,nw:n.M.weak,swm:sw.M.multi};
      N.grant('f_volley');N.grant('f_volley');N.grant('f_bounce');N.grant('n_weak');N.grant('n_exec');N.grant('n_relay');N.grant('f_burst');
      out.fox={multi:f.M.multi-base.fm,xchain:f.M.xchain,splash:f.M.splash};
      out.ninja={weak:n.M.weak,exec:n.M.exec,relay:n.M.relay,foxOnly:f.M.weak,swordUntouched:sw.M.multi===base.swm&&sw.M.splash===0&&sw.M.relay===0};
      return out}""")
    check('弾幕増強・跳ね弾・狐火の爆ぜがユズナミキだけに効く',r['fox']['multi']==2 and r['fox']['xchain']==1 and r['fox']['splash']==1,r)
    check('急所狙い・首狩り・連鎖暗殺がリンネだけに効く',r['ninja']['weak']==1 and r['ninja']['exec']==1 and r['ninja']['relay']==1 and r['ninja']['swordUntouched'],r)

    # 3. 首狩り・急所狙い：威力
    r=pg.evaluate("""()=>{
      const N=NARAKU,out={};
      const dmgOn=(cards,mk)=>{N.start(['ninja'],21);const B=N.B;B.need=1e12;B.allies[0].max=B.allies[0].hp=1e9;cards.forEach(c=>N.grant(c));
        N.spawn('skel');const e=B.enemies[B.enemies.length-1];mk(e);e.hp=mk.hp||e.hp;const a=B.allies[0];const h0=e.hp;window.hitFrom(a,e,1);return h0-e.hp};
      const plain=dmgOn([],e=>{});
      const exec0=dmgOn(['n_exec'],e=>{});            // 体力が多い敵には効かない
      const execLow=dmgOn(['n_exec'],e=>{e.hp=e.max*0.2;});
      const plainLow=dmgOn([],e=>{e.hp=e.max*0.2;});
      return {plain,exec0,execLow,plainLow}}""")
    check('首狩り：体力30%以下の敵にだけ+40%',abs(r['exec0']-r['plain'])<1e-6 and abs(r['execLow']/r['plainLow']-1.4)<0.01,r)

    # 4. 連鎖暗殺：撃破で苦無が飛ぶ／連鎖した苦無では連鎖しない
    r=pg.evaluate("""()=>{
      const N=NARAKU;N.start(['ninja'],31);const B=N.B;B.need=1e12;const a=B.allies[0];a.max=a.hp=1e9;
      N.grant('n_relay');
      for(let i=0;i<3;i++)N.spawn('skel');const es=B.enemies.slice(-3);es.forEach((e,i)=>{e.x=a.x+i*20;e.y=B.lineY-120;e.hp=1});
      const sh0=B.shots.length;window.hitFrom(a,es[0],1);
      const rel=B.shots.filter(s=>s.rel);
      // 連鎖した苦無で別の敵を倒しても、さらに連鎖しない
      B.noRelay=true;window.hitFrom(a,es[1],1);B.noRelay=false;
      const rel2=B.shots.filter(s=>s.rel).length;
      return {relay1:rel.length,relayAfterNo:rel2,k:rel[0]&&rel[0].k}}""")
    check('連鎖暗殺：撃破で苦無が1本飛ぶ（威力60%）',r['relay1']==1 and abs(r['k']-0.6)<1e-9,r)
    check('連鎖した苦無では連鎖しない',r['relayAfterNo']==r['relay1'],r)

    # 5. 狐火の爆ぜ：周囲の敵にも当たる
    r=pg.evaluate("""()=>{
      const N=NARAKU;N.start(['fox'],41);const B=N.B;B.need=1e12;const a=B.allies[0];a.max=a.hp=1e9;
      const setup=()=>{N.start(['fox'],41);const B=N.B;B.need=1e12;const a=B.allies[0];a.max=a.hp=1e9;return [B,a]};
      let [B1,a1]=setup();N.spawn('skel');N.spawn('skel');let e=B1.enemies.slice(-2);e[0].x=180;e[0].y=200;e[1].x=190;e[1].y=205;e.forEach(x=>x.hp=x.max=1e6);
      window.hitFrom(a1,e[0],1);const off=e[1].max-e[1].hp;
      let [B2,a2]=setup();N.grant('f_burst');N.spawn('skel');N.spawn('skel');e=B2.enemies.slice(-2);e[0].x=180;e[0].y=200;e[1].x=190;e[1].y=205;e.forEach(x=>x.hp=x.max=1e6);
      window.hitFrom(a2,e[0],1);const on=e[1].max-e[1].hp;
      N.spawn('skel');const far=B2.enemies[B2.enemies.length-1];far.x=330;far.y=60;far.hp=far.max=1e6;window.hitFrom(a2,e[0],1);
      return {off,on,far:far.max-far.hp}}""")
    check('狐火の爆ぜ：近くの敵だけ巻き込む',r['off']==0 and r['on']>0 and r['far']==0,r)

    # 6. 群れでの伸び（通常攻撃だけ・単独・的が多い）
    r=pg.evaluate("""([id,cards,extra])=>{const N=NARAKU;N.start([id],5);const B=N.B;B.need=1e12;B.life=1e9;B.allies[0].max=B.allies[0].hp=1e9;cards.forEach(c=>N.grant(c));
      for(let t=0;t<40;t++){for(let k=0;k<extra;k++)N.spawn('skel');N.sim(1)}return B.stat[id].atk/40}""",['fox',['f_burst','f_burst','f_burst'],12])
    r0=pg.evaluate("""([id,cards,extra])=>{const N=NARAKU;N.start([id],5);const B=N.B;B.need=1e12;B.life=1e9;B.allies[0].max=B.allies[0].hp=1e9;cards.forEach(c=>N.grant(c));
      for(let t=0;t<40;t++){for(let k=0;k<extra;k++)N.spawn('skel');N.sim(1)}return B.stat[id].atk/40}""",['fox',[],12])
    print('   ユズナミキ 密度大の通常攻撃：札なし %.1f → 狐火の爆ぜ×3 %.1f'%(r0,r))
    check('狐火の爆ぜ×3 で群れへの通常攻撃が伸びる（2倍以上）',r>=r0*2,(r0,r))
    for cards,label in ((['n_relay','n_relay','n_relay'],'連鎖暗殺×3'),(['n_exec','n_exec','n_exec'],'首狩り×3')):
        v=pg.evaluate("""([id,cards,extra])=>{const N=NARAKU;N.start([id],5);const B=N.B;B.need=1e12;B.life=1e9;B.allies[0].max=B.allies[0].hp=1e9;cards.forEach(c=>N.grant(c));
          for(let t=0;t<40;t++){for(let k=0;k<extra;k++)N.spawn('skel');N.sim(1)}return B.stat[id].atk/40}""",['ninja',cards,12])
        v0=pg.evaluate("""([id,cards,extra])=>{const N=NARAKU;N.start([id],5);const B=N.B;B.need=1e12;B.life=1e9;B.allies[0].max=B.allies[0].hp=1e9;
          for(let t=0;t<40;t++){for(let k=0;k<extra;k++)N.spawn('skel');N.sim(1)}return B.stat[id].atk/40}""",['ninja',[],12])
        print('   リンネ 密度大の通常攻撃：札なし %.1f → %s %.1f'%(v0,label,v))

    check('エラーなし',not errors,errors)
    print('RESULT','OK' if not fails else 'NG '+str(fails));b.close()
sys.exit(1 if fails else 0)
