"""Heuristic scoring for Connect 4 positions.

The heuristic is intentionally stronger than a simple piece-counting model.
It rewards actual connect-fours, near-complete threats, and control of the
center column while also penalizing the opponent's opportunities.
"""

from __future__ import annotations

from dataclasses import dataclass

from connect4.board import COMPUTER, HUMAN, Connect4Board, EMPTY


@dataclass(slots=True)
class HeuristicWeights:
    """Tunable weights used by the evaluation function."""

    connect4: int = 12_000
    open_three: int = 220
    open_two: int = 45
    center_piece: int = 9


class HeuristicEvaluator:
    """Evaluate a board from the computer's perspective.

    Positive scores are good for the computer, negative scores are good for the
    human player.
    """

    def __init__(self, weights: HeuristicWeights | None = None) -> None:
        self.weights = weights or HeuristicWeights()

    def evaluate(self, board: Connect4Board) -> int:
        """Return a signed score for the current board.

        The scoring is computed in a single window pass for efficiency while
        preserving the same behavior as the previous implementation.
        """

        score = 0

        center_column = board.cols // 2
        ai_center_count = sum(1 for row in range(board.rows) if board.grid[row][center_column] == COMPUTER)
        human_center_count = sum(1 for row in range(board.rows) if board.grid[row][center_column] == HUMAN)
        score += (ai_center_count - human_center_count) * self.weights.center_piece

        for window in self._iter_windows(board):
            score += self._window_delta(window)

        return score

    def _window_delta(self, window: tuple[int, int, int, int]) -> int:
        ai_count = window.count(COMPUTER)
        human_count = window.count(HUMAN)
        empty_count = 4 - ai_count - human_count

        if ai_count > 0 and human_count > 0:
            return 0

        if ai_count == 4:
            return 2 * self.weights.connect4
        if human_count == 4:
            return -2 * self.weights.connect4
        if ai_count == 3 and empty_count == 1:
            return 2 * self.weights.open_three
        if human_count == 3 and empty_count == 1:
            return -2 * self.weights.open_three
        if ai_count == 2 and empty_count == 2:
            return 2 * self.weights.open_two
        if human_count == 2 and empty_count == 2:
            return -2 * self.weights.open_two

        return 0

    def _iter_windows(self, board: Connect4Board):
        """Yield every four-cell window on the board as a tuple of values."""

        for row in range(board.rows):
            for col in range(board.cols - 3):
                yield (
                    board.grid[row][col],
                    board.grid[row][col + 1],
                    board.grid[row][col + 2],
                    board.grid[row][col + 3],
                )

        for row in range(board.rows - 3):
            for col in range(board.cols):
                yield (
                    board.grid[row][col],
                    board.grid[row + 1][col],
                    board.grid[row + 2][col],
                    board.grid[row + 3][col],
                )

        for row in range(board.rows - 3):
            for col in range(board.cols - 3):
                yield (
                    board.grid[row][col],
                    board.grid[row + 1][col + 1],
                    board.grid[row + 2][col + 2],
                    board.grid[row + 3][col + 3],
                )

        for row in range(3, board.rows):
            for col in range(board.cols - 3):
                yield (
                    board.grid[row][col],
                    board.grid[row - 1][col + 1],
                    board.grid[row - 2][col + 2],
                    board.grid[row - 3][col + 3],
                )
