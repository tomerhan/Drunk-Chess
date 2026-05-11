# Drunk Chess ♟️🥴

A Python-based chess variant where the board is an unreliable narrator. Built with Pygame and `python-chess`, the game frequently generates visual lies, forcing players to track the true state of the game in their heads.

## ✨ Features

* **Visual Lies:** Up to 40% of displayed moves are "hallucinations" (random legal moves that weren't actually played), indicated by a glowing purple aura.
* **The "Reveal" Mechanic:** Attempting an illegal move because you fell for a visual lie halts the game, flashes a warning, and forces the board to sync with reality.
* **Auto-Asset Management:** High-quality piece graphics are automatically downloaded and cached on the first run.
* **Cross-Platform:** Optimized for both desktop and mobile environments (including Android via Pydroid 3) with dynamic screen scaling and centering.

## ⚙️ Installation

1. Clone this repository or download the source code.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
*   Python 3.10+
*   [python-chess](https://python-chess.readthedocs.io/)
*   (Optional) [Stockfish](https://stockfishchess.org/) executable for AI gameplay.

## Installation & Running

1. Clone the repository:
   ```bash
   git clone [https://github.com/tomerhan/drunk-chess.git](https://github.com/tomerhan/drunk-chess.git)
   cd drunk-chess

🚀 Quick Start
​Run the game directly from your terminal:

python main.py
How to Play:
​You play as White, the engine plays as Black.
​Click a piece to see its valid moves, then click a highlighted square to move.
​Watch out for the "VISUAL LIE!" warning. If you lose track of the real board and attempt an invalid move, the game will trigger a REVEAL to restore reality, and you must try your turn again.
​Play continues until a Checkmate or Stalemate is reached on the true board.
​🛠️ Built With
​Python 3
​Pygame
​python-chess
