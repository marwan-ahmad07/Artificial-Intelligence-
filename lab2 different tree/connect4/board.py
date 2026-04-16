"""Core Connect 4 board mechanics.

This module keeps the game state independent from the GUI and AI layers.
It provides move validation, drop/undo operations, and final sequence counting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator

EMPTY = 0
HUMAN = 1
COMPUTER = 2

PLAYER_NAMES = {
    EMPTY: "Empty",
    HUMAN: "Human",
    COMPUTER: "Computer",
}


@dataclass(slots=True)
class MoveRecord:
    """Represents a committed move on the board."""

    row: int
    col: int
    player: int


class Connect4Board:
    """Mutable Connect 4 board with a fixed rectangular grid."""

    def __init__(self, rows: int = 6, cols: int = 7) -> None:
        if rows < 6 or cols < 7:
            raise ValueError("Connect 4 requires at least 6 rows and 7 columns.")

        self.rows = rows
        self.cols = cols
        self.grid: list[list[int]] = [[EMPTY for _ in range(cols)] for _ in range(rows)]
        self.last_move: MoveRecord | None = None

    def clone(self) -> "Connect4Board":
        """Create a deep copy of the board for AI search."""

        cloned = Connect4Board(self.rows, self.cols)
        cloned.grid = [row[:] for row in self.grid]
        cloned.last_move = self.last_move
        return cloned

    def is_valid_column(self, col: int) -> bool:
        """Return True when a piece can still be dropped in the column."""

        return 0 <= col < self.cols and self.grid[0][col] == EMPTY

    def valid_columns(self) -> list[int]:
        """Return all columns that still accept a move."""

        return [col for col in range(self.cols) if self.is_valid_column(col)]

    def drop_piece(self, col: int, player: int) -> int:
        """Drop a piece into a column and return the row where it lands."""

        if not self.is_valid_column(col):
            raise ValueError(f"Column {col} is not valid.")

        for row in range(self.rows - 1, -1, -1):
            if self.grid[row][col] == EMPTY:
                self.grid[row][col] = player
                self.last_move = MoveRecord(row=row, col=col, player=player)
                return row

        raise RuntimeError("No empty slot found despite the column being valid.")

    def undo_piece(self, col: int) -> int:
        """Remove the top-most piece from a column and return its row index."""

        for row in range(self.rows):
            if self.grid[row][col] != EMPTY:
                self.grid[row][col] = EMPTY
                self.last_move = None
                return row

        raise ValueError(f"Column {col} is already empty.")

    def is_full(self) -> bool:
        """Return True if no further moves can be played."""

        return not any(self.is_valid_column(col) for col in range(self.cols))

    def count_sequences(self, player: int) -> int:
        """Count every connect-four window that belongs entirely to one player.

        Overlapping windows are counted independently, which is intentional: the
        assignment defines the winner as the player with the highest total number
        of connect-fours across the final board.
        """

        return sum(1 for _ in self._iter_matching_windows(player))

    def winning_sequences(self, player: int) -> list[list[tuple[int, int]]]:
        """Return the coordinates for every connect-four sequence for a player."""

        return [list(window) for window in self._iter_matching_windows(player)]

    def _iter_matching_windows(self, player: int) -> Iterator[tuple[tuple[int, int], ...]]:
        """Yield all four-cell windows where every cell belongs to the player."""

        directions = ((0, 1), (1, 0), (1, 1), (-1, 1))

        for row in range(self.rows):
            for col in range(self.cols):
                for delta_row, delta_col in directions:
                    window = tuple(
                        (row + step * delta_row, col + step * delta_col)
                        for step in range(4)
                    )
                    if self._window_is_on_board(window) and all(
                        self.grid[r][c] == player for r, c in window
                    ):
                        yield window

    def _window_is_on_board(self, window: Iterable[tuple[int, int]]) -> bool:
        return all(0 <= row < self.rows and 0 <= col < self.cols for row, col in window)

    def board_signature(self) -> str:
        """Return a compact text representation used by debugging and tests."""

        return "\n".join(" ".join(str(cell) for cell in row) for row in self.grid)
