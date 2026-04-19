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
    """Result returned by a search call.
    
    This data structure represents the result of a best-move search:
    - column: the column index we choose (or None for leaf nodes)
    - score: the game value at this position (positive = good for AI, negative = good for opponent)
    
    Why: We need to return two pieces of information together (move + value) from each recursive call.
    """

    column: int | None
    score: float


class Connect4AI:
    """Computer player that selects moves via adversarial search.
    
    This class contains the AI that plays Connect 4 using three algorithms:
    1. Plain Minimax: calculates best move by examining game tree without pruning branches
    2. Alpha-Beta Pruning: same idea but prunes branches that aren't worth exploring
    3. Expectimax: like minimax but assumes AI can drift left or right (chance nodes)
    
    Data Structure: evaluator (HeuristicEvaluator) that rates how good any board position is.
    """

    def __init__(self, evaluator: HeuristicEvaluator | None = None) -> None:
        self.evaluator = evaluator or HeuristicEvaluator()

    def choose_move(
        self,
        board: Connect4Board,
        depth: int,
        algorithm: str,
        printer: TreePrinter | None = None,
    ) -> tuple[int, SearchStats]:
        """Pick the best column according to the configured algorithm.
        
        Function that selects the best move for the AI:
        - board: current game state
        - depth: how many levels of tree to examine (deeper = better but slower)
        - algorithm: one of three: "minimax" or "alpha-beta" or "expected"
        - printer: for printing tree traversal (for debugging)
        
        Return: (column, stats) which is the selected move and search information.
        """

        # Normalize user/GUI input so values like " Minimax " still work.
        normalized_algorithm = algorithm.lower().strip()
        if normalized_algorithm not in {"minimax", "alpha-beta", "expected"}:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        # ============ BEGIN SEARCH: Record time and number of nodes we examine ============
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
        # ============ BEGIN RECURSIVE SEARCH from tree root ============
        # At each search level, AI (MAX) and opponent (MIN) alternate moving.
        result = self._search(
            board=board,
            depth=depth,
            maximizing=True,  # AI always starts as MAX player
            algorithm=normalized_algorithm,
            stats=stats,
            printer=tree_printer,
            indent=0,
            alpha=-inf,  # worst possible value for MAX at start
            beta=inf,    # best possible value for MIN at start
        )

        # Close metrics and print a final summary line for this move.
        stats.stop()
        stats.selected_column = result.column
        stats.selected_score = result.score
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
        """Recursive search entry point.
        
        Core search function - called recursively:
        1. First from MAX node (AI chooses)
        2. Then MIN node (opponent chooses)
        3. Then MAX again... and so on
        
        Parameters:
        - maximizing: True for AI (MAX), False for opponent (MIN)
        - depth: how many levels remain to explore (0 = stop and evaluate)
        - alpha/beta: Alpha-Beta Pruning bounds (used to cut branches)
        """

        # Count every recursive call as one expanded node.
        stats.nodes_expanded += 1

        # ============ BASE CASE: Reached maximum depth or full board ============
        # Stop recursion either at depth limit or full board, then evaluate position.
        if depth == 0 or board.is_full():
            # When we stop: use heuristic to evaluate the game position
            score = float(self.evaluator.evaluate(board))
            printer.node(indent, "LEAF", f"depth={depth} heuristic={score:.2f}")
            printer.block(indent + 1, "BOARD VALUES", self._board_value_lines(board))
            return SearchResult(column=None, score=score)

        # ============ AT EACH LAYER: Decide if this is MAX or MIN layer ============
        # Decide which type of node to evaluate based on current turn and algorithm.
        if maximizing:
            # In EXPECTED algorithm: even MAX player passes through chance node first
            # (because AI can drift left or right at the chance node)
            # In expected mode, the maximizing player uses a chance node (expectimax).
            if algorithm == "expected":
                return self._expected_max_node(board, depth, algorithm, stats, printer, indent, alpha, beta)
            # In MINIMAX and ALPHA-BETA: MAX player chooses the best move
            # In minimax/alpha-beta modes, the maximizing player chooses the best child.
            return self._max_node(board, depth, algorithm, stats, printer, indent, alpha, beta)

        # ============ MIN LAYERS (opponent plays): choose worst value for AI ============
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
        """MAX node for minimax: try all legal columns and keep the highest score.
        
        ============ THIS IS THE CORE MINIMAX PART ============
        The MAX player (AI) chooses the best move from all possible moves.
        Plan:
        1. Try each legal column
        2. For each column: place piece, recursively call search for MIN (opponent), get result
        3. Pick the move that returned the highest score
        
        ============ AND ALSO ALPHA-BETA PRUNING HERE ============
        Alpha-Beta is an optimization: instead of exploring every branch, we prune branches
        that won't affect the final decision.
        
        The idea:
        - alpha = best value that MAX found so far (guaranteed lower bound)
        - beta = best value that MIN found (guaranteed upper bound)
        - If alpha >= beta, then MIN's parent won't choose this branch, so we can prune
        
        In this MAX node: we track alpha (because MAX increases alpha when finding better moves)
        """
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
                maximizing=False,  # opponent (MIN) plays next
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

            # ============ ALPHA-BETA PRUNING in MAX node ============
            # Alpha-beta pruning for MAX: update alpha and cut remaining branches when possible.
            if algorithm == "alpha-beta":
                # alpha = best lower bound guaranteed for MAX on this path.
                alpha = max(alpha, best_score)
                # If alpha >= beta, we can prune! Because MIN's parent won't choose this branch anyway
                if beta <= alpha:
                    printer.node(indent + 1, "PRUNE", f"alpha={alpha:.2f} beta={beta:.2f}")
                    # Remaining siblings cannot improve the final decision.
                    break  # Exit loop - no point checking remaining moves

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
        """MIN node for minimax: simulate opponent moves and keep the lowest score.
        
        ============ THIS IS THE CORE MINIMAX PART - opponent layer ============
        The MIN player (opponent) chooses the move that gives the lowest score to AI.
        Plan:
        1. Try each legal column
        2. For each column: place piece, recursively call search for MAX (AI next), get result
        3. Pick the move that returned the lowest score (worst for AI)
        
        ============ AND ALSO ALPHA-BETA PRUNING HERE ============
        In this MIN node: we track beta (because MIN decreases beta)
        - If beta <= alpha, then MAX's parent will prune this branch, so we prune here too
        """
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
                maximizing=True,  # AI (MAX) plays next
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

            # ============ ALPHA-BETA PRUNING in MIN node ============
            # Alpha-beta pruning for MIN: update beta and cut remaining branches when possible.
            if algorithm == "alpha-beta":
                # beta = best upper bound guaranteed for MIN on this path.
                beta = min(beta, best_score)
                # If beta <= alpha, we can prune! Because MAX's parent won't choose this branch
                if beta <= alpha:
                    printer.node(indent + 1, "PRUNE", f"alpha={alpha:.2f} beta={beta:.2f}")
                    # Remaining siblings cannot change MIN's final choice.
                    break  # Exit loop

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
        """Expectimax MAX node: choose the move with the highest expected score.
        
        ============ THIS IS EXPECTIMAX PART - DIFFERENT FROM MINIMAX ============
        In MINIMAX: we assume both players choose perfectly.
        In EXPECTIMAX: we assume AI can make mistakes and drift left or right!
        
        The idea:
        - Instead of choosing one move and returning a fixed score
        - We choose a move, but when executed: 60% goes to target column, 20% left, 20% right
        - The score we return is the "weighted average" (expected value) of all outcomes
        
        We are in MAX here, so we choose the move with the highest expected score
        """
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

        ============ THIS IS EXPECTIMAX PART - THE CHANCE NODE ============
        When AI tries to play in a certain column, it can succeed or drift:
        - 60% goes to the target column
        - 20% drifts left (if there's a column to the left)
        - 20% drifts right (if there's a column to the right)

        We compute expected value = sum(probability * score of each outcome)
        
        The AI tries to play the selected column, but there is a probability of
        drifting to an adjacent legal column. If only one side exists, the extra
        probability mass is assigned to that side so the distribution still sums
        to 1.0.
        """

        # Adjacent columns are possible drift targets if they are legal moves.
        left = column - 1 if column - 1 >= 0 and board.is_valid_column(column - 1) else None
        right = column + 1 if column + 1 < board.cols and board.is_valid_column(column + 1) else None

        # ============ DETERMINE PROBABILITIES FOR ALL POSSIBLE OUTCOMES ============
        # Expected outcomes: 60% intended column, 20/20% to adjacent columns when both are valid.
        outcomes: list[tuple[float, int]] = [(0.6, column)]  # 60% to target
        
        if left is not None and right is not None:
            # In normal cases: 20% left and 20% right
            outcomes.append((0.2, left))
            outcomes.append((0.2, right))
        elif left is not None or right is not None:
            # If only one side exists (board edge): give the 20% to the other side for 0.4 total
            # If only one side exists, it receives the whole side probability mass (0.4).
            outcomes.append((0.4, left if left is not None else right))

        # ============ ACCUMULATE WEIGHTED VALUES FROM ALL POSSIBLE OUTCOMES ============
        # Accumulate weighted average from all chance outcomes.
        total = 0.0
        printer.node(indent, "CHANCE", f"column={column} outcomes={len(outcomes)}")

        for probability, actual_column in outcomes:
            # ============ FOR EACH OUTCOME: PLAY THE MOVE AND CALCULATE SCORE ============
            # Chance node aggregation: expected value = sum(probability * child_score).
            # For each stochastic outcome, recurse as if that actual column happened.
            board.drop_piece(actual_column, COMPUTER)
            child = self._search(
                board=board,
                depth=depth - 1,
                maximizing=False,  # opponent (MIN) plays next
                algorithm=algorithm,
                stats=stats,
                printer=printer,
                indent=indent + 1,
                alpha=alpha,
                beta=beta,
            )
            board.undo_piece(actual_column)
            
            # Calculate weighted score: probability × value
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

        ============ ALGORITHM OPTIMIZATION: ORDER COLUMNS STRATEGICALLY ============
        
        In Connect 4: center columns are stronger than edge columns
        - Helps the game look intelligent (focus on center first)
        - Helps Alpha-Beta Pruning cut branches faster (strong moves checked early)
        
        Idea: order columns by how close they are to center
        
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
        """Prefer the move closer to the center column when scores tie.
        
        ============ DECISION TIEBREAKER: WHEN SCORES ARE EQUAL ============
        When we have two moves with the same score, choose the one closer to center
        (because center is strategically stronger in Connect 4)
        
        Example: Score 50 from column 2, and Score 50 from column 5 (if board has 7 columns)
        → Give priority to column 2 (closer to center)
        """

        if current is None:
            return True

        # Tie-breaker policy: choose the move closest to center, then smaller index.
        center = cols // 2
        candidate_distance = abs(candidate - center)
        current_distance = abs(current - center)
        return candidate_distance < current_distance or (
            candidate_distance == current_distance and candidate < current
        )

    def _board_value_lines(self, board: Connect4Board) -> list[str]:
        """Return a readable matrix of board values for tree output.
        
        Helper function for debugging: prints board in readable format in tree visualization
        """

        header = " ".join(f"c{col}" for col in range(board.cols))
        rows = [f"r{row}: " + "  ".join(str(cell) for cell in board.grid[row]) for row in range(board.rows)]
        return [header, *rows]
