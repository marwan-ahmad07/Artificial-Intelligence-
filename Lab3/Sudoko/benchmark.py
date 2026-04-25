import time
import copy
from sudoku_solver import generate_random_puzzle, solve_with_ac3, solve_mac, solve_backtracking

def is_solved_board(board):
    for r in range(9):
        if 0 in board[r]:
            return False
        if len(set(board[r])) != 9:
            return False

    for c in range(9):
        col = [board[r][c] for r in range(9)]
        if len(set(col)) != 9:
            return False

    for start_r in range(0, 9, 3):
        for start_c in range(0, 9, 3):
            block = []
            for r in range(start_r, start_r + 3):
                for c in range(start_c, start_c + 3):
                    block.append(board[r][c])
            if len(set(block)) != 9:
                return False

    return True

def benchmark():
    difficulties = ["easy", "intermediate", "hard"]
    
    print("Starting Sudoku Benchmark...\n")
    
    for diff in difficulties:
        print(f"--- Benchmarking '{diff}' difficulty ---")
        
        # Generate 5 puzzles for average
        ac3_times = []
        mac_times = []
        backtrack_times = []
        ac3_success_count = 0
        mac_success_count = 0
        backtrack_success_count = 0
        
        for _ in range(5):
            board = generate_random_puzzle(diff)
            
            # 1. Pure AC-3
            b1 = copy.deepcopy(board)
            start = time.perf_counter()
            success = solve_with_ac3(b1)
            ac3_times.append(time.perf_counter() - start)
            if success:
                ac3_success_count += 1
                
            # 2. MAC (AC-3 + Backtracking)
            b2 = copy.deepcopy(board)
            start = time.perf_counter()
            mac_success = solve_mac(b2)
            mac_times.append(time.perf_counter() - start)
            if mac_success and is_solved_board(b2):
                mac_success_count += 1
            
            # 3. Pure Backtracking
            b3 = copy.deepcopy(board)
            start = time.perf_counter()
            backtrack_success = solve_backtracking(b3)
            backtrack_times.append(time.perf_counter() - start)
            if backtrack_success and is_solved_board(b3):
                backtrack_success_count += 1
            
        avg_ac3 = sum(ac3_times) / 5
        avg_mac = sum(mac_times) / 5
        avg_bt = sum(backtrack_times) / 5
        
        print(f"AC-3 Only -> Solved {ac3_success_count}/5, Avg Time: {avg_ac3:.5f}s")
        print(f"MAC (AC-3+BT) -> Solved {mac_success_count}/5, Avg Time: {avg_mac:.5f}s")
        print(f"Pure Backtrack -> Solved {backtrack_success_count}/5, Avg Time: {avg_bt:.5f}s")
        print()
        
if __name__ == "__main__":
    benchmark()
