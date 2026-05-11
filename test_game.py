import unittest
import chess
from game.board import DrunkChessGame

class TestDrunkChess(unittest.TestCase):
    def setUp(self):
        self.game = DrunkChessGame()

    def test_real_board_integrity(self):
        success, display_move, reveal = self.game.process_turn("e2e4")
        self.assertTrue(success)
        self.assertFalse(reveal)
        self.assertEqual(self.game.real_board.piece_at(chess.E4).symbol(), 'P')

    def test_illegal_move_triggers_reveal(self):
        success, display_move, reveal = self.game.process_turn("e2e5")
        self.assertFalse(success)
        self.assertTrue(reveal)

    def test_fake_move_probability(self):
        fake_count = 0
        for _ in range(1000):
            temp_game = DrunkChessGame()
            _, display_move, _ = temp_game.process_turn("g1f3")
            if display_move != "g1f3":
                fake_count += 1
        self.assertTrue(20 < fake_count < 80)

if __name__ == '__main__':
    unittest.main()
