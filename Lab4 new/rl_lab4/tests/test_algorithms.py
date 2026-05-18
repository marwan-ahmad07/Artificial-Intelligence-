import numpy as np
from rl_lab4.gridworld import GridWorld
from rl_lab4.value_iteration import value_iteration
from rl_lab4.policy_iteration import policy_iteration


def make_rewards(R1, R2):
    rewards = np.zeros((5,5), dtype=float)
    rewards[0] = [R1, 1, 0, -1, R2]
    for r in range(1,5):
        rewards[r] = [2, 1, 0, -1, -2]
    return rewards


def test_value_and_policy_iteration_agree():
    cases = [(100, 110), (10, 100), (1, 10), (10, 15)]
    for R1, R2 in cases:
        rewards = make_rewards(R1, R2)
        env = GridWorld(rewards, terminal_states=[(0,0),(0,4)])
        V_vi, policy_vi = value_iteration(env, gamma=0.95)
        V_pi, policy_pi = policy_iteration(env, gamma=0.95)
        # check value at a few representative states are close
        for s in [(0,1),(2,2),(4,3)]:
            assert abs(V_vi[s] - V_pi[s]) < 1e-2


def test_policy_iteration_random_starts_converge():
    cases = [(100, 110), (10, 100), (1, 10), (10, 15)]
    for R1, R2 in cases:
        rewards = make_rewards(R1, R2)
        env = GridWorld(rewards, terminal_states=[(0,0),(0,4)])
        V_vi, policy_vi = value_iteration(env, gamma=0.95)
        # run multiple random starts
        for seed in range(5):
            Vb, pb = policy_iteration(env, gamma=0.95, random_seed=seed)
            # final policy should match VI-derived optimal policy
            for s in env.all_states():
                assert pb[s] == policy_vi[s]
