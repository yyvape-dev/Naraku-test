# ユズナミキ「狐火乱舞」の候補

専用の生成原画をGodot 4.6.3で、着火→低く走る炎→左右で高さの異なる巻き上がり→炎片→薄い煙として構成する。通常着弾の拡大・均等配置ではない。前回評価された自然なコマ運び、配色、光量を優先する。

```sh
godot --path dev/godot/fox_skill --rendering-method gl_compatibility --audio-driver Dummy -- --bake
python3 dev/godot/fox_skill/pack.py
python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets
```

描画可能なディスプレイが必要。51コマ／1.35秒、初動0.4秒60fps・次0.7秒30fps・最後24fps。224px、8列×7行の床／空中各1アトラス。配布643,414bytes、復号22,478,848bytes（約21.44MiB）。共有224px補間Canvasは200,704bytes、発動ごとには生成しない。premultiplied RGBをstraight alphaに変換してから格納し、Canvasで隣接コマのpremultiplied RGBAを混ぜてから戦場へ合成する。

`?foxfirefx=godot`で狐火乱舞だけ候補へ切り替える。通常攻撃と共通被弾も候補にするなら `?hitfx=godot&foxfirefx=godot`。標準ゲームは従来。スキル候補の2アトラスはフラグが有効なときだけ復号する。素材が未読込・欠落の場合は従来演出へ戻る。百鬼狐火には適用しない。

55ダメージ・命中0.16秒・半径72・装填5秒・二重詠唱0.38秒遅れの60%威力を維持。技の発動から0.16秒で全範囲のダメージが確定し、そこから見た目の炎が約0.19秒で広がる。見た目の伝播は追加の命中判定ではない。残る煙にもダメージなし。新候補では共通の爆発・魔法陣と直線の発射ビームを置換し、体の狐火と既存の発動モーションは維持。軽い画面振動は初撃だけ。

比較 `dev/mock/fox_skill_demo.html`。左従来／右候補。停止・スロー・時間指定・床／空中切替・敵種切替。両側で共通被弾を有効にし、スキル本体だけ比較する。時間表示は命中から。戦闘処理は実際のuseCardを使い、以後の戦闘を固定して演出を進める。

検証 `python3 dev/tests/fox_skill.py --base-url http://127.0.0.1:8003`。記録 `dev/reports/fox-skill/`。通常ゲームへの採用とPages公開は別。実機Safari性能は未確認。
