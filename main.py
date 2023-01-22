import random
import pygame
import time
import os

from dataBase import create_data_base, add_record_data_base, get_record_data_base
from random import choice, randrange
from copy import deepcopy
from itertools import product

if not os.path.exists('tetris.db'):
    create_data_base()


def check_borders():
    if figure[i].x < 0 or figure[i].x > width - 1:
        return False
    if figure[i].y > height - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True


def set_record(score, time):
    if int(get_record_data_base()[1]) >= score:
        return
    add_record_data_base(score, time)


def random_color():
    n = random.randrange(0, 19)
    return ['red', 'yellow', 'green', 'blue', 'pink', 'white', 'orange', 'brown', '#b8860b',
            '#006400', 'lime', 'purple', 'gray', '#00fa9a', '#00ffff', '#00bfff', '#191970', '#8b008b', '#1e90ff'
            ][n]


width, height = 10, 20
TILE = 35
GAMES_RES = width * TILE, height * TILE
RES = 700, 740
fps = 60
time_str = ""

FIGURE_POSITION: list[list[tuple[int, int]]] = [
    [(-1, 0), (-2, 0), (0, 0), (1, 0)],
    [(0, -1), (-1, -1), (-1, 0), (0, 0)],
    [(-1, 0), (-1, 1), (0, 0), (0, -1)],
    [(0, 0), (-1, 0), (0, 1), (-1, -1)],
    [(0, 0), (0, -1), (0, 1), (1, -1)],
    [(-1, 0), (-2, 0), (0, 0), (1, 0)]
]

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(RES)
    pygame.display.set_caption("TETRIS")

    game_screen = pygame.Surface(GAMES_RES)
    game_over_screen = pygame.Surface(GAMES_RES)
    sound = pygame.Surface((200, 70))

    clock = pygame.time.Clock()

    grid: list = list(pygame.Rect(i * TILE, j * TILE, TILE, TILE) for i in range(width) for j in range(height))

    figures: list = list()
    for figure_position in FIGURE_POSITION:
        _figures = list()
        for i, j in figure_position:
            _figures.append(pygame.Rect(i + width // 2, j + 1, 1, 1))
        figures.append(_figures)

    figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
    field = list(list(0 for i in range(width)) for j in range(height))

    animation_count, animation_speed, animation_limit = 0, 2, 2000
    figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))

    background = pygame.image.load('images/pygame.jpg').convert()
    game_background = pygame.image.load('images/board_1.png').convert()

    main_font = pygame.font.Font('fonts/unicephalon.otf', 65)
    font = pygame.font.Font('fonts/tet.ttf', 20)
    game_font = pygame.font.Font('fonts/unicephalon.otf', 35)
    game_text = pygame.font.Font('fonts/tet.ttf', 10)
    sound_text = pygame.font.Font('fonts/tet.ttf', 35)

    title_tetris = main_font.render('TETRIS', True, pygame.Color('orange'))
    title_score = font.render('score:', True, pygame.Color('red'))
    title_time_screen = font.render('time:', True, pygame.Color('red'))
    title_record_score = font.render('record score:', True, pygame.Color('yellow'))
    title_record_time = font.render('record time:', True, pygame.Color('yellow'))

    get_color = random_color

    color, next_color = get_color(), get_color()

    game_next = pygame.Surface((125, 125))

    score, lines = 0, 0
    scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

    time_start = time.time()
    game_over = False
    flag = False

    pygame.draw.rect(sound, '#00db6a', (0, 0, 200, 70), border_radius=15)

    pygame.mixer.music.load('music/game.mp3')
    pygame.mixer.music.play(-1)
    pause = False
    sound.blit(sound_text.render('SOUND', True, pygame.Color('black')), (15, 15))
    sound_flag = True
    color_sound = '#00db6a'

    x_pos, y_pos = 0, 0
    running = True

    while running:
        rotate1 = False
        rotate2 = False
        dx = 0
        dy = 0
        if not game_over:
            screen.blit(background, (0, 0))
            screen.blit(game_screen, (340, 20))
            game_screen.blit(game_background, (0, 0))

        # небольшая задержка
        for i in range(lines):
            pygame.time.wait(200)

        # нажатие клавиш
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and not pause:
                    dx -= 1
                if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and not pause:
                    dx += 1
                if (event.key == pygame.K_DOWN or event.key == pygame.K_s) and not pause:
                    animation_limit = 100
                    dy += 1
                if (event.key == pygame.K_UP or event.key == pygame.K_w) and not pause:
                    animation_limit = 2000
                if event.key == pygame.K_RSHIFT and not pause:
                    rotate1 = True
                if event.key == pygame.K_LSHIFT and not pause:
                    rotate2 = True
                if event.key == pygame.K_SPACE and game_over:
                    game_over = False
                    time_start = time.time()
                    flag = True
                    pause = False
                    animation_speed = 2
                if event.key == pygame.K_ESCAPE:
                    pause = not pause
                    time_pause = time.time()
            if event.type == pygame.MOUSEMOTION:
                x_pos, y_pos = event.pos
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 20 <= x_pos <= 220 and 640 <= y_pos <= 710:
                    sound_flag = not sound_flag
                    if sound_flag and not game_over:
                        color_sound = '#00db6a'
                        pygame.mixer.music.play(-1)
                    elif sound_flag:
                        color_sound = '#00db6a'
                    else:
                        color_sound = 'red'
                        pygame.mixer.music.stop()

        if not game_over and not pause:

            # перемещение вправо, влево
            figure_old = deepcopy(figure)
            for i in range(4):
                figure[i].x += dx
                figure[i].y += dy
                if not check_borders():
                    figure = deepcopy(figure_old)
                    break

            # увеличение скорости и падение фигуры
            animation_count += animation_speed
            if animation_count > animation_limit:
                animation_count = 0
                figure_old = deepcopy(figure)
                for i in range(4):
                    figure[i].y += 1
                    if not check_borders():
                        for i in range(4):
                            field[figure_old[i].y][figure_old[i].x] = color
                        figure, color = next_figure, next_color
                        next_figure, next_color = deepcopy(choice(figures)), get_color()
                        animation_limit = 2000
                        break

            # вращение вправо
            center = figure[0]
            figure_old = deepcopy(figure)
            if rotate1:
                for i in range(4):
                    x = figure[i].y - center.y
                    y = figure[i].x - center.x
                    figure[i].x = center.x - x
                    figure[i].y = center.y + y
                    if not check_borders():
                        figure = deepcopy(figure_old)
                        break
                rotate2 = False

            # вращение влево
            center = figure[0]
            figure_old = deepcopy(figure)
            if rotate2:
                for i in range(4):
                    x = figure[i].y - center.y
                    y = figure[i].x - center.x
                    figure[i].x = center.x + x
                    figure[i].y = center.y - y
                    if not check_borders():
                        figure = deepcopy(figure_old)
                        break
                rotate1 = False

            # проверка линий
            line, lines = height - 1, 0
            for row in range(height - 1, -1, -1):
                count = 0
                for i in range(width):
                    if field[row][i]:
                        count += 1
                    field[line][i] = field[row][i]
                if count < width:
                    line -= 1
                else:
                    # увеличение скорости если линии полные
                    if sound_flag:
                        pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/line_bonus.mp3'))
                    animation_speed += 2
                    lines += 1

            # очки
            score += scores[lines]

        if not game_over:
            # отрисовка поля
            [pygame.draw.rect(game_screen, (60, 60, 60), i, 1) for i in grid]

        if not game_over:
            # отрисовка падающей фигуры
            for i in range(4):
                figure_rect.x = figure[i].x * TILE
                figure_rect.y = figure[i].y * TILE
                pygame.draw.rect(game_screen, color, figure_rect)

            # отрисовка фигурка которые лежат
            for y, raw in enumerate(field):
                for x, col in enumerate(raw):
                    if col:
                        figure_rect.x, figure_rect.y = x * TILE, y * TILE
                        pygame.draw.rect(game_screen, col, figure_rect)

            # отрисовка поля следующей фигуры
            game_next.fill((0, 0, 0))

            for i in range(4):
                figure_rect.x = next_figure[i].x * 25 - 75
                figure_rect.y = next_figure[i].y * 25 + 25
                new_width = 25
                new_x, new_y = figure_rect.x, figure_rect.y
                pygame.draw.rect(game_next, next_color, (new_x, new_y, new_width, new_width))

            for i, j in product(range(5), range(5)):
                pygame.draw.rect(game_next, (100, 100, 100), (j * 25, i * 25, 25, 25), 1)

            # подсчёт времени
            time_now = int(time.time() - time_start)
            hour, minute, second = time_now // 3600, time_now // 60, time_now % 60
            time_str = ""
            if len(str(hour)) == 2:
                time_str += str(hour) + ':'
            else:
                time_str += '0' + str(hour) + ':'
            if len(str(minute)) == 2:
                time_str += str(minute) + ':'
            else:
                time_str += '0' + str(minute) + ':'
            if len(str(second)) == 2:
                time_str += str(second)
            else:
                time_str += '0' + str(second)

            # получение рекордов
            record_time, record_score = get_record_data_base()
        else:
            game_next.fill((0, 0, 0))
            for i in range(5):
                for j in range(5):
                    pygame.draw.rect(game_next, (100, 100, 100), (j * 25, i * 25, 25, 25), 1)

        if not game_over:

            # окончание игры
            for i in range(width):
                if ((field[0][i] or field[1][i] or field[2][i]) and 4 <= i <= 6) or field[0][i]:
                    if sound_flag:
                        pygame.mixer.music.load('music/game_over.mp3')
                        pygame.mixer.music.play()
                    set_record(score, time_str)
                    field = [[0 for i in range(width)] for i in range(height)]
                    anim_count, anim_speed, anim_limit = 0, 2, 2000
                    score = 0
                    game_over = True
                    game_over_screen.fill((0, 0, 0))
                    game_over_screen.blit(game_font.render(('GAME OVER'), True, pygame.Color('white')), (65, 300))
                    game_over_screen.blit(game_text.render(('TO START A NEW GAME'), True,
                                                           pygame.Color('white')), (70, 360))
                    game_over_screen.blit(game_text.render(('PRESS THE SPACE BAR'), True,
                                                           pygame.Color('white')), (70, 380))
                    screen.blit(game_over_screen, (340, 20))

        if flag:
            if sound_flag:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/bonus (2).mp3'))
                print(grid)
            for i in grid:
                pygame.draw.rect(game_screen, get_color(), i)
                screen.blit(game_screen, (340, 20))
                pygame.display.flip()
                clock.tick(200)
                flag = False
            if sound_flag:
                pygame.mixer.music.load('music/game.mp3')
                pygame.mixer.music.play(-1)

        # отрисовка холстов
        screen.blit(title_tetris, (10, 10))
        screen.blit(game_next, (190, 90))
        screen.blit(title_score, (20, 90))
        screen.blit(font.render(str(score), True, pygame.Color('white')), (20, 120))
        screen.blit(title_time_screen, (20, 160))
        screen.blit(font.render(str(time_str), True, pygame.Color('white')), (20, 200))
        screen.blit(title_record_score, (20, 260))
        screen.blit(font.render(str(record_score), True, pygame.Color('green')), (20, 300))
        screen.blit(title_record_time, (20, 340))
        screen.blit(font.render(str(record_time), True, pygame.Color('green')), (20, 380))
        pygame.draw.rect(sound, color_sound, (0, 0, 200, 70), border_radius=15)
        sound.blit(sound_text.render('SOUND', True, pygame.Color('black')), (15, 15))
        screen.blit(sound, (20, 640))

        pygame.display.flip()
        clock.tick()
    pygame.quit()