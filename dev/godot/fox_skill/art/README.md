# 狐火乱舞の専用原画

`main.png`: 2026-10-15、ユーザーの「スキルに進む」依頼に対しGPT Imageで生成した透過原画。生成指示は `../prompts/main.txt`。元生成物 `/workspace/generated_images/exec-0b1f5bd6-e9da-4bf4-9982-d426fc787979.png` を保持したままコピー。特定ゲームの素材は使用していない。

低い接地点から左右に異なる形・高さで巻き上がる1つながりの炎。生成時の接地点指定は(.5,.65)だったが、実際の絵を確認すると明るい根元は約(.59,.80)。この実測値に合わせてGodotのアンカーと伝播原点を設定した。原画単体で完成とは評価しない。

補助素材は兄弟ディレクトリ `../../fox/art/` の既存素材を共有する：
- `fragments.png` / `embers.png` / `smoke.png`: 前回の専用生成素材。指示・出典は同ディレクトリREADMEと `../../fox/prompts/source.txt`。
- `support_smoke.png`: Kenney Particle Pack 1.1 / smoke_06.png、CC0。https://kenney.nl/assets/particle-pack 。ライセンス `../../fox/art/KENNEY_LICENSE.txt` を同梱済み。
- `jettelly_smoke.png`: Jettelly Smoke Pack 01 / jettelly_smoke_8x8_04.png、CC0。https://jettelly.com 。ライセンス `../../fox/art/JETTELLY_LICENSE.txt` を同梱済み。

Godotは上記画像を絶対パスに解決して読み込む。主役は今回の専用原画、素材集は低濃度の煙のみ。Jettellyのタイルは変形せず、コマの混入を避ける。紫は煙のみに限定する。
