# Встановлення необхідних бібліотек: sounddevice для роботи з мікрофоном,
# numpy для математичних операцій, pygame для графіки та ігрової логіки
import sounddevice as sd  # Бібліотека для роботи з аудіо пристроями
import numpy as np        # Бібліотека для математичних обчислень з масивами
from pygame import *      # Імпорт всіх модулів pygame для створення ігор
from random import randint # Функція для генерації випадкових чисел

# ====== НАЛАШТУВАННЯ АУДІО ======
sr = 16000                # Частота дискретизації аудіо (16 кГц - достатньо для голосу)
block = 256               # Розмір блоку аудіо даних (менше значення = швидша реакція)
mic_level = 0.0           # Змінна для зберігання поточного рівня гучності з мікрофона

def audio_cb(indata, frames, time, status):
    # Callback функція, що викликається автоматично при надходженні аудіо даних
    global mic_level      # Використовуємо глобальну змінну mic_level
    if status:            # Перевірка на помилки в аудіо потоці
        return            # Якщо є помилка - виходимо з функції
    rms = float(np.sqrt(np.mean(indata**2)))  # Обчислюємо RMS (середньоквадратичне значення) - міра гучності
    mic_level = 0.85 * mic_level + 0.15 * rms # Згладжування рівня звуку (85% старе значення + 15% нове)

# ====== ІНІЦІАЛІЗАЦІЯ PYGAME ======
init()                    # Ініціалізація всіх модулів pygame
window_size = 1200, 800   # Розміри вікна гри (ширина, висота)
window = display.set_mode(window_size)  # Створення ігрового вікна
clock = time.Clock()      # Об'єкт для контролю частоти кадрів (FPS)
try:
    bg_image = image.load("images/backgrounds.png").convert()
    bg_image = transform.scale(bg_image,window_size)

    bird_image = image.load("images/backgrounds.png").convert_alpha()
    bird_image = transform.scale(bird_image,100,100)

    pipe_image = image.load("images/pipe.png").convert()

    ground_image = image.load("images/ground.png").convert()
    ground_image = transform.scale(ground_image,(window_size[0],100))
except:
    bg_image = None
    bird_image = None
    pipe_image = None
    ground_image = None


# ====== НАЛАШТУВАННЯ ГРАВЦЯ ======
player_rect = Rect(150, window_size[1]//2-100, 100, 100)  # Прямокутник гравця (x, y, ширина, висота)

def generate_pipes(count, pipe_width=140, gap=280, min_height=50, max_height=440, distance=650):
    # Функція генерації труб для перешкод
    pipes = []            # Список для зберігання всіх труб
    start_x = window_size[0]  # Початкова позиція X (праворуч від екрану)
    for i in range(count):    # Цикл створення заданої кількості пар труб
        height = randint(min_height, max_height)  # Випадкова висота верхньої труби
        top_pipe = Rect(start_x, 0, pipe_width, height)  # Створення верхньої труби
        # Створення нижньої труби (відступ gap від верхньої)
        bottom_pipe = Rect(start_x, height + gap, pipe_width, window_size[1] - (height + gap))
        pipes.extend([top_pipe, bottom_pipe])  # Додавання обох труб до списку
        start_x += distance   # Зсув X позиції для наступної пари труб
    return pipes             # Повернення списку всіх створених труб

# ====== ІГРОВІ ЗМІННІ ======
pies = generate_pipes(150)    # Створення 150 пар труб (перешкод)
main_font = font.Font(None, 100)  # Шрифт для відображення рахунку
score = 0                     # Початковий рахунок гравця
lose = False                  # Прапорець стану програшу
wait = 40                     # Лічильник очікування після програшу

# ====== ФІЗИЧНІ ПАРАМЕТРИ РУХУ ======
y_vel = 0.0                   # Швидкість руху по вертикалі
gravity = 0.6                 # Сила гравітації (прискорення вниз)
THRESH = 0.001                # Поріг гучності для спрацьовування "стрибка"
IMPULSE = -8.0                # Сила стрибка вгору (від'ємне значення = вгору)

# Запуск аудіо потоку з мікрофона з вказаними параметрами
with sd.InputStream(samplerate=sr, channels=1, blocksize=block, callback=audio_cb):
    while True:               # Головний ігровий цикл
        for e in event.get(): # Обробка всіх подій pygame
            if e.type == QUIT:    # Якщо натиснуто кнопку закриття вікна
                quit()            # Вихід з програми

        # ====== ЛОГІКА РУХУ ГРАВЦЯ ======
        if mic_level > THRESH:    # Якщо рівень звуку перевищує поріг
            y_vel = IMPULSE       # Надаємо імпульс вгору (стрибок)
        y_vel += gravity          # Додаємо гравітацію до швидкості
        player_rect.y += int(y_vel)  # Оновлюємо позицію гравця по Y

        # ====== ВІДОБРАЖЕННЯ ГРАФІКИ ======
        window.fill('sky blue')  # Заповнення фону блакитним кольором
        draw.rect(window, 'red', player_rect)  # Малювання червоного квадрата гравця

        # ====== ОБРОБКА ТРУБ (ПЕРЕШКОД) ======
        for pie in pies[:]:       # Ітерація по копії списку труб
            if not lose:          # Якщо гра не закінчена
                pie.x -= 10       # Рух труби вліво зі швидкістю 10 пікселів/кадр
            draw.rect(window, 'green', pie)  # Малювання зеленої труби
            if pie.x <= -100:     # Якщо труба вийшла за ліву межу екрану
                pies.remove(pie)  # Видалення труби зі списку
                score += 0.5      # Збільшення рахунку (0.5 за кожну трубу = 1 за пару)
            if player_rect.colliderect(pie):  # Перевірка зіткнення гравця з трубою
                lose = True       # Встановлення прапорця програшу

        # ====== ГЕНЕРАЦІЯ НОВИХ ТРУБ ======
        if len(pies) < 8:         # Якщо залишилось менше 8 труб
            pies += generate_pipes(150)  # Генерація додаткових 150 пар труб

        # ====== ВІДОБРАЖЕННЯ РАХУНКУ ======
        score_text = main_font.render(f'{int(score)}', 1, 'black')  # Створення тексту рахунку
        # Відображення рахунку по центру вгорі екрану
        window.blit(score_text, (window_size[0]//2 - score_text.get_rect().w//2, 40))

        display.update()          # Оновлення екрану (показ всіх змін)
        clock.tick(60)            # Обмеження до 60 FPS

        # ====== ПЕРЕЗАПУСК ГРИ ======
        keys = key.get_pressed()  # Отримання стану всіх клавіш
        if keys[K_r] and lose:    # Якщо натиснуто 'R' і гра програна
            lose = False          # Скидання прапорця програшу
            score = 0             # Скидання рахунку
            pies = generate_pipes(150)  # Генерація нових труб
            player_rect.y = window_size[1]//2-100  # Повернення гравця в початкову позицію
            y_vel = 0.0           # Скидання швидкості

        # ====== ОБМЕЖЕННЯ РУХУ ГРАВЦЯ ======
        if player_rect.bottom > window_size[1]:  # Якщо гравець торкнувся нижньої межі
            player_rect.bottom = window_size[1]  # Встановлення позиції на нижню межу
            y_vel = 0.0           # Скидання швидкості
        if player_rect.top < 0:   # Якщо гравець торкнувся верхньої межі
            player_rect.top = 0   # Встановлення позиції на верхню межу
            if y_vel < 0:         # Якщо швидкість була направлена вгору
                y_vel = 0.0       # Скидання швидкості

        # ====== ЛОГІКА ПІСЛЯ ПРОГРАШУ ======
        if lose and wait > 1:     # Якщо програв і ще є час очікування
            for pie in pies:      # Для всіх труб
                pie.x += 8        # Рух труб назад (ефект зупинки)
            wait -= 1             # Зменшення лічильника очікування
        else:                     # Якщо час очікування закінчився
            lose = False          # Скидання прапорця програшу
            wait = 40             # Скидання лічильника очікування