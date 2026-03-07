# 8-Puzzle Solver - Assignment 1

**Student:** Marwan Ahmed  
**Course:** Artificial Intelligence - Term 8  
**Assignment:** Assignment 1

## Overview

This project implements a comprehensive 8-puzzle solver using multiple AI search algorithms. The 8-puzzle is a sliding puzzle that consists of a 3×3 grid with 8 numbered tiles and one blank space. The goal is to rearrange the tiles from a random initial configuration to reach the goal state.

### Goal State

```
┌─────┬─────┬─────┐
│     │  1  │  2  │
├─────┼─────┼─────┤
│  3  │  4  │  5  │
├─────┼─────┼─────┤
│  6  │  7  │  8  │
└─────┴─────┴─────┘
```

## Features

### 1. **Multiple Search Algorithms**

- **BFS (Breadth-First Search)**
- **DFS (Depth-First Search)** with depth limit
- **Iterative Deepening DFS**
- **A\* Search** with Manhattan Distance heuristic
- **A\* Search** with Euclidean Distance heuristic

### 2. **Comprehensive GUI**

- Clean, modern interface
- Interactive board input with preset configurations
- Real-time visualization of solution steps
- Algorithm comparison table
- Solution tree display

### 3. **Performance Metrics**

- Nodes expanded
- Search depth
- Path cost (solution length)
- Running time
- Success/failure status

## Installation & Requirements

### Prerequisites

- Python 3.7 or higher
- tkinter (usually comes with Python)

### Running the Application

```bash
python 8_puzzle_solver.py
```

The GUI will launch automatically.

## Algorithm Details

### 1. Breadth-First Search (BFS)

**Description:** Explores all nodes at the present depth before moving to nodes at the next depth level.

**Properties:**

- **Complete:** Always finds a solution if one exists
- **Optimal:** Finds the shortest path
- **Time Complexity:** O(b^d) where b is branching factor, d is depth
- **Space Complexity:** O(b^d)

**When to use:** When you need the shortest solution and have enough memory.

### 2. Depth-First Search (DFS)

**Description:** Explores as far as possible along each branch before backtracking.

**Properties:**

- **Complete:** Only with depth limit
- **Optimal:** Does not guarantee shortest path
- **Time Complexity:** O(b^m) where m is maximum depth
- **Space Complexity:** O(bm) - much better than BFS

**When to use:** When memory is limited and solution quality is less critical.

### 3. Iterative Deepening DFS (IDDFS)

**Description:** Combines the space efficiency of DFS with the optimality of BFS by running DFS with increasing depth limits.

**Properties:**

- **Complete:** Always finds a solution if one exists
- **Optimal:** Finds the shortest path
- **Time Complexity:** O(b^d)
- **Space Complexity:** O(bd) - best of both worlds!

**When to use:** Best uninformed search algorithm for most cases.

### 4. A\* Search with Manhattan Distance

**Description:** Uses the Manhattan distance heuristic (sum of horizontal and vertical distances) to guide the search.

**Heuristic Formula:**

```
h(n) = Σ |current_row - goal_row| + |current_col - goal_col|
```

**Properties:**

- **Complete:** Always finds a solution
- **Optimal:** Always finds the shortest path (heuristic is admissible)
- **Time Complexity:** O(b^d) but much faster in practice
- **Space Complexity:** O(b^d)
- **Heuristic:** Admissible and consistent

**When to use:** Best choice for 8-puzzle - usually fastest and optimal.

### 5. A\* Search with Euclidean Distance

**Description:** Uses the straight-line distance to guide the search.

**Heuristic Formula:**

```
h(n) = Σ √((current_row - goal_row)² + (current_col - goal_col)²)
```

**Properties:**

- **Complete:** Always finds a solution
- **Optimal:** Always finds the shortest path
- **Faster than BFS/DFS** but slightly slower than Manhattan in practice
- **Heuristic:** Admissible but less informative than Manhattan for grid-based puzzles

**When to use:** Alternative to Manhattan; slightly less effective for 8-puzzle.

## Code Structure

```
8_puzzle_solver.py
│
├── 1) CORE DATA STRUCTURES
│   ├── PuzzleState class           # Represents a board configuration
│   ├── SearchMetrics dataclass     # Tracks algorithm performance
│   └── Helper functions            # Path reconstruction, board formatting
│
├── 2) HEURISTICS
│   ├── manhattan_distance()        # Manhattan heuristic
│   └── euclidean_distance()        # Euclidean heuristic
│
├── 3) SEARCH ALGORITHMS
│   ├── bfs_search()                # Breadth-First Search
│   ├── dfs_search()                # Depth-First Search
│   ├── iterative_deepening_dfs()   # IDDFS
│   └── a_star_search()             # A* with configurable heuristic
│
├── 4) VALIDATION + INPUT UTILITIES
│   ├── inversion_count()           # Count board inversions
│   ├── is_solvable()               # Check if puzzle is solvable
│   └── parse_board_input()         # Parse user input
│
├── 5) APP-FACING LOGIC
│   └── run_selected_algorithm()    # Main orchestrator
│
├── 6) GUI TEXT FORMATTERS
│   ├── metrics_report_text()       # Format algorithm results
│   ├── comparison_table_text()     # Format comparison table
│   └── solution_tree_text()        # Format solution path tree
│
├── 7) GUI LAYER
│   └── PuzzleSolverApp class       # Main GUI application
│
└── 8) MAIN ENTRY POINT
    └── main()                      # Application entry point
```

## Usage Guide

### Using the GUI

1. **Enter Board Configuration:**
   - Manually enter numbers 0-8 (0 represents the blank tile)
   - Or use preset buttons: Easy, Medium, Goal, Clear

2. **Select Algorithm:**
   - Choose from dropdown menu
   - Or select "Run All Algorithms" to compare all methods

3. **Solve:**
   - Click "Solve" button
   - View results in the output panel

4. **Visualize Solution:**
   - Select algorithm from visualization dropdown
   - Use Prev/Next buttons to step through solution
   - Click "Play" for automatic playback

### Example Test Cases

#### Easy Configuration (5 moves)

```
1 2 5
3 4 8
6 0 7
```

#### Medium Configuration (21 moves)

```
1 8 2
0 4 3
7 6 5
```

#### Hard Configuration (27 moves)

```
8 6 7
2 5 4
3 0 1
```

#### Unsolvable Configuration

```
1 2 3
4 5 6
8 7 0
```

_Note: Has odd number of inversions, therefore unsolvable_

## Solvability Check

The program automatically checks if a puzzle configuration is solvable before attempting to solve it.

**Rule:** For the 8-puzzle, a configuration is solvable if and only if the number of **inversions** is **even**.

**Inversion:** A pair of tiles (a, b) where a appears before b in the board but a > b (excluding the blank tile).

### Example:

```
Board: [1, 2, 5, 3, 4, 0, 6, 7, 8]
Inversions: (5,3), (5,4) = 2 inversions (EVEN)
Result: Solvable ✓
```

## Performance Comparison

Typical performance on an easy puzzle (4-move solution):

| Algorithm       | Nodes Expanded | Path Cost | Time (sec) |
| --------------- | -------------- | --------- | ---------- |
| BFS             | 15-20          | 4         | ~0.001     |
| DFS             | 5-50           | 4-50      | ~0.001     |
| Iterative DFS   | 20-30          | 4         | ~0.001     |
| A\* (Manhattan) | 8-12           | 4         | ~0.0005    |
| A\* (Euclidean) | 10-15          | 4         | ~0.0006    |

**Winner:** A\* with Manhattan Distance - Fewest nodes expanded, optimal solution, fastest time! **BEST**

## Key Implementation Details

### 1. State Representation

- Board stored as immutable tuple for hashability
- Allows efficient use in sets and dictionaries
- Blank tile represented as 0

### 2. Visited Set

- All algorithms use a visited set to avoid cycles
- Prevents infinite loops and redundant work
- Critical for performance

### 3. Priority Queue for A\*

- Uses Python's heapq module
- Tuple ordering: (f_score, g_score, state)
- g_score as tiebreaker ensures consistent behavior

### 4. Depth Limit for DFS

- Default max depth: 50
- Prevents infinite recursion
- Can be adjusted based on problem difficulty

### 5. Path Reconstruction

- Each state stores reference to parent
- Backtrack from goal to start
- Reverse to get forward path

## Testing & Validation

The code includes comprehensive validation:

1. **Input Validation**
   - Checks for exactly 9 values
   - Ensures each digit 0-8 appears exactly once
   - Provides clear error messages

2. **Solvability Check**
   - Calculates inversion count
   - Warns user before attempting unsolvable puzzles

3. **Algorithm Correctness**
   - All algorithms tested on multiple configurations
   - Verified against known optimal solutions
   - Edge cases handled (already solved, unsolvable)

## Future Enhancements

Possible improvements:

1. **More Heuristics:**
   - Misplaced tiles heuristic
   - Linear conflict heuristic
   - Pattern database heuristics

2. **Advanced Algorithms:**
   - IDA\* (Iterative Deepening A\*)
   - Bidirectional search
   - Parallel search

3. **Features:**
   - Save/load puzzle configurations
   - Animation speed control
   - Statistics export
   - Custom goal states

## Common Issues & Solutions

### Issue: "Unsolvable Board" message

**Solution:** The puzzle configuration has an odd number of inversions. Try a different configuration or use preset buttons.

### Issue: DFS finds very long solution

**Solution:** This is expected behavior. DFS is not optimal. Use BFS, IDDFS, or A\* for shortest paths.

### Issue: Slow performance on hard puzzles

**Solution:**

- Use A\* with Manhattan distance (fastest)
- Avoid DFS for complex puzzles
- Consider increasing timeout or depth limit

## References

1. Russell, S., & Norvig, P. (2020). _Artificial Intelligence: A Modern Approach_ (4th ed.)
2. Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). _A Formal Basis for the Heuristic Determination of Minimum Cost Paths_
3. Korf, R. E. (1985). _Depth-first iterative-deepening: An optimal admissible tree search_

## License

This project is created for educational purposes as part of the Artificial Intelligence course.

## Contact

For questions or issues, please contact:

- **Student:** Marwan Ahmed
- **Course:** Artificial Intelligence - Term 8

---

**Note:** This implementation prioritizes code clarity and educational value. All algorithms include detailed comments and docstrings explaining their operation.
