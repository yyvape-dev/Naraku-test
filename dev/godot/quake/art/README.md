GPT Image生成原画：slash/impact/rock/dust/fissure/ridge（各1254×1254透過PNG）。追加の亀裂・隆起岩の指示はprompts/06_fissure.txtと07_ridge.txt。motion_board.pngは演出方向の6段階案で、ランタイムのシートではない。

無料補助素材（CC0）：
- support_smoke.png：Kenney Particle Pack、smoke_06.png。https://kenney.nl/assets/particle-pack 。KENNEY_LICENSE.txtを同梱。
- dust_mask.png：ユーザー提供Jettelly Smoke Pack 01、jettelly_smoke_8x8_04.png（4096×4096、8×8）。https://jettelly.com 。JETTELLY_LICENSE.txtを同梱。Godotでは1024pxへ縮小して粉塵の形のマスクに利用。

生成原本と補助素材をGodotで動かし、色・透過・発光の変化を焼いて配布する。

rift_spikes.png：乾坤一擲用にGPT Imageで追加生成した尖った玄武岩の塊。生成指示はprompts/08_rift_spikes.txt、実寸・透過範囲はmanifest.json。

rift_scar.png：作り直し用の専用GPT Image原画。ジグザグの連続した深い裂け目と剥がれた岩盤。prompts/09_rift_scar.txt。rift_spikes.pngは旧候補の原画で、現行rift.gdは使わない。

rift_jagged.png：現行版の専用GPT Image原画。平たい縁を減らし、大小・角度の異なる巨大な尖岩が占める地形。赤い溶岩状の裂け目。prompts/10_rift_jagged.txt。rift_scar.pngは旧候補として保持。
