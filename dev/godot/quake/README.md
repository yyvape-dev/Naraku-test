# GPT Image原画＋Godot：大地割りの演出試作

`art/`の主斬撃・命中・石片・砂煙はGPT Image生成原画（1254×1254透過PNG）。`art/motion_board.png`も同じ4枚を参照して画像生成した6段階の演出案。プロンプトは`prompts/`。Godotではこの案を参考に、方向ワイプ、ノイズで崩れる消え方、石片の移動と回転、低い砂煙の拡散を実装した。画像生成が動画を出力したわけではない。

```sh
godot --path dev/godot/quake
# 描画可能なディスプレイで透過連番を書き出す：
godot --path dev/godot/quake --rendering-method gl_compatibility --audio-driver Dummy -- --bake
python3 dev/godot/quake/pack.py
python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets
```

床／空中各36コマ、40fps、0.9秒。floor192px・air256pxの6×6アトラス。Godot透明Viewportのpremultiplied RGBをpack.pyでstraight alphaに補正。PNG連番と`.godot/`は再生成するためGit対象外。今回の生成はXorg dummy画面＋Mesa llvmpipeの実描画。

配布アトラス計約381KiB、復号後約14MiB。HTMLは2枚を共有して切り出し描画。床は敵の下、石片・斬撃・破裂は味方の上。描画アンカー(0.5,0.5625)。ダメージ130・命中0.16秒・範囲88・押し戻し44・装填9秒は維持。

通常ゲームは従来演出へ戻している。試作は`?quakefx=godot`で有効。比較ページ`dev/mock/quake_demo.html`の右側で原画版を再生できる。素材未読込時は従来演出へフォールバック。見た目の最終採用と実機Safariの負荷は未確認。
