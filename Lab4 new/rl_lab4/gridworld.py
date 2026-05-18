import numpy as np
from typing import List, Tuple, Dict

# Actions: 0=Up,1=Down,2=Left,3=Right
ACTIONS = [0, 1, 2, 3]


class GridWorld:
    def __init__(self, rewards: np.ndarray, terminal_states: List[Tuple[int, int]]):
        self.rewards = rewards
        self.n_rows, self.n_cols = rewards.shape
        self.terminal_states = set(terminal_states)

    def in_bounds(self, r, c):
        return 0 <= r < self.n_rows and 0 <= c < self.n_cols

    def is_terminal(self, s: Tuple[int, int]):
        return s in self.terminal_states

    def step_from(self, s: Tuple[int, int], a: int) -> Tuple[Tuple[int,int], float]:
        # deterministic outcome of applying action a from s (for single outcome)
        if self.is_terminal(s):
            return s, self.rewards[s]
        r, c = s
        if a == 0:  # Up
            nr, nc = r - 1, c
        elif a == 1:  # Down
            nr, nc = r + 1, c
        elif a == 2:  # Left
            nr, nc = r, c - 1
        else:  # Right
            nr, nc = r, c + 1
        if not self.in_bounds(nr, nc):
            nr, nc = r, c  # collision -> no movement
        return (nr, nc), self.rewards[nr, nc]

    def transitions(self, s: Tuple[int,int], a: int) -> List[Tuple[float, Tuple[int,int], float, bool]]:
        # return list of (prob, next_state, reward, done)
        if self.is_terminal(s):
            return [(1.0, s, self.rewards[s], True)]
        probs = {a: 0.7}
        other = [act for act in ACTIONS if act != a]
        for act in other:
            probs[act] = probs.get(act, 0) + 0.1
        results = []
        for act, p in probs.items():
            (nr, nc), rwd = self.step_from(s, act)
            done = (nr, nc) in self.terminal_states
            results.append((p, (nr, nc), float(rwd), done))
        return results

    def all_states(self) -> List[Tuple[int,int]]:
        return [(r, c) for r in range(self.n_rows) for c in range(self.n_cols)]
