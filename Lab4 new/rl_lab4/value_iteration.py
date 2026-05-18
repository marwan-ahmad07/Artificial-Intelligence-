import numpy as np
from typing import Tuple, Dict
from .gridworld import GridWorld, ACTIONS


def value_iteration(env: GridWorld, gamma: float = 0.95, theta: float = 1e-4, max_iter: int = 10000):
    V = {s: 0.0 for s in env.all_states()}
    for t in range(max_iter):
        delta = 0.0
        for s in env.all_states():
            if env.is_terminal(s):
                continue
            v = V[s]
            q_values = []
            for a in ACTIONS:
                q = 0.0
                for p, s2, r, done in env.transitions(s, a):
                    q += p * (r + (0 if done else gamma * V[s2]))
                q_values.append(q)
            V[s] = max(q_values)
            delta = max(delta, abs(v - V[s]))
        if delta < theta:
            break

    # derive policy
    policy = {s: None for s in env.all_states()}
    for s in env.all_states():
        if env.is_terminal(s):
            policy[s] = None
            continue
        best_a = None
        best_q = -float('inf')
        for a in ACTIONS:
            q = 0.0
            for p, s2, r, done in env.transitions(s, a):
                q += p * (r + (0 if done else gamma * V[s2]))
            if q > best_q:
                best_q = q
                best_a = a
        policy[s] = best_a

    return V, policy
