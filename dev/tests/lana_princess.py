"""Verify outfit persistence, half-speed timing, source frames and raw/smooth parity.
Run against the linked HTTP build, with Playwright Chromium installed.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
original=Image.open(root/'assets/sword_princess.webp').convert('RGBA')
smooth=Image.open(root/'assets/sword_princess_smooth.webp').convert('RGBA')
for i in range(16):
    assert np.array_equal(np.asarray(original.crop((352*i,0,352*(i+1),560))),
                          np.asarray(smooth.crop((704*i,0,704*i+352,560))))

with sync_playwright() as p:
    b=p.chromium.launch()
    page=b.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.goto(sys.argv[1])
    page.wait_for_function('window.NARAKU && NARAKU.SPR.ally.sword')  # 姫騎士の絵は衣装を選んだ時に切り分ける（2026-10-18 メモリ対策）
    assert page.evaluate('!NARAKU.SPR.ally.sword_princess && !NARAKU.SPR.ally.sword_princess_smooth')
    page.evaluate("NARAKU.fresh();NARAKU.town.view('char','sword')")
    page.select_option('[data-lana-costume]','princess')
    page.check('[data-lana-smooth]')
    page.reload()
    page.wait_for_function('window.NARAKU && NARAKU.SPR.ally.sword_princess_smooth')
    assert page.evaluate('NARAKU.costume.get()') == dict(costume='princess',smooth=True)
    assert page.evaluate("NARAKU.look.frames('sword')") == 31
    result=page.evaluate("""()=>{
      const N=NARAKU,run=(costume,smooth)=>{
        N.costume.set(costume,smooth);N.start(['sword','fox','mage'],4242);N.sim(40);
        const B=N.B;return JSON.stringify([B.t,B.idx,B.kills,B.gold,B.life,B.lv,B.allies.map(a=>[a.hp,a.cdT,a.animT]),B.enemies.map(e=>[e.idx,e.hp,e.x,e.y])]);
      };
      const raw=run('princess',false),smooth=run('princess',true);
      const timing=(costume)=>{N.costume.set(costume,false);N.start(['sword'],42);N.B.allies[0].cdT=0;N.spawn('skel');const e=N.B.enemies[0];e.x=N.B.allies[0].x;e.y=N.B.allies[0].y-45;N.sim(1/60);const a=N.B.allies[0];return [a.animDur,a.pend&&a.pend.t,a.cdT]};
      const old=timing('normal'),slow=timing('princess');
      const ms=[10,8,8,8,6,4,2,2,4,6,6,8,8,8,8,8],ms2=ms.flatMap((n,i)=>i<15?[n/2,n/2]:[n]);
      let timeline=true;for(let i=0;i<1000;i++){
        const u=i/1000,a=N.frameAt({ms,hit:7},16,u,.55),c=N.frameAt({ms:ms2,hit:14},31,u,.55);
        if(Math.floor(c/2)!==a)timeline=false;
      }
      N.costume.set('princess',true);const atlas=N.SPR.ally.sword_princess_smooth;delete N.SPR.ally.sword_princess_smooth;
      const fallback=N.look.frames('sword')===16;N.SPR.ally.sword_princess_smooth=atlas;
      N.costume.set('princess',false);const pd=N.costume.d('sword'),pSeq=N.costume.ultSeq(),pCol=N.costume.col();
      N.costume.set('normal',false);const nd=N.costume.d('sword'),nSeq=N.costume.ultSeq(),nCol=N.costume.col();
      const holy=pd.atk==='line'&&pd.range===265&&pd.fb==='princess'&&!pd.far&&nd.atk==='circle'&&!!nd.far&&/^lanaPU/.test(pSeq)&&/^lanaU/.test(nSeq)&&pCol!==nCol&&N.CHARS.sword.atk==='circle';
      return {holy,halfSpeed:Math.abs(slow[0]-.9)<1e-8&&Math.abs(old[0]-.45)<1e-8&&Math.abs(slow[1]-.9*.55)<1e-8&&Math.abs(slow[2]/old[2]-2.3/1.15)<1e-6,parity:raw===smooth,timeline,fallback,hit:N.frameAt({ms,hit:7},16,.55,.55)===7&&N.frameAt({ms:ms2,hit:14},31,.55,.55)===14};
    }""")
    assert all(result.values()),result
    assert not errors,errors
    b.close()
print('OK: holy-gold swap and princess line attack; original pixels retained; selection persists; half-speed duration, cadence, hit sync, fallback and raw/smooth battle parity')
