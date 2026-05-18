import random
from typing import Dict, Tuple
from .gridworld import GridWorld, ACTIONS


def policy_evaluation(policy, env: GridWorld, gamma: float = 0.95, theta: float = 1e-4):
    V = {s: 0.0 for s in env.all_states()}
    while True:
        delta = 0.0
        for s in env.all_states():
            if env.is_terminal(s):
                continue
            v = V[s]
            a = policy[s]
            q = 0.0
            for p, s2, r, done in env.transitions(s, a):
                q += p * (r + (0 if done else gamma * V[s2]))
            V[s] = q
            delta = max(delta, abs(v - V[s]))
        if delta < theta:
            break
    return V


def policy_improvement(V, env: GridWorld, gamma: float = 0.95):
    policy_stable = True
    policy = {}
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
    return policy


def policy_iteration(env: GridWorld, gamma: float = 0.95, max_iter: int = 1000, initial_policy: dict = None, random_seed: int = None):
    # start with random policy unless an initial_policy is provided
    if random_seed is not None:
        random.seed(random_seed)
    if initial_policy is None:
        policy = {s: (None if env.is_terminal(s) else random.choice(ACTIONS)) for s in env.all_states()}
    else:
        policy = dict(initial_policy)
    for _ in range(max_iter):
        V = policy_evaluation(policy, env, gamma)
        new_policy = policy_improvement(V, env, gamma)
        if all(new_policy[s] == policy[s] for s in env.all_states()):
            return V, new_policy
        policy = new_policy
    return V, policy
