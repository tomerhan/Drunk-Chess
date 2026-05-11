import pygame
import chess
import os
import time
import urllib.request
import ssl
from game.board import DrunkChessGame
from engine.ai import MobileAI

# --- Paths and Constants ---
LIGHT, DARK = (238, 238, 210), (118, 150, 86)
HIGHLIGHT = (186, 202, 68)
ERROR_RED = (255, 50, 50)
FAKE_AURA = (180, 50, 255) # Purple glow for visual lies
WHITE_PIECE, BLACK_PIECE = (255, 255, 255), (0, 0, 0)

IMAGE_NAMES = {
    'P': 'wP', 'N': 'wN', 'B': 'wB', 'R': 'wR', 'Q': 'wQ', 'K': 'wK',
    'p': 'bP', 'n': 'bN', 'b': 'bB', 'r': 'bR', 'q': 'bQ', 'k': 'bK'
}

PIECE_CHARS = {
    'P': 'P', 'N': 'N', 'B': 'B', 'R': 'R', 'Q': 'Q', 'K': 'K',
    'p': 'P', 'n': 'N', 'b': 'B', 'r': 'R', 'q': 'Q', 'k': 'K'
}

def download_assets():
    """Downloads piece images directly, bypassing Pydroid SSL blocks."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    pieces = ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK']
    
    # Check if we already have the images
    if all(os.path.exists(os.path.join(assets_dir, f"{p}.png")) for p in pieces):
        return assets_dir
        
    print("Downloading high-quality chess pieces... Please wait a moment.")
    
    # Bypass SSL verification which often causes Pydroid to crash
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except AttributeError:
        pass

    for name in pieces:
        url = f"https://images.chesscomfiles.com/chess-themes/pieces/neo/150/{name.lower()}.png"
        filepath = os.path.join(assets_dir, f"{name}.png")
        if not os.path.exists(filepath):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                    out_file.write(response.read())
            except Exception as e:
                print(f"Warning: Could not download {name}: {e}")
                
    print("Download complete! Starting UI...")
    return assets_dir

def load_images(sq_size):
    imgs = {}
    assets_dir = download_assets()
    
    if assets_dir:
        for sym, name in IMAGE_NAMES.items():
            path = os.path.join(assets_dir, f"{name}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                imgs[sym] = pygame.transform.smoothscale(img, (int(sq_size * 0.85), int(sq_size * 0.85)))
    return imgs

def draw_board(screen, belief_board, selected_square, valid_moves, reveal_msg, conf):
    y_offset, sq_size, imgs, pre_rendered_texts = conf['y'], conf['sq'], conf['imgs'], conf['txts']
    
    for r in range(8):
        for c in range(8):
            sq_index = (7-r)*8 + c
            rect = pygame.Rect(c * sq_size, y_offset + r * sq_size, sq_size, sq_size)
            
            color = HIGHLIGHT if selected_square == sq_index else (LIGHT if (r + c) % 2 == 0 else DARK)
            pygame.draw.rect(screen, color, rect)
            
            if sq_index in valid_moves:
                pygame.draw.circle(screen, (50, 150, 50), rect.center, sq_size//6)
            
            piece = belief_board.piece_at(sq_index)
            if piece:
                if piece.symbol() in imgs:
                    img = imgs[piece.symbol()]
                    screen.blit(img, (rect.centerx - img.get_width()//2, rect.centery - img.get_height()//2))
                else:
                    shadow, text_surf = pre_rendered_texts[piece.symbol()]
                    screen.blit(shadow, (rect.centerx - shadow.get_width()//2 + 3, rect.centery - shadow.get_height()//2 + 3))
                    screen.blit(text_surf, (rect.centerx - text_surf.get_width()//2, rect.centery - text_surf.get_height()//2))

    if reveal_msg:
        overlay = pygame.Surface((conf['w'], 120)); overlay.set_alpha(200); overlay.fill(ERROR_RED)
        screen.blit(overlay, (0, y_offset + conf['b']//2 - 60))
        msg = conf['sf'].render("REVEAL! Reality Restored.", True, WHITE_PIECE)
        screen.blit(msg, (conf['w']//2 - msg.get_width()//2, y_offset + conf['b']//2 - msg.get_height()//2))

def animate_move(screen, belief_board, move_uci, selected_square, valid_moves, reveal_msg, conf, was_fake):
    y_offset, sq_size, imgs, pre_rendered_texts = conf['y'], conf['sq'], conf['imgs'], conf['txts']
    
    move = chess.Move.from_uci(move_uci)
    piece = belief_board.piece_at(move.from_square)
    if not piece: return
    
    start_x = (move.from_square % 8) * sq_size
    start_y = y_offset + (7 - (move.from_square // 8)) * sq_size
    end_x = (move.to_square % 8) * sq_size
    end_y = y_offset + (7 - (move.to_square // 8)) * sq_size
    
    belief_board.remove_piece_at(move.from_square)
    
    frames = 6
    clock = pygame.time.Clock()
    
    fake_text = conf['sf'].render("VISUAL LIE!", True, FAKE_AURA) if was_fake else None
    
    for i in range(frames + 1):
        screen.fill((0, 0, 0))
        
        progress = i / frames
        curr_x = start_x + (end_x - start_x) * progress
        curr_y = start_y + (end_y - start_y) * progress
        
        draw_board(screen, belief_board, selected_square, valid_moves, reveal_msg, conf)
        
        center_x = curr_x + sq_size // 2
        center_y = curr_y + sq_size // 2
        
        if was_fake:
            pygame.draw.circle(screen, FAKE_AURA, (center_x, center_y), int(sq_size * 0.5), 4)
            if fake_text:
                screen.blit(fake_text, (center_x - fake_text.get_width()//2, center_y - sq_size))
        
        if piece.symbol() in imgs:
            img = imgs[piece.symbol()]
            screen.blit(img, (center_x - img.get_width()//2, center_y - img.get_height()//2))
        else:
            shadow, text_surf = pre_rendered_texts[piece.symbol()]
            screen.blit(shadow, (center_x - shadow.get_width()//2 + 3, center_y - shadow.get_height()//2 + 3))
            screen.blit(text_surf, (center_x - text_surf.get_width()//2, center_y - text_surf.get_height()//2))
        
        pygame.display.flip()
        clock.tick(60)
    
    belief_board.set_piece_at(move.from_square, piece)

def main():
    pygame.init()
    time.sleep(0.1)
    
    if not pygame.display.get_init(): pygame.display.init()
    if not pygame.font.get_init(): pygame.font.init()
    
    BOARD_SIZE = 720
    
    if 'ANDROID_ARGUMENT' in os.environ:
        os.environ['SDL_VIDEODRIVER'] = 'android'
    
    info = pygame.display.Info()
    if info.current_w > 0:
        SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
        W_ADJ = SCREEN_WIDTH if SCREEN_HEIGHT > SCREEN_WIDTH else min(SCREEN_WIDTH, SCREEN_HEIGHT, BOARD_SIZE)
        SQ_SIZE = W_ADJ // 8
        BOARD_SIZE = SQ_SIZE * 8
        y_offset = (SCREEN_HEIGHT - BOARD_SIZE) // 2 if SCREEN_HEIGHT > BOARD_SIZE else 0
        
        try:
            mode = pygame.FULLSCREEN | pygame.SCALED if 'ANDROID_ARGUMENT' in os.environ else 0
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), mode)
        except:
            screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
            SCREEN_WIDTH, SCREEN_HEIGHT, y_offset = BOARD_SIZE, BOARD_SIZE, 0
    else:
        BOARD_SIZE, SQ_SIZE, y_offset = 720, 720//8, 0
        screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
        SCREEN_WIDTH, SCREEN_HEIGHT = BOARD_SIZE, BOARD_SIZE

    pygame.display.set_caption("Drunk Chess")
    
    conf = {
        'w': SCREEN_WIDTH, 'h': SCREEN_HEIGHT, 'y': y_offset, 'sq': SQ_SIZE, 'b': BOARD_SIZE,
        'imgs': load_images(SQ_SIZE),
        'f': pygame.font.SysFont("Arial", int(SQ_SIZE * 0.6), bold=True),
        'sf': pygame.font.SysFont("Arial", int(SQ_SIZE * 0.4), bold=True)
    }

    pre_rendered_texts = {}
    for sym, char in PIECE_CHARS.items():
        text_color = WHITE_PIECE if sym.isupper() else BLACK_PIECE
        shadow = conf['f'].render(char, True, (100, 100, 100, 150))
        text_surf = conf['f'].render(char, True, text_color)
        pre_rendered_texts[sym] = (shadow, text_surf)
    conf['txts'] = pre_rendered_texts

    game, ai, human_belief = DrunkChessGame(), MobileAI(), chess.Board()
    running, turn_white, selected_sq, valid_moves, reveal_msg, reveal_timer = True, True, None, [], False, 0

    while running:
        screen.fill((0, 0, 0))
        game_is_over = game.is_game_over()
        
        if reveal_msg and pygame.time.get_ticks() - reveal_timer > 2000: reveal_msg = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and turn_white and not reveal_msg and not game_is_over:
                x, y = event.pos[0], event.pos[1]
                
                if x >= 0 and x < BOARD_SIZE and y >= y_offset and y < (y_offset + BOARD_SIZE):
                    col, row = x // SQ_SIZE, 7 - ((y - y_offset) // SQ_SIZE)
                    sq_idx = row * 8 + col
                    
                    if sq_idx in valid_moves and selected_sq is not None:
                        move = chess.Move(selected_sq, sq_idx)
                        if human_belief.piece_at(selected_sq).piece_type == chess.PAWN and row in [0, 7]:
                             move.promotion = chess.QUEEN

                        success, display_move, needs_reveal, was_fake = game.process_turn(move.uci())
                        
                        if needs_reveal:
                            reveal_msg, reveal_timer = True, pygame.time.get_ticks()
                            human_belief.set_fen(game.get_real_fen())
                            ai.force_reveal(game.get_real_fen())
                        elif success:
                            animate_move(screen, human_belief, move.uci(), None, [], False, conf, was_fake)
                            human_belief.push(chess.Move.from_uci(move.uci()))
                            ai.sync_board(display_move)
                        
                        selected_sq, valid_moves = None, []
                        turn_white = human_belief.turn == chess.WHITE
                    else:
                        piece = human_belief.piece_at(sq_idx)
                        if piece and piece.color == chess.WHITE:
                            selected_sq, valid_moves = sq_idx, [m.to_square for m in human_belief.legal_moves if m.from_square == sq_idx]
                        else:
                            selected_sq, valid_moves = None, []

        if not turn_white and not reveal_msg and not game_is_over:
            pygame.time.wait(150)
            ai_move_uci = ai.get_move()
            
            if ai_move_uci:
                success, display_move, needs_reveal, was_fake = game.process_turn(ai_move_uci)
                
                if needs_reveal:
                    ai.force_reveal(game.get_real_fen())
                    human_belief.set_fen(game.get_real_fen())
                    reveal_msg, reveal_timer = True, pygame.time.get_ticks()
                else:
                    ai.sync_board(ai_move_uci)
                    try:
                        animate_move(screen, human_belief, display_move, None, [], False, conf, was_fake)
                        human_belief.push(chess.Move.from_uci(display_move))
                    except:
                        human_belief.set_fen(game.get_real_fen())
                        reveal_msg, reveal_timer = True, pygame.time.get_ticks()
                
                turn_white = human_belief.turn == chess.WHITE

        draw_board(screen, human_belief, selected_sq, valid_moves, reveal_msg, conf)
        
        if game_is_over:
            overlay = pygame.Surface((conf['w'], conf['h']))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            msg_text = "GAME OVER"
            if game.real_board.is_checkmate():
                msg_text = "CHECKMATE! You Won!" if not turn_white else "CHECKMATE! AI Won!"
            elif game.real_board.is_stalemate():
                msg_text = "STALEMATE! It's a draw."
                
            msg = conf['f'].render(msg_text, True, (255, 215, 0))
            screen.blit(msg, (conf['w']//2 - msg.get_width()//2, conf['h']//2 - msg.get_height()//2))

        pygame.display.flip()
    
    pygame.quit()
