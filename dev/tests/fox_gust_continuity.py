"""Compatibility entry point for the current fox-fire candidate checks."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('fox_sakura_continuity.py')),run_name="__main__")
