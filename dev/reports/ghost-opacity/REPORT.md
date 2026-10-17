# 5体目の幽霊に軽い透過（2026-10-17）

ユーザーが通常敵5体の実装を承認し、浮遊する5体目だけ少し透過するよう指定。

veil_ghostにopacity=0.78を設定し、描画時に既存のalphaへ掛け合わせる。通常/攻撃/調整プレビュー/被弾時の光/撃破・突破後の消失で一貫して適用し、描画後は元のalphaへ戻す。原画・WebP・解像度・8コマ構成・能力/戦闘処理は同じ。

実ブラウザのdrawImage呼び出しを記録し、新規4体の描画alpha=1、幽霊だけ0.78、被弾の追加描画は0.75×0.78=0.585と確認。opacity.json。実戦の前後比較はpreview-before.png/preview.png、battle-393.png。JSエラーなし。

既存normal_enemies.pyで5体の8コマ、自然出現、決定性、命中、浮遊霊の発射、凍結、欠損時フォールバックが成功。checks.json。リンク方式でindex.htmlを再ビルドし、JS構文とgit diff --checkも確認。

総合smoke/bootは前回と同じ環境用Chromiumハーネスで再検証。ゲームの通信エラーを除外せず、faviconだけ204。宿屋演出の完了を待ち、勝利時刻への移動はsim(.5)を使う。詳細smoke.log/boot.log。

boot操作は出撃→戦闘→勝利→帰還→各施設→写し復元→保存再開まで成功、errsなし。

透過版の総合smokeもRESULT OK・エラーなし（操縦9/12・火力優先11/12）、bootも保存再開まで成功。
