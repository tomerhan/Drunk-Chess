import chess
import random

class DrunkChessGame:
    def __init__(self):
        self.real_board = chess.Board()

    def process_turn(self, move_uci: str):
        try:
            move = chess.Move.from_uci(move_uci)
        except:
            return False, "", False, False

        # If user tried an illegal move based on a lie
        if move not in self.real_board.legal_moves:
            return False, "", True, False

        # Generate displayed move with visual lie probability
        display_move, was_fake = self._generate_display_move(move)
        self.real_board.push(move)
        
        # return success, display_move_uci, need_reveal, was_fake
        return True, display_move.uci(), False, was_fake

    def _generate_display_move(self, real_move: chess.Move):
        # Increased visual lie probability to 30% for frequent "hallucinations"
        if random.random() <= 0.30:
            legal_moves = [m for m in self.real_board.legal_moves if m != real_move]
            if legal_moves:
                fake_move = random.choice(legal_moves)
                # The displayed move is the lie
                return fake_move, True # was_fake is True
        # Default: The displayed move is the real move
        return real_move, False # was_fake is False

    def get_real_fen(self):
        return self.real_board.fen()

    def is_game_over(self):
        return self.real_board.is_game_over()
