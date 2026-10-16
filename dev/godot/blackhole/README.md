# シェリ超必殺「永劫凍獄」紫黒ブラックホール

現在：2026-10-16ユーザー承認でNaraku-testへ標準採用。Glow調整済み30fpsを標準とし、RIFE60fpsは`?blackholesmooth=1`または比較のチェックで選ぶ。`?blackholefx=legacy`で従来へ。以下の「候補・未公開」は制作途中の履歴。本番Narakuは今回変更しない。公開ビルドは`--link dev/assets/`。

ユーザーが2026-10-16に添付した「紫黒ブラックホール_6コマ透過PNG.zip」の6枚を使用。対象がシェリ超必殺であることはユーザー確認済み。原本はart/01.png〜06.pngへ無変更で保存。新規生成・外部画像なし。

## 構成

1536×1536透過原本。全6枚の四辺に最低168pxの透明余白。Godotの制作座標512×512、中心256,256、768×768で実描画。01〜03は渦の形成・拡大、04は凝縮、05〜06は破裂・消失として構成した解釈。

- 0〜0.52秒：小さな渦が現れる。0.20〜1.12秒：渦が広がる。
- 0.72〜2.12秒：大きな渦。中心と外周で異なる角速度、半径に沿う歪みで内部を流す。
- 1.87〜2.43秒：中心へ凝縮。2.37秒から破裂素材を重ね、2.4秒の既存大ダメージへ対応。
- 2.54〜3.20秒：破片と紫の光がノイズでほどける。3.2秒で削除。

床の青黒い影と紫の弱い光、空中の原画＋明るい芯の限定HDR Glow＋40個の固定seed GPU粒子。通常合成と黒背景の光を別々に焼き、pack.pyでstraight alphaへ合成。96コマ30fps、床192px・空中384px、12列8行。最大辺alpha=0、両層合計5,665,856bytes、復号約67.5MiB。空中透明度68%で敵の位置を透かす。主役原画の黒は通常合成で保つ。

## ゲームとの対応

`?blackholefx=godot`のみ候補。無指定／legacyは従来。名前・カットイン1.3秒・全域判定（防衛線の半分を中心、半高さlineY/2）・0.05秒40ダメージ＋凍結3秒・2.4秒230ダメージ・各倍率・エリートの凍結短縮は変更なし。吸引や移動、継続ダメージは追加しない。通常のmg_void/mg_infernoは変更しない。

全域判定はskRで割ってから掛ける現行仕様。最大範囲強化4回でも演出の寸法は不変。表示枠は戦場幅360×1.26=453.6論理px（透明余白込み）、中心(W/2,lineY×.48)。床は敵の後ろ、空中は敵の前・味方の後ろ。判定範囲全体に絵があるという意味ではない。素材未読込時は従来へ戻る。共有アトラス各1枚を使用し、コマごとのImage/Canvas生成はしない。

## 再出力

Godot 4.6.3、gl_compatibility、Xorg dummy＋llvmpipeで確認。描画可能なX11が必要。

```sh
DISPLAY=:97 sh dev/godot/blackhole/bake.sh
python3 dev/tools/dev/build_blackhole_player.py
python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets --link dev/assets/
python3 dev/tests/blackhole.py
```

比較はdev/mock/blackhole_demo.html。必要素材だけ外部読込、プレイヤー1つ、進捗・失敗・再読込表示、保存の読書きなし。停止・再生・1/2と1/4速度・時点・床/空中・従来/候補切替。時刻はカットイン終了後。通常採用もGitHub公開も未実施。

## 追加：Flowframesと同系統のRIFE v4.6で中割り

ユーザーの指定により、Godotの30fps出力のコマ間へRIFE中間画像を追加。FlowframesのGUIを動かしたものではなく、公式rife-ncnn-vulkan 20221029同梱のrife-v4.6をCPU Vulkan（Mesa lavapipe）で使用する。

`interpolate.py`は元の共有WebPからpremultiplied RGBとアルファを別々に補間する。ディレクトリモードの`-n 192`は出力iを元のi/2に対応させることを公式ソースで確認。95区間の中間を各層1枚のアトラスへまとめ、偶数時点は元のアトラスを直接使用する。元の画像を再圧縮・置換しない。最後は元の最終コマを保持し、先頭へループしない。96元コマ＋95中間＋最終保持＝192時点、60fps、寿命3.2秒は不変。

```sh
# RIFE_BIN、RIFE_MODEL、VK_DRIVER_FILES、LD_LIBRARY_PATHを準備した環境で：
LP_NUM_THREADS=4 OMP_NUM_THREADS=4 python3 dev/godot/blackhole/interpolate.py
python3 dev/tools/dev/build_blackhole_player.py
python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets --link dev/assets/
python3 dev/tests/blackhole_rife.py
```

比較の「RIFE中割り・60fps」を外すと元の30fps。中割り素材未読込時は30fpsへ戻り、元素材も欠損した場合は従来演出へ戻る。中割りだけで各層の復号メモリが追加され、元と合わせ約135MiBになる。サイズ・時間はrife.json参照。中割りは候補であり、通常採用・GitHub公開は未実施。

## Glow適用の再確認と調整

ユーザーの指示で `.agents/skills/naraku-vfx/SKILL.md` のGlow・GPU粒子工程とquake_bloomの手本を再確認。光の回だけ2D HDRをオン、WorldEnvironmentのBG_CANVAS＋加算Glow、黒背景で光／透明背景で抜きを別々に焼く方式を維持。ShaderMaterialには光専用の`render_mode blend_add`を明示し、光の芯のHDR出力を調整した。通常合成の原画は変更しない。

- `flow_common.gdshaderinc`：渦の歪み・透過と、紫を残すHDRの芯。`flow_light.gdshader`は加算、`flow.gdshader`は通常合成。
- `particle_light.gdshader`：COLORから粒子のテクスチャ・色・アルファを受け継ぎ、明るい芯だけをHDRへ。40個・固定seed・30fpsは維持。
- 空中のGlow intensity .45→.65、中間のぼかしレベルを強める。床は従来値を保持。2.4秒前後の芯を短く強める。黒い主形状をぼかす処理は加えない。
- `--probe`は同一時点をGlow無効／有効で撮影。測定を混ぜないためGPU粒子は非表示。1.2秒と2.433333秒の差分をmeasure_glow.pyで測る。実際のにじみが出たことを確認するための検証で、設定の存在だけを合格にしない。
- `dev/reports/blackhole/glow-before`と`glow-after`が実Godot出力、`glow-measure.json`が測定、`glow-contact.png`が原画と光を合成した比較。
- 空中の光を焼き直した後、その結果からRIFEも再生成。床は未変更。`--bake --air-only --light-only`、`pack.py --air-only`、`interpolate.py --air-only`でこの経路だけ再生成できる。

通常の全工程は、必要なDISPLAYとRIFE/Vulkan環境を設定したうえで `sh dev/godot/blackhole/build.sh`。GodotからRIFEまでを一度に実行する。比較用候補をビルドするだけで、公開や通常採用はしない。
