from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    lab2_path = repo_root / "lab2"
    sys.path.insert(0, str(lab2_path))

    from connect4.gui import Connect4App

    app = Connect4App()
    app.run()


if __name__ == "__main__":
    main()
