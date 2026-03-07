from __future__ import annotations
import heapq
import math
import time
import tkinter as tk
from collections import deque
from dataclasses import dataclass, field
from tkinter import messagebox, scrolledtext, ttk
from typing import Callable, Dict, List, Optional, Set, Tuple


# ============================================================================
# DATA STRUCTURES SECTION
# ============================================================================
# This section contains all data structures used in the 8-puzzle solver:
# - ConfigTuple: Type alias for puzzle board configuration
# - GameNode: Represents a state in the puzzle search space
# - AlgorithmStats: Stores metrics and results from search algorithms
# ============================================================================

# Type alias for representing a puzzle board configuration as a tuple of 9 integers
ConfigTuple = Tuple[int, ...]


class GameNode:
    """
    Represents a single state (node) in the 8-puzzle search space.
    
    Attributes:
        config/board: Current board configuration (tuple of 9 integers, 0 = blank)
        prev_node/parent: Reference to parent node for path reconstruction
        action/move: The action that led to this state (Up/Down/Left/Right/Initial)
        level/depth: Depth in the search tree from root (used as g(n) cost in A*)
        empty_idx/blank_pos: Index position of blank tile (0) for efficient moves
    
    Methods:
        reached_target/is_goal: Check if this is the goal state
        generate_successors/get_neighbors: Generate all valid next states
        display/print_board: Print the board in a formatted visual
    
    The class provides multiple property aliases for compatibility with different
    naming conventions and testing frameworks.
    """
    
    # Goal state configuration: blank (0) in top-left, tiles 1-8 in order
    TARGET_CONFIG: ConfigTuple = (0, 1, 2, 3, 4, 5, 6, 7, 8)
    GOAL_STATE: ConfigTuple = (0, 1, 2, 3, 4, 5, 6, 7, 8)

    def __init__(self, config: ConfigTuple, prev_node: Optional[GameNode] = None, 
                 action: str = "Initial", level: int = 0) -> None:
        # Primary attributes
        self.config = config                    # Main board configuration
        self.prev_node = prev_node              # Parent node for path tracing
        self.action = action                    # Move that created this state
        self.level = level                      # Depth from root (g-cost)
        self.empty_idx = config.index(0)        # Blank tile position
        
        # Compatibility aliases for different naming conventions
        self.board = config                     # Alias for config
        self.parent = prev_node                 # Alias for prev_node
        self.move = action                      # Alias for action
        self.depth = level                      # Alias for level
        self.blank_pos = config.index(0)        # Alias for empty_idx

    def __eq__(self, other: object) -> bool:
        """Two nodes are equal if their board configurations match."""
        return isinstance(other, GameNode) and self.config == other.config

    def __hash__(self) -> int:
        """Hash based on board config for use in sets/dicts (visited tracking)."""
        return hash(self.config)

    def __lt__(self, other: GameNode) -> bool:
        """Comparison for heap operations in priority queue (A* search)."""
        return self.config < other.config

    def reached_target(self) -> bool:
        """Check if this state is the goal state."""
        return self.config == self.TARGET_CONFIG
    
    def is_goal(self) -> bool:
        """Alias for reached_target() - check if goal state reached."""
        return self.config == self.TARGET_CONFIG

    def generate_successors(self) -> List[GameNode]:
        """
        Generate all valid successor states by moving the blank tile.
        Returns a list of GameNode objects representing valid moves.
        """
        successors: List[GameNode] = []
        row_idx, col_idx = divmod(self.empty_idx, 3)  # Convert linear index to 2D coordinates

        # Define possible moves: Up, Down, Left, Right
        action_map = [("Up", -1, 0), ("Down", 1, 0), ("Left", 0, -1), ("Right", 0, 1)]

        for action_name, row_delta, col_delta in action_map:
            new_row, new_col = row_idx + row_delta, col_idx + col_delta
            # Check if the new position is within the 3x3 board boundaries
            if 0 <= new_row < 3 and 0 <= new_col < 3:
                target_idx = new_row * 3 + new_col
                config_list = list(self.config)
                # Swap blank tile with the target tile
                config_list[self.empty_idx], config_list[target_idx] = config_list[target_idx], config_list[self.empty_idx]
                successors.append(GameNode(tuple(config_list), self, action_name, self.level + 1))

        return successors
    
    def get_neighbors(self) -> List[GameNode]:
        """Alias for generate_successors() - returns list of valid next states."""
        return self.generate_successors()

    def display(self) -> None:
        """Display the current board state in formatted view."""
        print(render_configuration(self.config))
    
    def print_board(self) -> None:
        """Alias for display() - prints board to console."""
        print(render_configuration(self.config))


def render_configuration(config: ConfigTuple) -> str:
    """
    Converts a puzzle configuration into a formatted string representation.
    Uses box-drawing characters to create a visual board.
    """
    result_lines = []
    border_top = "┌─────┬─────┬─────┐"
    separator = "├─────┼─────┼─────┤"
    border_bottom = "└─────┴─────┴─────┘"

    for row in range(3):
        row_content = []
        for col in range(3):
            tile_value = config[row * 3 + col]
            display_val = " " if tile_value == 0 else str(tile_value)
            row_content.append(f" {display_val:^3} ")
        result_lines.append("│" + "│".join(row_content) + "│")

    return "\n".join([border_top, result_lines[0], separator, result_lines[1], separator, result_lines[2], border_bottom])


@dataclass
class AlgorithmStats:
    """
    Stores comprehensive performance metrics and results from search algorithm execution.
    
    Core Metrics:
        algo_label: Name/identifier of the algorithm (e.g., "BFS", "A* Manhattan")
        visited_count: Number of nodes expanded/explored during search
        max_depth: Maximum depth reached in search tree
        solution_cost: Length of solution path (number of moves to goal)
        time_start/time_end: Timestamps for measuring execution time
        action_sequence: Ordered list of moves from start to goal
        node_sequence: Ordered list of board states from start to goal
        found_solution: Boolean indicating if goal was successfully reached
    
    Property Aliases:
        Provides alternative names for compatibility (algorithm_name, nodes_expanded,
        search_depth, path_cost, etc.)
    """
    algo_label: str                                          # Algorithm name
    visited_count: int = 0                                   # Nodes explored
    max_depth: int = 0                                       # Max search depth
    solution_cost: int = 0                                   # Path length
    time_start: float = 0.0                                  # Start timestamp
    time_end: float = 0.0                                    # End timestamp
    action_sequence: List[str] = field(default_factory=list)     # Move sequence
    node_sequence: List[GameNode] = field(default_factory=list)  # State sequence
    found_solution: bool = False                             # Success flag
    
    # Property aliases for compatibility with different naming conventions
    @property
    def algorithm_name(self) -> str:
        """Alias for algo_label."""
        return self.algo_label
    
    @property
    def nodes_expanded(self) -> int:
        """Alias for visited_count."""
        return self.visited_count
    
    @property
    def search_depth(self) -> int:
        """Alias for max_depth."""
        return self.max_depth
    
    @property
    def path_cost(self) -> int:
        """Alias for solution_cost."""
        return self.solution_cost
    
    @property
    def start_time(self) -> float:
        """Alias for time_start."""
        return self.time_start
    
    @property
    def end_time(self) -> float:
        """Alias for time_end."""
        return self.time_end
    
    @property
    def path_moves(self) -> List[str]:
        """Alias for action_sequence."""
        return self.action_sequence
    
    @property
    def path_states(self) -> List[GameNode]:
        """Alias for node_sequence."""
        return self.node_sequence
    
    @property
    def success(self) -> bool:
        """Alias for found_solution."""
        return self.found_solution

    def elapsed_time(self) -> float:
        """Calculate total algorithm execution time in seconds."""
        return self.time_end - self.time_start
    
    def running_time(self) -> float:
        """Alias for elapsed_time() - returns execution time in seconds."""
        return self.elapsed_time()

    def generate_report(self) -> None:
        """Print a formatted console report of algorithm performance and results."""
        print(f"\n{'=' * 60}")
        print(f"Algorithm: {self.algo_label}")
        print(f"{'=' * 60}")
        print(f"Solution Found: {'YES' if self.found_solution else 'NO'}")
        print(f"Path Cost: {self.solution_cost}")
        print(f"Nodes Expanded: {self.visited_count}")
        print(f"Search Depth: {self.max_depth}")
        print(f"Running Time: {self.elapsed_time():.6f} seconds")
        print(f"Path to Goal ({max(0, len(self.action_sequence) - 1)} steps):")
        for idx, action in enumerate(self.action_sequence):
            if action != "Initial":
                print(f"  Step {idx}: {action}")
        print(f"{'=' * 60}")


# ============================================================================
# ALGORITHMS SECTION
# ============================================================================
# This section contains all search algorithms, heuristics, and utility functions:
#
# HELPER FUNCTIONS:
#   - trace_back_path: Reconstruct solution path from goal to start
#
# HEURISTIC FUNCTIONS (for informed search):
#   - compute_manhattan_cost: Manhattan distance heuristic (h1)
#   - compute_euclidean_cost: Euclidean distance heuristic (h2)
#
# UNINFORMED SEARCH ALGORITHMS:
#   - breadth_first_strategy: BFS - optimal, explores level-by-level
#   - depth_first_strategy: DFS - memory efficient, uses depth limit
#   - iterative_depth_strategy: IDDFS - combines BFS optimality + DFS efficiency
#
# INFORMED SEARCH ALGORITHMS:
#   - informed_search_strategy: A* search with pluggable heuristic function
#
# VALIDATION & UTILITY:
#   - count_inversions: Count tile order inversions for solvability check
#   - check_solvability: Determine if puzzle configuration is solvable
#   - parse_input_string: Parse user input into board configuration
#   - execute_algorithm: Main dispatcher to run selected algorithm(s)
#   - format_stats_report: Format algorithm results as text
#   - format_comparison_table: Create comparison table for multiple algorithms
#   - format_tree_visualization: Generate solution tree visualization
# ============================================================================

def trace_back_path(target_node: GameNode) -> Tuple[List[str], List[GameNode]]:
    """
    Reconstructs the solution path from start to goal by following parent pointers.
    Returns a tuple of (actions, nodes) representing the path.
    """
    actions: List[str] = []
    nodes: List[GameNode] = []
    current: Optional[GameNode] = target_node
    while current is not None:
        actions.append(current.action)
        nodes.append(current)
        current = current.prev_node
    actions.reverse()
    nodes.reverse()
    return actions, nodes


def compute_manhattan_cost(node: GameNode) -> int:
    """
    Calculates Manhattan distance heuristic (h(n)) for A* search.
    For each tile, computes the sum of horizontal and vertical distances
    from its current position to its goal position.
    This is an admissible heuristic (never overestimates the cost).
    """
    total_cost = 0
    for idx, tile in enumerate(node.config):
        if tile != 0:
            curr_row, curr_col = divmod(idx, 3)
            target_row, target_col = divmod(tile, 3)
            total_cost += abs(curr_row - target_row) + abs(curr_col - target_col)
    return total_cost


def compute_euclidean_cost(node: GameNode) -> float:
    """
    Calculates Euclidean distance heuristic (h(n)) for A* search.
    For each tile, computes the straight-line distance from its current
    position to its goal position using the Pythagorean theorem.
    This is also an admissible heuristic.
    """
    total_cost = 0.0
    for idx, tile in enumerate(node.config):
        if tile != 0:
            curr_row, curr_col = divmod(idx, 3)
            target_row, target_col = divmod(tile, 3)
            total_cost += math.sqrt((curr_row - target_row) ** 2 + (curr_col - target_col) ** 2)
    return total_cost


def breadth_first_strategy(start_node: GameNode) -> AlgorithmStats:
    """
    Breadth-First Search (BFS) - Uninformed search algorithm.
    
    Strategy: Explores nodes level by level using a queue (FIFO).
    Guarantees: Finds the shortest path (optimal for uniform cost).
    Completeness: Complete if solution exists.
    Time Complexity: O(b^d) where b=branching factor, d=depth
    Space Complexity: O(b^d) - stores all nodes at current level
    """
    stats = AlgorithmStats("BFS (Breadth-First Search)")
    stats.time_start = time.time()

    # Quick check: If start state is already the goal, return immediately
    if start_node.reached_target():
        stats.found_solution = True
        stats.time_end = time.time()
        stats.action_sequence = ["Initial"]
        stats.node_sequence = [start_node]
        return stats

    # Initialize frontier (FIFO queue) and explored set (visited tracking)
    frontier = deque([start_node])        # Queue for BFS level-by-level expansion
    explored: Set[GameNode] = {start_node}  # Track visited states to avoid cycles

    # Main BFS loop: process nodes level by level
    while frontier:
        current_node = frontier.popleft()  # Get next node from front of queue
        stats.visited_count += 1            # Increment expanded nodes counter
        stats.max_depth = max(stats.max_depth, current_node.level)  # Track depth

        # Generate and process all valid successor states
        for successor in current_node.generate_successors():
            if successor in explored:
                continue  # Skip already visited states

            explored.add(successor)  # Mark as visited

            # Goal test: if we found the solution
            if successor.reached_target():
                stats.solution_cost = successor.level
                stats.max_depth = max(stats.max_depth, successor.level)
                stats.found_solution = True
                stats.action_sequence, stats.node_sequence = trace_back_path(successor)
                stats.time_end = time.time()
                return stats

            # Add to queue for later exploration
            frontier.append(successor)

    # No solution found after exploring all reachable states
    stats.time_end = time.time()
    return stats


def depth_first_strategy(start_node: GameNode, depth_cap: int = 50) -> AlgorithmStats:
    """
    Depth-First Search (DFS) - Uninformed search algorithm.
    
    Strategy: Explores as deep as possible before backtracking (uses stack/recursion).
    Guarantees: Does NOT guarantee optimal solution.
    Completeness: Complete only with depth limit (to avoid infinite loops).
    Time Complexity: O(b^m) where m=maximum depth
    Space Complexity: O(bm) - only stores path from root to current node
    """
    stats = AlgorithmStats("DFS (Depth-First Search)")
    stats.time_start = time.time()
    explored: Set[GameNode] = set()

    def explore_depth(node: GameNode) -> Optional[GameNode]:
        """Recursive DFS helper with depth limit and cycle detection."""
        # Prune if already explored or exceeded depth limit
        if node in explored or node.level > depth_cap:
            return None

        explored.add(node)  # Mark as visited
        stats.visited_count += 1
        stats.max_depth = max(stats.max_depth, node.level)

        # Goal test at current node
        if node.reached_target():
            return node

        # Recursively explore each successor (go deep first)
        for successor in node.generate_successors():
            outcome = explore_depth(successor)
            if outcome is not None:
                return outcome  # Solution found in this branch

        return None  # No solution in this branch

    # Start the recursive DFS exploration
    solution_node = explore_depth(start_node)

    # Build solution path if goal was found
    if solution_node is not None:
        stats.solution_cost = solution_node.level
        stats.found_solution = True
        stats.action_sequence, stats.node_sequence = trace_back_path(solution_node)

    stats.time_end = time.time()
    return stats


def iterative_depth_strategy(start_node: GameNode, max_limit: int = 50) -> AlgorithmStats:
    """
    Iterative Deepening Depth-First Search (IDDFS).
    
    Strategy: Repeatedly performs DFS with increasing depth limits (0, 1, 2, ...).
    Combines benefits of BFS (optimal, complete) and DFS (memory efficient).
    Guarantees: Finds optimal solution like BFS.
    Time Complexity: O(b^d) - similar to BFS despite repeated work
    Space Complexity: O(bd) - memory efficient like DFS
    """
    stats = AlgorithmStats("Iterative Deepening DFS")
    stats.time_start = time.time()

    def depth_limited_search(node: GameNode, limit: int, explored: Set[GameNode]) -> Optional[GameNode]:
        if node.level > limit or node in explored:
            return None

        explored.add(node)
        stats.visited_count += 1
        stats.max_depth = max(stats.max_depth, node.level)

        if node.reached_target():
            return node

        for successor in node.generate_successors():
            outcome = depth_limited_search(successor, limit, explored)
            if outcome is not None:
                return outcome

        return None

    # Incrementally increase depth limit from 0 to max_limit
    # Each iteration runs a complete DFS up to that depth
    for current_limit in range(max_limit + 1):
        solution_node = depth_limited_search(start_node, current_limit, set())
        if solution_node is not None:
            # Solution found at this depth limit
            stats.solution_cost = solution_node.level
            stats.found_solution = True
            stats.action_sequence, stats.node_sequence = trace_back_path(solution_node)
            stats.time_end = time.time()
            return stats

    # No solution found within max depth limit
    stats.time_end = time.time()
    return stats


def informed_search_strategy(start_node: GameNode, cost_function: Callable[[GameNode], float], 
                             function_label: str) -> AlgorithmStats:
    """
    A* Search - Informed search algorithm using heuristics.
    
    Strategy: Uses f(n) = g(n) + h(n) where:
              g(n) = actual cost from start to node n
              h(n) = estimated cost from node n to goal (heuristic)
    Uses a priority queue to always expand the most promising node.
    
    Guarantees: Optimal if heuristic is admissible (never overestimates).
    Completeness: Complete if solution exists.
    Time/Space Complexity: Depends on heuristic quality, can be exponential.
    
    Common heuristics:
    - Manhattan Distance: Sum of horizontal + vertical distances
    - Euclidean Distance: Straight-line distance
    """
    stats = AlgorithmStats(f"A* Search ({function_label})")
    stats.time_start = time.time()

    # Quick check: if start is already goal
    if start_node.reached_target():
        stats.found_solution = True
        stats.time_end = time.time()
        stats.action_sequence = ["Initial"]
        stats.node_sequence = [start_node]
        return stats

    # Priority queue stores (f_score, g_score, node) where f = g + h
    # Always expands node with lowest f-value first
    priority_queue: List[Tuple[float, int, GameNode]] = [(cost_function(start_node), 0, start_node)]
    explored: Set[GameNode] = set()  # Track visited states to avoid cycles

    # Main A* loop: always expand the node with lowest f(n) = g(n) + h(n)
    while priority_queue:
        f_score, g_score, current_node = heapq.heappop(priority_queue)  # Get best node

        # Skip if already expanded (can have duplicates in heap)
        if current_node in explored:
            continue

        explored.add(current_node)  # Mark as expanded
        stats.visited_count += 1
        stats.max_depth = max(stats.max_depth, current_node.level)

        # Goal test: check if we reached the target
        if current_node.reached_target():
            stats.solution_cost = current_node.level
            stats.found_solution = True
            stats.action_sequence, stats.node_sequence = trace_back_path(current_node)
            stats.time_end = time.time()
            return stats

        # Generate successors and add to priority queue with f-values
        for successor in current_node.generate_successors():
            if successor in explored:
                continue
            g_val = successor.level              # g(n): actual cost from start
            h_val = cost_function(successor)     # h(n): heuristic estimate to goal
            heapq.heappush(priority_queue, (g_val + h_val, g_val, successor))  # f = g + h

    # No solution found (priority queue exhausted)
    stats.time_end = time.time()
    return stats


def count_inversions(config: ConfigTuple) -> int:
    """
    Counts the number of inversions in the puzzle configuration.
    An inversion occurs when a larger tile appears before a smaller tile.
    Used to determine if a puzzle configuration is solvable.
    """
    filtered = [x for x in config if x != 0]  # Exclude the blank tile
    inv_count = 0
    for i in range(len(filtered)):
        for j in range(i + 1, len(filtered)):
            if filtered[i] > filtered[j]:
                inv_count += 1
    return inv_count


def check_solvability(config: ConfigTuple) -> bool:
    """
    Determines if a puzzle configuration is solvable.
    For 8-puzzle, a configuration is solvable if and only if
    the number of inversions is even.
    """
    return count_inversions(config) % 2 == 0


def parse_input_string(input_str: str) -> ConfigTuple:
    tokens = input_str.replace(",", " ").split()
    if len(tokens) != 9:
        raise ValueError("Please enter exactly 9 numbers.")

    config_values = tuple(int(x) for x in tokens)
    if set(config_values) != set(range(9)):
        raise ValueError("Board must contain each number 0 through 8 exactly once.")

    return config_values


def execute_algorithm(start_node: GameNode, algorithm_choice: str) -> Dict[str, AlgorithmStats]:
    """
    Main algorithm dispatcher - executes selected search algorithm(s).
    
    Args:
        start_node: Initial puzzle state to solve from
        algorithm_choice: String key selecting algorithm:
            'bfs' - Breadth-First Search
            'dfs' - Depth-First Search
            'iddfs' - Iterative Deepening DFS
            'astar-m' - A* with Manhattan distance heuristic
            'astar-e' - A* with Euclidean distance heuristic
            'all' - Run all algorithms for comparison
    
    Returns:
        Dictionary mapping algorithm display names to their AlgorithmStats results
    """
    algorithm_choice = algorithm_choice.strip().lower()

    # Map algorithm keys to their execution functions
    algo_mapping: Dict[str, Callable[[], AlgorithmStats]] = {
        "bfs": lambda: breadth_first_strategy(start_node),
        "dfs": lambda: depth_first_strategy(start_node),
        "iddfs": lambda: iterative_depth_strategy(start_node),
        "astar-m": lambda: informed_search_strategy(start_node, compute_manhattan_cost, "Manhattan Distance"),
        "astar-e": lambda: informed_search_strategy(start_node, compute_euclidean_cost, "Euclidean Distance"),
    }

    # Special case: run all algorithms for comparison
    if algorithm_choice == "all":
        return {
            "BFS": algo_mapping["bfs"](),
            "DFS": algo_mapping["dfs"](),
            "Iterative DFS": algo_mapping["iddfs"](),
            "A* (Manhattan)": algo_mapping["astar-m"](),
            "A* (Euclidean)": algo_mapping["astar-e"](),
        }

    if algorithm_choice not in algo_mapping:
        raise ValueError("Invalid algorithm choice.")

    name_mapping = {
        "bfs": "BFS",
        "dfs": "DFS",
        "iddfs": "Iterative DFS",
        "astar-m": "A* (Manhattan)",
        "astar-e": "A* (Euclidean)",
    }
    return {name_mapping[algorithm_choice]: algo_mapping[algorithm_choice]()}


def format_stats_report(stats: AlgorithmStats) -> str:
    report_lines = [
        f"Algorithm: {stats.algo_label}",
        f"Solution Found: {'YES' if stats.found_solution else 'NO'}",
        f"Path Cost: {stats.solution_cost}",
        f"Nodes Expanded: {stats.visited_count}",
        f"Search Depth: {stats.max_depth}",
        f"Running Time: {stats.elapsed_time():.6f} seconds",
        f"Path to Goal ({max(0, len(stats.action_sequence) - 1)} steps):",
    ]
    for step_num, action in enumerate(stats.action_sequence):
        if action != "Initial":
            report_lines.append(f"  Step {step_num}: {action}")
    return "\n".join(report_lines)


def format_comparison_table(results_dict: Dict[str, AlgorithmStats]) -> str:
    header_line = (
        f"{'Algorithm':<25} {'Success':<8} {'Path Cost':<10} "
        f"{'Nodes Expanded':<15} {'Search Depth':<13} {'Time (sec)':<10}"
    )
    table_lines = [header_line, "-" * 85]
    for algo_name, stats in results_dict.items():
        table_lines.append(
            f"{algo_name:<25} "
            f"{('Yes' if stats.found_solution else 'No'):<8} "
            f"{stats.solution_cost:<10} "
            f"{stats.visited_count:<15} "
            f"{stats.max_depth:<13} "
            f"{stats.elapsed_time():<10.6f}"
        )
    return "\n".join(table_lines)


def format_tree_visualization(stats: AlgorithmStats) -> str:
    if not stats.found_solution:
        return "No solution tree to display."
    
    def mini_board_format(config: ConfigTuple) -> List[str]:
        board_rows = []
        for row in range(3):
            row_data = []
            for col in range(3):
                val = config[row * 3 + col]
                row_data.append("_" if val == 0 else str(val))
            board_rows.append(" ".join(row_data))
        return board_rows
    
    tree_lines = ["Solution Tree (Path from Start to Goal):", ""]
    
    for depth, (node, action) in enumerate(zip(stats.node_sequence, stats.action_sequence)):
        if depth == 0:
            tree_lines.append("Root: Start State")
            mini_lines = mini_board_format(node.config)
            for line in mini_lines:
                tree_lines.append("  " + line)
        else:
            spacing = "  " * depth
            tree_lines.append("")
            tree_lines.append(spacing + "│")
            tree_lines.append(spacing + "└──> " + f"{action}")
            mini_lines = mini_board_format(node.config)
            for line in mini_lines:
                tree_lines.append(spacing + "     " + line)
    
    tree_lines.append("")
    tree_lines.append(f"Path Length: {len(stats.action_sequence) - 1} moves")
    return "\n".join(tree_lines)


# ============================================================================
# GUI SECTION
# ============================================================================
# This section contains the complete graphical user interface using Tkinter.
#
# MAIN GUI CLASS:
#   - PuzzleSolverInterface: Complete interactive puzzle solver application
#
# FEATURES:
#   - 3x3 grid input for board configuration
#   - Preset puzzle buttons (Easy, Medium, Hard, Goal, Clear)
#   - Algorithm selection dropdown (BFS, DFS, IDDFS, A* variants, Run All)
#   - Results panel showing algorithm performance metrics
#   - Solution tree visualization panel
#   - Step-by-step visualization canvas with Prev/Play/Next controls
#   - Real-time status updates
#   - Scrollable interface for smaller screens
#   - Modern clean UI with custom color scheme
#
# The GUI provides a user-friendly way to:
#   1. Input puzzle configurations
#   2. Run search algorithms
#   3. Compare algorithm performance
#   4. Visualize solution paths step-by-step
# ============================================================================

class PuzzleSolverInterface:
    
    def __init__(self) -> None:
        self.main_window = tk.Tk()
        self.main_window.title("8-Puzzle Solver")
        self.main_window.geometry("900x650")
        self.main_window.minsize(850, 600)

        self.color_scheme = {
            "bg": "#f8f9fa",
            "panel": "#ffffff",
            "text": "#212529",
            "muted": "#6c757d",
            "accent": "#0d6efd",
            "canvas": "#e9ecef",
            "tile": "#cfe2ff",
            "tile_text": "#212529",
            "blank": "#dee2e6",
        }

        self.algo_options = {
            "BFS (Breadth-First Search)": "bfs",
            "DFS (Depth-First Search)": "dfs",
            "Iterative Deepening DFS": "iddfs",
            "A* (Manhattan Distance)": "astar-m",
            "A* (Euclidean Distance)": "astar-e",
            "Run All Algorithms": "all",
        }

        self.main_window.configure(bg=self.color_scheme["bg"])

        self.ui_style = ttk.Style(self.main_window)
        self.ui_style.theme_use("clam")
        self.ui_style.configure("TFrame", background=self.color_scheme["bg"])
        self.ui_style.configure("Card.TFrame", background=self.color_scheme["panel"])
        self.ui_style.configure("TLabel", background=self.color_scheme["bg"], foreground=self.color_scheme["text"])
        self.ui_style.configure("Title.TLabel", background=self.color_scheme["bg"], foreground=self.color_scheme["text"], font=("Arial", 18, "bold"))
        self.ui_style.configure("Subtitle.TLabel", background=self.color_scheme["bg"], foreground=self.color_scheme["muted"], font=("Arial", 9))
        self.ui_style.configure("Section.TLabel", background=self.color_scheme["panel"], foreground=self.color_scheme["text"], font=("Arial", 11, "bold"))
        self.ui_style.configure("Primary.TButton", font=("Arial", 10, "bold"), padding=6)
        self.ui_style.configure("TButton", font=("Arial", 10), padding=6)

        self.selected_algo = tk.StringVar(value="BFS (Breadth-First Search)")
        self.viz_algo = tk.StringVar(value="")
        self.step_info = tk.StringVar(value="Step 0/0 | Move: Initial")
        self.status_info = tk.StringVar(value="Ready. Enter board values and click Solve.")

        self.stored_results: Dict[str, AlgorithmStats] = {}
        self.state_sequence: List[GameNode] = []
        self.action_list: List[str] = []
        self.current_index = 0
        self.auto_playing = False

        self.input_fields: List[tk.Entry] = []

        self.construct_interface()
        self.populate_board((1, 2, 5, 3, 4, 8, 6, 0, 7))

    def construct_interface(self) -> None:
        wrapper = ttk.Frame(self.main_window, style="TFrame")
        wrapper.pack(fill=tk.BOTH, expand=True)

        self.scrollable_canvas = tk.Canvas(wrapper, bg=self.color_scheme["bg"], highlightthickness=0)
        vertical_scroll = ttk.Scrollbar(wrapper, orient=tk.VERTICAL, command=self.scrollable_canvas.yview)
        self.scrollable_canvas.configure(yscrollcommand=vertical_scroll.set)

        vertical_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollable_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        content_frame = ttk.Frame(self.scrollable_canvas, padding=(14, 12, 14, 12), style="TFrame")
        self.canvas_window = self.scrollable_canvas.create_window((0, 0), window=content_frame, anchor="nw")

        content_frame.bind("<Configure>", lambda e: self.scrollable_canvas.configure(scrollregion=self.scrollable_canvas.bbox("all")))
        self.scrollable_canvas.bind("<Configure>", lambda e: self.scrollable_canvas.itemconfigure(self.canvas_window, width=e.width))

        self.scrollable_canvas.bind_all("<MouseWheel>", self.handle_scroll)
        self.scrollable_canvas.bind_all("<Button-4>", self.handle_scroll)
        self.scrollable_canvas.bind_all("<Button-5>", self.handle_scroll)

        title_section = ttk.Frame(content_frame, style="TFrame")
        title_section.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_section, text="8-Puzzle Solver", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_section, text="Advanced puzzle solver with multiple algorithms and visualization.", style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))

        input_panel = ttk.Frame(content_frame, style="Card.TFrame", padding=12)
        input_panel.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_panel, text="Input & Solve", style="Section.TLabel").grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 8))

        ttk.Label(input_panel, text="Enter board values (0 is blank):", background=self.color_scheme["panel"]).grid(row=1, column=0, columnspan=4, sticky="w")

        grid_container = tk.Frame(input_panel, bg=self.color_scheme["panel"])
        grid_container.grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 6))

        for cell_num in range(9):
            input_box = tk.Entry(grid_container, width=3, justify="center", font=("Arial", 14, "bold"),
                                bg="#ffffff", fg=self.color_scheme["text"], relief=tk.FLAT,
                                highlightthickness=1, highlightbackground="#adb5bd", highlightcolor=self.color_scheme["accent"])
            input_box.grid(row=cell_num // 3, column=cell_num % 3, padx=5, pady=5, ipadx=3, ipady=5)
            self.input_fields.append(input_box)

        preset_buttons = tk.Frame(input_panel, bg=self.color_scheme["panel"])
        preset_buttons.grid(row=3, column=0, columnspan=4, sticky="w", pady=(2, 0))
        ttk.Button(preset_buttons, text="Easy", command=lambda: self.populate_board((1, 2, 5, 3, 4, 8, 6, 0, 7))).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(preset_buttons, text="Medium", command=lambda: self.populate_board((1, 8, 2, 0, 4, 3, 7, 6, 5))).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(preset_buttons, text="Hard", command=lambda: self.populate_board((8, 6, 7, 2, 5, 4, 3, 0, 1))).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(preset_buttons, text="Goal", command=lambda: self.populate_board(GameNode.TARGET_CONFIG)).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(preset_buttons, text="Clear", command=lambda: self.populate_board((0, 0, 0, 0, 0, 0, 0, 0, 0))).pack(side=tk.LEFT)

        ttk.Label(input_panel, text="Algorithm:", background=self.color_scheme["panel"]).grid(row=1, column=4, sticky="w", padx=(20, 0))
        algo_dropdown = ttk.Combobox(input_panel, textvariable=self.selected_algo, values=list(self.algo_options.keys()),
                                     state="readonly", width=28)
        algo_dropdown.grid(row=2, column=4, sticky="w", padx=(20, 0))

        ttk.Button(input_panel, text="Solve", style="Primary.TButton", command=self.run_solver).grid(row=2, column=5, padx=8)
        ttk.Button(input_panel, text="Reset", command=self.clear_all).grid(row=2, column=6, padx=8)

        status_display = ttk.Label(content_frame, textvariable=self.status_info, background=self.color_scheme["bg"],
                                   foreground=self.color_scheme["muted"], font=("Arial", 9))
        status_display.pack(fill=tk.X, pady=(0, 8))

        main_layout = ttk.Frame(content_frame, style="TFrame")
        main_layout.pack(fill=tk.BOTH, expand=True)

        left_panel = ttk.Frame(main_layout, style="Card.TFrame", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(left_panel, text="Results", style="Section.TLabel").pack(anchor="w")
        self.results_display = scrolledtext.ScrolledText(left_panel, height=18, font=("Courier New", 10), wrap=tk.WORD,
                                                        bg="#1a1d23", fg="#e9ecef", insertbackground="#e9ecef",
                                                        relief=tk.FLAT, padx=8, pady=8)
        self.results_display.pack(fill=tk.BOTH, expand=True, pady=(4, 8))

        ttk.Label(left_panel, text="Solution Tree", style="Section.TLabel").pack(anchor="w")
        self.tree_display = scrolledtext.ScrolledText(left_panel, height=10, font=("Courier New", 10), wrap=tk.WORD,
                                                      bg="#1a1d23", fg="#c3e6cb", insertbackground="#c3e6cb",
                                                      relief=tk.FLAT, padx=8, pady=8)
        self.tree_display.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        right_panel = ttk.Frame(main_layout, style="Card.TFrame", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(12, 0))

        ttk.Label(right_panel, text="Step Visualization", style="Section.TLabel").pack(anchor="w")

        selector_area = ttk.Frame(right_panel, style="Card.TFrame")
        selector_area.pack(fill=tk.X, pady=(4, 6))
        ttk.Label(selector_area, text="Visualize:", background=self.color_scheme["panel"]).pack(side=tk.LEFT)
        self.viz_dropdown = ttk.Combobox(selector_area, textvariable=self.viz_algo, values=[], state="readonly", width=22)
        self.viz_dropdown.pack(side=tk.LEFT, padx=(6, 0))
        self.viz_dropdown.bind("<<ComboboxSelected>>", self.switch_visualization)

        self.board_canvas = tk.Canvas(right_panel, width=360, height=360, bg=self.color_scheme["canvas"],
                                     highlightthickness=1, highlightbackground="#adb5bd")
        self.board_canvas.pack()

        ttk.Label(right_panel, textvariable=self.step_info, background=self.color_scheme["panel"],
                 foreground=self.color_scheme["muted"], font=("Arial", 10)).pack(pady=(6, 8))

        control_area = ttk.Frame(right_panel, style="Card.TFrame")
        control_area.pack()
        ttk.Button(control_area, text="< Prev", width=10, command=self.go_previous).grid(row=0, column=0, padx=4)
        ttk.Button(control_area, text="Play", width=10, command=self.toggle_autoplay).grid(row=0, column=1, padx=4)
        ttk.Button(control_area, text="Next >", width=10, command=self.go_next).grid(row=0, column=2, padx=4)

    def populate_board(self, config: ConfigTuple) -> None:
        for idx, value in enumerate(config):
            self.input_fields[idx].delete(0, tk.END)
            self.input_fields[idx].insert(0, str(value))

    def extract_board(self) -> ConfigTuple:
        try:
            config_values = tuple(int(field.get().strip()) for field in self.input_fields)
        except ValueError as e:
            raise ValueError("Each cell must contain a number from 0 to 8.") from e

        if set(config_values) != set(range(9)):
            raise ValueError("Board must contain each number 0 through 8 exactly once.")
        return config_values

    def run_solver(self) -> None:
        try:
            board_config = self.extract_board()
        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error))
            self.status_info.set("Input error: values must be 0-8 and unique.")
            return

        if not check_solvability(board_config):
            messagebox.showwarning("Unsolvable Board",
                                  f"This board is not solvable. Inversions: {count_inversions(board_config)} (must be even).")
            self.status_info.set("Board is unsolvable. Please enter another configuration.")
            return

        initial_node = GameNode(board_config)
        algo_key = self.algo_options[self.selected_algo.get()]
        self.stored_results = execute_algorithm(initial_node, algo_key)

        self.display_results(board_config)
        self.refresh_viz_options()
        self.status_info.set(f"Solved using {self.selected_algo.get()}.")

    def display_results(self, config: ConfigTuple) -> None:
        output_blocks: List[str] = [
            "Initial State:\n" + render_configuration(config),
            "Goal State:\n" + render_configuration(GameNode.TARGET_CONFIG),
        ]

        for name, stats in self.stored_results.items():
            output_blocks.append("=" * 60)
            output_blocks.append(name)
            output_blocks.append(format_stats_report(stats))

        if len(self.stored_results) > 1:
            output_blocks.append("=" * 60)
            output_blocks.append("Comparison Table")
            output_blocks.append(format_comparison_table(self.stored_results))

        self.results_display.delete("1.0", tk.END)
        self.results_display.insert(tk.END, "\n\n".join(output_blocks))

    def refresh_viz_options(self) -> None:
        option_list = list(self.stored_results.keys())
        self.viz_dropdown["values"] = option_list
        if option_list:
            self.viz_algo.set(option_list[0])
            self.load_visualization()

    def switch_visualization(self, event: object) -> None:
        self.load_visualization()

    def load_visualization(self) -> None:
        selected_name = self.viz_algo.get()
        if selected_name not in self.stored_results:
            return

        stats = self.stored_results[selected_name]
        self.state_sequence = stats.node_sequence
        self.action_list = stats.action_sequence
        self.current_index = 0
        self.auto_playing = False

        self.tree_display.delete("1.0", tk.END)
        self.tree_display.insert(tk.END, format_tree_visualization(stats))
        self.render_current_state()

    def render_current_state(self) -> None:
        self.board_canvas.delete("all")

        if not self.state_sequence:
            self.step_info.set("Step 0/0 | Move: N/A")
            return

        current_config = self.state_sequence[self.current_index].config
        current_action = self.action_list[self.current_index]

        cell_size = 100
        spacing = 8
        margin = 22

        for position, tile_val in enumerate(current_config):
            row, col = divmod(position, 3)
            x_start = margin + col * (cell_size + spacing)
            y_start = margin + row * (cell_size + spacing)
            x_end = x_start + cell_size
            y_end = y_start + cell_size

            if tile_val == 0:
                self.board_canvas.create_rectangle(x_start, y_start, x_end, y_end, outline="#6c757d",
                                                   width=2, dash=(4, 3), fill=self.color_scheme["blank"])
            else:
                self.board_canvas.create_rectangle(x_start, y_start, x_end, y_end, outline="#212529",
                                                   width=2, fill=self.color_scheme["tile"])
                self.board_canvas.create_text((x_start + x_end) / 2, (y_start + y_end) / 2, text=str(tile_val),
                                             font=("Arial", 24, "bold"), fill=self.color_scheme["tile_text"])

        self.step_info.set(f"Step {self.current_index}/{len(self.state_sequence)-1} | Move: {current_action}")

    def go_next(self) -> None:
        if self.state_sequence and self.current_index < len(self.state_sequence) - 1:
            self.current_index += 1
            self.render_current_state()

    def go_previous(self) -> None:
        if self.state_sequence and self.current_index > 0:
            self.current_index -= 1
            self.render_current_state()

    def toggle_autoplay(self) -> None:
        self.auto_playing = not self.auto_playing
        if self.auto_playing:
            self.advance_automatically()

    def advance_automatically(self) -> None:
        if not self.auto_playing:
            return
        if self.state_sequence and self.current_index < len(self.state_sequence) - 1:
            self.current_index += 1
            self.render_current_state()
            self.main_window.after(700, self.advance_automatically)
        else:
            self.auto_playing = False

    def clear_all(self) -> None:
        self.stored_results = {}
        self.state_sequence = []
        self.action_list = []
        self.current_index = 0
        self.auto_playing = False
        self.selected_algo.set("BFS (Breadth-First Search)")
        self.viz_algo.set("")
        self.viz_dropdown["values"] = []
        self.results_display.delete("1.0", tk.END)
        self.tree_display.delete("1.0", tk.END)
        self.board_canvas.delete("all")
        self.step_info.set("Step 0/0 | Move: Initial")
        self.status_info.set("Reset complete. Ready for a new puzzle.")
        self.populate_board((1, 2, 5, 3, 4, 8, 6, 0, 7))

    def handle_scroll(self, event: tk.Event) -> None:
        if getattr(event, "num", None) == 4:
            self.scrollable_canvas.yview_scroll(-1, "units")
        elif getattr(event, "num", None) == 5:
            self.scrollable_canvas.yview_scroll(1, "units")
        elif getattr(event, "delta", 0):
            self.scrollable_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def start(self) -> None:
        self.main_window.mainloop()


def execute_main() -> None:
    """Main entry point - creates and launches the GUI application."""
    application = PuzzleSolverInterface()
    application.start()


# ============================================================================
# COMPATIBILITY ALIASES
# ============================================================================
# These aliases provide backward compatibility with different naming conventions
# and enable the code to work with existing tests and external code that might
# use alternative names for classes and functions.
# ============================================================================
PuzzleState = GameNode
SearchMetrics = AlgorithmStats
bfs_search = breadth_first_strategy
dfs_search = depth_first_strategy
iterative_deepening_dfs = iterative_depth_strategy
a_star_search = informed_search_strategy
manhattan_distance = compute_manhattan_cost
euclidean_distance = compute_euclidean_cost
is_solvable = check_solvability
inversion_count = count_inversions
format_board = render_configuration
PuzzleSolverApp = PuzzleSolverInterface


if __name__ == "__main__":
    execute_main()
