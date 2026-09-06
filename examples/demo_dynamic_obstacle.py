from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    demo = Path(__file__).with_name("demo_navigation.py")
    raise SystemExit(subprocess.call([sys.executable, str(demo), "--scenario", "two_routes", *sys.argv[1:]]))
