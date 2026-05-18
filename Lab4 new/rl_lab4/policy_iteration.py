import random
from typing import Dict, Tuple
from .gridworld import GridWorld, ACTIONS


def policy_evaluation(policy, env: GridWorld, gamma: float = 0.95, theta: float = 1e-4):
    # Policy Evaluation computes V^pi for a fixed policy.
    # We repeatedly sweep the grid and update each state's value until it stabilizes.
    # Iteratively evaluate the current policy until values stop changing much.
    V = {s: 0.0 for s in env.all_states()}
    while True:
        delta = 0.0
        for s in env.all_states():
            if env.is_terminal(s):
                # Terminal states have no outgoing actions.
                continue
            v = V[s]
            a = policy[s]
            # Expected return of taking the policy's action and following the policy thereafter.
            q = 0.0
            for p, s2, r, done in env.transitions(s, a):
                # If the transition ends the episode, do not add discounted future value.
                q += p * (r + (0 if done else gamma * V[s2]))
            V[s] = q
            delta = max(delta, abs(v - V[s]))
        # Stop when the value function changes less than the threshold everywhere.
        if delta < theta:
            break
    return V


def policy_improvement(V, env: GridWorld, gamma: float = 0.95):
    # Policy Improvement builds a new policy by acting greedily w.r.t. V.
    # Build a new greedy policy by choosing the best action under the current V.
    policy = {}
    for s in env.all_states():
        if env.is_terminal(s):
            policy[s] = None
            continue
        best_a = None
        best_q = -float('inf')
        for a in ACTIONS:
            # Compute expected return for each action using the current value estimates.
            q = 0.0
            for p, s2, r, done in env.transitions(s, a):
                q += p * (r + (0 if done else gamma * V[s2]))
            if q > best_q:
                best_q = q
                best_a = a
        # Pick the action with the highest expected return.
        policy[s] = best_a
    return policy


def policy_iteration(env: GridWorld, gamma: float = 0.95, max_iter: int = 1000, initial_policy: dict = None, random_seed: int = None):
    # Policy Iteration alternates between:
    # 1) Evaluating the current policy, then
    # 2) Improving it greedily until it stops changing.
    # start with random policy unless an initial_policy is provided
    if random_seed is not None:
        random.seed(random_seed)
    if initial_policy is None:
        # Randomly choose an action for every non-terminal state as a starting point.
        policy = {s: (None if env.is_terminal(s) else random.choice(ACTIONS)) for s in env.all_states()}
    else:
        policy = dict(initial_policy)
    for _ in range(max_iter):
        # 1) Policy evaluation: estimate V^pi for the current policy.
        V = policy_evaluation(policy, env, gamma)
        # 2) Policy improvement: make the policy greedy with respect to V.
        new_policy = policy_improvement(V, env, gamma)
        # If the policy didn't change, we have converged to the optimal policy.
        if all(new_policy[s] == policy[s] for s in env.all_states()):
            return V, new_policy
        policy = new_policy
    # If max_iter is reached, return the best found so far.
    return V, policy
