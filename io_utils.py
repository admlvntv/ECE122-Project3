from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from board import Board
from pieces import Move

#Loads board from text file
def load_position(path: str | Path) -> Board:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Position file not found: {p}")
    return Board.from_text(p.read_text(encoding="utf-8"))

#Writes current board to text file
def save_position(board: Board, path: str | Path) -> None:
    p = Path(path)
    p.write_text(board.to_text(), encoding="utf-8")

#Writes the move history to a file as one move per line
def save_moves(moves: Iterable[Move], path: str | Path) -> None:
    p = Path(path)
    lines = [mv.uci() for mv in moves]
    p.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

#Loads a list of move strings from a file
def load_moves(path: str | Path) -> List[str]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Move file not found: {p}")
    out: List[str] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out
