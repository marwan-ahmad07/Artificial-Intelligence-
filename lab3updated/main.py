from pathlib import Path
import sys

import tkinter as tk


ROOT_DIR = Path(__file__).resolve().parent
SUDOKO_DIR = ROOT_DIR / "Sudoko"

if str(SUDOKO_DIR) not in sys.path:
    sys.path.insert(0, str(SUDOKO_DIR))

from sudoku_gui import SudokuGUI


def main():
    root = tk.Tk()
    SudokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()