import chess
import random

class DrunkChessGame:
    def __init__(self):
        self.real_board = chess.Board()

    def process_turn(self, move_uci: str) -> tuple[bool, str, bool]:
        """
        Returns: (is_legal_on_real_board, display_move_uci, needs_reveal)
        """
        try:
            move = chess.Move.from_uci(move_uci)
        except ValueError:
            return False, "", False

        if move not in self.real_board.legal_moves:
            return False, "", True 

        display_move = self._generate_display_move(move)
        self.real_board.push(move)
        
        return True, display_move.uci(), False

    def _generate_display_move(self, real_move: chess.Move) -> chess.Move:
        if random.random() <= 0.05:
            legal_moves = list(self.real_board.legal_moves)
            if len(legal_moves) > 1:
                fake_moves = [m for m in legal_moves if m != real_move]
                return random.choice(fake_moves)
        return real_move

    def get_real_fen(self) -> str:
        return self.real_board.fen()

    def is_game_over(self) -> bool:
        return self.real_board.is_game_over()
