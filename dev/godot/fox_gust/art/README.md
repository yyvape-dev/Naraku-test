# 使用素材と採否

- `rear.png`, `front.png`, `fragment_a.png`, `fragment_b.png`, `root.png` は `dev/design/fox_fire_gust/generated/03_source_materials.png` の機械的切り出し。GPT Image生成原本と指示は同設計パッケージに保存済み。矩形は `../prepare.py`。4コマ連番として使用していない。
- 大きな着火爆発は全体不採用。中央の狭い範囲だけ `root.png` とし、短い接触に使用する。奥の炎、低い手前の炎、燃焼裂片は部分採用した。
- 水面：`../../fox_bloom/art/water_source.png` を参照。元はGPT Image生成。生成指示と出典は同フォルダのREADMEとprompts。局所反射だけに使用し、開花や常設池は引き継がない。
- 煙：`../../fox/art/smoke.png` を参照。同作業のGPT Image生成素材。元生成物と指示は同フォルダREADME。
- 新たな外部素材は追加していない。Jettelly／Kenneyの既存素材集は今回の新スキル主演出では使用していない。併用できる既存通常着弾の出典・ライセンスは `../../fox/art/` に残す。

桜の気配は裂片の丸みと切れ目の連想に留めている。明確に桜と読める形を達成したとは判定しない。

## 桜を強める改訂

`sakura_burst.png` はGPT Imageで生成。原本 `/workspace/generated_images/exec-4ff5f9ed-c859-45da-bf1c-e553e9d32d55.png` を保持しコピーした。指示は `../prompts/sakura_burst.txt`。ユーザーの「桜の気配を派手に、通常攻撃との差を」という追加評価に対応する。炎の材質と五つの裂け目を部分採用し、全形を長く保持しない。詳しい採否は `dev/design/fox_fire_gust/SAKURA_REVISION.md`。前の「桜の連想は未達」という記録は改訂前の評価。
