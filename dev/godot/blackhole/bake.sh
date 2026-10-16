#!/bin/sh
set -eu
export XDG_DATA_HOME="${XDG_DATA_HOME:-/tmp/naraku-godot/data}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-/tmp/naraku-godot/config}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/tmp/naraku-godot/cache}"
cd "$(dirname "$0")"
"${GODOT:-godot}" --path . --editor --import --rendering-method gl_compatibility --rendering-driver opengl3 --audio-driver Dummy --quit
mkdir -p frames
timeout 300 "${GODOT:-godot}" --path . --rendering-method gl_compatibility --rendering-driver opengl3 --audio-driver Dummy --fixed-fps 30 -- --bake
python3 pack.py
