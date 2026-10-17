# ラナ（姫騎士）のユーザー原画

出典：ユーザー添付 `keyframes_16_upscaled_3x.zip`（2026-10-17）。16枚の原画とCSVを無変更で保存。

`python dev/tools/dev/lana_princess.py dev/cardart/src_lana_princess /tmp/lana-work` で固定クロップの不透明連番を用意する。全コマ共通の画角・足元を使い、上げた剣と下方向の斬撃まで収める。

RIFE：nihui/rife-ncnn-vulkan、20221029 Ubuntu版、rife-v4.6。0〜14の各隣接ペアに `-0 /tmp/lana-work/00000000.png -1 /tmp/lana-work/00000001.png -o /tmp/lana-work/mid/00000000.png -m <rife-v4.6の場所> -j 1:1:1` のように中間コマを1枚ずつ作成。背景はこの時点ではマゼンタのまま。CPU VulkanではlavapipeのICDをVK_ICD_FILENAMESで指定する。

`python dev/tools/dev/lana_princess.py dev/cardart/src_lana_princess /tmp/lana-work --pack` でマゼンタ抜き・青の色かぶり除去・可逆WebP化する。16コマの原画版と31コマの補間版を出力。原画版の16コマは補間版にも全画素一致で残る。フレーム配分は `../lana_princess.json`。命中は元8コマ目／補間15コマ目を既存HIT_AT=0.55へ合わせる。

比較ページ：`dev/mock/lana_princess.html`。補間では大きく姿勢を変える箇所で剣先が少し曲がるため、既定ではオフの試験オプション。衣装も初期値は通常。顔・カード・カットイン用の姫騎士原画は今回含まれていない。
