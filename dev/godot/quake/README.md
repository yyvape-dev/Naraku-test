# 大地割り：Godot 4.6のVFX制作試作

GodotのNode2D描画で、0.9秒の決定的なタイムラインを制作。最初の0.17秒に斬撃と閃光、0.3秒まで床の衝撃波、重力で飛ぶ陰影付きの石片、低い砂煙と亀裂が消える。通常起動ではループして調整できる。

```sh
godot --path dev/godot/quake
# 描画可能なディスプレイ上で透過PNG連番を書き出す：
godot --path dev/godot/quake --rendering-method gl_compatibility --audio-driver Dummy -- --bake
python3 dev/godot/quake/pack.py
python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets
```

headlessのdummy描画ではPNGを作れない。今回の環境ではXorgのdummy画面とMesa llvmpipeで実レンダリングした。連番PNGは再生成できるためGitに含めず、Godotプロジェクトと配布アトラスを保管する。

floor/air各36コマ・40fps。floorは192px、airは256pxの6×6アトラス。計約337KiB、復号後約14MiB。Godotの透明Viewportから読み戻すRGBはpremultiplied alphaなので、pack.pyでstraight alphaに戻してPNG/WebP/Canvasの二重減衰を防ぐ。HTML側は2枚を共有し、各演出は切り出し描画のみ。床は敵の下、石片・閃光は味方の上。アンカー(0.5,0.5625)。当たり判定・130ダメージ・0.16秒命中・9秒装填は変更なし。画像の読み込み失敗時は従来演出に戻る。

比較：`dev/mock/quake_demo.html`。通常ゲームで従来へ戻すにはURLに `?quakefx=legacy`。実機Safariの速度と品質は未確認。最初の試作であり、他のスキルは未変更。
