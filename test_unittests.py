from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from board import Board
from io_utils import load_position, save_position


class TestBoard(unittest.TestCase):
    def test_start_position_move_count(self):
        """Initial chess position should have the standard number of legal moves."""
        b = Board()
        self.assertEqual(len(b.generate_legal_moves()), 20)

    def test_make_and_undo(self):
        """A legal move should change the turn, and undo should restore the board."""
        b = Board()

        b.play_move_text("e2e4")
        self.assertEqual(b.turn, "b")

        b.undo_last()
        self.assertEqual(b.turn, "w")
        self.assertEqual(len(b.generate_legal_moves()), 20)

    def test_illegal_move_rejected(self):
        """Illegal move should raise ValueError."""
        b = Board()

        with self.assertRaises(ValueError):
            b.play_move_text("e2e5")

    def test_save_load_roundtrip(self):
        """Saving and loading a position should preserve the board state."""
        b = Board()
        b.play_move_text("e2e4")

        tmp_dir = Path(tempfile.mkdtemp())
        path = tmp_dir / "pos.txt"

        save_position(b, path)
        b2 = load_position(path)

        self.assertEqual(b2.turn, b.turn)
        self.assertEqual(b2.position_key(), b.position_key())


if __name__ == "__main__":
    unittest.main()