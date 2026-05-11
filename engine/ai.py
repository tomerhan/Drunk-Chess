import chess
import random

class MobileAI:
    def __init__(self):
        # AI works on its own beliefs
        self.belief_board = chess.Board()

    def get_move(self):
        legal_moves = list(self.belief_board.legal_moves)
        if not legal_moves:
            return ""
        # Choose a random legal move
        return random.choice(legal_moves).uci()

    def sync_board(self, uci_move: str):
        move = chess.Move.from_uci(uci_move)
        if move in self.belief_board.legal_moves:
            self.belief_board.push(move)

    def force_reveal(self, real_fen: str):
        self.belief_board.set_fen(real_fen)
