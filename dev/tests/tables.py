# 探索の机のバリエーション（2026-10-18）。通常はシードで6枚から1枚・宝物の匂いは墓所・大異変は血。
# 使い方: python3 dev/tests/tables.py http://127.0.0.1:8765/index.html [撮影先フォルダ]
import sys
from playwright.sync_api import sync_playwright
url=sys.argv[1];out=sys.argv[2] if len(sys.argv)>2 else None
ok=True
def chk(c,msg):
    global ok
    print(('OK  ' if c else 'NG  ')+msg); ok=ok and c
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':393,'height':852},device_scale_factor=2 if out else 1)
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:140]))
    pg.goto(url);pg.wait_for_timeout(500);pg.evaluate('try{localStorage.clear()}catch(e){}');pg.reload();pg.wait_for_timeout(3000)
    def run(seed,an='none'):
        pg.evaluate("([s,a])=>NARAKU.startRun(['fox','sword','mage'],s,1,a)",[seed,an]);pg.wait_for_timeout(200)
        k=pg.evaluate('NARAKU.tableKey()')
        for _ in range(30):   # 差し替えの絵が読み終わり、描き直されるまで待つ
            if pg.evaluate('NARAKU.tableShown()')==k: break
            pg.wait_for_timeout(100)
        return k,pg.evaluate('NARAKU.tableShown()')
    seen={}
    for s in range(1,60):
        k,shown=run(s)
        if k not in seen:
            seen[k]=s;chk(shown==k,f'通常 seed{s}: 選ばれた机 {k} が表示される（表示 {shown}）')
            if out: pg.screenshot(path=f'{out}/table_{k}.png')
        if len(seen)>=6: break
    chk(set(seen)=={'base','warm','moon','frost','war','hallow'},'通常の机は6種類すべて出る（tomb・bloodは出ない）: '+','.join(sorted(seen)))
    k1,_=run(7);k2,_=run(7);chk(k1==k2,'同じ探索（同じシード）なら同じ机')
    for an,want in (('treasure','tomb'),('cata','blood')):
        k,shown=run(11,an);chk(k==want and shown==want,f'異変 {an} → {want}（表示 {shown}）')
        if out: pg.screenshot(path=f'{out}/table_{want}.png')
    bg=pg.evaluate("document.querySelector('#app').style.background");chk('linear-gradient(rgba(8, 5, 3, 0.15)' in bg,'盤の内側の暗さが下部エリアの背景にも重なる')
    chk(not errs,'エラーなし '+str(errs[:2]))
    b.close()
print('RESULT','OK' if ok else 'NG')
