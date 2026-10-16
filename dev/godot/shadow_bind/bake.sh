#!/bin/sh
# Requires a working X11 display, Godot 4.6.3, Python + Pillow/numpy.
set -eu
cd "$(dirname "$0")"
GODOT_BIN="${GODOT:-godot}"
"$GODOT_BIN" --path . --editor --import --rendering-method gl_compatibility --rendering-driver opengl3 --audio-driver Dummy --quit
mkdir -p frames
timeout 240 "$GODOT_BIN" --path . --rendering-method gl_compatibility --audio-driver Dummy --fixed-fps 30 -- --bake
python3 pack.py
