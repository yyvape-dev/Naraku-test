# 制作と検証

設計を実装する作業で参照する。設計だけの依頼にゲーム検証済みという状態を付けない。

Godotで出現順・方向・重さ・飛散・光・消え際を構成する。床と空中を分けて透過連番を書き出し、共有アトラスとしてHTML Canvasへ組み込む。ゲーム全体の移植を前提にしない。

生成・書き出し前の [最大表示条件と画素数の設計](resolution.md)、組み込み後の [コードで仕上げた演出のレビュー](finish-review.md) を併用する。技術的な検証だけで最終品質を合格にしない。

## 組み込みと検証

- ダメージ、命中時刻、範囲、鈍足などの効果を、演出だけの変更で動かさない。視覚の進行と命中の時刻が独立している場合は記録する。
- 床の地形は敵の背面、剣戟・飛散物は必要に応じ前面へ分ける。
- Godotの透過Viewportから得たpremultiplied RGBを、Canvas用straight alphaへ正しく変換する。
- アトラスのコマ数、列数、可変時間、寿命とHTML側の切り出しを一致させる。余韻だけ低fpsにするなど容量と復号メモリも考慮する。
- 素材未読込時の従来演出へのフォールバックを維持する。
- 変更に応じて戦闘状態比較、寿命・片付け、JSエラー、実画面を確認する。ブラウザーの測定を実機スマートフォンの性能保証にしない。

## 既存の入口

- ソース：dev/naraku_src.html、配布：index.html
- 再ビルド：python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets
- Godot・書き出し：dev/godot/quake/README.md、pack.py
- 比較：dev/mock/quake_demo.html、dev/mock/rift_demo.html
- 狐火通常着弾：dev/godot/fox/、dev/mock/fox_hit_demo.html（?hitfx=godot）
- 狐火乱舞：前の炎候補dev/godot/fox_skill/（?foxfirefx=godot）、花・水面候補dev/godot/fox_bloom/とdev/mock/fox_bloom_demo.html（?foxfirefx=bloom）。通常攻撃と百鬼狐火を区別し、超必殺へ誤適用しない。
- 検証：dev/tests/godot_quake.py、dev/tests/godot_rift.py、dev/reports/
- 引き継ぎ：dev/HANDOFF.md。最新日付の記録（現在は先頭）と実コードで採用状態を確認する。


乾坤一擲の過去の個別仕様はダメージ3秒、見た目4.2秒、2.8秒から1.4秒のフェード。他の技の既定値にはしない。裂け目と尖った隆起を主役にし、平たい岩盤の枠で面積を埋めないという評価も、この技の文脈で参照する。

桜を強めた狐火の最新候補：`dev/godot/fox_gust/`、比較 `dev/mock/fox_sakura_demo.html`、`?foxfirefx=gust`。旧224px候補は `?foxfirefx=gust-v1`。最新候補は固定格子ではなく1280pxの可変区画を `dev/assets/vfx_meta.json` の配置に従って復元する。`dev/reports/fox-sakura/` に最大拡大・DPR・復号メモリの測定を残す。

2026-10-15の後続ユーザー指示で、作業ブランチの狐火乱舞はフラグなしでも桜の狐火を使う。`?foxfirefx=legacy` で従来へ戻す。標準プレイの検証は `dev/reports/fox-default/`。作業ブランチへの採用をmainマージ・Pages公開と同一視しない。
