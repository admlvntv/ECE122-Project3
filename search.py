from __future__ import annotations
#File implements decision makinh
import math # For infinity
import time # For optional time limits
from dataclasses import dataclass #Transposition table entries
from typing import Dict, Optional, Tuple

from board import Board
from eval import Evaluator
from movegen import ordered_moves
from pieces import Move

MATE_SCORE = 100000 #Used to represent checkmare


@dataclass #Transposition table record, stores depth score
class TTEntry:
    depth: int
    score: int


class Searcher: #Search enginer class
    def __init__(self, evaluator: Optional[Evaluator] = None, use_tt: bool = True):
        self.evaluator = evaluator or Evaluator()
        self.use_tt = use_tt
        self.tt: Dict[str, TTEntry] = {}
        self.nodes = 0
        self.start_time = 0.0
        self.time_limit: Optional[float] = None

    def clear(self) -> None: #Empties transposition table
        self.tt.clear()

    def _out_of_time(self) -> bool: #Checks whether search time limit is reached
        return self.time_limit is not None and (time.time() - self.start_time) >= self.time_limit

    def find_best_move(self, board: Board, max_depth: int = 3, time_limit: Optional[float] = None) -> Tuple[Optional[Move], int]:
        #Resets node count, store start time, set time limit if wanted, generate all legal moves, handle terminal positions
        self.nodes = 0
        self.start_time = time.time()
        self.time_limit = time_limit

        legal = ordered_moves(board)
        if not legal:
            if board.in_check(board.turn):
                return None, -MATE_SCORE
            return None, 0

        best_move = None
        best_score = -math.inf
        for depth in range(1, max_depth + 1):
            score, move = self._search_root(board, depth)
            if move is not None:
                best_move = move
                best_score = score
            if self._out_of_time():
                break
        return best_move, int(best_score)

    def _search_root(self, board: Board, depth: int) -> Tuple[int, Optional[Move]]:
        #Initializes alpha, beta, loops through ordered moves, applies each move, calls negamax on resulting pos
        #Undoes move, tracks best score and move
        alpha = -math.inf
        beta = math.inf
        best_score = -math.inf
        best_move = None

        for move in ordered_moves(board):
            if self._out_of_time():
                break
            board.apply_move(move)
            score = -self._negamax(board, depth - 1, -beta, -alpha, ply=1)
            board.undo_move(move)

            if score > best_score:
                best_score = score
                best_move = move
            if score > alpha:
                alpha = score

        if best_move is None:
            return 0, None
        return int(best_score), best_move

    def _negamax(self, board: Board, depth: int, alpha: float, beta: float, ply: int) -> int:
        #Basically minimax, where one recursive rule works for both players by negating
        #the returned score
        #Increments nodecount, checks time limit, checks transposition table, generates legal moves
        #handles terminal positions, recursively explores moves, updates alpha, cuts off branch when 
        #alpha>=beta, if no legal moves then returns large negative score, if in check, meaning checkmate, otherwise
        #return 0 for stalemate. If transpos table enabled, result is caches by position key+depth
        self.nodes += 1

        if self._out_of_time():
            return self.evaluator.evaluate(board)

        key = board.position_key() + f"|d{depth}"
        if self.use_tt and key in self.tt and self.tt[key].depth >= depth:
            return self.tt[key].score

        legal = ordered_moves(board)
        if depth == 0 or not legal:
            if not legal:
                if board.in_check(board.turn):
                    return -MATE_SCORE + ply
                return 0
            return self.evaluator.evaluate(board)

        best = -math.inf
        for move in legal:
            board.apply_move(move)
            score = -self._negamax(board, depth - 1, -beta, -alpha, ply + 1)
            board.undo_move(move)

            if score > best:
                best = score
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break

        if self.use_tt:
            self.tt[key] = TTEntry(depth=depth, score=int(best))
        return int(best)
