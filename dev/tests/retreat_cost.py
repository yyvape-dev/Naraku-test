"""帰還の代償の確認。使い方: python3 dev/tests/retreat_cost.py <http の配布版URL>
   入口で金50%・装備の約半分を失い、奥ほど減る／同じ種と歩みなら同じ装備を失う／踏破・全滅は従来どおり／街の蓄えに入るのは持ち帰り分だけ"""
import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(sys.argv[1]); pg.wait_for_function('window.NARAKU_READY',timeout=120000)
    r=pg.evaluate("""(()=>{const N=NARAKU,out={};N.fresh();N.startRun(['fox','sword','mage'],7);
      const R=N.R,M=R.map,fill=()=>{R.gold=1000;R.loot=[];for(let i=0;i<10;i++)R.loot.push({id:0,s:'w',b:0,r:0,p:'',n:0,pw:9+i})};
      const at=L=>{const n=M.nodes.find(o=>o.L===L);R.at=n.id};
      fill();at(1);const a=N.retreatCost();out.start=[a.gold,a.keep.length];
      const a2=N.retreatCost();out.same=JSON.stringify(a.keep.map(x=>x.pw))===JSON.stringify(a2.keep.map(x=>x.pw));
      at(M.steps);const z=N.retreatCost();out.end=[z.gold,z.keep.length];
      const mid=Math.ceil(M.steps/2);at(mid);const m=N.retreatCost();out.mid=[m.gold,m.keep.length,+m.dep.toFixed(2)];
      const g0=N.S.gold,inv0=N.S.inv.length;N.retreat();out.banked=[N.S.gold-g0,N.S.inv.length-inv0];out.expect=[m.gold,m.keep.length];
      return out})()""")
    print(r)
    ok=r['start']==[500,5] and r['end']==[1000,10] and r['same'] and r['banked']==r['expect'] and 500<r['mid'][0]<1000 and 5<=r['mid'][1]<=10
    assert ok and not errs,(r,errs)
    b.close()
print('OK: retreat keeps 50%..100% gold and loses ~half..0 gear by depth; deterministic; banked amounts match')
