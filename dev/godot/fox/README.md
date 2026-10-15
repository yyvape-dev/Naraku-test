# 狐火の通常着弾・共通被弾動作の候補

専用生成原画をGodot 4.6.3で動かし、Kenney・JettellyのCC0煙を低濃度で補助。発生→方向に裂ける炎→遅れる炎片→煙と火の粉へ消える。通常弾の非表示は維持。赤黒い地割れを流用しない。

```sh
python3 dev/godot/fox/prepare.py
godot --path dev/godot/fox --rendering-method gl_compatibility --audio-driver Dummy -- --bake
python3 dev/godot/fox/pack.py
python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets
```

描画可能なディスプレイが必要。33コマ／0.8秒。初動0.3秒を60fps・以後30fps、192px・8列×5行の床／空中アトラス。2枚合計277,554bytes、復号11,796,480bytes。premultiplied RGBをstraight alphaへ変換。共有アトラスから切り出し、1枚の共有192px Canvasで隣接コマのpremultiplied RGBAを線形補間。発動ごとのCanvas生成はなし。最後は透明へ補間する。単純なsource-overの二重フェードによる中間の暗化を避ける。

`?hitfx=godot`で調整版、`?hitfx=godot-v1`で前回候補（24コマ40/20fps・コマ保持・旧配色）。比較画面は左が前回候補、右が調整版。通常ゲームは従来。素材未読込時は従来着弾に戻る。比較 `dev/mock/fox_hit_demo.html`。停止、スロー、時間指定、煙／炎／被弾動作の切替、敵種切替、0.42秒間隔の反復。比較は実際の通常攻撃命中ルーチンを使用。

共通被弾：命中方向への短いひるみと戻り、加算発光の減衰。大鬼38%・女王15%の描画変位。静的な物理座標・攻撃周期・命中・ダメージ・押し戻しは変えない。継続ダメージはひるみを発生させない。被弾補助状態はWeakMapと寿命付きFXで管理。

今回の主VFXはユズナミキ通常攻撃のみ。狐火乱舞・影縫い・百鬼狐火の主演出は未変更。全体被弾動作も候補フラグ内。生成画像の拡縮だけを完成としていないが、特定の商用3Dゲームと同等品質を保証するものではない。実機Safariの評価は未実施。


## 自然感の調整

ユーザーの追加方針：ドット感よりコマ割りによる自然な動き、自然な配色と光量を優先。命中点に炎の根元を固定して、拡大時のずれを修正。初動を60fpsで記録しコマ間補間。局所的な明るさの揺れを±3%に抑え、明るい芯から暖色中間調へ冷める色変化を追加。全体の周期的な発光で流動感を代用しない。Jettellyの各タイルはUV変形しない（隣コマの混入を防ぐ）。

前回候補のアトラスは `dev/assets/vfx_foximpact_v1_{floor,air}.webp` に保存。比較用2枚も合わせた追加アトラスの復号メモリは18,874,368bytes。VFXローダーはこれらも共有ロードするため、調整版2枚だけの数値と混同しない。

時間連続性と中間光量の検証：`python3 dev/tests/fox_continuity.py --base-url http://127.0.0.1:8000`。
