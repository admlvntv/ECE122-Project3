#Orders legal moves so search alg can examine promising moves first

from __future__ import annotations

from typing import List

from board import Board
from pieces import Move


def move_score(board: Board, move: Move) -> int:
    #Assigns heuristic score to move, scoring ideas are:
    #Captures are valued, promotions get large bonus, king
    #moves get tiny bonus, central squares get small bonus
    score = 0
    src_piece = board.piece_at(*move.src)
    dst_piece = board.piece_at(*move.dst)

    if dst_piece is not None:
        score += 10_000 + dst_piece.value - (src_piece.value if src_piece else 0)

    if move.promotion is not None:
        promo_bonus = {"q": 900, "r": 500, "b": 330, "n": 320}
        score += 8_000 + promo_bonus.get(move.promotion, 0)

    # Slight preference for forcing king moves and central moves.
    if src_piece is not None and src_piece.kind == "K":
        score += 10

    center_distance = abs(move.dst[0] - 3.5) + abs(move.dst[1] - 3.5)
    score += int(20 - center_distance)

    return score

#Gets all legal moves, sorts from best to worst looking using move score
#helps with alpha beta pruning
def ordered_moves(board: Board) -> List[Move]:
    moves = board.generate_legal_moves()
    moves.sort(key=lambda mv: move_score(board, mv), reverse=True)
    return moves
