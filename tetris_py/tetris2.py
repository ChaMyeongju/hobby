import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 500  # 오른쪽에 버튼 공간 추가
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10  # 게임 그리드의 너비
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

# Assign colors to specific shapes
SHAPE_COLORS = {
    0: CYAN,     # I
    1: YELLOW,   # O
    2: MAGENTA,  # T
    3: ORANGE,   # L
    4: BLUE,     # J
    5: GREEN,    # S
    6: RED       # Z
}
# Shape colors
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class Button:
    """
    버튼 클래스는 간단한 텍스트 버튼을 생성하고 클릭할 수 있도록 합니다.
    """
    def __init__(self, text, x, y, width, height, color, hover_color, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen):
        """
        버튼을 화면에 그리는 함수
        """
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        font = pygame.font.SysFont(None, 24)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_click(self, event):
        """
        마우스 클릭을 확인하여 버튼의 액션을 실행하는 함수
        """
        if event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()


class Tetris:
    """
    테트리스 게임 클래스는 게임 로직을 관리합니다.
    """
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_shape = None
        self.next_shape = self.get_new_shape()
        self.score = 0
        self.game_over = False
        self.drop_speed = 500  # 블록이 떨어지는 속도 (밀리초)
        self.drop_time = pygame.time.get_ticks()
        self.move_time = 0  # 마지막 키 입력 시간
        self.move_delay = 150  # 키보드 입력 간 딜레이 (밀리초)
        self.game_started = False  # 게임 시작 여부
        self.create_buttons()

    def create_buttons(self):
        """
        게임 시작 및 종료 버튼을 생성합니다.
        """
        button_x = SCREEN_WIDTH - 130  # 버튼 위치 (오른쪽)
        button_y_start = SCREEN_HEIGHT - 150  # 버튼들이 시작하는 Y 위치 (아래쪽)

        self.start_button = Button("Start", button_x, button_y_start, 100, 40, GREEN, BLUE, self.start_game)
        self.quit_button = Button("Quit", button_x, button_y_start + 50, 100, 40, RED, MAGENTA, self.quit_game)

        # 속도 선택 버튼 (1, 2, 3 버튼을 생성하여 속도 선택)
        self.speed_button1 = Button("Speed 1", button_x, button_y_start-150, 100, 40, GREEN, BLUE, lambda: self.set_speed(500))
        self.speed_button2 = Button("Speed 2", button_x, button_y_start-100, 100, 40, GREEN, BLUE, lambda: self.set_speed(250))
        self.speed_button3 = Button("Speed 3", button_x, button_y_start-50, 100, 40, GREEN, BLUE, lambda: self.set_speed(125))

        # Pause/Resume 버튼은 처음에는 없음 (게임이 시작된 후 추가)
        self.pause_button = None

    def set_speed(self, speed):
        """
        속도를 설정하는 함수. 선택된 속도에 따라 게임의 drop_speed를 설정합니다.
        """
        self.drop_speed = speed  # 블록이 떨어지는 속도 설정
        print(f"Speed set to {speed}ms per block drop.")

    def toggle_pause(self):
        """
        게임 일시정지 및 다시 시작을 제어하는 함수. 버튼 텍스트를 Pause/Resume으로 변경.
        """
        if self.paused:
            self.paused = False
            self.pause_button.text = "Pause"
        else:
            self.paused = True
            self.pause_button.text = "Resume"

    def start_game(self):
        """
        게임을 시작하는 함수. 게임이 이미 종료된 경우 상태를 초기화하여 새 게임을 시작합니다.
        """
        if not self.game_started:  # 게임이 시작 중이 아니면 새 게임 시작
            self.game_over = False  # 게임 종료 상태 해제
            self.score = 0          # 점수 초기화
            self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]  # 그리드 초기화
            self.current_shape = self.get_new_shape()  # 새로운 블록 생성
            self.next_shape = self.get_new_shape()     # 다음 블록 생성
            self.drop_time = pygame.time.get_ticks()   # 블록 낙하 시간 초기화
            self.game_started = True                   # 게임이 시작됨을 표시
            self.paused = False

            # 속도 선택 후에만 게임이 시작되므로, 속도가 설정되지 않았으면 기본값 설정
            if not hasattr(self, 'drop_speed'):
                self.drop_speed = 500  # 기본 속도

            # Pause 버튼 추가 (게임 시작 후에만 보임)
            button_x = SCREEN_WIDTH - 130  # 버튼 위치 (오른쪽)
            button_y_start = SCREEN_HEIGHT - 150  # 버튼들이 시작하는 Y 위치 (아래쪽)

            self.pause_button = Button("Pause", button_x, button_y_start - 50, 100, 40, YELLOW, BLUE, self.toggle_pause)


    def quit_game(self):
        """
        게임을 종료하는 함수. 게임이 종료되면 창은 닫히지 않습니다.
        """
        self.game_started = False
        self.game_over = True
        self.pause_button = None  # 게임 종료 시 Pause/Resume 버튼 제거

    def get_new_shape(self):
        """
        랜덤한 블록과 그에 대응하는 고유한 색상을 반환하는 함수.
        """
        shape_index = random.randint(0, len(SHAPES) - 1)  # 블록 모양을 랜덤으로 선택
        shape = SHAPES[shape_index]
        color = SHAPE_COLORS[shape_index]  # 선택된 블록에 해당하는 색상
        return {'shape': shape, 'color': color, 'x': GRID_WIDTH // 2 - len(shape[0]) // 2, 'y': 0}

    def draw_grid(self):
        """
        게임 그리드를 화면에 그리는 함수.
        """
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, self.grid[y][x], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
                pygame.draw.rect(self.screen, WHITE, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

    def draw_border(self):
        """
        테두리를 그리는 함수. 그리드의 바깥쪽 테두리를 그립니다.
        """
        border_rect = pygame.Rect(0, 0, GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE)
        pygame.draw.rect(self.screen, WHITE, border_rect, 5)  # 테두리를 그리며, 두께는 5px

    def draw_shape(self, shape):
        """
        현재 블록을 화면에 그리는 함수.
        """
        for y, row in enumerate(shape['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, shape['color'], ((shape['x'] + x) * GRID_SIZE, (shape['y'] + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
                    pygame.draw.rect(self.screen, WHITE, ((shape['x'] + x) * GRID_SIZE, (shape['y'] + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

    def draw_next_shape_and_score(self):
        """
        다음에 나올 블록과 점수를 오른쪽 상단에 그리는 함수.
        """
        next_shape_x = GRID_WIDTH * GRID_SIZE + 20  # 오른쪽 그리드 공간의 시작 위치
        next_shape_y = 50  # 상단에서의 위치
        font = pygame.font.SysFont(None, 36)

        # "Next" 텍스트 표시
        next_text = font.render("Next:", True, WHITE)
        self.screen.blit(next_text, (next_shape_x, next_shape_y - 40))

        # 다음에 나올 블록 표시
        shape = self.next_shape['shape']
        color = self.next_shape['color']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, color, (next_shape_x + x * GRID_SIZE, next_shape_y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(self.screen, WHITE, (next_shape_x + x * GRID_SIZE, next_shape_y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

        # 점수 표시
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (next_shape_x, next_shape_y + 100))

    # def draw_next_shape(self):
    #     """
    #     다음에 나올 블록을 오른쪽 상단에 그리는 함수.
    #     """
    #     # 오른쪽 상단에 5x5 공간을 만듦
    #     next_shape_x = GRID_WIDTH * GRID_SIZE + 20  # 오른쪽 그리드 공간의 시작 위치
    #     next_shape_y = 50  # 상단에서의 위치
    #     font = pygame.font.SysFont(None, 36)
    #     next_text = font.render("Next:", True, WHITE)
    #     self.screen.blit(next_text, (next_shape_x, next_shape_y - 40))

    #     # next_shape 블록을 그리기
    #     shape = self.next_shape['shape']
    #     color = self.next_shape['color']

    #     # next_shape가 표시될 영역
    #     for y, row in enumerate(shape):
    #         for x, cell in enumerate(row):
    #             if cell:
    #                 pygame.draw.rect(self.screen, color, (next_shape_x + x * GRID_SIZE, next_shape_y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    #                 pygame.draw.rect(self.screen, WHITE, (next_shape_x + x * GRID_SIZE, next_shape_y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)


    def move_shape(self, dx, dy):
        """
        블록을 x축(dx)과 y축(dy)으로 이동시키는 함수.
        """
        self.current_shape['x'] += dx
        self.current_shape['y'] += dy
        if self.check_collision():
            self.current_shape['x'] -= dx
            self.current_shape['y'] -= dy
            return False
        return True

    def rotate_shape(self):
        """
        현재 블록을 회전시키는 함수.
        """
        shape = self.current_shape['shape']
        rotated_shape = [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0]) - 1, -1, -1)]
        old_shape = self.current_shape['shape']
        self.current_shape['shape'] = rotated_shape
        if self.check_collision():
            self.current_shape['shape'] = old_shape

    def check_collision(self):
        """
        블록이 그리드 경계나 다른 블록과 충돌하는지 확인하는 함수.
        """
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
        """
        현재 블록을 그리드에 고정하고 새로운 블록을 생성하는 함수.
        """
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
        """
        가득 찬 라인을 지우고 점수를 추가하는 함수. 일반적인 테트리스 점수 계산 방식으로 점수를 계산합니다.
        """
        lines_to_clear = [y for y in range(GRID_HEIGHT) if all(self.grid[y][x] != BLACK for x in range(GRID_WIDTH))]
        
        if lines_to_clear:
            # 줄을 지운 횟수에 따라 점수를 다르게 부여
            lines_cleared = len(lines_to_clear)
            score_increase = {1: 100, 2: 300, 3: 500, 4: 800}.get(lines_cleared, 0)
            self.score += score_increase

            # 줄을 제거하고 빈 줄을 위로 추가
            for y in lines_to_clear:
                del self.grid[y]
                self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])

            print(f"Cleared {lines_cleared} lines, Score: {self.score}")


    def handle_input(self):
        """
        키보드 입력을 처리하는 함수. 좌우 이동, 회전, 아래로 이동을 관리합니다.
        """
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
            if keys[pygame.K_SPACE]:
                # 스페이스바를 누르면 블록이 즉시 바닥까지 낙하
                while self.move_shape(0, 1):
                    pass  # 더 이상 내려갈 수 없을 때까지 계속 아래로 이동
                self.lock_shape()  # 바닥에 도착하면 블록을 고정
                self.move_time = current_time  # 입력 시간 업데이트

    def display_game_over(self):
        """
        게임 종료 시 화면에 'Game Over' 메시지를 표시하는 함수.
        """
        font = pygame.font.SysFont(None, 48)
        game_over_surf = font.render("Game Over", True, RED)
        game_over_rect = game_over_surf.get_rect(center=(GRID_WIDTH * GRID_SIZE // 2, GRID_HEIGHT * GRID_SIZE // 2))
        self.screen.blit(game_over_surf, game_over_rect)

    def run(self):
        """
        메인 게임 루프를 실행하는 함수. 게임 상태에 따라 게임을 업데이트합니다.
        """
        running = True  # 전체 프로그램의 실행 상태를 관리

        while running:  # 전체 프로그램이 실행되는 동안 계속 루프
            current_time = pygame.time.get_ticks()

            self.screen.fill(BLACK)

            

            if self.game_started and not self.game_over:

                self.draw_grid()
                self.draw_shape(self.current_shape)
                self.draw_next_shape_and_score()  # 다음 블록과 점수를 화면에 표시

                if not self.paused:

                    # 블록이 일정 시간마다 떨어지도록 처리
                    if current_time - self.drop_time > self.drop_speed:
                        if not self.move_shape(0, 1):
                            self.lock_shape()
                        self.drop_time = current_time

                    self.handle_input()

                else:
                    # 게임이 일시정지된 상태에서는 그리드 업데이트 중단
                    pass


            elif self.game_over:
                # 게임 종료 시 테두리와 'Game Over' 메시지 표시
                self.draw_border()  # 게임 오버 시에도 테두리를 그리기
                self.display_game_over()                

            # 버튼 그리기 (Pause/Resume 버튼은 게임 중에만 표시)
            if self.pause_button:
                self.pause_button.draw(self.screen)

            self.start_button.draw(self.screen)
            self.quit_button.draw(self.screen)

            # 게임이 시작되기 전에만 속도 선택 버튼을 보여줌
            if not self.game_started:
                self.speed_button1.draw(self.screen)
                self.speed_button2.draw(self.screen)
                self.speed_button3.draw(self.screen)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False  # 창을 닫기 위해서는 running을 False로 설정

                # 버튼 클릭 이벤트 처리
                if self.pause_button:
                    self.pause_button.check_click(event)
                self.start_button.check_click(event)
                self.quit_button.check_click(event)

                # 게임 시작 전 속도 선택 버튼 처리
                if not self.game_started:
                    self.speed_button1.check_click(event)
                    self.speed_button2.check_click(event)
                    self.speed_button3.check_click(event)

            # Quit 버튼을 눌렀을 때는 게임만 멈추지만 창은 계속 열려 있음
            if self.game_over:
                self.game_started = False  # 게임이 끝났으니 다시 시작할 수 있음

            self.clock.tick(30)

        # 프로그램이 종료될 때만 pygame.quit()을 호출
        pygame.quit()

if __name__ == "__main__":
    Tetris().run()
