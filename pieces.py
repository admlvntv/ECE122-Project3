"""This file is used to define the basic chess concepts, squares, 
moves, the piece base class, the individual piece types.
"""

from __future__ import annotations
"""This delays evaluation of type hints until runtime is finished. 
It is useful because later in the file, Move refers to Piece, and 
Piece refers to Board, if you don't have this, it'd create forward-reference issues.
"""
from dataclasses import dataclass#dataclass lets us define Move with minimal boilerplate.

from typing import List, Optional, Tuple, TYPE_CHECKING
#List, Optional, Tuple are type annotations.
#TYPE_CHECKING is being used to avoid circular imports at runtime.

if TYPE_CHECKING:
    from board import Board
#This import is only used by static type checkers. prevents circular import problem 
# between pieces.py and board.py.

Square = Tuple[int, int]#Defines a square as a pair of integers (row, col).



def in_bounds(r: int, c: int) -> bool:
    #Checks whether a coordinate is on the 8×8 board.

    return 0 <= r < 8 and 0 <= c < 8


def square_name(r: int, c: int) -> str:
    #Converts internal board coordinates like (6, 4) into chess notation like e2.
    return f"{chr(ord('a') + c)}{8 - r}"


def parse_square(text: str) -> Square:
    #Converts notation like "e2" into internal coordinates

    text = text.strip().lower()
    if len(text) != 2:
        raise ValueError(f"Invalid square: {text}")
    file_ch, rank_ch = text[0], text[1]
    if file_ch < "a" or file_ch > "h" or rank_ch < "1" or rank_ch > "8":
        raise ValueError(f"Invalid square: {text}")
    c = ord(file_ch) - ord("a")
    r = 8 - int(rank_ch)
    return r, c


@dataclass
class Move:
    src: Square#Starting square
    dst: Square#Ending square
    promotion: Optional[str] = None#Promotion
    moved_piece: Optional["Piece"] = None#Moved piece
    captured_piece: Optional["Piece"] = None#Captured piece
    prev_turn: Optional[str] = None#Turn before the move, for undo

    def uci(self) -> str:
        #Returns the move in coordinate format like e2e4 or e7e8q.

        text = square_name(*self.src) + square_name(*self.dst)
        if self.promotion:
            text += self.promotion.lower()
        return text

    def __str__(self) -> str:
        return self.uci()


class Piece:
    #Default piece type and value. Subclasses override these.
    kind = "?"
    value = 0

    def __init__(self, color: str):
        #Creates a piece with color "w" or "b".
        if color not in ("w", "b"):
            raise ValueError("color must be 'w' or 'b'")
        self.color = color

    @property
    def symbol(self) -> str:
        #Returns the printed character for this piece. white=uppercase, black=lower
        return self.kind.upper() if self.color == "w" else self.kind.lower()

    def copy(self) -> "Piece":
        #Creates a new piece of the same type and color,used when cloning boards.
        return type(self)(self.color)

    def _slide_moves(self, board: "Board", r: int, c: int, dirs: List[Tuple[int, int]]) -> List[Move]:
       """
        Generate moves for pieces that move continuously in a direction (sliding pieces).

        Parameters:
            board: the current board object
            r: current row of the piece
            c: current column of the piece
            directions: list of (row_change, col_change) pairs representing directions

        Output:
            A list of Move objects representing valid moves.

        Rules:
            - For each direction, keep moving until:
                • You go out of bounds
                • You hit another piece
            - If a square is empty -> add move and continue
            - If it has an enemy piece -> add move and STOP in that direction
            - If it has your own piece -> STOP immediately (do not add move)
            - Do not modify the board

        Hint:
            Use a loop to continue stepping in each direction.
        """
        # TODO: Implement sliding movement logic
        pass

    def _step_moves(self, board: "Board", r: int, c: int, deltas: List[Tuple[int, int]]) -> List[Move]:

        """
        Generate moves for pieces that move a fixed distance (one step per direction).

        Parameters:
            board: the current board object (used to check positions and pieces)
            r: current row of the piece
            c: current column of the piece
            steps: list of (row_change, col_change) pairs representing possible moves

        Output:
            A list of Move objects representing valid moves for this piece.

        Rules:
            - Each step represents a single possible move (no looping).
            - The move must stay inside the board.
            - If the destination square is empty -> add the move.
            - If the destination has an enemy piece -> add the move.
            - If the destination has your own piece -> do NOT add the move.
            - Do not modify the board.

        Hint:
            Loop through each (dr, dc) in steps and check the resulting square.
        """
        # TODO: Implement step-based movement logic
        pass
       

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        #Abstract method implemented by subclasses
        raise NotImplementedError

    def attacks(self, board: "Board", r: int, c: int) -> List[Square]:
        #Returns all attacked squares on p-l moves, used for check detection
        return [mv.dst for mv in self.pseudo_legal_moves(board, r, c)]


class Pawn(Piece):
    #Pawn behavior
    kind = "P"
    value = 100 #Worth 100 in ealuation function

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
                """
        Generate all pseudo-legal moves for a pawn.

        Parameters:
            board: the current board object
            r: current row of the pawn
            c: current column of the pawn

        Output:
            A list of Move objects for this pawn.

        Rules:
            - Pawn moves depend on color:
                • White moves up (row decreases)
                • Black moves down (row increases)
            - Forward move:
                • Can move 1 square forward if empty
            - Capture move:
                • Can move diagonally forward if an enemy piece is present

            ● pawn may move 2 squares from starting position
            ● promotion must include q, r, b, n
            - Do NOT allow moving off the board
            - Do NOT modify the board

        Hint:
            Check forward square and diagonal squares separately.
        """
        # TODO: Implement pawn movement logic
        pass

#Same template now for rest
class Knight(Piece):
    kind = "N"
    value = 320

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
                """
        Generate all pseudo-legal moves for a knight.

        Parameters:
            board: the current board object
            r: current row of the knight
            c: current column of the knight

        Output:
            A list of Move objects.

        Rules:
            - Knight moves in L-shapes:
                (±2, ±1) and (±1, ±2)
            - Knight can jump over pieces
            - If destination is empty → add move
            - If destination has enemy piece → add move
            - If destination has own piece → do NOT add
            - Must stay within board bounds

        Hint:
            Use a predefined list of 8 possible moves.
        """
        # TODO: Implement knight movement logic using step moves
        pass


class Bishop(Piece):
    kind = "B"
    value = 330

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        return self._slide_moves(board, r, c, [(-1, -1), (-1, 1), (1, -1), (1, 1)])


class Rook(Piece):
    kind = "R"
    value = 500

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
         """
        Generate all pseudo-legal moves for a rook.

        Parameters:
            board: the current board object
            r: current row of the rook
            c: current column of the rook

        Output:
            A list of Move objects.

        Rules:
            - Rook moves in straight lines:
                 Up, Down, Left, Right
            - Must continue moving until blocked
            - Use sliding movement logic
            - Do not modify the board

        Hint:
            Call the sliding move helper with the correct directions.
        """
        # TODO: Implement rook movement using sliding moves
        pass



class Queen(Piece):
    kind = "Q"
    value = 900

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        return self._slide_moves(board, r, c, [
            (-1, -1), (-1, 1), (1, -1), (1, 1),
            (-1, 0), (1, 0), (0, -1), (0, 1),
        ])


class King(Piece):
    kind = "K"
    value = 20000

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        return self._step_moves(board, r, c, [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        ])

#Maps piece symbol to class
PIECE_MAP = {
    "p": Pawn,
    "n": Knight,
    "b": Bishop,
    "r": Rook,
    "q": Queen,
    "k": King,
}

#Converts char from text board file into a piece object/None
def piece_from_symbol(ch: str) -> Optional[Piece]:
    if ch == ".":
        return None
    if len(ch) != 1 or ch.lower() not in PIECE_MAP:
        raise ValueError(f"Unknown piece symbol: {ch}")
    cls = PIECE_MAP[ch.lower()]
    color = "w" if ch.isupper() else "b"
    return cls(color)

#Other way round.
def symbol_from_piece(piece: Optional[Piece]) -> str:
    return "." if piece is None else piece.symbol
