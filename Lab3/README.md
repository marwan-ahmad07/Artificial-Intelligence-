# Sudoku AI Solver

## Description
This application is a Sudoku game and AI solver developed as part of Artificial Intelligence Lab 3. It models the game as a Constraint Satisfaction Problem (CSP) and uses Arc Consistency (AC-3) and Backtracking algorithms to solve puzzles of varying difficulties.

## Files Included
- sudoku_gui.py: The main Graphical User Interface for the application.
- sudoku_solver.py: The core AI logic containing the CSP representation, AC-3, and Backtracking algorithms.
- benchmark.py: A script used to generate performance metrics for the report.

## Requirements
- Python 3.x
- tkinter (Standard GUI library for Python)

## How to Run
Navigate to the directory containing the files and execute the GUI script:
python3 sudoku_gui.py

## Features

Mode 1: Generate and AI Solves
Select a difficulty (easy, intermediate, or hard) and click "Generate Puzzle" to create a solvable board. You can then use the AI to solve it by clicking either "Solve (AC-3 Only)" or "Solve (MAC/Backtrack)".

Mode 2: User Input
Clear the board and manually type in your own Sudoku puzzle. The application will validate if your input is solvable before allowing the AI to solve it.

Mode 3: Interactive Play (Bonus)
Play Sudoku interactively. When you type a number, the application validates your input in real-time. If you violate a Sudoku constraint (row, column, or 3x3 grid), the cell turns red and a warning is displayed.
