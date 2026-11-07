"""
Змейка • Neon Edition — одностраничная реализация.

Запуск:  python snake.py
Требуется только стандартная библиотека Python (Tkinter).

Управление:
    WASD / стрелки — движение
    Space          — пауза
    R              — рестарт
    Esc            — выход
"""

import os
import random
import tkinter as tk

# ============================ НАСТРОЙКИ ============================

CELL = 30
COLS = 20
ROWS = 20
WIDTH = CELL * COLS
HEIGHT = CELL * ROWS

BG_COLOR = "#1e1e2e"
GRID_COLOR = "#2a2a3e"
SNAKE_HEAD = "#7ef29d"
SNAKE_BODY = "#4fc98a"
FOOD_COLOR = "#ff5b5b"
GOLD_COLOR = "#ffd23f"
POISON_COLOR = "#a259ff"
PORTAL_COLOR = "#4fc3f7"
TEXT_COLOR = "#f0f0f0"

START_SPEED = 130
MIN_SPEED = 55
SPEED_STEP = 10

SCORE_FOOD = 1
SCORE_GOLD = 5
SCORE_POISON = -2

HIGHSCORE_FILE = "highscore.txt"
IMG_DIR = "img"


# ============================== ЗМЕЙКА =============================

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        cx, cy = COLS // 2, ROWS // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.pending_direction = (1, 0)
        self.grow = 0

    def set_direction(self, new_dir):
        if (new_dir[0] == -self.direction[0] and
                new_dir[1] == -self.direction[1]):
            return
        self.pending_direction = new_dir

    def move(self):
        self.direction = self.pending_direction
        hx, hy = self.body[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)
        self.body.insert(0, new_head)
        if self.grow > 0:
            self.grow -= 1
        else:
            self.body.pop()
        return new_head

    def check_wall_collision(self):
        x, y = self.body[0]
        return x < 0 or x >= COLS or y < 0 or y >= ROWS

    def check_self_collision(self):
        return self.body[0] in self.body[1:]


# =============================== ЕДА ===============================

class Food:
    def __init__(self):
        self.apple = None
        self.gold = None
        self.gold_age = 0
        self.poison = None
        self.portal = None

    def _free_cell(self, occupied):
        free = [(x, y) for x in range(COLS) for y in range(ROWS)
                if (x, y) not in occupied]
        return random.choice(free) if free else None

    def respawn_all(self, snake_body):
        occupied = set(snake_body)
        self.apple = self._free_cell(occupied); occupied.add(self.apple)
        self.gold = self._free_cell(occupied);  occupied.add(self.gold)
        self.poison = self._free_cell(occupied); occupied.add(self.poison)
        self.gold_age = 0
        if random.random() < 0.3:
            p1 = self._free_cell(occupied); occupied.add(p1)
            p2 = self._free_cell(occupied)
            self.portal = (p1, p2)
        else:
            self.portal = None

    def tick_gold(self):
        if self.gold is not None:
            self.gold_age += 1
            if self.gold_age > 10:      # золото живёт 10 тиков
                self.gold = None
                self.gold_age = 0

    def try_eat(self, head):
        if head == self.apple:
            self.apple = None
            return "apple"
        if head == self.gold:
            self.gold = None
            self.gold_age = 0
            return "gold"
        if head == self.poison:
            self.poison = None
            return "poison"
        return None

    def try_portal(self, head):
        if self.portal and head in self.portal:
            p1, p2 = self.portal
            return p2 if head == p1 else p1
        return None


# ============================== ИГРА ===============================

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.speed = START_SPEED
        self.game_over = False
        self.paused = False
        self.eaten_total = 0
        self.highscore = self._load_highscore()
        self.food.respawn_all(self.snake.body)

    def _load_highscore(self):
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE) as f:
                    return int(f.read().strip() or 0)
            except ValueError:
                return 0
        return 0

    def _save_highscore(self):
        if self.score > self.highscore:
            self.highscore = self.score
            try:
                with open(HIGHSCORE_FILE, "w") as f:
                    f.write(str(self.highscore))
            except OSError:
                pass

    def change_direction(self, d):
        self.snake.set_direction(d)

    def toggle_pause(self):
        if not self.game_over:
            self.paused = not self.paused

    def restart(self):
        self.snake.reset()
        self.food = Food()
        self.food.respawn_all(self.snake.body)
        self.score = 0
        self.speed = START_SPEED
        self.game_over = False
        self.paused = False
        self.eaten_total = 0

    def tick(self):
        if self.game_over or self.paused:
            return

        head = self.snake.move()

        teleport = self.food.try_portal(head)
        if teleport:
            self.snake.body[0] = teleport
            head = teleport

        if self.snake.check_wall_collision() or self.snake.check_self_collision():
            self.game_over = True
            self._save_highscore()
            return

        event = self.food.try_eat(head)
        if event == "apple":
            self.score += SCORE_FOOD
            self.snake.grow += 1
            self.eaten_total += 1
            if self.eaten_total % 5 == 0 and self.speed > MIN_SPEED:
                self.speed -= SPEED_STEP
        elif event == "gold":
            self.score += SCORE_GOLD
            self.snake.grow += 2
        elif event == "poison":
            self.score += SCORE_POISON
            if self.speed > MIN_SPEED:
                self.speed -= SPEED_STEP // 2

        self.food.tick_gold()

        occupied = set(self.snake.body)
        if self.food.apple is None:
            self.food.apple = self.food._free_cell(occupied)
            occupied.add(self.food.apple)
        if self.food.gold is None:
            self.food.gold = self.food._free_cell(occupied)
            occupied.add(self.food.gold)
        if self.food.poison is None:
            self.food.poison = self.food._free_cell(occupied)


# ============================ ПРИЛОЖЕНИЕ ===========================

class SnakeApp:
    def __init__(self, root):
        self.root = root
        root.title("Змейка • Neon Edition")
        root.resizable(False, False)
        root.configure(bg=BG_COLOR)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()

        self.hud = tk.Label(root, text="", bg=BG_COLOR, fg=TEXT_COLOR,
                            font=("Consolas", 14, "bold"))
        self.hud.pack(fill="x")

        self.game = Game()
        self.after_id = None

        # попытка загрузить картинки из img/ (не обязательно)
        self.images = self._load_images()

        root.bind("<KeyPress>", self.on_key)
        self.schedule_tick()
        self.draw()

    # ---- картинки ----
    def _load_images(self):
        imgs = {}
        names = {"apple": "apple.png", "gold": "gold.png",
                 "poison": "poison.png", "portal": "portal.png"}
        for key, fname in names.items():
            path = os.path.join(IMG_DIR, fname)
            if os.path.exists(path):
                try:
                    imgs[key] = tk.PhotoImage(file=path)
                except tk.TclError:
                    pass
        return imgs

    # ---- ввод ----
    def on_key(self, e):
        k = e.keysym.lower()
        if k in ("w", "up"):
            self.game.change_direction((0, -1))
        elif k in ("s", "down"):
            self.game.change_direction((0, 1))
        elif k in ("a", "left"):
            self.game.change_direction((-1, 0))
        elif k in ("d", "right"):
            self.game.change_direction((1, 0))
        elif k == "space":
            self.game.toggle_pause()
        elif k == "r":
            self.game.restart()
            self.schedule_tick()
        elif k == "escape":
            self.root.destroy()

    # ---- игровой цикл ----
    def schedule_tick(self):
        if self.after_id:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
        self.after_id = self.root.after(self.game.speed, self.loop)

    def loop(self):
        self.game.tick()
        self.draw()
        if not self.game.game_over:
            self.schedule_tick()
        else:
            self.draw_game_over()

    # ---- отрисовка ----
    def draw_grid(self):
        for x in range(0, WIDTH, CELL):
            self.canvas.create_line(x, 0, x, HEIGHT, fill=GRID_COLOR)
        for y in range(0, HEIGHT, CELL):
            self.canvas.create_line(0, y, WIDTH, y, fill=GRID_COLOR)

    def cell_rect(self, cell, color, pad=2):
        x, y = cell
        self.canvas.create_rectangle(
            x * CELL + pad, y * CELL + pad,
            (x + 1) * CELL - pad, (y + 1) * CELL - pad,
            fill=color, outline=""
        )

    def draw_item(self, cell, kind, fallback_color, pad=2):
        if cell is None:
            return
        if kind in self.images:
            x, y = cell
            self.canvas.create_image(
                x * CELL + CELL // 2, y * CELL + CELL // 2,
                image=self.images[kind]
            )
        else:
            self.cell_rect(cell, fallback_color, pad=pad)

    def draw(self):
        self.canvas.delete("all")
        self.draw_grid()

        # змейка
        for i, seg in enumerate(self.game.snake.body):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            self.cell_rect(seg, color, pad=1)

        # еда и порталы
        f = self.game.food
        self.draw_item(f.apple, "apple", FOOD_COLOR)
        self.draw_item(f.gold, "gold", GOLD_COLOR)
        self.draw_item(f.poison, "poison", POISON_COLOR)
        if f.portal:
            for p in f.portal:
                self.draw_item(p, "portal", PORTAL_COLOR, pad=4)

        # HUD
        state = "   [ПАУЗА]" if self.game.paused else ""
        self.hud.config(
            text=f"Счёт: {self.game.score}   "
                 f"Рекорд: {self.game.highscore}   "
                 f"Скорость: {self.game.speed} мс{state}"
        )

    def draw_game_over(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT,
                                     fill=BG_COLOR, stipple="gray25")
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 40,
                                fill=TEXT_COLOR, font=("Consolas", 26, "bold"),
                                text="ИГРА ОКОНЧЕНА")
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 10,
                                fill=TEXT_COLOR, font=("Consolas", 18),
                                text=f"Ваш счёт: {self.game.score}")
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 50,
                                fill=TEXT_COLOR, font=("Consolas", 14),
                                text="Нажмите R — играть снова")


# ============================== ЗАПУСК =============================

def main():
    root = tk.Tk()
    SnakeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()