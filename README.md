<div align="center">
  <h1>🧠 Artificial Intelligence Engineering Labs</h1>
  <p><em>A comprehensive collection of intelligent agents, search algorithms, and adversarial game engines.</em></p>
</div>

---

## 📌 Overview

This repository contains my core laboratory assignments and projects for the **Artificial Intelligence** course (Term 8). The projects are implemented in **Python** and demonstrate advanced problem-solving techniques using state-space search, constraint satisfaction, and adversarial game theory.

## 📂 Laboratory Breakdown

### 🔹 [Lab 1: Search Algorithms](./Lab1)
Implementation of fundamental artificial intelligence search strategies to navigate state spaces and reach goal configurations.
- **Uninformed Search**: Breadth-First Search (BFS), Depth-First Search (DFS).
- **Informed Search**: A* Search with custom heuristic functions.
- **Application**: Solving deterministic pathfinding problems while analyzing time and space complexity.

### 🔹 [Lab 2: Adversarial Search (Connect 4 AI Engine)](./lab2)
Development of an intelligent game-playing agent capable of playing Connect 4 at a highly competitive level.
- **Algorithm**: Minimax algorithm with **Alpha-Beta Pruning** to drastically reduce computation time.
- **Heuristics**: Advanced board evaluation heuristics to score configurations dynamically.
- **Visualization**: Real-time rendering of the AI's principal variation decision tree.

### 🔹 [Lab 3: Constraint Satisfaction (Sudoku CSP Solver)](./Lab3)
Engineering an intelligent agent capable of solving complex Sudoku puzzles using Constraint Satisfaction Problem (CSP) techniques.
- **Algorithm**: Backtracking Search across variable assignments.
- **Optimization**: Integrated **Arc Consistency (AC-3/MAC)** for rigorous constraint propagation, significantly pruning the search space.
- **Benchmarking**: Performance evaluation across varying puzzle difficulties with a graphical user interface.

### 🔹 [Lab 4: Reinforcement Learning (Gridworld Planning)](./Lab4%20new/rl_lab4)
Implementation of classic reinforcement learning planning methods to solve a Gridworld environment.
- **Algorithms**: Value Iteration and Policy Iteration for optimal policy derivation.
- **Visualization**: Interactive GUI to visualize the agent's policy and state values.
- **Testing**: Unit tests validating algorithm correctness on standard scenarios.

---

## ⚙️ Technologies & Tools
- **Language**: Python 3.x
- **Core Concepts**: Graph Theory, Game Theory, Constraint Satisfaction, Heuristic Evaluation

## 🚀 How to Run
Each laboratory folder contains its own independent source code and specific instructions.
1. Clone the repository.
2. Navigate to the specific lab directory (e.g., `cd lab2`).
3. Execute the primary Python script to launch the AI agent.
