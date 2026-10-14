# 狐火の通常着弾・共通被弾動作の候補

専用生成原画をGodot 4.6.3で動かし、Kenney・JettellyのCC0煙を低濃度で補助。発生→方向に裂ける炎→遅れる炎片→煙と火の粉へ消える。通常弾の非表示は維持。赤黒い地割れを流用しない。

```sh
python3 dev/godot/fox/prepare.py
godot --path dev/godot/fox --rendering-method gl_compatibility --audio-driver Dummy -- --bake
python3 dev/godot/fox/pack.py
python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets
```

描画可能なディスプレイが必要。24コマ／0.8秒。初動40fps・煙20fps、192px・8列×3行の床／空中アトラス。2枚合計208,528bytes、復号7,077,888bytes。premultiplied RGBをstraight alphaへ変換。共有アトラスから切り出し、発動ごとのCanvas生成はなし。

`?hitfx=godot`のみ候補有効。通常ゲームは従来。素材未読込時は従来着弾に戻る。比較 `dev/mock/fox_hit_demo.html`。停止、スロー、時間指定、煙／炎／被弾動作の切替、敵種切替、0.42秒間隔の反復。比較は実際の通常攻撃命中ルーチンを使用。

共通被弾：命中方向への短いひるみと戻り、加算発光の減衰。大鬼38%・女王15%の描画変位。静的な物理座標・攻撃周期・命中・ダメージ・押し戻しは変えない。継続ダメージはひるみを発生させない。被弾補助状態はWeakMapと寿命付きFXで管理。

今回の主VFXはユズナミキ通常攻撃のみ。狐火乱舞・影縫い・百鬼狐火の主演出は未変更。全体被弾動作も候補フラグ内。生成画像の拡縮だけを完成としていないが、特定の商用3Dゲームと同等品質を保証するものではない。実機Safariの評価は未実施。
