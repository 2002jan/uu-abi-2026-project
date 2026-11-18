import sys
from pathlib import Path

from panel.command import main as panel_main


def main() -> None:
    app = Path(__file__).with_name("app.py")
    sys.argv = ["panel", "serve", str(app), *sys.argv[1:]]
    sys.exit(panel_main())
