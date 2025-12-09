import pygame
import json
import random
import sys
import os

# загружаем настройки игры из файла config.json
def load_config(path="config.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print("Ошибка загрузки config.json:", e)
        sys.exit()  # если конфиг не найден — выходим

config = load_config()  # читаем конфиг

pygame.init()  # инициализация pygame
screen = pygame.display.set_mode((config["window_width"], config["window_height"]))  # создаем окно
pygame.display.set_caption("Змейка")  # название окна
clock = pygame.time.Clock()  # таймер для кадров

CELL_SIZE = 30  # размер клетки змейки
FONT = pygame.font.SysFont(None, 36)  # шрифт для текста
SAVE_FILE = "highscore.txt"  # файл для рекордов

# музыка
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # путь к папке с кодом
music_path = os.path.join(BASE_DIR, "crazy_frog.mp3")  # путь к музыке

if os.path.isfile(music_path):
    pygame.mixer.music.load(music_path)  # загружаем музыку
    pygame.mixer.music.set_volume(0.3)  # громкость
    pygame.mixer.music.play(-1)  # включаем на повтор
else:
    print(f"Файл музыки не найден: {music_path}")  # если музыки нет

# класс змейки
class Snake:
    def __init__(self, x, y):
        self.body = [(x-2, y), (x-1, y), (x, y)]  # стартовая длина змейки 3 клетки
        self.direction = (1, 0)  # изначально движется вправо
        self.grow_flag = False  # флаг для роста

    def set_direction(self, d):
        # чтобы змейка не могла идти в противоположную сторону сразу
        if d[0] == -self.direction[0] and d[1] == -self.direction[1]:
            return
        self.direction = d

    def move(self):
        head_x, head_y = self.body[-1]  # берем голову
        new_head = (head_x + self.direction[0], head_y + self.direction[1])  # новое положение головы
        self.body.append(new_head)  # добавляем новую голову
        if not self.grow_flag:
            self.body.pop(0)  # удаляем хвост если не растем
        else:
            self.grow_flag = False  # сбрасываем флаг роста

    def grow(self):
        self.grow_flag = True  # включаем рост змейки

    def check_collision(self):
        head = self.body[-1]
        return head in self.body[:-1]  # проверяем столкновение с телом

    def draw(self, surface):
        for segment in self.body:
            pygame.draw.rect(surface, (0, 255, 0),
                             (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))  # рисуем каждую клетку

# класс еды
class Food:
    def __init__(self, snake):
        self.position = (0, 0)
        self.respawn(snake)  # ставим еду в начале

    def respawn(self, snake):
        # выбираем случайное место для еды, где нет змейки
        while True:
            x = random.randint(0, config["window_width"] // CELL_SIZE - 1)
            y = random.randint(0, config["window_height"] // CELL_SIZE - 1)
            if (x, y) not in snake.body:
                self.position = (x, y)
                break

    def draw(self, surface):
        pygame.draw.rect(surface, tuple(config["color_of_food"]),
                         (self.position[0]*CELL_SIZE, self.position[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))  # рисуем еду

# основной класс игры
class Game:
    def __init__(self):
        self.running = True  # флаг работы игры
        self.snake = Snake(5, 5)  # стартовая позиция змейки
        self.food = Food(self.snake)  # создаем еду
        self.score = 0  # очки
        self.highscore = self.load_highscore()  # рекорд
        self.difficulty = "medium"  # по умолчанию средняя сложность
        self.speed = self.get_speed_by_difficulty(self.difficulty)  # скорость змейки
        self.paused = False

    def get_speed_by_difficulty(self, level):
        # задаем скорость для каждой сложности
        return {"easy": 8, "medium": 12, "hard": 18}.get(level, 12)

    def load_highscore(self):
        # читаем рекорд из файла
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    return int(f.read())
            except:
                return 0
        return 0

    def save_highscore(self):
        # сохраняем рекорд
        try:
            with open(SAVE_FILE, "w") as f:
                f.write(str(self.highscore))
        except:
            pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False  # если закрыли окно — выходим
            elif event.type == pygame.KEYDOWN:
                # управление стрелками
                if event.key == pygame.K_UP:
                    self.snake.set_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    self.snake.set_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    self.snake.set_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    self.snake.set_direction((1, 0))
                # смена сложности
                elif event.key == pygame.K_1:
                    self.difficulty = "easy"
                    self.speed = self.get_speed_by_difficulty("easy")
                elif event.key == pygame.K_2:
                    self.difficulty = "medium"
                    self.speed = self.get_speed_by_difficulty("medium")
                elif event.key == pygame.K_3:
                    self.difficulty = "hard"
                    self.speed = self.get_speed_by_difficulty("hard")
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused  # переключаем пауза/продолжить
    def update(self):
        if self.paused:
            return  # если пауза — не двигаем змейку, не обновляем игру
        self.snake.move()  # двигаем змейку

        # проверяем, съела ли змейка еду
        if self.snake.body[-1] == self.food.position:
            self.snake.grow()
            self.food.respawn(self.snake)
            self.score += 1
            if self.score > self.highscore:
                self.highscore = self.score
                self.save_highscore()  # сохраняем новый рекорд

        # проверка столкновений с телом или стенками
        head_x, head_y = self.snake.body[-1]
        if self.snake.check_collision() or not (0 <= head_x < config["window_width"] // CELL_SIZE) or not (0 <= head_y < config["window_height"] // CELL_SIZE):
            self.running = False  # если ударились — конец игры

    def draw(self):
        screen.fill(config["background_color"])  # заливаем фон
        self.snake.draw(screen)  # рисуем змейку
        self.food.draw(screen)  # рисуем еду

        # выводим очки, рекорд и сложность
        screen.blit(FONT.render(f"Score: {self.score}", True, (255, 255, 255)), (10, 10))
        screen.blit(FONT.render(f"Highscore: {self.highscore}", True, (255, 255, 0)), (10, 40))
        screen.blit(FONT.render(f"Difficulty: {self.difficulty}", True, (255, 255, 255)), (10, 70))

        pygame.display.flip()  # обновляем экран

    def run(self):
        # главный цикл игры
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(self.speed)  # контролируем FPS

# запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    print(f"Game Over! Your score: {game.score}, Highscore: {game.highscore}")
