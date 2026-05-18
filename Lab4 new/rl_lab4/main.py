import os
import sys
import numpy as np
# Ensure the project root is on sys.path so the script can be run directly
# (python rl_lab4/main.py) or as a module (python -m rl_lab4.main).
_pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from rl_lab4.gridworld import GridWorld
from rl_lab4.value_iteration import value_iteration
from rl_lab4.policy_iteration import policy_iteration


def make_rewards(R1, R2):
    # construct rewards matrix from assignment figure
    # top row: [R1,1,0,-1,R2]
    # rows 2-5: [2,1,0,-1,-2]
    rewards = np.zeros((5,5), dtype=float)
    rewards[0] = [R1, 1, 0, -1, R2]
    for r in range(1,5):
        rewards[r] = [2, 1, 0, -1, -2]
    return rewards


def policy_to_grid(policy, rows=5, cols=5):
    arrow = {0: '^', 1: 'v', 2: '<', 3: '>'}
    grid = [['' for _ in range(cols)] for _ in range(rows)]
    for (r, c), a in policy.items():
        grid[r][c] = 'T' if a is None else arrow[a]
    return grid


def print_policy(policy):
    grid = policy_to_grid(policy)
    for row in grid:
        print(' '.join(f'{x:>2}' for x in row))


def run_cases():
    cases = [(100, 110), (10, 100), (1, 10), (10, 15)]
    for R1, R2 in cases:
        print(f'=== Case R1={R1}, R2={R2} ===')
        rewards = make_rewards(R1, R2)
        env = GridWorld(rewards, terminal_states=[(0,0), (0,4)])
        V_vi, policy_vi = value_iteration(env, gamma=0.95)
        print('\nValue Iteration policy:')
        print_policy(policy_vi)
        V_pi, policy_pi = policy_iteration(env, gamma=0.95)
        print('\nPolicy Iteration policy (from one random start):')
        print_policy(policy_pi)
        # Bonus: run multiple random starts and ensure convergence to same optimal policy
        matches = []
        for seed in range(10):
            Vb, pb = policy_iteration(env, gamma=0.95, random_seed=seed)
            matches.append(all((pb[s] == policy_vi[s]) for s in env.all_states()))
        all_match = all(matches)
        print(f'\nPolicy Iteration from 10 random starts matches VI policy: {all_match}')
        # compare values
        print('\nSample V at center (2,2): VI={:.3f}, PI={:.3f}\n'.format(V_vi[(2,2)], V_pi[(2,2)]))


if __name__ == '__main__':
    run_cases()
