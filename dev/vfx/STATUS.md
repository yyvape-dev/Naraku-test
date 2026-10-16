# VFX作業の現在地

## 2026-10-16 戦略カードの操作・発動表示

- GitHub mainを取得してローカルで修正。公開pushは未承認・未実施。
- 戦略カードは1回目で青く発光して選択、同じカードの2回目で発動。戦場タップでは発動しない。別の札を選ぶと選択対象が変わる。
- 発動時は既存の戦略裏面・該当表面・カード枠を用い、画面前面で0.7秒の反転表示。0.72秒でDOMを破棄。操作は遮らず、効果の発生時刻・数値・20秒装填は維持。
- 動きを減らす設定では回転を省略し、表面の短い表示とする。
- 画像記録：dev/reports/strategy-confirm/。実機Safariは未確認。

## 次の調査（未実施）

狐火は品質未達・未採用。再生成を急がず、VFX Crafterの制作記録・公開コード・動画を調べ、利用できる工程・スキル・検証方法を検討する。Unity／Unrealへの移行は未決定。

- https://devpost.com/software/unreal-engine-visual-effects-designer-for-ai-game-developers
- https://github.com/dweihan9288/VFX-Crafter-Build-Week

今回取得した公開mainにはdev/vfx/STATUS.mdがなかったため、本ファイルを新規作成。前チャットの未公開記録を復元したものではない。

検証結果：戦略6種×4画面サイズのタッチ・全効果の既存テスト成功、一般回帰smoke RESULT OK（9/12・11/12）、JSエラーなし。戦場タップ・選択変更・停止中入力・演出片付けも確認。

## 2026-10-16 追加指示

戦略カード全6種のクールタイムを30秒から20秒に短縮。追撃の効果時間10秒は維持。ユーザーの「実装していいよ」を受け、操作・反転演出を通常版へ組み込み。公開pushは未実施。
20秒版strategy_slots.py：全6種×4画面サイズ、効果・20秒補充の検証成功、JSエラーなし。

## GitHub反映

ユーザーの「いや、GitHubにだよ」により公開push承認済み。戦略カード操作・反転演出・20秒装填を本追記と同一コミットでNaraku-test/mainへ反映。上記の未承認・未実施の記述は作業途中の履歴。

## 2026-10-16 影しばり（影縫い）リベンジ試作

ユーザー添付blue_purple_vfx_keyframes_transparent_png.zipの青紫5枚で制作。原画はdev/godot/shadow_bind/artに無変更保存。Godot 4.6.3のUV移流・ねじれ・ノイズ消失、限定したGlow、GPU粒子32個、床/空中2層。1.8秒・54コマ。通常/最大範囲・3シードの戦闘一致と命中0.16秒・鈍足4.5秒・装填8秒・追撃・フォールバック・片付けを検証済み。

確認入口はdev/mock/shadow_bind_demo.html（スロー・停止・時点・最大拡大・レイヤ）、ゲームは?shadowfx=godot。通常採用は未決定、無指定は従来。比較用の候補としてGitHubへ反映する。レポートdev/reports/shadow-bind/REPORT.md。最大で粗さ・遮蔽が出たため1024px実描画/空中512pxと拡大時の透明度を調整。復号約61.6MiB追加、実機Safari未確認。VFX Crafter調査は未実施のまま、ユーザー指示で本試作を先行。

## 2026-10-16 影しばり：2倍速と控えめな光

ユーザー指定で54コマを60fps再生、絵の長さを1.8→0.9秒へ。命中0.16秒と収束約0.39秒に青紫の短い光だまり・小さなにじみ、帯の明るい芯を最大約16%増。Godotで再描画。命中・ダメージ・鈍足・装填は維持。比較ページの時点範囲と説明・キャッシュ識別も更新。詳細dev/reports/shadow-bind/2x-light/REPORT.md。通常採用は引き続き未決定、?shadowfx=godotで候補。
検証済み：通常/最大×3シードの戦闘一致、0.9秒寿命、2端末サイズ、比較操作。JSエラーなし。GitHubへ更新する。

## 2026-10-16 広がる青黒〜紫のぼかした円

ユーザー指定で床レイヤーへ追加。内側は青黒い影、ぼかした縁と内側の薄い霧は青紫の光。中心から広がって薄れ、敵の後ろに描く。影の帯・前回の控えめな光・2倍速0.9秒は維持。ゲーム数値は変更しない。比較ページの「足元の影・柔らかな円」で切替可能。制作はGodotの床2パスを再出力、空中アトラスは変更しない。
円の実画面レビュー・通常/最大×3シードの戦闘一致・命中/鈍足/寿命/追撃/フォールバック検証が成功、JSエラーなし。レポートdev/reports/shadow-bind/soft-circle/REPORT.md。空中WebP未変更、床の四辺alpha=0。GitHubへ候補を更新する。

## 2026-10-16 公開比較ページの黒画面対策

ユーザー報告を受け公開URLをChromiumで実ブラウザ確認。こちらでは再現せず、JS/通信エラーなし。ただし約51MBのゲーム本体をiframe2枚で同時読込していたため、比較専用HTML約501KB＋必要素材約8.9MBへ分離。1プレイヤーで従来/試作を切替。進捗・失敗・再読み込みの表示を追加、読込中の黒い旧フレームを隠す。デコード後に表示し、比較はセーブに触らない。index.htmlとVFX内容は変更なし。ユーザー端末の直接原因は未確定。
軽量版をChromium/WebKitで起動し、実Canvasの戦場/VFX描画・切替・最大範囲・保存無効・失敗表示を確認。実機Safari未確認。素材/プレイヤーの内容ハッシュでキャッシュ対策済み。公開URLでも実ブラウザ検証する。
公開済みa9bca38の実URLをChromium/WebKitで確認し、両方で戦場/VFXが描画（約3.87秒/8.52秒）。切替・最大・失敗案内も成功。WebKit選択欄のコントラストも追加調整。

## 2026-10-16 RIFE v4.6 実行可否を確認

ユーザー提示のRIFE v4.6＋lavapipeを/tmpに準備し、CPUのVulkan実装で既存ラナ36→37の中間光画像と実アルファマスクを生成成功。光416×752は初回10.227秒/ウォーム2.412秒、マスク208×376は1.120秒。48→96の全体は未測定。元絵同等品質は保証せず、岩の縁のにじみ・RGB/アルファ境界を確認する。dev/reports/rife-proof/README.mdと比較画像を保存。ゲーム素材・公開ページは変更していない。対象連番の選択待ち。

## 2026-10-16 ラナ通常攻撃への対象訂正
ユーザー指定は必殺技VFXではなくラナの通常攻撃モーション。前のrife-proofは対象取り違えの技術試験。今回はsword.webpの12コマをRIFE v4.6＋lavapipeで24コマ化（35.48秒）。元コマ画素一致、premultiplied RGBとalphaを分離補間、6列4行。比較dev/mock/lana_attack_rife.html、速度0.45秒・命中0.2475秒維持。剣とマントの高速変形には歪みが残るため候補公開のみ、通常ゲーム未採用。詳細dev/motion/lana_rife/README.md。

## 2026-10-16 ラナ通常攻撃RIFEは不採用
ユーザーが効果の小ささと歪みを理由に不採用と決定。元の12コマを維持。比較ページは公開済み。前記の「候補・未採用」より本決定を優先する。

## 2026-10-16 シェリ超必殺・紫黒ブラックホール候補（ローカル）
ユーザー添付の透過PNG6枚を使用し、対象はシェリの超必殺と確認済み。原本1536×1536を無変更保存。Godot4.6.3で内部の差動回転・歪み・凝縮・破裂・ノイズ消失、限定Glowと固定seed GPU粒子を制作。96コマ30fps・3.2秒、床/空中2層。dev/godot/blackhole/に制作工程・素材出典・再生成手順。dev/mock/blackhole_demo.htmlが軽量比較、?blackholefx=godotでゲーム内候補、無指定は従来。通常採用・GitHub公開は未実施。
名前「永劫凍獄」・カットイン・0.05秒40ダメージ＋3秒凍結・2.4秒230ダメージ・全域範囲と各倍率は維持。吸引や追加判定なし。通常のシェリ札は従来。床は敵の後ろ、空中は敵の前/味方の後ろ・透明度68%。追加配布約5.4MiB・復号約67.5MiB。両層の四辺alpha=0。実機Safari未確認。検証記録dev/reports/blackhole/。
検証：軽量比較と配布index両方で3シード×範囲強化0/4の戦闘一致。初撃/最終撃/凍結/寿命/再開始/欠損時切替/通常札不変・カットイン・比較操作が成功、ChromiumのJSエラーなし。総合smokeは保存・探索再開まで成功、その次の探索終了で進まなくなり未完走。変更前HEADでも同じ箇所で停止するため既存問題の可能性があるが、原因は未確定。dev/reports/blackhole/REPORT.mdに制限を記録。

## 2026-10-16 シェリ超必殺候補へRIFE中割り
ユーザー「Froweflame？中割り増やすのも忘れずに」をFlowframesの意図として受け、同系統のRIFE v4.6でGodot30fps→60fps相当へ。96元コマ＋95中間＋末尾保持で192時点、3.2秒。元30fpsアトラスは維持し、中割りのみ共有アトラス2枚へ。比較の「RIFE中割り・60fps」で切替。欠損時は30fpsへ戻る。追加5,352,472bytes・復号約67.5MiB、元と合わせ約135MiB。通常採用・GitHub公開は未実施。
軽量比較と配布indexの両方で元コマ描画像素一致・中間変化・末尾保持・素材欠損切替が成功。戦闘一致・命中/凍結/寿命/再開始/フォールバック/通常札不変も再成功、切替UI・カットイン確認、JSエラーなし。急な凝縮→破裂の細部はやや柔らかくなる。dev/godot/blackhole/interpolate.py、rife.json、dev/reports/blackhole/rife-checks.json、rife-contact.png、preview60.mp4参照。実機Safari未確認。ラナ通常攻撃のRIFE不採用・元12コマ維持は変更なし。

## 2026-10-16 シェリ超必殺：GodotのGlow工程を再確認・調整
ユーザーが「ひかる、ぼやかすのGodotのスキルも」と指定。naraku-vfxのGlow/HDR/GPU粒子工程とquake_bloomを読み直し、実Godotの同時点Glowオン/オフ差分で確認。変更前も効いていたが控えめだったため、空中の明るい芯とにじみを強めた。光だけHDR・WorldEnvironment/BG_CANVAS＋Glow・黒背景の光/透明の抜きの別焼きを維持し、光専用blend_addとGPU粒子のCOLORを保つHDRシェーダーを明示。空中intensity .45→.65。通常合成の主形状と床は維持。
空中の光を再描画し、RIFE中割りも再生成。寿命3.2秒・命中/効果は維持。軽量比較と配布indexでRIFE原コマ一致・中間変化・末尾保持・欠損切替、通常/最大×3シードの戦闘一致と片付け等が再成功、JSエラーなし。新しい動画dev/reports/blackhole/preview-glow60.mp4。glow-measure.jsonとglow-before/afterに実測、glow-contact.pngに合成比較。通常採用・GitHub公開は未実施、実機Safari未確認。全工程dev/godot/blackhole/build.sh。

## 2026-10-16 GitHubテスト採用：シェリ超必殺（標準30fps）
ユーザーの「一旦テストのGitHubに実装していいよ」を受け、origin/main 6536fabのClaude修正を先に取得し統合。「起」の持ち越し状態コピー・勝利時反映、巻き戻し/敗北時の元状態保持、装備の元値(+強化分)表示、リンク方式の起動表示・先読みを維持。本番yyvape-dev/Narakuへの反映は今回行わない。
シェリ「永劫凍獄」は無指定でGodotの紫黒ブラックホール30fpsを使用。?blackholefx=legacyで従来へ戻せる。RIFEは改善が小さいため標準オフ、?blackholesmooth=1で60fps。通常起動時に中割り2枚を読まず、標準の追加復号は約67.5MiB。比較dev/mock/blackhole_demo.htmlでも標準30fps・中割りチェックで60fps。光のHDR/Glow・GPU粒子調整は両方に含む。命中/凍結/ダメージは従来。
公開ビルドは最新AGENTS.mdに従い --link dev/assets/、index.htmlは553285bytes前後（画像入り版はコミットしない）。比較プレイヤーは新しい起動ローディングを別の軽量読込へ差し替え、重なった起動幕が残らないようにした。blackhole_deploy.pyでデフォルト採用・中割りの未読込・2画面の描画、「起」の巻き戻し/勝利/敗北と装備表示の維持を検証済み。
総合smokeはClaude最新版のリンク方式へ統合後に完走、RESULT OK・エラーなし、操縦9/12・火力優先11/12。以前の「未完走」は途中経過。本検証ではChromium実行パスを指定し、既存のfavicon.ico欠損だけ204で代用。VFX素材やゲームの通信エラーは除外していない。ログdev/reports/blackhole/smoke-synced.log。

HTTPのboot操作検証も起動→出撃→戦闘→勝利→帰還→街の各施設→保存/再開まで成功、errs なし。実行パスとfavicon代用に加え、テストで勝利時刻へ飛ばす箇所を固定0.9秒待ちからsim(.5)で進め、レベルアップ/停止のタイミング差を避けた一時ハーネスを使用。製品コードの時間処理は変更なし。boot-synced.log参照。

## 次チャット向け確定状態（2026-10-16・公開確認後）
- コード公開コミット f5e7dd04dfecca3d1f174907298d50a0418bf492。Naraku-test/mainへ反映・GitHub Pages公開済み。以前の「候補・未公開」は履歴。今回、本番Narakuには出していない。
- ゲーム https://yyvape-dev.github.io/Naraku-test/?v=f5e7dd04 、比較 https://yyvape-dev.github.io/Naraku-test/dev/mock/blackhole_demo.html?v=f5e7dd04 。
- シェリ超必殺「永劫凍獄」：ユーザー原画6枚→Godotの渦/凝縮/破裂、Glow＋2D HDR＋GPU粒子。標準30fps・3.2秒、RIFE60fpsは任意。見た目の改善は小さく、急な破裂の細部は柔らかくなるため60fpsを積極的に推さない。30fpsは追加復号約67.5MiB、60fpsは合計約135MiB。無指定では中割りを通信/復号しない。?blackholesmooth=1で60fps、?blackholefx=legacyで旧演出。比較のチェックでも切替。
- 命中0.05秒40ダメージ＋3秒凍結、2.4秒230ダメージは維持。吸引・追加判定なし。ラナ通常攻撃のRIFE不採用・元12コマ維持も確定。
- Claudeの6536fabを先に取り込み、「起」の持ち越し修正・装備表示・画像リンク方式を維持。公開indexは553299bytes。再ビルドは python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets --link dev/assets/ 。巨大な画像埋込版をコミットしない。
- smoke RESULT OK（9/12・11/12）、boot操作成功、VFXの戦闘一致・時刻・削除・欠損時切替、RIFEの元コマ一致を確認。公開HTMLはローカルとSHA256一致。公開素材で375/393幅の描画・標準30fps・中割り未読込・Claude修正維持、公開比較の30/60fpsと旧演出切替を実ブラウザ確認しJSエラーなし。
- 公開ブラウザ検証ではChromiumに環境proxy CAが未登録だったため、通常TLS検証を行うPython urllibで公開レスポンスを取得してブラウザのrouteへ渡した。TLS検証は無効化していない。実機iPhone/Safariでの品質・性能は未確認。
- 制作/再生成 dev/godot/blackhole/、比較生成 dev/tools/dev/build_blackhole_player.py、検証 dev/tests/blackhole*.py、報告 dev/reports/blackhole/REPORT.md。全工程 build.sh はGodot→RIFE→リンク方式ビルド。/tmpのRIFEバイナリ/モデル/Vulkan環境は次セッションで残る保証なし。
- 次の技は未指定。作業開始時は最新mainを取得し、本書・dev/vfx/STATUS.mdの末尾に加え先頭の現状も読み、AGENTS.mdと .agents/skills/naraku-vfx/SKILL.md を確認する。Claudeとの同時更新を上書きしない。

追記：引き継ぎ保存時にClaudeの d4014c4（大地割りC案を標準採用）を検出し、その上へ本記録をリベースした。最新コードはd4014c4を含む。QUAKE_C・調整パネル「地割C」・localStorage naraku_quakeC、素材vfx_quakeC_floor/air.webpの追加を維持。詳細はHANDOFF先頭を参照。上記の公開実ブラウザ確認はシェリ公開f5e7dd0時点の結果で、d4014c4の戦闘一致/smokeはClaude側の記録。次の作業前にも最新mainを再取得すること。
