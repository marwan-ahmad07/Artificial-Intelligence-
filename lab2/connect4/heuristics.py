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
        """Return a signed score for the current board."""

        ai_score = self._player_score(board, COMPUTER)
        human_score = self._player_score(board, HUMAN)
        return ai_score - human_score

    def _player_score(self, board: Connect4Board, player: int) -> int:
        opponent = HUMAN if player == COMPUTER else COMPUTER
        score = 0

        # Final connect-fours dominate the score because the assignment defines
        # victory by the total number of completed four-in-a-row sequences.
        score += board.count_sequences(player) * self.weights.connect4

        center_column = board.cols // 2
        center_count = sum(1 for row in range(board.rows) if board.grid[row][center_column] == player)
        score += center_count * self.weights.center_piece

        for window in self._iter_windows(board):
            score += self._evaluate_window(window, player, opponent)

        return score

    def _evaluate_window(self, window: tuple[int, int, int, int], player: int, opponent: int) -> int:
        player_count = window.count(player)
        opponent_count = window.count(opponent)
        empty_count = window.count(EMPTY)

        if player_count > 0 and opponent_count > 0:
            return 0

        if player_count == 4:
            return self.weights.connect4
        if player_count == 3 and empty_count == 1:
            return self.weights.open_three
        if player_count == 2 and empty_count == 2:
            return self.weights.open_two
        if opponent_count == 3 and empty_count == 1:
            return -self.weights.open_three
        if opponent_count == 2 and empty_count == 2:
            return -self.weights.open_two

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
