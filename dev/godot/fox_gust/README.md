# 狐火乱舞：風にほどける狐火

[設計](../../design/fox_fire_gust/DESIGN.md)の最初の実装候補。火を主役に、根元の着火→奥の立ち上がり／手前の低い炎→首の破断→風で流れる燃焼裂片と火の粉→短い反射と煙を制作した。

```sh
python3 dev/godot/fox_gust/prepare.py
# 描画可能なディスプレイで実行する。
godot --path dev/godot/fox_gust --rendering-method gl_compatibility --audio-driver Dummy -- --bake
python3 dev/godot/fox_gust/pack.py
python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets
python3 -m http.server 8005 --bind 127.0.0.1
python3 dev/tests/fox_gust.py
python3 dev/tests/fox_gust_continuity.py
python3 dev/tests/fox_gust_frames.py
python3 dev/godot/fox_gust/capture.py
ffmpeg -y -stream_loop -1 -i dev/reports/fox-gust/wind-fire.mp4 -t 30 -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart dev/reports/fox-gust/wind-fire-30s.mp4
```

実行環境に応じて `DISPLAY` と書き込み可能な `XDG_DATA_HOME`／`XDG_CACHE_HOME`／`XDG_CONFIG_HOME` を設定する。

## 動きと光

生成素材を格子メッシュへ貼り、根元を固定したまま先端へ風の変形を増やす。大きな変形と細かなUV移流、首の局所浸食、上端からの燃料の消費を分けた。厚い花弁の開閉は使わない。前後レイヤは奥の主炎／中央の短い炎／反射と煙、手前の低い炎／接触芯／裂片を分ける。二層Canvas合成であり敵ごとの厳密な3D遮蔽ではない。

風は短い突風と位置による流速差を持つ共通の場。43個の火の粉は二つの発生点から三つの群で生まれ、軽い粒は抗力5–12/秒、重い燃えかすは2–4/秒で追従する。浮力／重力と局所の渦も加える。固定シード、1/180秒刻みで位置を再計算し、書き出しコマ間隔やシークに依存させない。主炎も同じ場の根元での突風を参照するが、流体シミュレーションではない。煙と水面の細かな移流は補助の独立した動き。

暖色中間調と暗部を残し、短い接触芯だけを明るくする。煙は命中後.24秒から薄く、反射は.035秒遅れて出て.675秒までに消える。閉じた池・円環や残留ダメージを作らない。

## ゲームとの接続

`?foxfirefx=gust`、比較は [fox_gust_demo.html](../../mock/fox_gust_demo.html)。左が前の開花、右が今回の狐火。停止・スロー・時間指定・前後レイヤ切替に対応。標準は従来演出、前候補のフラグも維持。

命中後1.4秒・57コマ（最初.5秒60fps、以後30fps）。224px・8列×8行・2アトラス。必要な候補2枚だけ復号する。premultiplied RGBをstraight alphaへ変換し、Canvas上でpremultiplied RGBA補間。配布と復号サイズはatlas.jsonに記録。共有補間Canvasは200,704 bytes。

55ダメージ／命中.16秒／半径72／装填5秒／二重詠唱は既存のまま。残留に追加ダメージなし。百鬼狐火は対象外。未読込時は従来へフォールバックする。

自己レビューと制限は [制作レビュー](../../reports/fox-gust/REPORT.md)。通常採用・Pages公開・実機Safari性能確認は未実施。
