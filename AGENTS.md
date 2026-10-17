# Naraku-test 制作指示

スキル・攻撃・着弾などのVFXを制作、変更、レビューするときは、先に [.agents/skills/naraku-vfx/SKILL.md](.agents/skills/naraku-vfx/SKILL.md) を読み、その工程と評価傾向を踏襲する。ユーザーが継続適用を指定した制作スキルである。新しいユーザー指示を優先する。

現在地と過去の判断は dev/HANDOFF.md の最新追記、制作手順は dev/godot/quake/README.md を確認する。候補演出の公開と通常ゲームへの採用を区別する。

## 公開ビルド（2026-10-16〜リンク方式。Claude・Codex共通）

- 公開ページの index.html は画像を埋め込まない「リンク方式」で作る：`python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets --link dev/assets/`。画像は dev/assets から読む（`?v=<中身のハッシュ>` 付き）。
- 確認は http で行う（file:// では canvas の getImageData が使えない）：リポジトリ直下で `python3 -m http.server 8765` → `python3 dev/tests/smoke.py http://127.0.0.1:8765/index.html …` と `python3 dev/tools/dev/boot.py http://127.0.0.1:8765/index.html …`。
- 画像入りの1ファイル版は必要なときだけ `--link` なしで作業フォルダへ出し、コミットしない。
- 本番 yyvape-dev/Naraku もテスト版と同じ dev/ 構成・同じリンク方式（2026-10-16 にテスト版の内容をそのまま本番へ反映）。本番へ出すときは、テスト版の dev/ と index.html をコピーする。

## 敵キャラの追加（2026-10-17〜継続）

- 生成のたびに、既存敵のサイズ・画風・足元アンカーを参照するよう指示する。
- 1体8コマ。最初の4コマは前進、後ろの4コマは攻撃。浮遊型は前半を浮遊移動にする。毎回の生成指示にこの構成を明記する。
- 移動と攻撃のコマ範囲を分けて再生する。原画は1体ずつ高解像度で生成し、本体400px以上を目安に画素数を保持する（220pxに縮小しない）。顔と体は正面向きで、画面手前へ前進する。実戦の表示高は既存通常敵の70〜88を参考にする。ボスの表示高を通常敵へ流用しない。

## 異変・街の噂と最新引き継ぎ（2026-10-17）

Claude向けの現在地は [dev/CLAUDE_HANDOFF.md](dev/CLAUDE_HANDOFF.md)、異変の確定仕様は [dev/OMENS_SPEC.md](dev/OMENS_SPEC.md) を参照。属性判定は全攻撃をキャラ固有属性へ統一し、技別の例外を追加しない。噂の閉状態は酒場アイコン＋「酒場の噂を聞く」だけの1行。過去の長い常設表示へ戻さない。最新のユーザー指示を優先する。
