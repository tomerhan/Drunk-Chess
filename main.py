import sys
from ui.cli import GameRunner

# Defines if AI should be used. Change to True if running on PC with Stockfish.
RUN_WITH_AI = False
STOCKFISH_PATH = "stockfish" 

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ai":
        RUN_WITH_AI = True
        
    runner = GameRunner(use_ai=RUN_WITH_AI, engine_path=STOCKFISH_PATH)
    
    try:
        runner.play()
    except KeyboardInterrupt:
        print("\nExiting game...")
    finally:
        runner.close()
