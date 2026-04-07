from __future__ import annotations

"""
Just a few test cases, there are a lot more hidden ones but these will be great to put you
on the right track
"""

from board import Board
from io_utils import load_position, save_position


def test_start_position_move_count():
    """initial chess position should have the standard number of legal moves"""
    b = Board()
    assert len(b.generate_legal_moves()) == 20, (
        "Starting position should have 20 legal moves"
    )


def test_make_and_undo():
    """legal move should change the turn, undo should restore the board"""
    b = Board()
    b.play_move_text("e2e4")
    assert b.turn == "b", "Turn should switch after a legal move"

    b.undo_last()
    assert b.turn == "w", "Undo should restore the previous turn"
    assert len(b.generate_legal_moves()) == 20, "Undo should restore the start position"


def test_illegal_move_rejected():
    """illegal move should raise ValueError"""
    b = Board()
    try:
        b.play_move_text("e2e5")
        raise AssertionError("Illegal move was accepted")
    except ValueError:
        pass


def test_save_load_roundtrip():
    """Saving and loading a position should preserve the board state"""
    import tempfile
    from pathlib import Path

    b = Board()
    b.play_move_text("e2e4")

    tmp_dir = Path(tempfile.mkdtemp())
    path = tmp_dir / "pos.txt"

    save_position(b, path)
    b2 = load_position(path)

    assert b2.turn == b.turn, "loaded turn should match saved turn"
    assert b2.position_key() == b.position_key(), "loaded board should match saved board"


def run_all():
    test_start_position_move_count()
    test_make_and_undo()
    test_illegal_move_rejected()
    test_save_load_roundtrip()
    print("You passed these, now think more about all the hidden test cases : ).")


if __name__ == "__main__":
    run_all()
