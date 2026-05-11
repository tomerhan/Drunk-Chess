import chess
from game.board import DrunkChessGame
from engine.ai import DrunkAI

class GameRunner:
    def __init__(self, use_ai: bool = False, engine_path: str = ""):
        self.game = DrunkChessGame()
        self.human_belief = chess.Board()
        self.use_ai = use_ai
        self.ai = DrunkAI(engine_path) if use_ai else None
        
        if self.ai and not self.ai.is_active:
            print(f"\n[!] AI Engine not found at '{engine_path}'. Playing Human vs Human instead.")
            self.use_ai = False

    def play(self):
        print("\n=== Welcome to Drunk Chess ===")
        print("Beware: 5% of moves are visual lies!\n")

        turn_is_white = True

        while not self.game.is_game_over():
            print("\n--- Your Board (Belief) ---")
            print(self.human_belief)
            
            if turn_is_white or not self.use_ai:
                player_color = "White" if turn_is_white else "Black"
                move_uci = input(f"\n[{player_color}] Enter your move (e.g., e2e4): ")
                
                success, display_move, needs_reveal = self.game.process_turn(move_uci)
                
                if needs_reveal:
                    print("\n[!] REVEAL! Your move is illegal on the TRUE board.")
                    self._sync_human_board()
                    continue
                
                if not success:
                    print("Invalid input. Try again.")
                    continue
                
                self.human_belief.push(chess.Move.from_uci(move_uci))
                
                if self.use_ai and turn_is_white:
                    self.ai.receive_display_move(display_move)
                
                turn_is_white = not turn_is_white

            else:
                print("\nAI is thinking...")
                move_uci = self.ai.get_best_move()
                success, display_move, needs_reveal = self.game.process_turn(move_uci)

                if needs_reveal:
                    print("\n[!] AI hallucinated! Forcing AI to sync with real board...")
                    self.ai.force_reveal(self.game.get_real_fen())
                    continue
                
                self.ai.apply_own_move(move_uci)
                print(f"AI played: {display_move}")
                
                try:
                    self.human_belief.push(chess.Move.from_uci(display_move))
                except AssertionError:
                    print("\n[!] The AI's move seems impossible on your board! Triggering Reveal...")
                    self._sync_human_board()
                
                turn_is_white = True

        print("\nGame Over!")
        print("Final True Board:")
        print(self.game.real_board)

    def _sync_human_board(self):
        real_fen = self.game.get_real_fen()
        self.human_belief.set_fen(real_fen)
        print("Your board has been corrected to the TRUE state.")

    def close(self):
        if self.ai:
            self.ai.close()
