from __future__ import annotations
import unittest
from board import Board
from pieces import Piece, Pawn, Knight, Rook, Move
from eval import Evaluator

class TestPartner(unittest.TestCase):
    # 1. Move Parsing + Move Application
    def test_move_parsing_and_application(self):
        b = Board() # Initial position
        
        # Valid move accepted
        move = b.try_parse_move("e2e4")
        self.assertIsNotNone(move)
        
        # Illegal move text rejected (invalid format or impossible move)
        with self.assertRaises(ValueError):
            b.try_parse_move("e2e9") # Out of bounds
        with self.assertRaises(ValueError):
            b.try_parse_move("e2e5") # Illegal pawn move
            
        # Move application
        b.apply_move(move)
        
        # Moved piece appears on destination, source becomes empty
        self.assertEqual(b.piece_at(4, 4).symbol, "P") # e4
        self.assertIsNone(b.piece_at(6, 4)) # e2
        
        # Turn changes after move
        self.assertEqual(b.turn, "b")
        
        # Undo support remains correct
        b.undo_last()
        self.assertEqual(b.turn, "w")
        self.assertEqual(b.piece_at(6, 4).symbol, "P")
        self.assertIsNone(b.piece_at(4, 4))

    # 2. Pseudo-Legal Piece Movement
    def test_pseudo_legal_movement(self):
        b = Board(setup=False)
        
        # Test Rook sliding moves and blocking
        rook = Rook("w")
        b.grid[4][4] = rook # e4
        # Add friendly piece at e6 (2, 4)
        b.grid[2][4] = Pawn("w")
        # Add enemy piece at e2 (6, 4)
        b.grid[6][4] = Pawn("b")
        
        moves = rook.pseudo_legal_moves(b, 4, 4)
        move_dsts = [m.dst for m in moves]
        
        # Sliding stops before friendly piece
        self.assertNotIn((2, 4), move_dsts)
        self.assertIn((3, 4), move_dsts)
        
        # Sliding stops at enemy piece (capture allowed)
        self.assertIn((6, 4), move_dsts)
        self.assertNotIn((7, 4), move_dsts)
        
        # Test Knight L-shaped moves
        b = Board(setup=False)
        knight = Knight("w")
        b.grid[4][4] = knight
        moves = knight.pseudo_legal_moves(b, 4, 4)
        self.assertEqual(len(moves), 8)
        
        # Test Pawn moves
        b = Board(setup=False)
        pawn = Pawn("w")
        b.grid[6][4] = pawn # e2
        moves = pawn.pseudo_legal_moves(b, 6, 4)
        move_dsts = [m.dst for m in moves]
        self.assertIn((5, 4), move_dsts) # e3
        self.assertIn((4, 4), move_dsts) # e4 (double move)
        
        # Pawn capture and promotion
        b = Board(setup=False)
        b.grid[1][4] = Pawn("w") # e7
        b.grid[0][3] = Pawn("b") # d8 (enemy)
        moves = b.grid[1][4].pseudo_legal_moves(b, 1, 4)
        
        promo_moves = [m for m in moves if m.promotion is not None]
        self.assertTrue(len(promo_moves) > 0)
        self.assertEqual(set(m.promotion for m in promo_moves), {"q", "r", "b", "n"})

    # 3. Board Move Collection
    def test_board_move_collection(self):
        b = Board()
        
        # Only pieces of side to move generate moves
        moves = b.generate_pseudo_legal_moves()
        for m in moves:
            piece = b.piece_at(*m.src)
            self.assertEqual(piece.color, "w")
            
        # All pseudo-legal moves collected into one list
        # In start pos, 20 pseudo-legal moves for white
        self.assertEqual(len(moves), 20)
        
        # Returned objects are moves
        self.assertTrue(all(isinstance(m, Move) for m in moves))
        
        # Board is not modified during generation
        key_before = b.position_key()
        b.generate_pseudo_legal_moves()
        self.assertEqual(b.position_key(), key_before)

    # 4. Legal Move Filtering + Game End Detection
    def test_legal_move_filtering_and_game_end(self):
        # Legal move generation removes moves that leave mover in check
        b = Board(setup=False)
        from pieces import King, Rook as RookPiece
        b.grid[7][4] = King("w") # e1
        b.grid[0][4] = RookPiece("b") # e8
        b.turn = "w"
        
        # King is in check by Rook on e8.
        # Moving another piece (if any) should be illegal if it doesn't block or capture.
        b.grid[7][0] = RookPiece("w") # a1
        
        legal_moves = b.generate_legal_moves()
        for m in legal_moves:
            # Apply move and check if still in check
            b.apply_move(m)
            self.assertFalse(b.in_check("w"))
            b.undo_last()
            
        # Checkmate
        b = Board(setup=False)
        b.grid[0][0] = King("b")
        b.grid[7][0] = King("w")
        b.grid[1][0] = RookPiece("b")
        b.grid[1][1] = RookPiece("b")
        b.turn = "w"
        
        self.assertTrue(b.is_game_over())
        self.assertEqual(b.result(), "Black wins by checkmate") # Black wins
        
        # Stalemate
        b = Board(setup=False)
        from pieces import Queen
        b.grid[0][0] = King("b")
        b.grid[7][7] = King("w")
        b.grid[1][2] = Queen("w")
        b.turn = "b"
        # King at a8 (0,0) is not in check, but has no moves.
        self.assertEqual(len(b.generate_legal_moves()), 0)
        self.assertFalse(b.in_check("b"))
        self.assertEqual(b.result(), "draw by stalemate")
        
        # Ongoing
        b = Board()
        self.assertEqual(b.result(), "ongoing")

    # 5. Board Evaluation
    def test_board_evaluation(self):
        evaluator = Evaluator()
        b = Board()
        
        # Board positions receive integer scores
        score = evaluator.evaluate(b)
        self.assertIsInstance(score, int)
        
        # Favorable positions for side to move have better evaluations
        # White just played e4, it should be slightly better for white if it's white's turn?
        # Actually evaluate() is from side to move's perspective.
        b = Board()
        score_start = evaluator.evaluate(b) # White's turn
        
        b.apply_move(b.try_parse_move("e2e4")) # Black's turn
        score_after_e4 = evaluator.evaluate(b) # Black's perspective
        
        # Evaluation uses board state without permanently changing it
        key_before = b.position_key()
        evaluator.evaluate(b)
        self.assertEqual(b.position_key(), key_before)

if __name__ == "__main__":
    unittest.main()
