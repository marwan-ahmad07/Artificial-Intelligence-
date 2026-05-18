# Reinforcement Learning Assignment Report

## 1. Introduction & Environment Setup

The goal of this assignment is to implement and analyze reinforcement learning algorithms on a 5x5 stochastic grid world. The environment tests the agent's ability to navigate towards specific goal states while avoiding penalties and managing stochastic movement.

### Grid World Mechanics
- **State Space**: A 5x5 grid (25 total states).
- **Action Space**: Four possible actions: Up, Down, Left, Right.
- **Transition Model (Stochastic)**: When the agent attempts an action, there is a:
  - **70%** probability of moving in the intended direction.
  - **10%** probability of moving in each of the orthogonal directions.
  - **10%** probability of moving in the opposite direction.
  - If a movement results in hitting a grid boundary (wall), the agent remains in its current state.
- **Discount Factor ($\gamma$)**: 0.95. This parameter heavily influences the agent's preference for immediate vs. future rewards.

### Reward Structure
The grid has a deterministic reward structure based on the columns, except for two parameterizable goal states ($R_1$ and $R_2$):
- **Column 0**: Position (0,0) yields reward **$R_1$**. Rows 1-4 yield +2.
- **Column 1**: All cells yield +1.
- **Column 2**: All cells yield 0.
- **Column 3**: All cells yield -1 (Acts as a barrier/penalty zone).
- **Column 4**: Position (0,4) yields reward **$R_2$**. Rows 1-4 yield -2 (A severe penalty zone).

## 2. Algorithms Used

### Value Iteration
Value iteration computes the optimal value function $V^*(s)$ by iteratively applying the Bellman Optimality Equation until convergence:
$$ V(s) \leftarrow \max_a \sum_{s'} P(s'|s,a) [R(s,a) + \gamma V(s')] $$
The optimal policy $\pi^*(s)$ is then extracted by acting greedily with respect to the converged values.

### Policy Iteration (Bonus)
Policy iteration alternates between two steps until the policy stops changing:
1. **Policy Evaluation**: Calculate the value of the current policy $V^\pi(s)$.
2. **Policy Improvement**: Update the policy by choosing the action that maximizes the expected return.

Both algorithms were tested and were mathematically proven to converge to the identical optimal policy for all test cases. 

## 3. Test Cases & Policy Analysis

The behavior of the optimal policy heavily depends on the balance between the two goal state rewards ($R_1$ and $R_2$). Four distinct test cases were evaluated.

### Case 1: $R_1 = 100$, $R_2 = 110$
**Policy Structure**:
- **Top row**: Mixed `Up` and `Left` directions.
- **Middle rows**: Primarily `Up` towards the top targets.
- **Bottom row**: `Up` to escape the lower regions.
- **Right side**: `Up` to urgently avoid the accumulating -2 penalties.

**Intuitive Explanation**:
Despite $R_2$ being larger by 10 points, the policies frequently point towards $R_1$ (e.g., cell (0,1) pointing `Left`). Because the discount factor is 0.95, traveling extra steps geometrically decays future rewards. $R_1$ is quickly accessible from the left side. Travelling to $R_2$ from the left side requires navigating the penalty columns (-1, -2) and taking more time, meaning the discounted value of 110 is comparable to the immediately accessible 100. This creates a "safe haven" psychology where the agent avoids the risk of negative columns.

### Case 2: $R_1 = 10$, $R_2 = 100$
**Policy Structure**:
- Strong overall `Right` and `Up` movement across the grid.
- Few or no cells point `Left` towards $R_1$.

**Intuitive Explanation**:
The 90-point gap is immense. The $R_2$ goal acts as a dominant attractor for the entire grid. Even with the discount factor applied across multiple steps and the risk of the penalty columns (-1 and -2), the final payoff of 100 mathematically overwhelms the local +10 of $R_1$. Consequently, the agent confidently pushes through the penalty zones and risks stochastic slips to eventually reach the highly lucrative top-right corner.

### Case 3: $R_1 = 1$, $R_2 = 10$
**Policy Structure**:
- **Top-left**: Mixed `Up` and `Left` (proximity to $R_1$).
- **Middle/Right**: `Up` mostly, avoiding moving `Right` too early.
- **Bottom**: Slower drift towards the right.

**Intuitive Explanation**:
The 9-point gap creates a clear preference for $R_2$, but the absolute scale of the rewards is lower. Because the target reward is smaller, the penalty columns (-1 and -2) exert a much stronger repelling force. A -2 penalty is 20% of the maximum reward, which makes traversing the bottom right extremely costly. Therefore, the agent prioritizes avoiding the -2 zones by moving `Up` earlier rather than immediately rushing `Right`. The discount factor decay over large distances also makes $R_2$ less dominant for states on the far left.

### Case 4: $R_1 = 10$, $R_2 = 15$
**Policy Structure**:
- Almost **universally `Up`** across the bottom 4 rows.
- `Right` movement is strictly reserved for the top row to safely cross over to $R_2$.

**Intuitive Explanation**:
At first glance, one might expect the agent to move `Right` towards the larger 15 reward. However, the optimal policy is overwhelmingly `Up`. This is a brilliant mathematical consequence of "penalty avoidance routing." 
Columns 3 and 4 contain severe penalties (-1 and -2) in rows 1 through 4. If the agent moves `Right` while in the lower rows, it will enter these negative columns and accumulate severe penalties while trying to move up to $R_2$. The mathematically optimal route is to move `Up` through the "safe" columns (Cols 0, 1, 2 which yield +2, +1, 0) until reaching the top row (row 0), and *only then* move `Right`. In the top row, moving right bypasses the -2 cells completely! Furthermore, for the left side of the grid, the 0.95 discount factor makes the much closer $R_1=10$ just as attractive. Thus, the agent intelligently routes around hazards rather than blindly chasing the highest number.

## 4. Convergence & Algorithm Comparison

| Case | Value Iteration (Iters) | Policy Iteration (Iters) | Converged to Same Policy? |
| :--- | :---: | :---: | :---: |
| $R_1=100, R_2=110$ | ~356 | ~3 | Yes |
| $R_1=10, R_2=100$  | ~354 | ~5 | Yes |
| $R_1=1, R_2=10$    | ~308 | ~5 | Yes |
| $R_1=10, R_2=15$   | ~317 | ~6 | Yes |

**Key Takeaways**:
1. **Convergence**: Policy Iteration requires significantly fewer iterations (4-6 iterations) from a random starting policy compared to Value Iteration (300+ iterations). PI updates the policy directly through exact evaluation steps, resolving the optimal discrete actions much faster than the continuous value landscape converges in VI.
2. **Equivalence**: Both algorithms perfectly converge to the exact same optimal policy, validating the theoretical framework of Markov Decision Processes.
