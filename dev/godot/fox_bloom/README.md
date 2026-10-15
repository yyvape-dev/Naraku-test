# 狐火乱舞：火の水面に咲く花

前の炎候補へのユーザー評価「地味で平面的」を受け、百鬼狐火の花・花弁・火の水面から構成し直す候補。前の試作を改善成功として継承しない。

```sh
godot --path dev/godot/fox_bloom --rendering-method gl_compatibility --audio-driver Dummy -- --bake
python3 dev/godot/fox_bloom/pack.py
python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets
```

Godot 4.6.3の実3Dで制作するが、ゲームはHTML Canvasのまま。2種類の専用花弁原画を8×24分割の曲面メッシュへ貼り、6枚の幅・長さ・傾き・開花時刻を変える。つぼみの立ち上がり→外へ開く花弁→9枚の花弁が離れて旋回し落下する。水面は専用の液体原画を変形・移流し、微小な頂点変位と花弁の鏡像を重ねる。規則的な同心円だけで水を表現しない。

3Dの奥側の花弁・水面・反射は `floor` アトラス（敵より後ろ）、手前の花弁は `air` アトラス（敵より前）。舞う花弁もZ位置で前後に分ける。二層の合成なので、敵ごとに厳密な3D遮蔽を計算するものではない。

69コマ／1.8秒、最初0.5秒60fps・後半30fps。各224px・8列×9行。premultiplied RGBをstraight alphaへ補正し、共有Canvas上でコマ間のpremultiplied RGBAを補間する。2枚合計1,446,688bytes・復号28,901,376bytes。共有補間Canvas200,704bytes。

`?foxfirefx=bloom`が新候補、`?foxfirefx=godot`は前の炎候補、標準は従来。`?hitfx=godot`併用で通常着弾・共通被弾も候補にできる。必要なスキルアトラスだけ復号し、未読込時は従来演出。百鬼狐火に誤適用しない。

55ダメージ・命中0.16秒・半径72・装填5秒・二重詠唱は維持。命中後に花が開くので、見た目の伝播とダメージ時刻は別。1.8秒の水面・花弁の残留に追加ダメージなし。

比較 `dev/mock/fox_bloom_demo.html` は左が前の炎、右が新しい開花。停止・スロー・時間指定・奥／手前の切替。記録 `dev/reports/fox-bloom/`、検証 `dev/tests/fox_bloom.py` と `dev/tests/fox_bloom_continuity.py`。動画は30秒リピートを提示する。通常採用・Pages公開・実機Safari性能確認は未実施。


30秒リピート動画：`ffmpeg -stream_loop -1 -i fire-water-bloom.mp4 -t 30 -c copy -movflags +faststart fire-water-bloom-30s.mp4`。再生ボタン操作で冒頭を見逃しても繰り返し確認できる形で提示する。
