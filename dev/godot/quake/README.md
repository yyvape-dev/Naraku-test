# 赤黒い剣戟と地割れの候補演出

GPT Image原画をGodot 4.6.3で動かし、HTML Canvas用の床／空中アトラスへ書き出す。斬撃から広範囲へ亀裂が伸び、岩が隆起、粉塵が舞い、割れ目が減衰しながら脈打つ。岩は約1.8秒まで残り、2.4秒で消える。

```sh
godot --path dev/godot/quake
# 描画可能なディスプレイで実行（今回はXorg dummy＋Mesa llvmpipe）：
godot --path dev/godot/quake --rendering-method gl_compatibility --audio-driver Dummy -- --bake
python3 dev/godot/quake/pack.py
python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets
```

58コマ／2.4秒。初動40fps、拡散25fps、残留15fps、崩壊25fps。timeline.jsonに各時刻を記録。床256px・空中224pxの8×8アトラス。pack.pyでpremultiplied RGBをstraight alphaへ補正。配布1,030,912bytes、復号29,622,272bytes。PNG連番と.godotはGit対象外。

床は敵の下、空中は味方の上。アンカー(0.5,0.5625)。ダメージ130・命中0.16秒・範囲88・押し戻し44・装填9秒を維持。残留岩は視覚演出で追加ダメージなし。

通常ゲームは従来演出。試作は?quakefx=godot。比較ページdev/mock/quake_demo.htmlで再生、停止、スロー、時間指定、床／空中の表示切替が可能。quake.gdのflagsでblade/cracks/ridge/dust/pulse/debrisを構成する。素材未読込時は従来演出へフォールバック。

原画の出典はart/README.md。実機Safariの負荷と最終採用は未確認。

2026-10-14 光量調整：斬撃の芯を明るくし、亀裂の光の常時成分・脈動を増幅。近傍の発光部分だけを抽出して淡い赤色のにじみを追加し、岩全体は明るくしない。演出時間と戦闘処理は維持。

## 乾坤一擲の候補

```sh
godot --path dev/godot/quake --rendering-method gl_compatibility --audio-driver Dummy rift.tscn -- --bake
python3 dev/godot/quake/pack.py --rift
python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets
```

rift.gdは専用原画art/rift_scar.pngの連続したジグザグの裂け目と剥離岩盤を、手前から奥へ不均等な速度で開く。7区間の連続した剣戟、飛散岩と薄い粉塵、裂け目から突き出す赤黒い発光を重ねる。主役の岩盤は一枚の連続地形で、同じ岩の塊を並べない。補助の飛散岩・煙と発光shaderは既存素材を共有する。

75コマ25fps、3秒、床／空中各1アトラス。脈動は0.5秒周期、2.52秒から崩壊。HTML側も初動と0.5秒周期で画面を振動させる。

候補の切替は?riftfx=godot。比較はdev/mock/rift_demo.html。初撃90、地割れ3秒・40dps・0.5秒刻み、列半幅30と鈍足は従来どおり。斬撃の進行は視覚演出で、初撃の判定を遅らせない。通常ゲームと超必殺の天地開闢には適用しない。rift_spikes.pngは旧候補の原画として保持。
