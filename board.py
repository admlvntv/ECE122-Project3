#Stores board, applies move, undo moves, check legal, serializez board state

from __future__ import annotations

from typing import List, Optional, Tuple

from pieces import (
    Bishop,
    King,
    Knight,
    Move,
    Pawn,
    Piece,
    Queen,
    Rook,
    in_bounds,
    parse_square,
    piece_from_symbol,
    symbol_from_piece,
)

Square = Tuple[int, int]


class Board:
    def __init__(self, setup: bool = True):
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        #create grid
        self.turn: str = "w" #White moves first
        self.history: List[Move] = []#Stores moves for undo and logging
        if setup:
            self.setup_start() #Initialize board

    @staticmethod
    def opposite(color: str) -> str:
        #Returns opposite side
        return "b" if color == "w" else "w"

    def setup_start(self) -> None:
        #Place piece in position
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        back_rank = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for c, cls in enumerate(back_rank):
            self.grid[7][c] = cls("w")
            self.grid[0][c] = cls("b")
        for c in range(8):
            self.grid[6][c] = Pawn("w")
            self.grid[1][c] = Pawn("b")
        self.turn = "w"
        self.history.clear()

    def clone(self) -> "Board":
        #Creates a deep copy of the board so changes to the copy do not affect the original.
        b = Board(setup=False)
        b.turn = self.turn
        b.grid = [[p.copy() if p is not None else None for p in row] for row in self.grid]
        return b

    def piece_at(self, r: int, c: int) -> Optional[Piece]:
        #Returns piece at square
        if not in_bounds(r, c):
            return None
        return self.grid[r][c]

    def king_pos(self, color: str) -> Optional[Square]:
        #Finds king for color
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p is not None and p.color == color and isinstance(p, King):
                    return (r, c)
        return None

    def square_attacked(self, r: int, c: int, by_color: str) -> bool:
        #Checkif square is attacked by color,
        #Loops through all pieces of color and checks whether any attached square matches
        for rr in range(8):
            for cc in range(8):
                p = self.grid[rr][cc]
                if p is None or p.color != by_color:
                    continue
                for ar, ac in p.attacks(self, rr, cc):
                    if (ar, ac) == (r, c):
                        return True
        return False

    def in_check(self, color: Optional[str] = None) -> bool:
        #Determine if color isin chechk
        if color is None:
            color = self.turn
        kpos = self.king_pos(color)
        if kpos is None:
            return False
        return self.square_attacked(kpos[0], kpos[1], self.opposite(color))

    def apply_move(self, move: Move) -> None:
        """
        Apply a move to the board.

        Parameters:
            move: a Move object containing start and end positions

        Output:
            None (the board is modified directly)

        Rules:
            - Move the piece from its start position to its end position
            - If a piece exists at the destination -> it is captured
            - The starting square must become empty
            - Update the board state correctly
            - Do not create a new board
            ● must store moved_piece, captured_piece, and previous turn in move
            ● must append move to history

        Hint:
            Access the piece using its starting position, then update both squares.
        """
        # Source and destination coordinates
        sr, sc = move.src
        dr, dc = move.dst
        piece = self.grid[sr][sc]
        
        # Store metadata for potential undoing
        move.moved_piece = piece
        move.captured_piece = self.grid[dr][dc]
        move.prev_turn = self.turn
        
        # Update the grid: move piece and clear source square
        self.grid[dr][dc] = piece
        self.grid[sr][sc] = None

        # Handle default pawn promotion case
        if not move.promotion and piece.kind == "P" and (dr == 0 or dr == 7):
            move.promotion = "Q"
        
        # Handle special pawn promotion case
        if move.promotion:
            # Create a new piece based on the promotion symbol
            promo_piece = piece_from_symbol(move.promotion)
            # Ensure it has the correct color (same as moving pawn)
            promo_piece.color = self.turn
            self.grid[dr][dc] = promo_piece
            
        # Record move in history and toggle turn
        self.history.append(move)
        self.turn = self.opposite(self.turn)

    def undo_move(self, move: Move) -> None:
        #Restores moving piece to source, capture piece to dest, previous turn
        sr, sc = move.src
        dr, dc = move.dst
        if move.prev_turn is None:
            raise ValueError("Move does not contain undo information")
        self.turn = move.prev_turn
        self.grid[sr][sc] = move.moved_piece
        self.grid[dr][dc] = move.captured_piece
        if self.history and self.history[-1] == move:
            self.history.pop()

    def undo_last(self) -> Move:
        #Undo recent
        if not self.history:
            raise ValueError("No moves to undo")
        move = self.history[-1]
        self.undo_move(move)
        return move

    def generate_pseudo_legal_moves(self) -> List[Move]:
        """
        Generate all pseudo-legal moves for the current player.

        Parameters:
            None (uses the current board state)

        Output:
            A list of Move objects representing all possible moves.

        Rules:
            - Loop through all squares on the board
            - For each piece belonging to the current player:
                 Call its pseudo_legal_moves() function
            - Combine all moves into one list
            - Do not modify the board

        Hint:
            Check piece color before generating moves.
        """
        moves = []
        # Scan the entire 8x8 grid for pieces
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                # Only generate moves for pieces belonging to the current player
                if piece and piece.color == self.turn:
                    moves.extend(piece.pseudo_legal_moves(self, r, c))
        return moves

    def generate_legal_moves(self) -> List[Move]:
        """
        Generate all legal moves for the current player.

        Parameters:
            None

        Output:
            A list of Move objects representing legal moves.

        Rules:
            - Start with pseudo-legal moves
            - For each move:
                 Apply the move temporarily
                 Check if the player is in check
                 If still in check → discard move
                 Otherwise → keep move
            - Undo the move after checking
            - Do not permanently modify the board

        Hint:
            Use apply_move() and undo functionality if available.
        """
        legal_moves = []
        # Get all moves that don't consider king safety first
        pseudo_moves = self.generate_pseudo_legal_moves()
        
        for move in pseudo_moves:
            # Temporarily apply each move to see if it's safe
            self.apply_move(move)
            # If our king is not in check after the move, it's legal
            if not self.in_check(move.prev_turn):
                legal_moves.append(move)
            # Undo move to restore original board state
            self.undo_move(move)
            
        return legal_moves

    def is_game_over(self) -> bool:
        """
        Determine whether the game has ended.

        Parameters:
            None

        Output:
            True if the game is over, False otherwise.

        Rules:
            - Game is over if:
                 The current player has no legal moves

            - Do not modify the board

        Hint:
            Check if there are no legal moves
        """
        # The game ends if the side to move has no legal moves available
        return len(self.generate_legal_moves()) == 0

    def result(self) -> str:
        """
        Return the result of the game.

        Parameters:
            None

        Output:
            ● "ongoing"
            ● "<opposite side> wins by checkmate"
            ● "draw by stalemate"

        Rules:

        - If no legal moves exist:
            If in check → opponent wins
            Otherwise → draw (stalemate)

        Hint:
            Use is_game_over() and in_check() to decide.
        """
        # If the game is still going, return 'ongoing'
        if not self.is_game_over():
            return "ongoing"
            
        # Check for checkmate vs stalemate
        if self.in_check():
            winner = "Black" if self.turn == "w" else "White"
            return f"{winner} wins by checkmate"
        else:
            return "draw by stalemate"

    def position_key(self) -> str:
        #Builds a string representation of the board plus side to move.
        rows = []
        for r in range(8):
            rows.append("".join(symbol_from_piece(p) for p in self.grid[r]))
        return f"{self.turn}|" + "/".join(rows)

    def to_text(self) -> str:
        #Serialize board to plain text
        lines = [f"turn {self.turn}"]
        for r in range(8):
            lines.append("".join(symbol_from_piece(p) for p in self.grid[r]))
        return "\n".join(lines) + "\n"

    @classmethod
    def from_text(cls, text: str) -> "Board":
        #Loads board from text
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        if len(lines) < 9:
            raise ValueError("Position file must contain one turn line and 8 board lines")
        first = lines[0].split()
        if len(first) != 2 or first[0].lower() != "turn" or first[1] not in ("w", "b"):
            raise ValueError("First line must be 'turn w' or 'turn b'")
        board = cls(setup=False)
        board.turn = first[1]
        if len(lines[1:9]) != 8:
            raise ValueError("Board must have 8 rows")
        for r in range(8):
            row = lines[1 + r]
            if len(row) != 8:
                raise ValueError(f"Row {r+1} must have exactly 8 characters")
            for c, ch in enumerate(row):
                board.grid[r][c] = piece_from_symbol(ch)
        return board

    def __str__(self) -> str:
        #Create display
        out = []
        out.append("    a   b   c   d   e   f   g   h")
        out.append("  +---+---+---+---+---+---+---+---+")
        for r in range(8):
            rank = 8 - r
            cells = []
            for c in range(8):
                p = self.grid[r][c]
                cells.append(f" {symbol_from_piece(p)} ")
            out.append(f"{rank} |" + "|".join(cells) + f"| {rank}")
            out.append("  +---+---+---+---+---+---+---+---+")
        out.append("    a   b   c   d   e   f   g   h")
        out.append(f"Turn: {'White' if self.turn == 'w' else 'Black'}")
        if self.in_check(self.turn):
            out.append("Check!")
        return "\n".join(out)

    def try_parse_move(self, text: str) -> Move:
        """
        Convert a user input string into a Move object.

        Parameters:
            text: a string representing a move (e.g., "e2e4")

        Output:
            A Move object if valid, Raises an error if the input is invalid

        Rules:
            - Extract starting and ending positions from the string
            - Convert letters to columns (a=0, b=1, etc.)
            - Convert numbers to rows
            - Raise an error if input is invalid

        Hint:
            Carefully map chess notation to array indices.
        """
        # Clean input and check for minimum length
        text = text.strip()
        if len(text) < 4:
            raise ValueError(f"Move text too short: {text}")
            
        # Parse the two squares involved
        src = parse_square(text[0:2])
        dst = parse_square(text[2:4])
        # Check if there is a promotion piece specified (e.g. 'e7e8q')
        if len(text) > 4 and text[4] not in "kqrb": # check if the promotion piece is a valid piece
            raise ValueError(f"Invalid promotion symbol: {text[4]}")
        elif len(text) > 4:
            promo = text[4].upper()
        else:
            promo = None
        
        # Look for a matching legal move in the current position
        # A move is considered valid if it is in the list of legal moves
        for move in self.generate_legal_moves():
            if move.src == src and move.dst == dst and move.promotion == promo:
                return move
                
        # If no legal move matches, the input is considered 'invalid'
        raise ValueError(f"Illegal move: {text}")

    def play_move_text(self, text: str) -> Move:
        #Parse move, apply, return move
        move = self.try_parse_move(text)
        self.apply_move(move)
        return move
