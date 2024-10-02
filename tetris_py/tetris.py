import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Shape colors
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_shape = self.get_new_shape()
        self.next_shape = self.get_new_shape()
        self.score = 0
        self.game_over = False
        self.drop_speed = 500  # 블록이 떨어지는 속도 (밀리초)
        self.drop_time = pygame.time.get_ticks()
        self.move_time = 0  # 마지막 키 입력 시간
        self.move_delay = 150  # 키보드 입력 간 딜레이 (밀리초)

    def get_new_shape(self):
        shape = random.choice(SHAPES)
        color = random.choice(SHAPE_COLORS)
        return {'shape': shape, 'color': color, 'x': GRID_WIDTH // 2 - len(shape[0]) // 2, 'y': 0}

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, self.grid[y][x], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
                pygame.draw.rect(self.screen, WHITE, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

    def draw_shape(self, shape):
        for y, row in enumerate(shape['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, shape['color'], ((shape['x'] + x) * GRID_SIZE, (shape['y'] + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
                    pygame.draw.rect(self.screen, WHITE, ((shape['x'] + x) * GRID_SIZE, (shape['y'] + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

    def move_shape(self, dx, dy):
        self.current_shape['x'] += dx
        self.current_shape['y'] += dy
        if self.check_collision():
            self.current_shape['x'] -= dx
            self.current_shape['y'] -= dy
            return False
        return True

    def rotate_shape(self):
        shape = self.current_shape['shape']
        rotated_shape = [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0]) - 1, -1, -1)]
        old_shape = self.current_shape['shape']
        self.current_shape['shape'] = rotated_shape
        if self.check_collision():
            self.current_shape['shape'] = old_shape

    def check_collision(self):
        shape = self.current_shape['shape']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    if (self.current_shape['x'] + x < 0 or
                        self.current_shape['x'] + x >= GRID_WIDTH or
                        self.current_shape['y'] + y >= GRID_HEIGHT or
                        self.grid[self.current_shape['y'] + y][self.current_shape['x'] + x] != BLACK):
                        return True
        return False

    def lock_shape(self):
        shape = self.current_shape['shape']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_shape['y'] + y][self.current_shape['x'] + x] = self.current_shape['color']
        self.clear_lines()
        self.current_shape = self.next_shape
        self.next_shape = self.get_new_shape()
        if self.check_collision():
            self.game_over = True

    def clear_lines(self):
        lines_to_clear = [y for y in range(GRID_HEIGHT) if all(self.grid[y][x] != BLACK for x in range(GRID_WIDTH))]
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        self.score += len(lines_to_clear)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        # 일정 시간 간격으로만 입력 처리
        if current_time - self.move_time > self.move_delay:
            if keys[pygame.K_LEFT]:
                self.move_shape(-1, 0)
                self.move_time = current_time
            if keys[pygame.K_RIGHT]:
                self.move_shape(1, 0)
                self.move_time = current_time
            if keys[pygame.K_DOWN]:
                self.move_shape(0, 1)
                self.move_time = current_time
            if keys[pygame.K_UP]:
                self.rotate_shape()
                self.move_time = current_time

    def run(self):
        while not self.game_over:
            current_time = pygame.time.get_ticks()

            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_shape(self.current_shape)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

            self.handle_input()

            # 블록이 일정 시간마다 떨어지도록 처리
            if current_time - self.drop_time > self.drop_speed:
                if not self.move_shape(0, 1):
                    self.lock_shape()
                self.drop_time = current_time

            self.clock.tick(30)  # 30 FPS로 설정하여 입력 반응을 빠르게 함

        pygame.quit()

if __name__ == "__main__":
    Tetris().run()
