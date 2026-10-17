"""鍛え直し（二つ名の引き直し）と格上げの確認。使い方: python3 dev/tests/smith_reforge.py <http の配布版URL>
   値段の上がり方と帰還での戻り、同じ二つ名が出ないこと、元に戻す、格上げの成否と成功率の上がり方・基礎値の倍率・金と資材の消費、二つ名なしの装備への付与"""
import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(sys.argv[1]); pg.wait_for_function('window.NARAKU_READY',timeout=120000)
    r=pg.evaluate("""(()=>{const N=NARAKU,M=N.smith;N.fresh();const S=N.S,res={};
      const mk=(s,b,r,p,pw)=>{const it={id:S.nid++,s,b,r,p,n:0,pw};S.inv.push(it);return it};
      S.gold=1e10;S.mats=1e7;
      const w=mk('w',0,3,'sharp',30),c0=M.rfCost(w);let ok=true,prev=w.p;
      for(let i=0;i<20;i++){const c=M.rfCost(w);if(Math.abs(c/(c0*Math.pow(1.5,i))-1)>0.03)ok=false;M.reforge(w.id);if(w.p===prev)ok=false;prev=w.p}
      res.escalate=ok;S.runs++;res.reset=M.rfCost(w)===c0;
      const before=w.p;M.reforge(w.id);const after=w.p;M.reforgeUndo(w.id);res.undo=w.p===before&&after!==before&&!M.reforgeUndo(w.id);
      // 格上げ：大量に試して成功率（初回の確率）を見る
      const trial=(r0,n)=>{let succ=0;for(let i=0;i<n;i++){const it=mk('a',0,r0,r0?'vital':'',10*[1,1.2,1.45,1.8][r0]);const g=S.gold,m=S.mats,c=M.upCost(it);const o=M.upgrade(it.id);
        if(S.gold!==g-c.gold||S.mats!==m-c.mats)return -1;if(o==='ok'){succ++;if(it.r!==r0+1||Math.abs(it.pw-10*[1,1.2,1.45,1.8][r0+1])>0.11||!it.p)return -2}else if(it.upF!==1||it.r!==r0)return -3;S.inv.pop()}return succ/n};
      res.p0=trial(0,2000);res.p1=trial(1,2000);res.p2=trial(2,4000);
      const it=mk('a',0,2,'vital',14.5);const pA=M.upCost(it).p;let k=0;while(M.upgrade(it.id)==='fail'&&k<500)k++;res.pity=pA===0.08&&it.r===3&&it.upF===0&&M.upCost(it)===null;
      const poor=mk('w',0,1,'sharp',12);S.gold=0;res.noGold=M.reforge(poor.id)===false&&M.upgrade(poor.id)===false;
      const none=mk('w',0,0,'',9);S.gold=1e10;res.noAffix=M.reforge(none.id)===false;
      return res})()""")
    print(r)
    ok=r['escalate'] and r['reset'] and r['undo'] and r['pity'] and r['noGold'] and r['noAffix'] and abs(r['p0']-0.45)<0.05 and abs(r['p1']-0.2)<0.04 and abs(r['p2']-0.08)<0.025
    assert ok and not errs,(r,errs)
    b.close()
print('OK: reforge escalation/reset/undo, upgrade rates 45/20/8%, pity, costs, power scaling')
