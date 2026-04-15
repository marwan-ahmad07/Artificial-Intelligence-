"""AI search strategies for Connect 4.

This module implements three selectable search modes:
- Plain minimax
- Minimax with alpha-beta pruning
- Expected minimax with probabilistic move displacement
"""

from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import Optional

from connect4.board import COMPUTER, HUMAN, Connect4Board
from connect4.heuristics import HeuristicEvaluator
from connect4.tree import SearchStats, TreePrinter


@dataclass(slots=True)
class SearchResult:
    """Result returned by a search call."""

    column: int | None
    score: float


class Connect4AI:
    """Computer player that selects moves via adversarial search."""

    def __init__(self, evaluator: HeuristicEvaluator | None = None) -> None:
        self.evaluator = evaluator or HeuristicEvaluator()

    def choose_move(
        self,
        board: Connect4Board,
        depth: int,
        algorithm: str,
        printer: TreePrinter | None = None,
    ) -> tuple[int, SearchStats]:
        """Pick the best column according to the configured algorithm."""

        # Normalize user/GUI input so values like " Minimax " still work.
        normalized_algorithm = algorithm.lower().strip()
        if normalized_algorithm not in {"minimax", "alpha-beta", "expected"}:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        # Start timing and node-count metrics for this single AI decision.
        stats = SearchStats(algorithm=normalized_algorithm, depth=depth)
        stats.start()

        # TreePrinter is only for visualization in console; it does not affect logic.
        tree_printer = printer or TreePrinter(enabled=True, max_depth=3)
        tree_printer.reset()
        tree_printer.banner(
            f"AI search start | algorithm={normalized_algorithm} | depth={depth} | nodes=0"
        )

        # Root of the game tree: AI is always the maximizing player.
        result = self._search(
            board=board,
            depth=depth,
            maximizing=True,
            algorithm=normalized_algorithm,
            stats=stats,
            printer=tree_printer,
            indent=0,
            alpha=-inf,
            beta=inf,
        )

        # Close metrics and print a final summary line for this move.
        stats.stop()
        tree_printer.banner(
            "AI search end | move={move} | score={score:.2f} | nodes={nodes} | time={time:.2f} ms".format(
                move=result.column,
                score=result.score,
                nodes=stats.nodes_expanded,
                time=stats.elapsed_milliseconds,
            )
        )

        # Fallback safety: if search returns no move, pick the first legal column.
        if result.column is None:
            valid_columns = board.valid_columns()
            if not valid_columns:
                raise RuntimeError("No valid move available for the AI.")
            return valid_columns[0], stats

        return result.column, stats

    def _search(
        self,
        board: Connect4Board,
        depth: int,
        maximizing: bool,
        algorithm: str,
        stats: SearchStats,
        printer: TreePrinter,
        indent: int,
        alpha: float,
        beta: float,
    ) -> SearchResult:
        """Recursive search entry point."""

        # Count every recursive call as one expanded node.
        stats.nodes_expanded += 1

        # Stop recursion either at depth limit or full board, then evaluate position.
        if depth == 0 or board.is_full():
            score = float(self.evaluator.evaluate(board))
            printer.node(indent, "LEAF", f"depth={depth} score={score:.2f}")
            return SearchResult(column=None, score=score)

        # Decide which type of node to evaluate based on current turn and algorithm.
        if maximizing:
            # In expected mode, the maximizing player uses a chance node (expectimax).
            if algorithm == "expected":
                return self._expected_max_node(board, depth, algorithm, stats, printer, indent, alpha, beta)
            # In minimax/alpha-beta modes, the maximizing player chooses the best child.
            return self._max_node(board, depth, algorithm, stats, printer, indent, alpha, beta)

        # The minimizing player (opponent) chooses the worst score for the AI.
        return self._min_node(board, depth, algorithm, stats, printer, indent, alpha, beta)

    def _max_node(
        self,
        board: Connect4Board,
        depth: int,
        algorithm: str,
        stats: SearchStats,
        printer: TreePrinter,
        indent: int,
        alpha: float,
        beta: float,
    ) -> SearchResult:
        # MAX node for minimax: try all legal columns and keep the highest score.
        best_score = -inf
        best_column: int | None = None

        printer.node(indent, "MAX", f"depth={depth} alpha={alpha:.2f} beta={beta:.2f}")

        # Explore legal moves in a center-first order for stronger play/pruning.
        for column in self._ordered_columns(board):
            # Apply one candidate move, recurse, then undo (backtracking).
            board.drop_piece(column, COMPUTER)
            child = self._search(
                board=board,
                depth=depth - 1,
                maximizing=False,
                algorithm=algorithm,
                stats=stats,
                printer=printer,
                indent=indent + 1,
                alpha=alpha,
                beta=beta,
            )
            board.undo_piece(column)

            printer.branch(indent + 1, f"column={column} -> score={child.score:.2f}")

            # Keep the highest score seen so far (best move for MAX/AI).
            if child.score > best_score or (
                child.score == best_score and self._prefer_column(column, best_column, board.cols)
            ):
                best_score = child.score
                best_column = column

            # Alpha-beta pruning for MAX: update alpha and cut remaining branches when possible.
            if algorithm == "alpha-beta":
                # alpha = best lower bound guaranteed for MAX on this path.
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    printer.node(indent + 1, "PRUNE", f"alpha={alpha:.2f} beta={beta:.2f}")
                    # Remaining siblings cannot improve the final decision.
                    break

        printer.node(indent, "MAX-CHOICE", f"column={best_column} score={best_score:.2f}")
        return SearchResult(column=best_column, score=best_score)

    def _min_node(
        self,
        board: Connect4Board,
        depth: int,
        algorithm: str,
        stats: SearchStats,
        printer: TreePrinter,
        indent: int,
        alpha: float,
        beta: float,
    ) -> SearchResult:
        # MIN node for minimax: simulate opponent moves and keep the lowest score.
        best_score = inf
        best_column: int | None = None

        printer.node(indent, "MIN", f"depth={depth} alpha={alpha:.2f} beta={beta:.2f}")

        # Opponent also explores legal moves in the same center-first order.
        for column in self._ordered_columns(board):
            # Apply opponent move, recurse, then undo (backtracking).
            board.drop_piece(column, HUMAN)
            child = self._search(
                board=board,
                depth=depth - 1,
                maximizing=True,
                algorithm=algorithm,
                stats=stats,
                printer=printer,
                indent=indent + 1,
                alpha=alpha,
                beta=beta,
            )
            board.undo_piece(column)

            printer.branch(indent + 1, f"column={column} -> score={child.score:.2f}")

            # Keep the lowest score seen so far (best move for MIN/opponent).
            if child.score < best_score or (
                child.score == best_score and self._prefer_column(column, best_column, board.cols)
            ):
                best_score = child.score
                best_column = column

            # Alpha-beta pruning for MIN: update beta and cut remaining branches when possible.
            if algorithm == "alpha-beta":
                # beta = best upper bound guaranteed for MIN on this path.
                beta = min(beta, best_score)
                if beta <= alpha:
                    printer.node(indent + 1, "PRUNE", f"alpha={alpha:.2f} beta={beta:.2f}")
                    # Remaining siblings cannot change MIN's final choice.
                    break

        printer.node(indent, "MIN-CHOICE", f"column={best_column} score={best_score:.2f}")
        return SearchResult(column=best_column, score=best_score)

    def _expected_max_node(
        self,
        board: Connect4Board,
        depth: int,
        algorithm: str,
        stats: SearchStats,
        printer: TreePrinter,
        indent: int,
        alpha: float,
        beta: float,
    ) -> SearchResult:
        # Expectimax MAX node: choose the move with the highest expected score.
        best_score = -inf
        best_column: int | None = None

        printer.node(indent, "EXPECT-MAX", f"depth={depth}")

        # Evaluate each candidate move by averaging over stochastic outcomes.
        for column in self._ordered_columns(board):
            expected_score = self._expected_score_for_move(
                board=board,
                column=column,
                depth=depth,
                algorithm=algorithm,
                stats=stats,
                printer=printer,
                indent=indent + 1,
                alpha=alpha,
                beta=beta,
            )
            printer.branch(indent + 1, f"column={column} -> expected_score={expected_score:.2f}")

            # Keep the action with highest expected utility.
            if expected_score > best_score or (
                expected_score == best_score and self._prefer_column(column, best_column, board.cols)
            ):
                best_score = expected_score
                best_column = column

        printer.node(indent, "EXPECT-CHOICE", f"column={best_column} score={best_score:.2f}")
        return SearchResult(column=best_column, score=best_score)

    def _expected_score_for_move(
        self,
        board: Connect4Board,
        column: int,
        depth: int,
        algorithm: str,
        stats: SearchStats,
        printer: TreePrinter,
        indent: int,
        alpha: float,
        beta: float,
    ) -> float:
        """Compute the expected value for the stochastic AI move.

        The AI tries to play the selected column, but there is a probability of
        drifting to an adjacent legal column. If only one side exists, the extra
        probability mass is assigned to that side so the distribution still sums
        to 1.0.
        """

        # Adjacent columns are possible drift targets if they are legal moves.
        left = column - 1 if column - 1 >= 0 and board.is_valid_column(column - 1) else None
        right = column + 1 if column + 1 < board.cols and board.is_valid_column(column + 1) else None

        # Expected outcomes: 60% intended column, 20/20% to adjacent columns when both are valid.
        outcomes: list[tuple[float, int]] = [(0.6, column)]
        if left is not None and right is not None:
            outcomes.append((0.2, left))
            outcomes.append((0.2, right))
        elif left is not None or right is not None:
            # If only one side exists, it receives the whole side probability mass (0.4).
            outcomes.append((0.4, left if left is not None else right))

        # Accumulate weighted average from all chance outcomes.
        total = 0.0
        printer.node(indent, "CHANCE", f"column={column} outcomes={len(outcomes)}")

        for probability, actual_column in outcomes:
            # Chance node aggregation: expected value = sum(probability * child_score).
            # For each stochastic outcome, recurse as if that actual column happened.
            board.drop_piece(actual_column, COMPUTER)
            child = self._search(
                board=board,
                depth=depth - 1,
                maximizing=False,
                algorithm=algorithm,
                stats=stats,
                printer=printer,
                indent=indent + 1,
                alpha=alpha,
                beta=beta,
            )
            board.undo_piece(actual_column)
            weighted_score = probability * child.score
            total += weighted_score
            printer.branch(
                indent + 1,
                f"p={probability:.1f} actual_column={actual_column} child={child.score:.2f} weighted={weighted_score:.2f}",
            )

        printer.node(indent, "CHANCE-RESULT", f"column={column} expected={total:.2f}")
        return total

    def _ordered_columns(self, board: Connect4Board) -> list[int]:
        """Return valid columns ordered from the center outward.

        Center-first ordering makes the evaluation look more human-like and also
        improves alpha-beta pruning efficiency because stronger moves are checked
        earlier.
        """

        # Typical Connect 4 strategy prefers central columns.
        center = board.cols // 2
        # Sort by distance to center, then by index for deterministic tie-breaking.
        order = sorted(range(board.cols), key=lambda col: (abs(col - center), col))
        return [col for col in order if board.is_valid_column(col)]

    def _prefer_column(self, candidate: int, current: Optional[int], cols: int) -> bool:
        """Prefer the move closer to the center column when scores tie."""

        if current is None:
            return True

        # Tie-breaker policy: choose the move closest to center, then smaller index.
        center = cols // 2
        candidate_distance = abs(candidate - center)
        current_distance = abs(current - center)
        return candidate_distance < current_distance or (
            candidate_distance == current_distance and candidate < current
        )
