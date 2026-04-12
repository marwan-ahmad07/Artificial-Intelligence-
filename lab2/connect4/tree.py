"""Console tree printing and search metrics utilities."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter


@dataclass(slots=True)
class SearchStats:
    """Runtime metrics collected for a single AI move."""

    algorithm: str
    depth: int
    nodes_expanded: int = 0
    started_at: float = 0.0
    finished_at: float = 0.0

    def start(self) -> None:
        self.started_at = perf_counter()

    def stop(self) -> None:
        self.finished_at = perf_counter()

    @property
    def elapsed_seconds(self) -> float:
        return max(0.0, self.finished_at - self.started_at)

    @property
    def elapsed_milliseconds(self) -> float:
        return self.elapsed_seconds * 1000.0


class TreePrinter:
    """Pretty-print a recursive minimax tree in the terminal."""

    def __init__(self, enabled: bool = True, max_depth: int | None = 3) -> None:
        self.enabled = enabled
        self.max_depth = max_depth
        self._truncation_announced = False

    def reset(self) -> None:
        """Reset per-search state used by compact logging."""

        self._truncation_announced = False

    def _depth_allowed(self, depth: int) -> bool:
        if self.max_depth is None:
            return True

        if depth <= self.max_depth:
            return True

        if not self._truncation_announced:
            indent = "  " * self.max_depth
            print(f"{indent}... deeper levels hidden (set TreePrinter.max_depth=None for full trace)")
            self._truncation_announced = True
        return False

    def banner(self, title: str) -> None:
        if not self.enabled:
            return
        line = "-" * 76
        print(f"\n{line}\n[SEARCH] {title}\n{line}")

    def node(self, depth: int, label: str, message: str) -> None:
        if not self.enabled:
            return
        if not self._depth_allowed(depth):
            return
        indent = "  " * depth
        print(f"{indent}{label:<12} {message}")

    def branch(self, depth: int, message: str) -> None:
        if not self.enabled:
            return
        if not self._depth_allowed(depth):
            return
        indent = "  " * depth
        print(f"{indent}-> {message}")
