#!/bin/sh
# Full material -> Godot bake -> RIFE -> comparison/game build. Stops on any failure.
# Requires DISPLAY, working Godot, and RIFE/Vulkan environment (see README).
set -eu
cd "$(dirname "$0")/../../.."
sh dev/godot/blackhole/bake.sh
python3 dev/godot/blackhole/interpolate.py
python3 dev/tools/dev/build_blackhole_player.py
python3 dev/tools/embed.py dev/naraku_src.html index.html dev/assets --link dev/assets/
