#Used to evaluate board pos numerically
from __future__ import annotations

from board import Board
#piece value
PIECE_VALUES = {
    "P": 100,
    "N": 320,
    "B": 330,
    "R": 500,
    "Q": 900,
    "K": 0,
}
#Piece square tables, they give small bonus or penalty
#Based on where the piece is located, helps engine prefer
#reasonable positional play over material counting
PAWN_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

KNIGHT_TABLE = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]

BISHOP_TABLE = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]

ROOK_TABLE = [
    [0, 0, 0, 5, 5, 0, 0, 0],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

QUEEN_TABLE = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20],
]

KING_TABLE = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20],
]

#Engine
class Evaluator:
    def __init__(self):
        #Lookup tab;e
        self.tables = {
            "P": PAWN_TABLE,
            "N": KNIGHT_TABLE,
            "B": BISHOP_TABLE,
            "R": ROOK_TABLE,
            "Q": QUEEN_TABLE,
            "K": KING_TABLE,
        }
#Positional bonus for piece on specific square
    def _table_bonus(self, kind: str, color: str, r: int, c: int) -> int:
        table = self.tables[kind]
        if color == "w":
            return table[r][c]
        return table[7 - r][c]
#white uses table directly, black uses vertically mirrored row index

#Computes score from white's pov:
#Loops over all squares, adds piece values+pos bonus for white piece
#Subtracts piece vals+pos bonus for black pieces
#Adds mobility bonus based on legal move counts
#Adds subs check penalty
    def white_score(self, board: Board) -> int:
        score = 0
        for r in range(8):
            for c in range(8):
                piece = board.grid[r][c]
                if piece is None:
                    continue
                bonus = self._table_bonus(piece.kind, piece.color, r, c)
                if piece.color == "w":
                    score += PIECE_VALUES[piece.kind] + bonus
                else:
                    score -= PIECE_VALUES[piece.kind] + bonus

        # Mobility bonus
        current_turn = board.turn
        try:
            board.turn = "w"
            white_mobility = len(board.generate_legal_moves())
            board.turn = "b"
            black_mobility = len(board.generate_legal_moves())
        finally:
            board.turn = current_turn

        score += 2 * (white_mobility - black_mobility)

        if board.in_check("w"):
            score -= 30
        if board.in_check("b"):
            score += 30

        return score
#Returns score from perspective of side to move, makes negamax work naturally
    def evaluate(self, board: Board) -> int:
                """
        Evaluate the board position.

        Parameters:
            board: the current board object

        Output:
            An integer score:
                Positive -> good for the side to move
                Negative -> bad for the side to move

        Rules:
            ● Compute white_score(board)
            ● If board.turn == "w" -> return that score
            ● If board.turn == "b" -> return the negated score
            ● Must not leave the board changed after evaluation

        Hint:
            Use white_score(board), then adjust the sign based on whose turn it is.
        """
        # TODO: Implement board evaluation
        pass
