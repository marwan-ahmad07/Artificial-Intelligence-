import numpy as np
from typing import Tuple, Dict
from .gridworld import GridWorld, ACTIONS


def value_iteration(env: GridWorld, gamma: float = 0.95, theta: float = 1e-4, max_iter: int = 10000):
    # Value Iteration alternates between a Bellman optimality backup and a
    # convergence check; it directly estimates the optimal value function V*.
    # - gamma: discount factor (how much we care about future rewards)
    # - theta: small threshold to decide when values have converged
    # - max_iter: safety cap to avoid infinite loops
    # Initialize all state values to zero.
    V = {s: 0.0 for s in env.all_states()}
    for t in range(max_iter):
        delta = 0.0
        for s in env.all_states():
            if env.is_terminal(s):
                # Terminal states keep their value; no action is taken there.
                continue
            v = V[s]
            q_values = []
            for a in ACTIONS:
                # One-step lookahead: expected return of action a from state s.
                q = 0.0
                for p, s2, r, done in env.transitions(s, a):
                    # If this transition ends the episode, ignore future value.
                    q += p * (r + (0 if done else gamma * V[s2]))
                q_values.append(q)
            # Update V(s) to the best action value (Bellman optimality backup).
            V[s] = max(q_values) #V(s) = max over actions [ reward + gamma * future value ]
            # Track the largest update across all states in this sweep. 
            delta = max(delta, abs(v - V[s])) 
        # Stop when the largest change is below the threshold.
        if delta < theta:
            break

    # Derive a greedy policy from the converged value function.
    policy = {s: None for s in env.all_states()}
    for s in env.all_states():
        if env.is_terminal(s):
            policy[s] = None
            continue
        best_a = None
        best_q = -float('inf')
        for a in ACTIONS:
            # Choose the action that maximizes expected return under V.
            q = 0.0
            for p, s2, r, done in env.transitions(s, a):
                q += p * (r + (0 if done else gamma * V[s2]))
            if q > best_q:
                best_q = q
                best_a = a
        # Store the greedy action for this state.
        policy[s] = best_a

    return V, policy
