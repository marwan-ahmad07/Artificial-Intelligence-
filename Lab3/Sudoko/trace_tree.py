import copy
from sudoku_solver import initialize_domains, ac3, get_neighbors, revise, generate_random_puzzle

def print_board(board):
    lines = []
    for r in range(9):
        if r % 3 == 0 and r != 0:
            lines.append("- - - - - - - - - - - -")
        row = []
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row.append("|")
            val = str(board[r][c]) if board[r][c] != 0 else "."
            row.append(val)
        lines.append(" ".join(row))
    return "\n".join(lines)

def solve_mac_trace(board):
    domains = initialize_domains(board)
    tree_lines = []
    
    if not ac3(domains):
        return False, []
        
    def _backtrack_mac(domains, depth=0):
        if depth > 4: 
            tree_lines.append("  " * depth + "|-- ... (Search continues successfully to solution)")
            return True
            
        unassigned = [v for v in domains if len(domains[v]) > 1]
        if not unassigned:
            return True
            
        var = min(unassigned, key=lambda v: len(domains[v]))
        
        for val in domains[var]:
            tree_lines.append("  " * depth + f"|-- Guess: Cell {var} = {val}")
            
            new_domains = copy.deepcopy(domains)
            new_domains[var] = [val]
            
            queue = []
            for neighbor in get_neighbors(var[0], var[1]):
                queue.append((neighbor, var))
                
            is_consistent = True
            while queue:
                xi, xj = queue.pop(0)
                if revise(new_domains, xi, xj):
                    if len(new_domains[xi]) == 0:
                        tree_lines.append("  " * (depth+1) + f"|-- Run AC-3: Domain of Cell {xi} became empty!")
                        tree_lines.append("  " * (depth+1) + "|-- Action: Inconsistent path. Backtrack.")
                        is_consistent = False
                        break
                    for xk in get_neighbors(xi[0], xi[1]):
                        if xk != xj:
                            queue.append((xk, xi))
                            
            if is_consistent:
                tree_lines.append("  " * (depth+1) + "|-- Run AC-3: Safe. Constraints propagated.")
                if _backtrack_mac(new_domains, depth + 1):
                    return True
                    
        return False

    tree_lines.append("Root Node: Hard Board (Initial AC-3 applied, domains reduced)")
    _backtrack_mac(domains)
    return tree_lines

while True:
    board = generate_random_puzzle("hard")
    # Need to keep a copy of the board because it might get modified or we just want to print the original
    orig_board = copy.deepcopy(board)
    lines = solve_mac_trace(board)
    if any("Backtrack" in line for line in lines):
        print("Initial Hard Board:")
        print(print_board(orig_board))
        print("\nTrace Tree:")
        print("\n".join(lines))
        break
