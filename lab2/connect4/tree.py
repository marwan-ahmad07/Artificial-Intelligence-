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

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def banner(self, title: str) -> None:
        if not self.enabled:
            return
        line = "=" * 92
        print(f"\n{line}\n{title}\n{line}")

    def node(self, depth: int, label: str, message: str) -> None:
        if not self.enabled:
            return
        indent = "  " * depth
        print(f"{indent}{label}: {message}")

    def branch(self, depth: int, message: str) -> None:
        if not self.enabled:
            return
        indent = "  " * depth
        print(f"{indent}- {message}")
