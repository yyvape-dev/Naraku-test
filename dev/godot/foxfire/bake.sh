#!/bin/sh
# 狐火乱舞（ユーザー原画5枚＋発光・GPU粒子）を焼いて、ゲーム形式のアトラス2枚を out/ に出す。
# 必要：Godot 4.4.1 / xvfb-run（Linux）/ Python3 + Pillow + numpy
set -e
cd "$(dirname "$0")"
G="${GODOT:-godot}"
if ! command -v "$G" >/dev/null 2>&1; then
  mkdir -p .godot-bin
  [ -x .godot-bin/godot ] || { curl -sSL -o .godot-bin/g.zip https://github.com/godotengine/godot/releases/download/4.4.1-stable/Godot_v4.4.1-stable_linux.x86_64.zip && unzip -o -q .godot-bin/g.zip -d .godot-bin && mv .godot-bin/Godot_v4.4.1-stable_linux.x86_64 .godot-bin/godot; }
  G=.godot-bin/godot
fi
mkdir -p art && cp ../../cardart/foxfire_src/vfx_frame_0*.png art/
xvfb-run -a -s "-screen 0 1024x768x24" "$G" --path . --import >/dev/null 2>&1 || true
rm -rf frames
# --fixed-fps 30 で1フレーム＝1/30秒に固定（GPU粒子を毎回同じ形に焼くため）
timeout 900 xvfb-run -a -s "-screen 0 1024x768x24" "$G" --path . --rendering-method gl_compatibility --audio-driver Dummy --fixed-fps 30 -- --bake
python3 pack.py out
