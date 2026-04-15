"""Console tree printing and search metrics utilities."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable


@dataclass(slots=True)
class SearchStats:
    """Runtime metrics collected for a single AI move."""

    algorithm: str
    depth: int
    nodes_expanded: int = 0
    selected_column: int | None = None
    selected_score: float = 0.0
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


@dataclass(slots=True)
class TraceEvent:
    """Structured search-trace event used by GUI renderers."""

    kind: str
    depth: int
    text: str
    lines: list[str] | None = None


class TreePrinter:
    """Pretty-print a recursive minimax tree in the terminal."""

    def __init__(
        self,
        enabled: bool = True,
        max_depth: int | None = 3,
        sinks: list[Callable[[str], None]] | None = None,
    ) -> None:
        self.enabled = enabled
        self.max_depth = max_depth
        self.sinks = sinks or [print]
        self.lines: list[str] = []
        self.events: list[TraceEvent] = []
        self._truncation_announced = False

    def reset(self) -> None:
        """Reset per-search state used by compact logging."""

        self._truncation_announced = False
        self.lines.clear()
        self.events.clear()

    def _emit(self, text: str) -> None:
        self.lines.append(text)
        for sink in self.sinks:
            sink(text)

    def _record(self, kind: str, depth: int, text: str, lines: list[str] | None = None) -> None:
        self.events.append(TraceEvent(kind=kind, depth=depth, text=text, lines=lines))

    def _depth_allowed(self, depth: int) -> bool:
        if self.max_depth is None:
            return True

        if depth <= self.max_depth:
            return True

        if not self._truncation_announced:
            indent = "  " * self.max_depth
            message = "... deeper levels hidden (set TreePrinter.max_depth=None for full trace)"
            self._emit(f"{indent}{message}")
            self._record(kind="truncated", depth=self.max_depth, text=message)
            self._truncation_announced = True
        return False

    def banner(self, title: str) -> None:
        if not self.enabled:
            return
        line = "-" * 76
        self._emit(f"\n{line}")
        self._emit(f"[SEARCH] {title}")
        self._emit(line)
        self._record(kind="banner", depth=0, text=title)

    def node(self, depth: int, label: str, message: str) -> None:
        if not self.enabled:
            return
        if not self._depth_allowed(depth):
            return
        indent = "  " * depth
        self._emit(f"{indent}{label:<12} {message}")
        self._record(kind="node", depth=depth, text=f"{label}: {message}")

    def branch(self, depth: int, message: str) -> None:
        if not self.enabled:
            return
        if not self._depth_allowed(depth):
            return
        indent = "  " * depth
        self._emit(f"{indent}-> {message}")
        self._record(kind="branch", depth=depth, text=message)

    def block(self, depth: int, label: str, lines: list[str]) -> None:
        """Print a labeled multiline block while preserving tree indentation."""

        if not self.enabled:
            return
        if not self._depth_allowed(depth):
            return

        if not lines:
            self.node(depth, label, "(empty)")
            return

        indent = "  " * depth
        self._emit(f"{indent}{label}:")
        child_indent = "  " * (depth + 1)
        for line in lines:
            self._emit(f"{child_indent}{line}")
        self._record(kind="block", depth=depth, text=label, lines=lines)
