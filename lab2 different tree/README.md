# Connect 4 Assignment

Run the game with:

```bash
python main.py
```

The GUI supports three AI modes, configurable depth, restart, move timing, node counting, and readable search-tree tracing.

## GUI visibility improvements

- A **Scoreboard** panel now shows live human/computer connect-four counts and the heuristic board score.
- A **Search Tree** panel now shows a depth-limited AI trace for the most recent computer move.
- The same tree trace is still printed to the terminal for debugging.

## Console trace readability

Search traces are now printed in a compact format and limited to depth 3 by default.
This keeps terminal output readable while still showing top-level search decisions.

## Heuristic validation and benchmark

Run correctness tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Run the heuristic benchmark:

```bash
python tests/benchmark_heuristic.py
```
