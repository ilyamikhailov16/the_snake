from random import choice

import pygame

# Константы для размеров поля и сетки, а также центральной позиции:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (0, 0, 0)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Чёрный цвет
BLACK_COLOR = (0, 0, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption("Змейка")

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Общий класс родитель для всех игровых объектов."""

    def __init__(self, position=CENTER_POSITION, body_color=None):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """
        Служит для отрисовки объектов
        Необходимо переопределить в каждом классе.
        """
        pass


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        super().__init__()

        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR

    def update_direction(self):
        """Обновление текущего направления движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self, target_object):
        """
        обновляет позицию змейки (координаты каждой секции),
        добавляя новую голову в начало списка positions и
        удаляя последний элемент, если длина змейки не увеличилась.
        Перезагружает игру при столкновении c самим собой и переносит змейку
        на противоположную сторону экрана при выходе за границы.
        """
        self.update_direction()

        # Получаем следующую позицию для головы
        # в соответствие с направлением движения.
        new_positions = (
            self.get_head_position()[0] + GRID_SIZE * self.direction[0],
            self.get_head_position()[1] + GRID_SIZE * self.direction[1],
        )

        # Если позиция головы змейки совпала
        # с одной из позиций тела(змейка себя укусила),
        # то выполняем перезагрузку и стираем текущее отрисованное яблоко.
        for position in self.positions:
            if new_positions == position:
                for position in self.positions:
                    rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(screen, BLACK_COLOR, rect)
                    self.reset()
                    rect = pygame.Rect(target_object.position,
                                       (GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(screen, BLACK_COLOR, rect)

                return None

        # Если новая позиция головы вышла за пределы экрана,
        # переносим голову на противоположную сторону.
        if new_positions[0] > SCREEN_WIDTH - GRID_SIZE:
            new_positions = (0, new_positions[1])
        elif new_positions[0] < 0:
            new_positions = (SCREEN_WIDTH - GRID_SIZE, new_positions[1])
        elif new_positions[1] > SCREEN_HEIGHT - GRID_SIZE:
            new_positions = (new_positions[0], 0)
        elif new_positions[1] < 0:
            new_positions = (new_positions[0], SCREEN_HEIGHT - GRID_SIZE)

        # Обновляем змейку, добавляя новый элемент,
        # который теперь становится головой, по новой позиции.
        self.positions.insert(0, new_positions)

        # Если змейка после обновления не съела яблоко,
        # то и не увеличилась, удаляем последний элемент.
        if self.get_head_position() != target_object.position:
            rect = pygame.Rect(self.positions[-1], (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BLACK_COLOR, rect)
            self.positions.pop(-1)

        self.length = len(self.positions)
        self.draw()

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное положение."""
        self.length = 1
        self.positions = [CENTER_POSITION]
        self.direction = RIGHT
        self.next_direction = None


class Apple(GameObject):
    """Класс яблока"""

    def __init__(self):
        position = self.randomize_position()
        body_color = APPLE_COLOR
        super().__init__(position, body_color)

    def randomize_position(self):
        """Генерирует случайную позицию для яблока(в пределах экрана)."""
        x_positions = [
            x for x in range(0, (SCREEN_WIDTH - GRID_SIZE * 2) + 1, GRID_SIZE)
        ]
        y_positions = [
            y for y in range(0, (SCREEN_HEIGHT - GRID_SIZE * 2) + 1, GRID_SIZE)
        ]

        return choice(x_positions), choice(y_positions)

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


def handle_keys(game_object):
    """Функция обработки действий пользователя"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Главная функция, реализующая геймплей"""
    pygame.init()

    snake = Snake()
    snake.draw()
    apple = Apple()
    apple.draw()

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        past_lenth = snake.length
        snake.move(apple)
        new_lenth = snake.length

        # Если длина изменилась, то яблоко съели. Создаем новое яблоко.
        if past_lenth != new_lenth:
            apple = Apple()
            apple.draw()

        pygame.display.update()


if __name__ == "__main__":
    main()
