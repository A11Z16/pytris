import pygame
import random

# Oyun Ayarları
SCREEN_WIDTH, SCREEN_HEIGHT = 300, 600
GRID_SIZE = 30
COLUMNS, ROWS = SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE

# Renkler
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # Cyan (I-Şekli)
    (255, 255, 0),  # Sarı (O-Şekli)
    (128, 0, 128),  # Mor (T-Şekli)
    (0, 255, 0),    # Yeşil (S-Şekli)
    (255, 0, 0),    # Kırmızı (Z-Şekli)
    (0, 0, 255),    # Mavi (J-Şekli)
    (255, 165, 0)   # Turuncu (L-Şekli)
]

# Tetrimino Şekilleri
SHAPES = [
    [[1, 1, 1, 1]],  # I-Şekli
    [[1, 1],
     [1, 1]],  # O-Şekli
    [[0, 1, 0],
     [1, 1, 1]],  # T-Şekli
    [[0, 1, 1],
     [1, 1, 0]],  # S-Şekli
    [[1, 1, 0],
     [0, 1, 1]],  # Z-Şekli
    [[1, 0, 0],
     [1, 1, 1]],  # J-Şekli
    [[0, 0, 1],
     [1, 1, 1]]  # L-Şekli
]

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False

    def new_piece(self):
        shape = random.choice(SHAPES)
        color = random.randint(1, len(COLORS))
        return {'shape': shape, 'x': COLUMNS // 2 - len(shape[0]) // 2, 'y': 0, 'color': color}

    def can_move(self, dx, dy, shape=None):
        shape = shape or self.current_piece['shape']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    nx, ny = self.current_piece['x'] + x + dx, self.current_piece['y'] + y + dy
                    if nx < 0 or nx >= COLUMNS or ny >= ROWS or (ny >= 0 and self.grid[ny][nx]):
                        return False
        return True

    def rotate_piece(self):
        shape = [list(row) for row in zip(*self.current_piece['shape'][::-1])]
        if self.can_move(0, 0, shape):
            self.current_piece['shape'] = shape

    def freeze_piece(self):
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece['y'] + y][self.current_piece['x'] + x] = self.current_piece['color']
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if not self.can_move(0, 0):
            self.game_over = True

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        cleared = ROWS - len(new_grid)
        self.lines_cleared += cleared
        self.score += cleared * 100
        self.update_level()
        for _ in range(cleared):
            new_grid.insert(0, [0 for _ in range(COLUMNS)])
        self.grid = new_grid

    def update_level(self):
        self.level = self.lines_cleared // 5 + 1

    def move_piece(self, dx, dy):
        if self.can_move(dx, dy):
            self.current_piece['x'] += dx
            self.current_piece['y'] += dy
        elif dy > 0:
            self.freeze_piece()

    def draw_grid(self, screen):
        for y in range(ROWS):
            for x in range(COLUMNS):
                color = COLORS[self.grid[y][x] - 1] if self.grid[y][x] else BLACK
                pygame.draw.rect(screen, color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)

    def draw_piece(self, screen):
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    px = self.current_piece['x'] + x
                    py = self.current_piece['y'] + y
                    pygame.draw.rect(screen, COLORS[self.current_piece['color'] - 1],
                                     (px * GRID_SIZE, py * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)

    def draw(self, screen):
        self.draw_grid(screen)
        self.draw_piece(screen)

    def draw_score(self, screen):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH + 10, 10))
        screen.blit(level_text, (SCREEN_WIDTH + 10, 50))

    def draw_start_screen(self, screen):
        font = pygame.font.Font(None, 36)
        text = font.render("Press 'Space' to Start", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH + 200, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    tetris = Tetris()

    drop_time = 500
    last_drop = pygame.time.get_ticks()

    game_started = False
    running = True
    while running:
        screen.fill(BLACK)

        if not game_started:
            tetris.draw_start_screen(screen)
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        tetris.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        tetris.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        tetris.move_piece(0, 1)
                    elif event.key == pygame.K_UP:
                        tetris.rotate_piece()

            # Hız artırımı
            current_drop_time = max(50, drop_time - (tetris.level - 1) * 30)

            if pygame.time.get_ticks() - last_drop > current_drop_time:
                tetris.move_piece(0, 1)
                last_drop = pygame.time.get_ticks()

            tetris.draw(screen)
            tetris.draw_score(screen)

        pygame.display.flip()

        if tetris.game_over:
            print(f"Game Over! Your score: {tetris.score}")
            running = False

        clock.tick(60)

        if not game_started:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_started = True

    pygame.quit()

if __name__ == "__main__":
    main()
