from pathlib import Path
import re,json
from playwright.sync_api import sync_playwright
root=Path('/workspace/Naraku-test');out=Path(__file__).parent
lib=re.search(r'LIB=r"""(.*?)"""', (root/'dev/tests/smoke.py').read_text(),re.S).group(1)
results={}
with sync_playwright() as p:
 b=p.chromium.launch()
 for label,file in [('before',Path('/tmp/naraku-line-before.html')),('after',root/'index.html')]:
  page=b.new_page(viewport={'width':393,'height':659},is_mobile=True,has_touch=True)
  page.goto(file.as_uri());page.wait_for_function('window.NARAKU_READY');page.evaluate(lib)
  rows=[]
  for seed in range(1,11):
   row=page.evaluate('''seed=>{NARAKU.start(['fox','sword','mage'],seed);const mode=NARAKU.sim(181,T.BOT,T.pol('rnd',seed)),B=NARAKU.B;return {seed,mode,time:B.t,level:B.lv,life:B.life,kills:B.kills,allies:B.allies.map(a=>({id:a.d.id,hp:a.hp,alive:a.alive}))}}''',seed)
   rows.append(row);print(label,seed,row['mode'],round(row['time'],2),flush=True)
  results[label]=rows;page.close()
 b.close()
(out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
for label,rows in results.items():print(label,'wins',sum(r['mode']=='victory' for r in rows),'/10',flush=True)
