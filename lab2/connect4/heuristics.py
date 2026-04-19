"""Heuristic scoring for Connect 4 positions.

The heuristic is intentionally stronger than a simple piece-counting model.
It rewards actual connect-fours, near-complete threats, and control of the
center column while also penalizing the opponent's opportunities.

============ شرح الـ Heuristic - كيف نقيّم موضع اللوحة ============

الـ Heuristic هو "نسخة مختصرة" من اللعبة الكاملة - يقولنا:
هل هالموضع حسن للـ AI أم سيء؟ كام نقطة؟

في Minimax: لما نصل لأخر عمق نسمح، نستعمل الـ heuristic بدل ما نلعب اللعبة لآخرها.
كل موضع يأخذ score:
  - موجب = حسن للـ AI
  - سالب = حسن للخصم
  - 0 = محايد

الـ heuristic تركز على:
1. الأربعات (connect-4): أقوى pattern - خمس تعطي كتير من النقاط
2. الثلاثات المفتوحة (open-3): تهديد خطير - ممكن يبقى 4 بحركة واحدة
3. الثنيات المفتوحة (open-2): تهديد متوسط - قاعدة لتطوير أقوى
4. التحكم بالوسط (center): عمود وسط بيعطي استراتيجية أفضل
"""

from __future__ import annotations

from dataclasses import dataclass

from connect4.board import COMPUTER, HUMAN, Connect4Board, EMPTY


@dataclass(slots=True)
class HeuristicWeights:
    """Tunable weights used by the evaluation function.
    
    These weights control how many points we give for each pattern:
    
    - connect4: strongest pattern ever - four in a row = 12000 points!
    - open_three: threat very close to winning = 220 points
    - open_two: weaker threat but important for building strategies = 45 points
    - center_piece: each piece in center = 9 points (strategic value)
    
    Large weights (connect4) dominate everything - because they're most important!
    """

    connect4: int = 12_000   # winning position - الأهم!
    open_three: int = 220     # 3 في خط + مكان فارغ = تهديد قريب
    open_two: int = 45        # 2 في خط + مكانين فارغين = قاعدة
    center_piece: int = 9      # تحكم بالوسط جيد استراتيجياً


class HeuristicEvaluator:
    """Evaluate a board from the computer's perspective.

    ============ THE EVALUATOR - evaluates any position quickly and accurately ============
    
    This class calculates a score for the current position:
    - positive = good for AI (COMPUTER)
    - negative = good for opponent (HUMAN)
    
    It uses:
    1. Heuristic weights (the weights above)
    2. Scanning the board for "windows" of size 4×1 (horizontal, vertical, diagonal)
    3. Counting AI and opponent pieces in each window
    4. Applying weights and summing results

    Positive scores are good for the computer, negative scores are good for the
    human player.
    """

    def __init__(self, weights: HeuristicWeights | None = None) -> None:
        self.weights = weights or HeuristicWeights()

    def evaluate(self, board: Connect4Board) -> int:
        """Return a signed score for the current board.

        ============ MAIN EVALUATION FUNCTION ============
        
        Scans the board and calculates all patterns:
        1. Pieces in center (center control)
        2. All possible 4-cell windows (4×1): horizontal, vertical, diagonal
        
        Result = total sum of scores from all patterns
        
        The scoring is computed in a single window pass for efficiency while
        preserving the same behavior as the previous implementation.
        """

        # Final score seen by minimax/expectimax for this board state.
        score = 0

        # ============ PART 1: CENTER CONTROL (Center Control Bonus) ============
        # Center control bonus: central cells are strategically stronger in Connect 4.
        center_column = board.cols // 2
        # Count how many AI (COMPUTER) pieces in center column
        ai_center_count = sum(1 for row in range(board.rows) if board.grid[row][center_column] == COMPUTER)
        # Count how many opponent (HUMAN) pieces in center column
        human_center_count = sum(1 for row in range(board.rows) if board.grid[row][center_column] == HUMAN)
        # Add the difference multiplied by weight
        score += (ai_center_count - human_center_count) * self.weights.center_piece

        # ============ PART 2: 4-CELL WINDOWS - ALL POSSIBLE PATTERNS ============
        # Add contributions from every 4-cell window (horizontal, vertical, diagonals).
        for window in self._iter_windows(board):
            score += self._window_delta(window)

        return score

    def _window_delta(self, window: tuple[int, int, int, int]) -> int:
        """Score a single 4-cell window.
        
        ============ ANALYZE ONE WINDOW (4 consecutive cells) ============
        
        A window is 4 consecutive cells (horizontal, vertical, or diagonal)
        We count how many pieces for AI, opponent, and empty spaces
        
        Rules:
        1. If pieces from both players present = mixed window (no value here)
           (can never become 4-in-a-row here)
        2. If 4 pieces for AI = AI won!
        3. If 4 pieces for opponent = opponent won (bad!)
        4. If 3 AI + empty = threat!! One more = win
        5. If 3 opponent + empty = danger! We might lose
        6. If 2 AI + 2 empty = good foundation to build on
        7. If 2 opponent + 2 empty = foundation with danger from opponent
        8. Everything else = neutral (0)
        """
        # Count how many cells in this window belong to each side.
        ai_count = window.count(COMPUTER)
        human_count = window.count(HUMAN)
        empty_count = 4 - ai_count - human_count

        # Mixed windows (both players present) cannot become a direct 4-in-a-row threat.
        # If both players are present = window is neutral (no threat possible)
        if ai_count > 0 and human_count > 0:
            return 0

        # ============ STRONG PATTERNS FIRST ============
        # Stronger patterns receive larger absolute weights.
        
        # 1️⃣ DIRECT WIN: 4 in a row for AI
        if ai_count == 4:
            return 2 * self.weights.connect4  # Double weight! Very important!
        
        # 2️⃣ DIRECT LOSS: 4 in a row for opponent
        if human_count == 4:
            return -2 * self.weights.connect4  # Negative! Danger!
        
        # 3️⃣ CLOSE THREAT: 3 AI + 1 empty = if unblocked = AI wins
        if ai_count == 3 and empty_count == 1:
            return 2 * self.weights.open_three
        
        # 4️⃣ CLOSE THREAT from opponent: 3 opponent + 1 empty
        if human_count == 3 and empty_count == 1:
            return -2 * self.weights.open_three
        
        # 5️⃣ GOOD DEVELOPMENT: 2 AI + 2 empty = strong foundation
        if ai_count == 2 and empty_count == 2:
            return 2 * self.weights.open_two
        
        # 6️⃣ DEVELOPMENT from opponent: 2 opponent + 2 empty
        if human_count == 2 and empty_count == 2:
            return -2 * self.weights.open_two

        # ============ ANY OTHER PATTERN = NEUTRAL ============
        # Any other pattern is neutral in this heuristic.
        return 0

    def _iter_windows(self, board: Connect4Board):
        """Yield every four-cell window on the board as a tuple of values.
        
        ============ WINDOWS - 4×1 cells from all directions ============
        
        We scan the board and extract all possible sequences of 4 consecutive cells:
        1. Horizontal: left to right
        2. Vertical: top to bottom
        3. Diagonal 1: top-left to bottom-right (\\)
        4. Diagonal 2: bottom-left to top-right (/)
        
        Example for 7-column, 6-row board:
        - Horizontal windows: start from each row and slide right (3 windows per row)
        - Vertical windows: start from each column and slide down (3 windows per column)
        - Diagonal windows: all possible diagonals
        
        Goal: comprehensive, capture all possible patterns!
        """

        # ============ 1️⃣ HORIZONTAL WINDOWS ============
        # Horizontal windows.
        for row in range(board.rows):
            for col in range(board.cols - 3):  # last window at last 4 cells
                yield (
                    board.grid[row][col],
                    board.grid[row][col + 1],
                    board.grid[row][col + 2],
                    board.grid[row][col + 3],
                )

        # ============ 2️⃣ VERTICAL WINDOWS ============
        # Vertical windows.
        for row in range(board.rows - 3):  # last window at last 4 rows
            for col in range(board.cols):
                yield (
                    board.grid[row][col],
                    board.grid[row + 1][col],
                    board.grid[row + 2][col],
                    board.grid[row + 3][col],
                )

        # ============ 3️⃣ DIAGONAL WINDOWS (top-left to bottom-right \\) ============
        # Diagonal windows (top-left to bottom-right).
        for row in range(board.rows - 3):
            for col in range(board.cols - 3):
                yield (
                    board.grid[row][col],
                    board.grid[row + 1][col + 1],
                    board.grid[row + 2][col + 2],
                    board.grid[row + 3][col + 3],
                )

        # ============ 4️⃣ DIAGONAL WINDOWS (bottom-left to top-right /) ============
        # Diagonal windows (bottom-left to top-right).
        for row in range(3, board.rows):  # start from row 3 (after first 3)
            for col in range(board.cols - 3):
                yield (
                    board.grid[row][col],
                    board.grid[row - 1][col + 1],
                    board.grid[row - 2][col + 2],
                    board.grid[row - 3][col + 3],
                )
