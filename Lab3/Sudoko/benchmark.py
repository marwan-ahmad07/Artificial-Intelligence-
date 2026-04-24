import time
import copy
from sudoku_solver import generate_random_puzzle, solve_with_ac3, solve_mac, solve_backtracking

def benchmark():
    difficulties = ["easy", "intermediate", "hard"]
    results = {}
    
    print("Starting Sudoku Benchmark...\n")
    
    for diff in difficulties:
        print(f"--- Benchmarking '{diff}' difficulty ---")
        
        # Generate 5 puzzles for average
        ac3_times = []
        mac_times = []
        backtrack_times = []
        ac3_success_count = 0
        
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
            solve_mac(b2)
            mac_times.append(time.perf_counter() - start)
            
            # 3. Pure Backtracking
            b3 = copy.deepcopy(board)
            start = time.perf_counter()
            solve_backtracking(b3)
            backtrack_times.append(time.perf_counter() - start)
            
        avg_ac3 = sum(ac3_times) / 5
        avg_mac = sum(mac_times) / 5
        avg_bt = sum(backtrack_times) / 5
        
        print(f"AC-3 Only -> Solved {ac3_success_count}/5, Avg Time: {avg_ac3:.5f}s")
        print(f"MAC (AC-3+BT) -> Avg Time: {avg_mac:.5f}s")
        print(f"Pure Backtrack -> Avg Time: {avg_bt:.5f}s")
        print()
        
if __name__ == "__main__":
    benchmark()
