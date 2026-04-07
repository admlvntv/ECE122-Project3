"""
This essentially the command line controller;
it doesn't create chess rules itself but connects to Boards, Searcher,
IO helpers so that the game can run from one loop.
The user can type commands and main.py will either print the board,
load or save data, undo moves, send move text to Bard.play_move_text().
This call validates the move after which it applies and stories it in history for 
undo or logging. When it is engine's turn to play, main.py will ask 
Searcher.find_best_move() for a move and then applies that move to the same Board object.
"""

from __future__ import annotations

from board import Board
from io_utils import load_position, save_moves, save_position
from search import Searcher

#Command help to show all the commands
HELP = """Commands:
  board                 show board
  move e2e4             make a move
  hint                  suggest best move for side to move
  ai                    let engine make one move for side to move
  depth N               set engine search depth
  side white|black      choose human side
  load FILE             load position from file
  save FILE             save position to file
  log FILE              save move list to file
  undo                  undo last move
  new                   reset to start position
  auto N                let engine play N plies
  help                  show this help
  quit                  exit
"""

#Main CLI
class GameCLI:
    def __init__(self):
        self.board = Board() #Start new chess game
        self.searcher = Searcher()#Create engine search object
        self.depth = 3 #Search depth
        self.human_side = "w" #Human side plays white

    @property#Engine plays opposite of human
    def engine_side(self) -> str:
        return "b" if self.human_side == "w" else "w"

    def maybe_engine_move(self) -> None:
        #Checks if engine should move, check if game over, searches
        #for best move, applies move, print result
        if self.board.turn != self.engine_side:
            return
        if self.board.is_game_over():
            return
        move, score = self.searcher.find_best_move(self.board, max_depth=self.depth)
        if move is None:
            print("Engine has no legal move.")
            return
        self.board.apply_move(move)
        print(f"Engine plays {move.uci()}  (score {score}, nodes {self.searcher.nodes})")

    def run(self) -> None:
        #Prints board, prints result if done, reads command, parses it, executes action
        #catches error
        print("CLI Chess Engine")
        print("Type 'help' for commands.")
        while True:
            print()
            print(self.board)
            if self.board.is_game_over():
                print(self.board.result())

            cmd = input("> ").strip()
            if not cmd:
                continue
            parts = cmd.split()
            op = parts[0].lower()

            try:
                if op in ("quit", "exit"):
                    return
                elif op == "help":
                    print(HELP)
                elif op == "board":
                    continue
                elif op == "new":
                    self.board = Board()
                    print("New game started.")
                elif op == "depth":
                    if len(parts) != 2:
                        raise ValueError("Usage: depth N")
                    self.depth = int(parts[1])
                    if self.depth < 1:
                        raise ValueError("Depth must be at least 1")
                    print(f"Depth set to {self.depth}")
                elif op == "side":
                    if len(parts) != 2 or parts[1].lower() not in ("white", "black"):
                        raise ValueError("Usage: side white|black")
                    self.human_side = "w" if parts[1].lower() == "white" else "b"
                    print(f"You are now playing {'White' if self.human_side == 'w' else 'Black'}")
                elif op in ("move", "m"):
                    if len(parts) != 2:
                        raise ValueError("Usage: move e2e4")
                    if self.board.turn != self.human_side:
                        print("It is not your turn.")
                        continue
                    move = self.board.play_move_text(parts[1])
                    print(f"Played {move.uci()}")
                    self.maybe_engine_move()
                elif op == "hint":
                    move, score = self.searcher.find_best_move(self.board, max_depth=self.depth)
                    if move is None:
                        print("No legal moves.")
                    else:
                        print(f"Best move: {move.uci()}  (score {score}, nodes {self.searcher.nodes})")
                elif op == "ai":
                    self.maybe_engine_move()
                elif op == "auto":
                    if len(parts) != 2:
                        raise ValueError("Usage: auto N")
                    n = int(parts[1])
                    if n < 1:
                        raise ValueError("N must be at least 1")
                    for _ in range(n):
                        if self.board.is_game_over():
                            break
                        self.maybe_engine_move()
                elif op == "load":
                    if len(parts) != 2:
                        raise ValueError("Usage: load FILE")
                    self.board = load_position(parts[1])
                    print(f"Loaded {parts[1]}")
                elif op == "save":
                    if len(parts) != 2:
                        raise ValueError("Usage: save FILE")
                    save_position(self.board, parts[1])
                    print(f"Saved {parts[1]}")
                elif op == "log":
                    if len(parts) != 2:
                        raise ValueError("Usage: log FILE")
                    save_moves(self.board.history, parts[1])
                    print(f"Saved moves to {parts[1]}")
                elif op == "undo":
                    move = self.board.undo_last()
                    print(f"Undid {move.uci()}")
                else:
                    if len(op) in (4, 5):
                        if self.board.turn != self.human_side:
                            print("It is not your turn.")
                            continue
                        move = self.board.play_move_text(op)
                        print(f"Played {move.uci()}")
                        self.maybe_engine_move()
                    else:
                        print("Unknown command. Type 'help'.")
            except Exception as e:
                print(f"Error: {e}")


def main() -> None:
    GameCLI().run()


if __name__ == "__main__":
    main()
