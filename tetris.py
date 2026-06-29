import random
import sys

import pygame

# --- Game constants ---
COLS = 10
ROWS = 20
BLOCK = 30
SIDE_PANEL = 180
WIDTH = COLS * BLOCK + SIDE_PANEL
HEIGHT = ROWS * BLOCK
FPS = 60
DROP_EVENT = pygame.USEREVENT + 1
DROP_INTERVAL = 500

# Colors
BLACK = (18, 18, 18)
GRID = (35, 35, 35)
WHITE = (245, 245, 245)
GRAY = (160, 160, 160)
RED = (220, 60, 60)

COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 0),
    "Z": (240, 0, 0),
    "J": (0, 0, 240),
    "L": (240, 160, 0),
}

# Shapes are defined in a 4x4 box.
SHAPES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}


class Piece:
    def __init__(self, kind=None):
        self.kind = kind or random.choice(list(SHAPES.keys()))
        self.rotation = 0
        self.x = COLS // 2 - 2
        self.y = 0

    @property
    def blocks(self):
        return SHAPES[self.kind][self.rotation]

    @property
    def color(self):
        return COLORS[self.kind]

    def rotated(self):
        p = Piece(self.kind)
        p.rotation = (self.rotation + 1) % 4
        p.x = self.x
        p.y = self.y
        return p


def create_board():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]


def valid_position(board, piece, dx=0, dy=0):
    for bx, by in piece.blocks:
        x = piece.x + bx + dx
        y = piece.y + by + dy
        if x < 0 or x >= COLS or y < 0 or y >= ROWS:
            return False
        if board[y][x] is not None:
            return False
    return True


def lock_piece(board, piece):
    for bx, by in piece.blocks:
        x = piece.x + bx
        y = piece.y + by
        if 0 <= y < ROWS and 0 <= x < COLS:
            board[y][x] = piece.color


def clear_lines(board):
    new_board = [row for row in board if any(cell is None for cell in row)]
    cleared = ROWS - len(new_board)
    while len(new_board) < ROWS:
        new_board.insert(0, [None for _ in range(COLS)])
    return new_board, cleared


def draw_block(surface, x, y, color):
    rect = pygame.Rect(x * BLOCK, y * BLOCK, BLOCK, BLOCK)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, (0, 0, 0), rect, 1)


def draw_board(screen, board):
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * BLOCK, y * BLOCK, BLOCK, BLOCK)
            pygame.draw.rect(screen, GRID, rect, 1)
            if board[y][x] is not None:
                draw_block(screen, x, y, board[y][x])


def draw_piece(screen, piece):
    for bx, by in piece.blocks:
        x = piece.x + bx
        y = piece.y + by
        if y >= 0:
            draw_block(screen, x, y, piece.color)


def draw_text(surface, font, text, x, y, color=WHITE):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))


def draw_side_panel(screen, font, small_font, score, lines, game_over):
    panel_x = COLS * BLOCK + 15
    pygame.draw.rect(screen, (24, 24, 24), (COLS * BLOCK, 0, SIDE_PANEL, HEIGHT))
    draw_text(screen, font, "TETRIS", panel_x, 20)
    draw_text(screen, small_font, f"Score: {score}", panel_x, 80)
    draw_text(screen, small_font, f"Lines: {lines}", panel_x, 110)
    draw_text(screen, small_font, "Controls:", panel_x, 160)
    controls = [
        "← → : move",
        "↓   : soft drop",
        "↑   : rotate",
        "Space: hard drop",
        "P   : restart",
        "Esc : quit",
    ]
    y = 188
    for line in controls:
        draw_text(screen, small_font, line, panel_x, y, GRAY)
        y += 24
    if game_over:
        draw_text(screen, small_font, "Game Over", panel_x, 360, RED)
        draw_text(screen, small_font, "Press P", panel_x, 390, RED)


def try_move(board, piece, dx, dy):
    if valid_position(board, piece, dx=dx, dy=dy):
        piece.x += dx
        piece.y += dy
        return True
    return False


def try_rotate(board, piece):
    rotated = piece.rotated()
    # Simple wall kicks to make rotation feel better.
    for dx in (0, -1, 1, -2, 2):
        if valid_position(board, rotated, dx=dx):
            piece.rotation = rotated.rotation
            piece.x += dx
            return True
    return False


def hard_drop(board, piece):
    dropped = 0
    while try_move(board, piece, 0, 1):
        dropped += 1
    return dropped


def new_game():
    return {
        "board": create_board(),
        "current": Piece(),
        "next": Piece(),
        "score": 0,
        "lines": 0,
        "game_over": False,
    }


def main():
    pygame.init()
    pygame.display.set_caption("Tetris")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 34, bold=True)
    small_font = pygame.font.SysFont("arial", 22)

    state = new_game()
    pygame.time.set_timer(DROP_EVENT, DROP_INTERVAL)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_p:
                    state = new_game()
                    continue

                if state["game_over"]:
                    continue

                if event.key == pygame.K_LEFT:
                    try_move(state["board"], state["current"], -1, 0)
                elif event.key == pygame.K_RIGHT:
                    try_move(state["board"], state["current"], 1, 0)
                elif event.key == pygame.K_DOWN:
                    if not try_move(state["board"], state["current"], 0, 1):
                        lock_piece(state["board"], state["current"])
                        state["board"], cleared = clear_lines(state["board"])
                        if cleared:
                            state["lines"] += cleared
                            state["score"] += [0, 100, 300, 500, 800][cleared]
                        state["current"] = state["next"]
                        state["next"] = Piece()
                        if not valid_position(state["board"], state["current"]):
                            state["game_over"] = True
                elif event.key == pygame.K_UP:
                    try_rotate(state["board"], state["current"])
                elif event.key == pygame.K_SPACE:
                    dropped = hard_drop(state["board"], state["current"])
                    state["score"] += dropped * 2
                    lock_piece(state["board"], state["current"])
                    state["board"], cleared = clear_lines(state["board"])
                    if cleared:
                        state["lines"] += cleared
                        state["score"] += [0, 100, 300, 500, 800][cleared]
                    state["current"] = state["next"]
                    state["next"] = Piece()
                    if not valid_position(state["board"], state["current"]):
                        state["game_over"] = True

            elif event.type == DROP_EVENT and not state["game_over"]:
                if not try_move(state["board"], state["current"], 0, 1):
                    lock_piece(state["board"], state["current"])
                    state["board"], cleared = clear_lines(state["board"])
                    if cleared:
                        state["lines"] += cleared
                        state["score"] += [0, 100, 300, 500, 800][cleared]
                    state["current"] = state["next"]
                    state["next"] = Piece()
                    if not valid_position(state["board"], state["current"]):
                        state["game_over"] = True

        screen.fill(BLACK)
        draw_board(screen, state["board"])
        draw_piece(screen, state["current"])
        draw_side_panel(screen, font, small_font, state["score"], state["lines"], state["game_over"])

        if state["game_over"]:
            overlay = pygame.Surface((COLS * BLOCK, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            msg = font.render("GAME OVER", True, WHITE)
            screen.blit(msg, (20, HEIGHT // 2 - 30))

        pygame.display.flip()


if __name__ == "__main__":
    main()
