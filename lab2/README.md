# Connect 4 Assignment

Run the game with:

```bash
python main.py
```

The GUI supports three AI modes, configurable depth, restart, move timing, node counting, and console minimax tracing.

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
