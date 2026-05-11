import pygame
import chess
from game.board import DrunkChessGame
from engine.ai import MobileAI

pygame.init()
WIDTH, HEIGHT = 720, 720
SQ_SIZE = WIDTH // 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drunk Chess")
font = pygame.font.SysFont("Arial", 48, bold=True)
small_font = pygame.font.SysFont("Arial", 24)

LIGHT = (238, 238, 210)
DARK = (118, 150, 86)
HIGHLIGHT = (186, 202, 68)
WHITE_PIECE = (255, 255, 255)
BLACK_PIECE = (0, 0, 0)
ERROR_RED = (255, 50, 50)

PIECE_CHARS = {
    'P': 'P', 'N': 'N', 'B': 'B', 'R': 'R', 'Q': 'Q', 'K': 'K',
    'p': 'P', 'n': 'N', 'b': 'B', 'r': 'R', 'q': 'Q', 'k': 'K'
}

def draw_board(screen, belief_board, selected_square, valid_moves, reveal_msg):
    for r in range(8):
        for c in range(8):
            sq_index = (7-r)*8 + c
            color = HIGHLIGHT if selected_square == sq_index else (LIGHT if (r + c) % 2 == 0 else DARK)
            rect = pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(screen, color, rect)

            if sq_index in valid_moves:
                pygame.draw.circle(screen, (50, 150, 50), rect.center, SQ_SIZE//6)

            piece = belief_board.piece_at(sq_index)
            if piece:
                char = PIECE_CHARS[piece.symbol()]
                text_color = WHITE_PIECE if piece.color == chess.WHITE else BLACK_PIECE
                text_surface = font.render(char, True, text_color)
                shadow = font.render(char, True, (100,100,100))
                screen.blit(shadow, (rect.centerx - shadow.get_width()//2 + 2, rect.centery - shadow.get_height()//2 + 2))
                screen.blit(text_surface, (rect.centerx - text_surface.get_width()//2, rect.centery - text_surface.get_height()//2))

    if reveal_msg:
        pygame.draw.rect(screen, ERROR_RED, (0, HEIGHT//2 - 40, WIDTH, 80))
        msg_surface = small_font.render("REVEAL! Board Corrected.", True, WHITE_PIECE)
        screen.blit(msg_surface, (WIDTH//2 - msg_surface.get_width()//2, HEIGHT//2 - msg_surface.get_height()//2))

def animate_move(screen, belief_board, move_uci, selected_square, valid_moves, reveal_msg):
    move = chess.Move.from_uci(move_uci)
    piece = belief_board.piece_at(move.from_square)
    if not piece: return

    clock = pygame.time.Clock()
    start_r, start_c = 7 - (move.from_square // 8), move.from_square % 8
    end_r, end_c = 7 - (move.to_square // 8), move.to_square % 8

    start_x, start_y = start_c * SQ_SIZE, start_r * SQ_SIZE
    end_x, end_y = end_c * SQ_SIZE, end_r * SQ_SIZE

    belief_board.remove_piece_at(move.from_square)

    frames = 15
    for frame in range(frames + 1):
        progress = frame / frames
        curr_x = start_x + (end_x - start_x) * progress
        curr_y = start_y + (end_y - start_y) * progress

        draw_board(screen, belief_board, selected_square, valid_moves, reveal_msg)

        char = PIECE_CHARS[piece.symbol()]
        text_color = WHITE_PIECE if piece.color == chess.WHITE else BLACK_PIECE
        text_surface = font.render(char, True, text_color)
        shadow = font.render(char, True, (100, 100, 100))
        
        center_x = curr_x + SQ_SIZE // 2
        center_y = curr_y + SQ_SIZE // 2

        screen.blit(shadow, (center_x - shadow.get_width()//2 + 2, center_y - shadow.get_height()//2 + 2))
        screen.blit(text_surface, (center_x - text_surface.get_width()//2, center_y - text_surface.get_height()//2))

        pygame.display.flip()
        clock.tick(60)

    belief_board.set_piece_at(move.from_square, piece)

def main():
    game = DrunkChessGame()
    ai = MobileAI()
    human_belief = chess.Board()
    
    running = True
    turn_is_white = True
    selected_square = None
    valid_moves = []
    reveal_msg = False
    reveal_timer = 0

    while running:
        current_time = pygame.time.get_ticks()
        
        if reveal_msg and current_time - reveal_timer > 2000:
            reveal_msg = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN and turn_is_white and not reveal_msg:
                x, y = pygame.mouse.get_pos()
                col = x // SQ_SIZE
                row = 7 - (y // SQ_SIZE)
                sq = row * 8 + col
                
                if sq in valid_moves and selected_square is not None:
                    move = chess.Move(selected_square, sq)
                    
                    if human_belief.piece_at(selected_square).piece_type == chess.PAWN and (row == 0 or row == 7):
                        move.promotion = chess.QUEEN

                    success, display_move, needs_reveal = game.process_turn(move.uci())
                    
                    if needs_reveal:
                        reveal_msg = True
                        reveal_timer = pygame.time.get_ticks()
                        human_belief.set_fen(game.get_real_fen())
                        ai.force_reveal(game.get_real_fen())
                        selected_square = None
                        valid_moves = []
                    elif success:
                        animate_move(screen, human_belief, move.uci(), selected_square, valid_moves, reveal_msg)
                        human_belief.push(chess.Move.from_uci(move.uci()))
                        ai.sync_board(display_move)
                        turn_is_white = False
                        selected_square = None
                        valid_moves = []

                else:
                    piece = human_belief.piece_at(sq)
                    if piece and piece.color == chess.WHITE:
                        selected_square = sq
                        valid_moves = [m.to_square for m in human_belief.legal_moves if m.from_square == sq]
                    else:
                        selected_square = None
                        valid_moves = []

        if not turn_is_white and not reveal_msg:
            pygame.time.wait(300)
            ai_move_uci = ai.get_move()
            
            if ai_move_uci:
                success, display_move, needs_reveal = game.process_turn(ai_move_uci)
                
                if needs_reveal:
                    ai.force_reveal(game.get_real_fen())
                    human_belief.set_fen(game.get_real_fen())
                    reveal_msg = True
                    reveal_timer = pygame.time.get_ticks()
                else:
                    ai.sync_board(ai_move_uci)
                    try:
                        animate_move(screen, human_belief, display_move, selected_square, valid_moves, reveal_msg)
                        human_belief.push(chess.Move.from_uci(display_move))
                    except AssertionError:
                        human_belief.set_fen(game.get_real_fen())
                        reveal_msg = True
                        reveal_timer = pygame.time.get_ticks()
            turn_is_white = True

        draw_board(screen, human_belief, selected_square, valid_moves, reveal_msg)
        pygame.display.flip()

    pygame.quit()
