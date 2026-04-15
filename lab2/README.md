# Connect 4 AI Project

This project is a Connect 4 game with an AI player that can run different search algorithms.
The AI decision process is implemented mainly in [connect4/ai.py](connect4/ai.py), and board scoring is implemented in [connect4/heuristics.py](connect4/heuristics.py).

## Run The Game

```bash
python main.py
```

## What Happens During An AI Move

When it is the computer's turn:

1. The game calls `choose_move(...)` in [connect4/ai.py](connect4/ai.py).
2. The selected algorithm is normalized and validated (`minimax`, `alpha-beta`, or `expected`).
3. Search stats start (node counter + timer).
4. Recursive search starts from the root using `_search(...)` with `maximizing=True`.
5. The recursion explores future moves up to the selected depth.
6. At leaf states (depth = 0 or board full), the board is scored by [connect4/heuristics.py](connect4/heuristics.py).
7. The best root move is returned to the game.

## AI Algorithms Explained

### 1) Minimax

Minimax assumes both players play optimally:

- MAX node = computer turn, tries to maximize score.
- MIN node = human turn, tries to minimize score.
- The algorithm alternates MAX/MIN until depth limit.
- Leaf values come from the heuristic evaluator.

In code:

- MAX logic is in `_max_node(...)` inside [connect4/ai.py](connect4/ai.py).
- MIN logic is in `_min_node(...)` inside [connect4/ai.py](connect4/ai.py).

### 2) Alpha-Beta Pruning

Alpha-beta is an optimization of minimax that returns the same final move but searches fewer nodes:

- `alpha` = best score MAX can guarantee so far.
- `beta` = best score MIN can guarantee so far.
- If `beta <= alpha`, remaining siblings are pruned.

In code:

- MAX updates alpha in `_max_node(...)` and may break early.
- MIN updates beta in `_min_node(...)` and may break early.

### 3) Expected Minimax (Expectimax Style)

In `expected` mode, the AI move is stochastic (not always exact column):

- Intended column probability = `0.6`
- Left adjacent legal column = `0.2`
- Right adjacent legal column = `0.2`
- If only one adjacent side is legal, it gets `0.4`

So each candidate action is evaluated by expected value:

$$
	ext{ExpectedScore} = \sum_i P(i) \times \text{ChildScore}(i)
$$

In code:

- `_expected_max_node(...)` chooses the move with highest expected score.
- `_expected_score_for_move(...)` computes weighted average outcomes.

## Heuristic Function (Board Evaluation)

The heuristic in [connect4/heuristics.py](connect4/heuristics.py) returns:

- Positive score: good for computer
- Negative score: good for human

### Scoring Components

1. Center control bonus:
- Pieces in center column are rewarded because central control creates more winning lines.

2. Window-based pattern scoring:
- The evaluator scans every 4-cell window in all directions:
	- Horizontal
	- Vertical
	- Diagonal down-right
	- Diagonal up-right

3. Pattern weights:
- 4-in-a-row (strongest)
- 3-in-a-row + 1 empty
- 2-in-a-row + 2 empty
- Opponent patterns subtract score

The current tunable weights are defined in `HeuristicWeights` in [connect4/heuristics.py](connect4/heuristics.py).

## Why This Works

- Search decides which future to choose.
- Heuristic estimates how good each future board is.
- Better heuristic quality usually means better practical play at fixed depth.
- Alpha-beta improves speed by cutting branches that cannot affect the final choice.

## Notes About Console Tree Output

`TreePrinter` prints a compact search trace to help understand node expansion and pruning.
By default it limits printed depth to keep output readable.

## Suggested Study Order

1. Read `choose_move(...)` in [connect4/ai.py](connect4/ai.py).
2. Follow `_search(...)` dispatch to MAX/MIN/EXPECT.
3. Study `_max_node(...)` and `_min_node(...)` first (minimax).
4. Then read alpha-beta conditions in the same two methods.
5. Finally read `_expected_max_node(...)` and `_expected_score_for_move(...)`.
6. Open [connect4/heuristics.py](connect4/heuristics.py) to see how leaf scores are produced.
