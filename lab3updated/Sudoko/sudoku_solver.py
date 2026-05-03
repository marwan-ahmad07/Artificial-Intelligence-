import random
import copy
import time
from collections import deque

def get_neighbors(r, c):
    """
    Get all related cells (arcs) for a specific cell at (r, c).
    A cell is constrained by other cells in its row, column, and 3x3 block.
    """
    # In the CSP view, every neighbor is a variable that shares a constraint
    # with (r, c), so those cells form the arcs used by AC-3 and backtracking.
    neighbors = set()
    # Add all cells in the same row and column
    for i in range(9):
        if i != c: neighbors.add((r, i))
        if i != r: neighbors.add((i, c))
    
    # Add all cells in the same 3x3 block
    start_r, start_c = (r // 3) * 3, (c // 3) * 3
    for i in range(start_r, start_r + 3):
        for j in range(start_c, start_c + 3):
            if (i, j) != (r, c):
                neighbors.add((i, j))
    return neighbors

def is_valid_assignment(board, r, c, val):
    """
    Check if placing 'val' at board[r][c] violates any Sudoku rules.
    Used for Backtracking.
    """
    # This is the CSP consistency check for one tentative assignment.
    # A value is only allowed if it does not conflict with any already placed
    # value in the same row, column, or 3x3 box.
    # Check row and col
    for i in range(9):
        if board[r][i] == val and i != c: return False
        if board[i][c] == val and i != r: return False
        
    # Check 3x3 block
    start_r, start_c = (r // 3) * 3, (c // 3) * 3
    for i in range(start_r, start_r + 3):
        for j in range(start_c, start_c + 3):
            if board[i][j] == val and (i, j) != (r, c): return False
    return True

def find_empty(board):
    """Find the first empty cell (value 0) in the board."""
    # Empty cells are the unassigned variables in the CSP.
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return (r, c)
    return None

def solve_backtracking(board):
    """
    Solves the Sudoku board using classical Backtracking algorithm.
    Returns True if a solution is found, False otherwise.
    The board is modified in-place.
    """
    empty = find_empty(board)
    if not empty:
        # No empty cells means every variable has been assigned consistently.
        return True # The board is fully solved
    r, c = empty
    
    # Depth-first search: try every possible digit for the chosen cell.
    for val in range(1, 10):
        if is_valid_assignment(board, r, c, val):
            # Make a tentative assignment and continue solving the remaining
            # cells under the new partial CSP state.
            board[r][c] = val
            # Recursively try to solve the rest of the board
            if solve_backtracking(board):
                return True
            # Backtrack: undo the guess so the next candidate starts from the
            # previous consistent state.
            board[r][c] = 0
            
    return False

def generate_random_puzzle(difficulty="intermediate"):
    """
    Generates a solvable Sudoku puzzle using Backtracking.
    Difficulty sets how many cells will be emptied:
    easy: 30 removed, intermediate: 45 removed, hard: 55 removed.
    """
    board = [[0]*9 for _ in range(9)]
    
    # To make generation fast, fill the 3 diagonal 3x3 boxes first.
    # These blocks do not constrain each other, so they can be randomized
    # independently before the full backtracking solve.
    for i in range(0, 9, 3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for r in range(3):
            for c in range(3):
                board[i+r][i+c] = nums.pop()
                
    # Complete the partially filled grid with backtracking to obtain one
    # valid full solution before we remove cells to form a puzzle.
    solve_backtracking(board)
    
    # Empty cells based on difficulty
    removals = {"easy": 30, "intermediate": 45, "hard": 55}
    num_remove = removals.get(difficulty.lower(), 45)
    
    # Get a list of all coordinates and shuffle them
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    
    # Remove the values to create the puzzle
    for r, c in cells[:num_remove]:
        board[r][c] = 0
        
    return board

def is_solvable(board):
    """
    Validates if a given board state has at least one valid solution.
    Does not modify the original board.
    """
    # Use a copy so the original puzzle stays unchanged while the solver
    # explores the search tree.
    temp_board = copy.deepcopy(board)
    return solve_backtracking(temp_board)

# --- Arc Consistency (AC-3) Implementation ---

def initialize_domains(board):
    """
    Initial Domain Reduction.
    For each cell, if it's filled, its domain is just that value.
    If it's empty, its domain is [1, 2, ..., 9].
    """
    # This is the CSP starting state: each variable gets a set of legal values
    # before any inference is applied.
    domains = {}
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                domains[(r, c)] = [board[r][c]]
            else:
                domains[(r, c)] = list(range(1, 10))
    return domains

def revise(domains, xi, xj):
    """
    Revise the domain of variable xi to ensure arc consistency with xj.
    If xj has only one value, and it exists in xi's domain, remove it from xi.
    Returns True if the domain of xi was changed.
    """
    # AC-3's revise step removes values from xi that cannot be supported by xj.
    revised = False
    for x in domains[xi][:]:
        # If D_j has only one value, and it's equal to x, then x is invalid for xi.
        if len(domains[xj]) == 1 and domains[xj][0] == x:
            domains[xi].remove(x)
            revised = True
    return revised

def ac3(domains):
    """
    Apply the AC-3 algorithm to enforce arc consistency.
    Returns True if it succeeds (no domain becomes empty), False otherwise.
    """
    # The queue stores every directed arc that might need to be rechecked.
    queue = deque()
    # Initialize the queue with all possible arcs in the Sudoku grid
    for r in range(9):
        for c in range(9):
            for neighbor in get_neighbors(r, c):
                queue.append(((r, c), neighbor))
                
    while queue:
        xi, xj = queue.popleft()
        # If a neighbor became tighter, xi may also need pruning.
        if revise(domains, xi, xj):
            # An empty domain means the CSP has become inconsistent.
            if len(domains[xi]) == 0:
                return False 
            # Any reduction can affect all other neighbors of xi, so push those
            # arcs back into the queue for another consistency check.
            for xk in get_neighbors(xi[0], xi[1]):
                if xk != xj:
                    queue.append((xk, xi))
    return True

def solve_with_ac3(board):
    """
    Attempt to solve the board using ONLY Arc Consistency (AC-3).
    This might fully solve easy puzzles, but will get stuck on hard ones.
    Updates the board in-place.
    Returns True if fully solved, False if partially solved or unsolvable.
    """
    domains = initialize_domains(board)
    
    # AC-3 is inference only: it narrows domains, but it does not guess.
    success = ac3(domains)
    if not success:
        return False
        
    solved = True
    for r in range(9):
        for c in range(9):
            if len(domains[(r, c)]) == 1:
                # If only one possible value remains, commit that forced value.
                board[r][c] = domains[(r, c)][0]
            else:
                # More than one possibility means the puzzle still needs search.
                board[r][c] = 0
                solved = False
                
    return solved

def solve_mac(board):
    """
    Maintaining Arc Consistency (MAC).
    Combines Backtracking with AC-3. This can solve ANY Sudoku puzzle.
    It runs AC-3, then guesses a value, and runs AC-3 again.
    """
    # MAC is a CSP search strategy: alternate inference (AC-3) and search
    # (backtracking) to cut down the branching factor.
    domains = initialize_domains(board)
    if not ac3(domains):
        return False
    
    if _backtrack_mac(domains, board):
        return True
    return False

def _backtrack_mac(domains, board):
    # Find an unassigned variable (domain size > 1).
    unassigned = [v for v in domains if len(domains[v]) > 1]
    if not unassigned:
        # Every domain is a singleton now, so copy the solution back to the grid.
        for r in range(9):
            for c in range(9):
                board[r][c] = domains[(r, c)][0]
        return True
        
    # Minimum Remaining Values (MRV): choose the cell with the smallest domain
    # to expose contradictions earlier and reduce the search tree.
    var = min(unassigned, key=lambda v: len(domains[v]))
    
    for val in domains[var]:
        # Copy the current CSP state so each branch explores independently.
        new_domains = copy.deepcopy(domains)
        new_domains[var] = [val]
        
        # After making a guess, re-run local AC-3 from the affected neighbors.
        queue = deque()
        for neighbor in get_neighbors(var[0], var[1]):
            queue.append((neighbor, var))
            
        # Propagate the consequences of the guess through the CSP.
        is_consistent = True
        while queue:
            xi, xj = queue.popleft()
            if revise(new_domains, xi, xj):
                if len(new_domains[xi]) == 0:
                    is_consistent = False
                    break
                for xk in get_neighbors(xi[0], xi[1]):
                    if xk != xj:
                        queue.append((xk, xi))
                        
        if is_consistent:
            # If the guess survives propagation, continue searching deeper.
            if _backtrack_mac(new_domains, board):
                return True
                
    return False
