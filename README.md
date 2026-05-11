# Drunk Chess ♟️🍺

Drunk Chess is a unique and chaotic Python-based chess variant. The core mechanic: **5% of all moves are visual lies.**

Both Human and AI players maintain a "Belief Board" based on what they see. However, the game engine silently maintains a "True Board". If a player attempts a move that is legal on their Belief Board but illegal on the True Board, a **Reveal** is triggered, forcing the player to sync with reality and calculate a new move.

## Features
*   **True State vs. Display State:** Complete separation of concerns between game logic and the UI/Belief state.
*   **AI Support (Stockfish):** The AI also falls victim to the visual lies and has to re-evaluate its strategy upon a Reveal.
*   **Unit Tested:** Core mechanics and probability logic are covered by automated tests.

## Requirements
*   Python 3.10+
*   [python-chess](https://python-chess.readthedocs.io/)
*   (Optional) [Stockfish](https://stockfishchess.org/) executable for AI gameplay.

## Installation & Running

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR-USERNAME/drunk-chess.git](https://github.com/YOUR-USERNAME/drunk-chess.git)
   cd drunk-chess
   
