# 狐火着弾の専用原画と補助素材

2026-10-14、ユーザー依頼「黒い砂漠のような高品質な炎によるアクション、エフェクト」を受けた通常攻撃着弾の候補。特定ゲームの画像は使用していない。

- `source_sheet.png`: GPT Imageで生成した1254×1254透過原本。元の生成物 `/workspace/generated_images/exec-b0de7aaf-1669-4136-a32f-b4e06a469b61.png` を保持。生成指示は `../prompts/source.txt`。
- `flame.png`, `fragments.png`, `smoke.png`, `embers.png`: 原本を役割ごとに切り出した制作素材。切り出し矩形は `../prepare.py` に記録。完成アニメーションではない。
- `support_smoke.png`: Kenney Particle Pack 1.1 / smoke_06.png。https://kenney.nl/assets/particle-pack 。既存プロジェクトから同じ素材を複製。CC0、KENNEY_LICENSE.txtを同梱。
- `jettelly_smoke.png`: Jettelly Smoke Pack 01 / jettelly_smoke_8x8_04.png。https://jettelly.com 。既存dust_mask.pngと同一。CC0、JETTELLY_LICENSE.txtを同梱。8×8の煙連番を低濃度で補助に使用。

生成の朱赤い炎が主役。煙・粒子集は補助に限定。Godotの局所UV移流、方向ワイプ、炎片の遅延、浸食と透明度で動かす。紫は煙のみ。原画の良さを完成品質の証明とはしない。
