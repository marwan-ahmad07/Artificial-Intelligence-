import tkinter as tk
from tkinter import messagebox, ttk
import copy
from sudoku_solver import (
    solve_backtracking,
    generate_random_puzzle,
    is_solvable,
    solve_with_ac3,
    solve_mac,
    is_valid_assignment
)

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku AI Solver")
        self.root.geometry("600x700")
        
        self.board = [[0]*9 for _ in range(9)]
        self.cells = {}
        
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header = tk.Label(self.root, text="Sudoku AI Agent", font=("Helvetica", 24, "bold"))
        header.pack(pady=10)
        
        # Frame for the board
        board_frame = tk.Frame(self.root, bg="black", bd=2)
        board_frame.pack(pady=10)
        
        # Create the 9x9 grid
        for r in range(9):
            for c in range(9):
                # Add thicker borders for 3x3 blocks
                pady = (3, 1) if r % 3 == 0 else (1, 1)
                padx = (3, 1) if c % 3 == 0 else (1, 1)
                if r == 8: pady = (pady[0], 3)
                if c == 8: padx = (padx[0], 3)
                
                cell_frame = tk.Frame(board_frame, bg="black")
                cell_frame.grid(row=r, column=c, padx=padx, pady=pady)
                
                # Student Style: Make it look nice and clean
                entry = tk.Entry(
                    cell_frame, width=2, font=("Helvetica", 20), justify="center",
                    bd=0, bg="white", fg="blue"
                )
                entry.pack(ipady=5, ipadx=5)
                # Validation binding for interactive mode
                entry.bind("<KeyRelease>", lambda e, row=r, col=c: self.on_cell_change(row, col))
                
                self.cells[(r, c)] = entry
                
        # Controls Frame
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=10)
        
        # Mode Selection
        self.mode_var = tk.StringVar(value="Mode 1")
        tk.Radiobutton(controls_frame, text="Mode 1: Generate & AI Solves", variable=self.mode_var, value="Mode 1", command=self.update_ui).grid(row=0, column=0, padx=10)
        tk.Radiobutton(controls_frame, text="Mode 2: User Input -> AI Solves", variable=self.mode_var, value="Mode 2", command=self.update_ui).grid(row=0, column=1, padx=10)
        tk.Radiobutton(controls_frame, text="Bonus: Interactive Play", variable=self.mode_var, value="Mode 3", command=self.update_ui).grid(row=0, column=2, padx=10)

        # Action Buttons
        actions_frame = tk.Frame(self.root)
        actions_frame.pack(pady=10)
        
        # Generate puzzle (For Mode 1)
        self.diff_var = tk.StringVar(value="intermediate")
        self.diff_menu = ttk.Combobox(actions_frame, textvariable=self.diff_var, values=["easy", "intermediate", "hard"], state="readonly", width=10)
        self.diff_menu.grid(row=0, column=0, padx=5)
        
        self.btn_generate = tk.Button(actions_frame, text="Generate Puzzle", command=self.generate_puzzle, bg="#e0e0e0")
        self.btn_generate.grid(row=0, column=1, padx=5)
        
        # Solve Buttons
        self.btn_ac3 = tk.Button(actions_frame, text="Solve (AC-3 Only)", command=self.solve_ac3, bg="#a3c2c2")
        self.btn_ac3.grid(row=0, column=2, padx=5)
        
        self.btn_mac = tk.Button(actions_frame, text="Solve (MAC/Backtrack)", command=self.solve_mac_backtrack, bg="#a3c2c2")
        self.btn_mac.grid(row=0, column=3, padx=5)
        
        self.btn_clear = tk.Button(actions_frame, text="Clear Board", command=self.clear_board, bg="#ffcccc")
        self.btn_clear.grid(row=0, column=4, padx=5)
        
        # Status Label
        self.status_label = tk.Label(self.root, text="Welcome! Select a mode and start.", font=("Helvetica", 14, "bold"), fg="#006600")
        self.status_label.pack(pady=10)
        
        self.update_ui()
        
    def update_ui(self):
        """Enable/Disable features based on selected mode."""
        mode = self.mode_var.get()
        if mode == "Mode 1":
            self.btn_generate.config(state="normal")
            self.diff_menu.config(state="normal")
            self.status_label.config(text="Mode 1: Generate a puzzle then let the AI solve it.")
        elif mode == "Mode 2":
            self.btn_generate.config(state="disabled")
            self.diff_menu.config(state="disabled")
            self.status_label.config(text="Mode 2: Type in a Sudoku board, then click solve.")
        else:
            # Interactive Play
            self.btn_generate.config(state="normal")
            self.diff_menu.config(state="normal")
            self.status_label.config(text="Interactive: Type numbers! It will validate instantly.")
            
    def get_board_from_ui(self):
        """Reads the current grid from the UI into the 2D array."""
        board = [[0]*9 for _ in range(9)]
        for r in range(9):
            for c in range(9):
                val = self.cells[(r, c)].get().strip()
                if val.isdigit() and 1 <= int(val) <= 9:
                    board[r][c] = int(val)
                else:
                    board[r][c] = 0
        return board
        
    def set_board_to_ui(self, board, original_board=None):
        """Displays the 2D array on the UI."""
        for r in range(9):
            for c in range(9):
                self.cells[(r, c)].delete(0, tk.END)
                if board[r][c] != 0:
                    self.cells[(r, c)].insert(0, str(board[r][c]))
                    # If this was part of the original puzzle, make it black, else blue
                    if original_board and original_board[r][c] != 0:
                        self.cells[(r, c)].config(fg="black")
                    else:
                        self.cells[(r, c)].config(fg="blue")
                else:
                    self.cells[(r, c)].config(fg="blue")
                    
    def clear_board(self):
        for r in range(9):
            for c in range(9):
                self.cells[(r, c)].delete(0, tk.END)
                self.cells[(r, c)].config(bg="white")
        self.board = [[0]*9 for _ in range(9)]
        self.status_label.config(text="Board cleared.", fg="black")

    def generate_puzzle(self):
        diff = self.diff_var.get()
        self.board = generate_random_puzzle(diff)
        self.set_board_to_ui(self.board, original_board=self.board)
        self.status_label.config(text=f"Generated {diff} puzzle.", fg="blue")
        # Reset background colors
        for r in range(9):
            for c in range(9):
                self.cells[(r, c)].config(bg="white")
                
    def on_cell_change(self, r, c):
        """Used for Bonus Interactive Mode to validate user input on the fly."""
        if self.mode_var.get() != "Mode 3": return
        
        val = self.cells[(r, c)].get().strip()
        self.cells[(r, c)].config(bg="white")
        
        if not val: return # Empty is fine
        
        if not (val.isdigit() and 1 <= int(val) <= 9):
            self.cells[(r, c)].config(bg="#FFCCCC")
            self.status_label.config(text=f"Invalid character at ({r+1}, {c+1})", fg="#CC0000")
            return
            
        val = int(val)
        
        # Temporarily clear the board cell so is_valid_assignment works correctly
        temp_board = self.get_board_from_ui()
        temp_board[r][c] = 0 
        
        if not is_valid_assignment(temp_board, r, c, val):
            self.cells[(r, c)].config(bg="#FFCCCC")
            self.status_label.config(text=f"Constraint violation at ({r+1}, {c+1})!", fg="#CC0000")
        else:
            self.status_label.config(text="Valid move.", fg="#006600")
            
    def validate_and_prep(self):
        """Ensures the board is solvable before attempting to solve."""
        current_board = self.get_board_from_ui()
        if not is_solvable(current_board):
            messagebox.showerror("Error", "The current board state is unsolvable or invalid!")
            return None
        return current_board
        
    def solve_ac3(self):
        current_board = self.validate_and_prep()
        if not current_board: return
        
        # Solve
        success = solve_with_ac3(current_board)
        self.set_board_to_ui(current_board)
        
        if success:
            self.status_label.config(text="Solved completely using AC-3!", fg="#006600")
        else:
            self.status_label.config(text="AC-3 got stuck! Try MAC/Backtrack.", fg="#CC6600")
            
    def solve_mac_backtrack(self):
        current_board = self.validate_and_prep()
        if not current_board: return
        
        # First try MAC (Maintaining Arc Consistency)
        if solve_mac(current_board):
            self.set_board_to_ui(current_board)
            self.status_label.config(text="Solved completely using MAC/Backtrack!", fg="#006600")
        else:
            self.status_label.config(text="Failed to solve.", fg="#CC0000")

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()
