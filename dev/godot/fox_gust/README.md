# 狐火乱舞：桜の燃焼ピークと風にほどける狐火

[設計と最新の採否](../../design/fox_fire_gust/SAKURA_REVISION.md)。短い桜状の燃焼ピーク、奥と手前の主炎、首の破断、同じ風を受ける火の粉43個と大きな燃焼片14枚、接地反射と煙を制作する。

```sh
python3 dev/godot/fox_gust/prepare.py
# 描画可能なディスプレイで実行。環境に応じDISPLAYと書込可能なXDG_*_HOMEを設定。
godot --path dev/godot/fox_gust --rendering-method gl_compatibility --audio-driver Dummy -- --bake
python3 dev/godot/fox_gust/pack.py
python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets
python3 -m http.server 8006 --bind 127.0.0.1
python3 dev/tests/fox_sakura_frames.py
python3 dev/tests/fox_sakura.py
python3 dev/tests/fox_sakura_continuity.py
python3 dev/tests/fox_sakura_scale.py
python3 dev/godot/fox_gust/capture_sakura.py
ffmpeg -y -stream_loop -1 -i dev/reports/fox-sakura/sakura-fire.mp4 -t 30 -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart dev/reports/fox-sakura/sakura-fire-30s.mp4
```

## 出力と組み込み

Godotは論理400の構成を1280pxで直接レンダリングする。57コマ・命中後1.4秒（最初.5秒60fps、以後30fps）。`pack.py` は192pxの区画ごとにアルファを調べ、透明部分を除いて可変位置へ詰める。1/255以下の透明度のみ除去。区画ごと3pxの余白を付け、各アトラスは4096px以内に制限する。premultiplied RGBをCanvas用straight alphaへ補正する。

配置・元位置・時刻・風の粒子レシピは `dev/assets/vfx_meta.json`、寸法と容量は `atlas.json`。embed.pyのVFXMETA経由でゲームへ渡す。Canvasは1280pxの共有合成面へ整数座標で復元し、premultiplied RGBAでコマ間を補間してから画面へ縮小する。区画を縮小して直接つなぎ、境界に隙間を作る方法は使わない。

火の粉と燃焼片は連番から外す。Godotの固定シードで作った `particles.json` の発生点・初速・抗力・寿命を共有し、Canvas側で1/180秒刻みの軌道を一度計算して描画する。共通の突風、位置による風速差、軽い粒の浮力、重い燃えかすの重力、局所の渦を使う。燃焼片は独立した高解像度素材2種。等角度の散会や同じ放物線ではない。流体シミュレーションではなく、主炎も共通の場の根元での突風を参照する演出。

## 比較と状態

フラグなしが最新の標準（`?foxfirefx=gust` も同じ）、[fox_sakura_demo.html](../../mock/fox_sakura_demo.html)で爆心拡大0〜4段を比較。`?foxfirefx=gust-v1` は前の224px候補。前の記録・動画は `dev/reports/fox-gust/` に保持する。`fox_gust_demo.html` は以前の開花と224px候補の比較を再現する。

55ダメージ／命中.16秒／基礎半径72／装填5秒／二重詠唱は維持。爆心拡大は実ゲームの `1.25^段数` を使用。残留に追加ダメージなし、百鬼狐火には適用しない。未読込時は従来へ戻る。`?foxfirefx=legacy` で従来演出を明示指定できる。

画素数・復号メモリ・実機性能を区別する。[制作レビューと測定](../../reports/fox-sakura/REPORT.md)を参照。作業ブランチでは通常の狐火乱舞へ組み込み済み。mainへのマージ・Pages公開・実機Safari性能確認は未実施。
