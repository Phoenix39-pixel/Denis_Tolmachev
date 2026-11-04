import tkinter as tk
import random


# ================== ОКНО ==================
root = tk.Tk()
root.title("Падающий урожай")

WIDTH = 500
HEIGHT = 560          # чуть выше, чтобы поместилась панель с таймером

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#87CEEB",
                   highlightthickness=0)
canvas.pack()

# ================== ИГРОВЫЕ ПЕРЕМЕННЫЕ ==================
GAME_TIME = 60
time_left = GAME_TIME
score = 0
game_active = True

fall_speed = 3
speed_increase = 0.02

TOP_PANEL = 60        # высота верхней панели с таймером
PLAY_TOP = TOP_PANEL  # игровое поле начинается ниже панели


# ================== ФОН ИГРОВОГО ПОЛЯ ==================
canvas.create_rectangle(0, PLAY_TOP, WIDTH, HEIGHT,
                        fill="#B0E0E6", outline="")
canvas.create_oval(-50, HEIGHT - 120, WIDTH + 50, HEIGHT + 100,
                   fill="#7CFC00", outline="")          # трава
canvas.create_oval(WIDTH - 200, PLAY_TOP + 20,
                   WIDTH - 80, PLAY_TOP + 140,
                   fill="#FFD700", outline="")          # солнце


# ================== ВЕРХНЯЯ ПАНЕЛЬ С ТАЙМЕРОМ ==================
# фон панели
canvas.create_rectangle(0, 0, WIDTH, TOP_PANEL,
                        fill="#2F4F4F", outline="")

# счёт слева
score_text = canvas.create_text(
    70, TOP_PANEL // 2, text="Счёт: 0",
    font=("Arial", 18, "bold"), fill="white"
)

# ---- КРУПНЫЙ ТАЙМЕР В ЦЕНТРЕ ----
timer_label = canvas.create_text(
    WIDTH // 2, 14,
    text="ВРЕМЯ",
    font=("Arial", 11, "bold"), fill="#FFD700"
)

timer_text = canvas.create_text(
    WIDTH // 2, 36,
    text=f"{time_left}",
    font=("Arial", 24, "bold"), fill="white"
)

# ---- ПОЛОСКА-ИНДИКАТОР ВРЕМЕНИ ----
BAR_X1 = WIDTH - 160
BAR_X2 = WIDTH - 20
BAR_Y1 = 20
BAR_Y2 = 42

canvas.create_rectangle(BAR_X1, BAR_Y1, BAR_X2, BAR_Y2,
                        fill="#555555", outline="white")

timer_bar = canvas.create_rectangle(
    BAR_X1, BAR_Y1, BAR_X2, BAR_Y2,
    fill="#00FF7F", outline=""
)


# ================== КОРЗИНКА ==================
basket_x = WIDTH // 2
basket_y = HEIGHT - 70

basket = canvas.create_text(
    basket_x, basket_y, text="🧺",
    font=("Arial", 40), fill="saddlebrown"
)


# ================== ПРЕДМЕТЫ ==================
objects = []


def create_object():
    if not game_active:
        return

    x = random.randint(30, WIDTH - 30)
    y = PLAY_TOP + 10

    r = random.random()

    if r < 0.55:
        item = canvas.create_text(x, y, text="🍎", font=("Arial", 28))
        object_type = "apple"
    elif r < 0.80:
        item = canvas.create_text(x, y, text="🍐", font=("Arial", 28))
        object_type = "pear"
    else:
        item = canvas.create_text(x, y, text="💣", font=("Arial", 28))
        object_type = "bomb"

    objects.append([item, x, y, object_type])

    interval = max(400, 1000 - (GAME_TIME - time_left) * 8)
    root.after(int(interval), create_object)


# ================== УПРАВЛЕНИЕ ==================
def move_left(event):
    global basket_x
    if game_active and basket_x > 30:
        basket_x -= 25
        canvas.move(basket, -25, 0)


def move_right(event):
    global basket_x
    if game_active and basket_x < WIDTH - 30:
        basket_x += 25
        canvas.move(basket, 25, 0)


# ================== ОБНОВЛЕНИЕ ТАЙМЕРА ==================
def update_timer():
    global time_left, game_active

    if not game_active:
        return

    time_left -= 1

    # обновляем цифру
    canvas.itemconfig(timer_text, text=f"{time_left}")

    # цвет цифры меняется при малом времени
    if time_left <= 10:
        canvas.itemconfig(timer_text, fill="#FF4444")
    elif time_left <= 30:
        canvas.itemconfig(timer_text, fill="#FFD700")
    else:
        canvas.itemconfig(timer_text, fill="white")

    # обновляем полоску-индикатор
    ratio = max(0, time_left / GAME_TIME)
    new_x = BAR_X1 + (BAR_X2 - BAR_X1) * ratio
    canvas.coords(timer_bar, BAR_X1, BAR_Y1, new_x, BAR_Y2)

    # цвет полоски
    if ratio > 0.5:
        bar_color = "#00FF7F"
    elif ratio > 0.25:
        bar_color = "#FFD700"
    else:
        bar_color = "#FF4444"
    canvas.itemconfig(timer_bar, fill=bar_color)

    if time_left <= 0:
        game_active = False
        end_game()
        return

    root.after(1000, update_timer)


# ================== ИГРОВОЙ ЦИКЛ ==================
def update_game():
    global score, fall_speed, time_left, game_active

    if not game_active:
        return

    fall_speed += speed_increase

    for obj in objects[:]:
        item = obj[0]
        x = obj[1]
        y = obj[2]
        object_type = obj[3]

        y += fall_speed
        obj[2] = y
        canvas.move(item, 0, fall_speed)

        # поймали
        if basket_y - 30 <= y <= basket_y + 10:
            if abs(x - basket_x) < 45:

                if object_type == "apple":
                    score += 1
                elif object_type == "pear":
                    score += 2
                else:  # bomb
                    score = max(0, score - 3)
                    time_left = max(1, time_left - 5)
                    canvas.itemconfig(timer_text, text=f"{time_left}")
                    # сразу обновим полоску
                    ratio = max(0, time_left / GAME_TIME)
                    new_x = BAR_X1 + (BAR_X2 - BAR_X1) * ratio
                    canvas.coords(timer_bar, BAR_X1, BAR_Y1, new_x, BAR_Y2)

                canvas.itemconfig(score_text, text=f"Счёт: {score}")

                canvas.delete(item)
                objects.remove(obj)
                continue

        # упало мимо
        if y > HEIGHT:
            canvas.delete(item)
            objects.remove(obj)

    if game_active:
        root.after(40, update_game)


# ================== КОНЕЦ ИГРЫ ==================
def end_game():
    canvas.delete("all")
    canvas.create_rectangle(0, 0, WIDTH, HEIGHT,
                            fill="#FFE4B5", outline="")

    canvas.create_text(
        WIDTH // 2, HEIGHT // 2 - 70,
        text="⏰ ВРЕМЯ ВЫШЛО!",
        font=("Arial", 28, "bold"), fill="darkred"
    )
    canvas.create_text(
        WIDTH // 2, HEIGHT // 2,
        text=f"Твой результат: {score} очков",
        font=("Arial", 20, "bold"), fill="black"
    )
    canvas.create_text(
        WIDTH // 2, HEIGHT // 2 + 50,
        text="Отличный урожай! 🍎🍐",
        font=("Arial", 16), fill="darkgreen"
    )
    canvas.create_text(
        WIDTH // 2, HEIGHT // 2 + 100,
        text="Запусти игру снова, чтобы побить рекорд!",
        font=("Arial", 12), fill="gray"
    )


# ================== ЗАПУСК ==================
root.bind("<Left>", move_left)
root.bind("<Right>", move_right)

create_object()
update_game()
update_timer()

root.mainloop()