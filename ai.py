import chess
import chess.engine

class DrunkAI:
    def __init__(self, engine_path: str):
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
            self.belief_board = chess.Board()
            self.is_active = True
        except FileNotFoundError:
            self.is_active = False

    def receive_display_move(self, move_uci: str):
        if not self.is_active: return
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.belief_board.legal_moves:
                self.belief_board.push(move)
        except ValueError:
            pass

    def get_best_move(self) -> str:
        if not self.is_active: return ""
        result = self.engine.play(self.belief_board, chess.engine.Limit(time=0.1))
        return result.move.uci()

    def apply_own_move(self, move_uci: str):
        if not self.is_active: return
        move = chess.Move.from_uci(move_uci)
        if move in self.belief_board.legal_moves:
            self.belief_board.push(move)

    def force_reveal(self, real_fen: str):
        if self.is_active:
            self.belief_board.set_fen(real_fen)

    def close(self):
        if self.is_active:
            self.engine.quit()
