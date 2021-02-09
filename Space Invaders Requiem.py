import sys
import sqlite3
import time
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QSize
import pygame
import os
import pygame_textinput
from random import randint

# Импорт всех необходимых библиотек

p_name = 'DEFAULT PLAYER'
best_score = 0
now_score = -10
wave = 10
FPS = 60
SIZE = W, H = 450, 750
buttons = pygame.sprite.Group()
r1mobs = pygame.sprite.Group()
r2mobs = pygame.sprite.Group()
r3mobs = pygame.sprite.Group()
ships = pygame.sprite.Group()
fons = pygame.sprite.Group()
ship_bullets = pygame.sprite.Group()
mob_bullets = pygame.sprite.Group()
status = 'm'
tickn = 1
step = 12
vstep = 8
alive = [[False, False, False, False, False, False], [False, False, False, False, False, False],
         [False, False, False, False, False, False]]
pal = False
mpal = False
def_chance = 201


class Leaderboard(QWidget):  # Окно с таблицей лидеров
    def __init__(self):
        super().__init__()
        self.setGeometry(630, 160, 500, 400)
        self.setMinimumSize(QSize(630, 400))
        self.setWindowTitle("Вы проиграли")

        self.table = QTableWidget(self)
        self.table.resize(630, 400)
        self.initUi()

    def initUi(self):

        self.columns = ['Name', 'Best score', 'Date']
        w = [260, 165, 160]
        self.colCount = len(self.columns)
        self.table.setRowCount(0)
        self.table.setColumnCount(self.colCount)
        for j in range(self.colCount):
            self.table.setColumnWidth(j, w[j])

        # Установим с помощью css вид заголовков (отступы, границу, заливку)
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {padding:    1px;
                                  text-align: center;
                                  background: #FF0000;
                                  color: black;}
            """)
        # Установим с помощью css вид ячейки (отступы, границу, заливку)
        self.table.setStyleSheet("""
            QTableWidget::item {padding: 1px;
                                border: 2px solid black;
                                text-align: center;
                                background: #eeeeff;}""")

    def upd(self):
        self.table.setHorizontalHeaderLabels(self.columns)  # Обновление и добавление данных в в выводимую таблицу
        self.con = sqlite3.connect("data/leaderboard.sqlite")
        cur = self.con.cursor()
        que = "SELECT * FROM leaders ORDER BY Score DESC"
        result = cur.execute(que).fetchall()
        self.table.setRowCount(len(result))
        self.table.setColumnCount(3)
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


# Обозначение глобальных переменных


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    global status
    status = 'm'
    def_music = 'data/8bit.mp3'
    rare_music = 'data/original_starman.mp3'
    attempt = randint(0, 10)
    if attempt == 1:
        pygame.mixer.music.load(rare_music)
    else:
        pygame.mixer.music.load(def_music)
    pygame.mixer.music.play()

    fon = load_image('menu_fon.png')
    screen.blit(fon, (0, 0))
    black_fon = load_image('back.png')

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 138 <= event.pos[0] <= 324 and 441 <= event.pos[1] <= 534 and status == 'm':
                    screen.blit(black_fon, (0, 0))
                    enter_name()
        pygame.display.flip()
        clock.tick(FPS)


def enter_name():
    pygame.display.set_caption('Введите имя:')
    global status, p_name, best_score, now_score
    status = 'e'
    name_fon_im = load_image('enter_name.png')
    name_fon = pygame.sprite.Sprite(fons)
    name_fon.image = name_fon_im
    name_fon.rect = name_fon.image.get_rect()
    name_fon.rect.topleft = (0, 0)
    textinput = pygame_textinput.TextInput()
    textinput.font_family = 'alienencounters'
    while True:
        br = False

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    br = True
        if br:
            break
        fons.draw(screen)

        textinput.update(events)
        screen.blit(textinput.get_surface(), (20, 350))

        pygame.display.update()

    con = sqlite3.connect("data/leaderboard.sqlite")
    cur = con.cursor()
    if textinput.get_text() != '':
        p_name = textinput.get_text().upper()
    else:
        p_name = 'DEFAULT PLAYER'
    if p_name != 'DEFAULT PLAYER':
        result = cur.execute("""SELECT Score FROM leaders 
        WHERE Name = '{}'""".format(str(p_name))).fetchone()  # Проверяем, существует ли такое имя в таблице
        if result is None:
            cur.execute("""INSERT INTO leaders
            VALUES('{}', {}, '{}')""".format(str(p_name), '0', str(time.ctime(time.time()))))
            best_score = 0
        else:
            best_score = result[0]
    else:  # Если игрок оставил поле пустым, то называем его default_player и устанавливаем счёт на 0
        result = cur.execute("""SELECT Score FROM leaders 
        WHERE Name = '{}'""".format(str(p_name))).fetchone()
        if result is None:
            cur.execute("""INSERT INTO leaders
            VALUES('{}', {}, '{}')""".format(str(p_name), '0', str(time.ctime(time.time()))))
            best_score = 0
        else:
            result = cur.execute("""UPDATE leaders SET Score=0
            WHERE Name='{}'""".format(str(p_name))).fetchone()
            best_score = 0
    con.commit()  # Обновляем БД
    game_start()


def game_start():
    global status, wave, now_score, pal, mpal, def_chance
    pygame.display.set_caption('Space Invaders Rebuild')
    screen.fill((225, 225, 225))
    status = 'g'
    frame = 1
    aa = 0
    def_chance = 201

    running = True

    while running:
        if frame < 60:
            frame += 1
            if wave == 1 and frame == 1:
                mobs_move()
            if wave == 2 and (frame == 1 or frame == 31):
                mobs_move()
            if wave == 3 and (frame == 1 or frame == 21 or frame == 41):
                mobs_move()
            if wave == 4 and (frame == 1 or frame == 16 or frame == 21 or frame == 36):
                mobs_move()
            if wave == 5 and (frame == 1 or frame == 13 or frame == 25 or frame == 37 or frame == 49):
                mobs_move()
            if 6 <= wave < 10 and (frame == 1 or frame == 11 or frame == 21 or frame == 31 or frame == 41 or
                                   frame == 51):
                mobs_move()
            if wave >= 10 and (frame == 1 or frame == 7 or frame == 13 or frame == 19 or frame == 25 or frame == 31 or
                               frame == 37 or frame == 43 or frame == 49 or frame == 55):
                mobs_move()
        else:
            frame = 0

        pygame.display.update()
        screen.fill((0, 0, 0))
        score_str = 'Score: {}'.format(now_score)
        wave_str = 'Wave: {}'.format(wave)
        font = pygame.font.Font(None, 20)

        sc_rendered = font.render(score_str, True, pygame.Color('Yellow'))
        sc_rect = sc_rendered.get_rect()
        screen.blit(sc_rendered, sc_rect)

        wv_rendered = font.render(wave_str, True, pygame.Color('Yellow'))
        wv_rect = wv_rendered.get_rect()
        wv_rect.y = 15
        screen.blit(wv_rendered, wv_rect)

        r1mobs.draw(screen)
        r2mobs.draw(screen)
        r3mobs.draw(screen)
        if pal:
            ship_bullets.draw(screen)
            ship_piu.rect.top -= 5
            if frame == 1:
                ship_piu.image = bullet_im1
            elif frame == 31:
                ship_piu.image = bullet_im2
            check_hit()
        ships.draw(screen)

        for i in range(len(alive)):
            for j in range(len(alive[i])):
                if alive[i][j]:
                    aa += 1
        if aa < 1:
            new_wave()
        else:
            check_lose()
        aa = 0
        if not mpal:
            tr = randint(1, def_chance)
            if tr == 50:
                mob_pif()
        else:
            mob_piu.rect.top += 3
            check_mob_hit()
            if frame == 1:
                mob_piu.image = bullet_im3
            elif frame == 31:
                mob_piu.image = bullet_im4
            mob_bullets.draw(screen)
            if mob_piu.rect.top > 750:
                mpal = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ship_piu.rect.topleft = ship.rect.topleft
                    pal = True
                if event.key == pygame.K_ESCAPE:
                    you_lose()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            ship_move_right()
        if keys[pygame.K_LEFT]:
            ship_move_left()

        clock.tick(FPS)
        pygame.display.flip()
    return


def mob_pif():
    global alive, mpal
    row = randint(1, 3)
    n = randint(1, 6)
    while True:
        if alive[row - 1][n - 1]:
            break
        else:
            row = randint(1, 3)
            n = randint(1, 6)
    if row == 1:
        i = 1
        for mob in r1mobs:
            if i == n:
                mob_piu.rect.midtop = mob.rect.midtop
            i += 1
    elif row == 2:
        i = 1
        for mob in r2mobs:
            if i == n:
                mob_piu.rect.midtop = mob.rect.midtop
            i += 1
    elif row == 3:
        i = 1
        for mob in r3mobs:
            if i == n:
                mob_piu.rect.midtop = mob.rect.midtop
            i += 1
    mpal = True


def check_mob_hit():
    if mob_piu.rect.top > 690 and abs(ship.rect.right - mob_piu.rect.right) < 21:
        you_lose()


def check_lose():
    i = 0
    for mob in r1mobs:
        if alive[0][i]:
            if mob.rect.top >= 686:
                print('через чек')
                you_lose()
        i += 1
    i = 0
    for mob in r2mobs:
        if alive[0][i]:
            if mob.rect.top >= 686:
                print('через чек')
                you_lose()
        i += 1
    i = 0
    for mob in r3mobs:
        if alive[0][i]:
            if mob.rect.top >= 686:
                print('через чек')
                you_lose()
        i += 1


def you_lose():
    global best_score, now_score, alive, mpal
    for i in range(len(alive)):
        for j in range(len(alive[i])):
            alive[i][j] = False
    mpal = False
    if best_score < now_score:
        con = sqlite3.connect("data/leaderboard.sqlite")  # Обновление рекорда в таблице
        cur = con.cursor()
        cur.execute(
            """UPDATE leaders SET Score={}, Date='{}' WHERE Name='{}'""".format(now_score, str(
                time.ctime(time.time())), str(p_name), ))
        con.commit()
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        lead = Leaderboard()
        lead.upd()
        lead.show()
        start_screen()
        sys.exit(app.exec())


def check_hit():
    global pal, ship_piu, now_score, alive, mpal
    if pal:
        i = 0
        for mob in r1mobs:
            if alive[0][i]:
                if 0 < (ship_piu.rect.left + 22) - (mob.rect.left + 16) < 32:
                    if 0 < (ship_piu.rect.top + 12) - (mob.rect.top + 32) < 25:
                        mob.image = ded
                        alive[0][i] = False
                        pal = False
                        now_score += 3
            i += 1
        i = 0
        for mob in r2mobs:
            if alive[1][i]:
                if 0 < (ship_piu.rect.left + 22) - (mob.rect.left + 16) < 46:
                    if 0 < (ship_piu.rect.top + 12) - (mob.rect.top + 32) < 25:
                        mob.image = ded
                        alive[1][i] = False
                        pal = False
                        now_score += 2
            i += 1
        i = 0
        for mob in r3mobs:
            if alive[2][i]:
                if 0 < (ship_piu.rect.left + 22) - (mob.rect.left + 16) < 50:
                    if 0 < (ship_piu.rect.top + 12) - (mob.rect.top + 32) < 25:
                        mob.image = ded
                        alive[2][i] = False
                        pal = False
                        now_score += 1
            i += 1
        if mpal:
            if 0 < abs((ship_piu.rect.left + 21) - (mob_piu.rect.left + 21)) < 6:
                if 0 < abs((ship_piu.rect.top + 12) - (mob_piu.rect.top + 12)) < 25:
                    pal = False
                    mpal = False
                    now_score += 10


def ship_move_right():
    global ships
    if ship.rect[0] < 400:
        ship.rect.left += 5


def ship_move_left():
    global ships
    if ship.rect[0] > 2:
        ship.rect.left -= 5


def new_wave():
    global alive, r1mobs, r2mobs, r3mobs, def_chance
    global wave, best_score, now_score, row1sp1, row2sp1, row3sp1, tickn
    wave += 1
    tickn = 1
    if def_chance > 10:
        def_chance - 20

    print('Волна пошла')

    ship_piu.rect.topleft = (1000, 1000)

    ship.rect.topleft = (201, 702)

    mob11.rect.topleft = (5, 30)
    mob12.rect.topleft = (80, 30)
    mob13.rect.topleft = (155, 30)
    mob14.rect.topleft = (230, 30)
    mob15.rect.topleft = (305, 30)
    mob16.rect.topleft = (380, 30)
    mob11.image = row1sp1
    mob12.image = row1sp1
    mob13.image = row1sp1
    mob14.image = row1sp1
    mob15.image = row1sp1
    mob16.image = row1sp1

    mob21.rect.topleft = (8, 105)
    mob22.rect.topleft = (83, 105)
    mob23.rect.topleft = (158, 105)
    mob24.rect.topleft = (233, 105)
    mob25.rect.topleft = (308, 105)
    mob26.rect.topleft = (383, 105)
    mob21.image = row2sp1
    mob22.image = row2sp1
    mob23.image = row2sp1
    mob24.image = row2sp1
    mob25.image = row2sp1
    mob26.image = row2sp1

    mob31.rect.topleft = (8, 180)
    mob32.rect.topleft = (83, 180)
    mob33.rect.topleft = (158, 180)
    mob34.rect.topleft = (233, 180)
    mob35.rect.topleft = (308, 180)
    mob36.rect.topleft = (383, 180)
    mob31.image = row3sp1
    mob32.image = row3sp1
    mob33.image = row3sp1
    mob34.image = row3sp1
    mob35.image = row3sp1
    mob36.image = row3sp1

    for i in range(len(alive)):
        for j in range(len(alive[i])):
            alive[i][j] = True
    now_score += 10
    if best_score < now_score:
        con = sqlite3.connect("data/leaderboard.sqlite")  # Обновление рекорда в таблице
        cur = con.cursor()
        cur.execute(
            """UPDATE leaders SET Score={}, Date='{}' WHERE Name='{}'""".format(now_score, str(time.ctime(time.time())),
                                                                                str(p_name), ))
        con.commit()


def mobs_move():
    global tickn, r1mobs, r2mobs, r3mobs
    if tickn == 1:
        i = 0
        for mob in r1mobs:
            if alive[0][i]:
                mob.rect.topleft = (mob.rect.left + step, mob.rect.top)
                mob.image = row1sp2
            i += 1
        i = 0
        for mob in r2mobs:
            if alive[1][i]:
                mob.rect.topleft = (mob.rect.left - step, mob.rect.top)
                mob.image = row2sp2
            i += 1
        i = 0
        for mob in r3mobs:
            if alive[2][i]:
                mob.rect.topleft = (mob.rect.left + step, mob.rect.top)
                mob.image = row3sp2
            i += 1
        tickn = 2

    elif tickn == 2:
        i = 0
        for mob in r1mobs:
            if alive[0][i]:
                mob.rect.topleft = (mob.rect.left - step, mob.rect.top)
                mob.image = row1sp1
            i += 1
        i = 0
        for mob in r2mobs:
            if alive[1][i]:
                mob.rect.topleft = (mob.rect.left + step, mob.rect.top)
                mob.image = row2sp1
            i += 1
        i = 0
        for mob in r3mobs:
            if alive[2][i]:
                mob.rect.topleft = (mob.rect.left - step, mob.rect.top)
                mob.image = row3sp1
            i += 1
        tickn = 3

    elif tickn == 3:
        i = 0
        for mob in r1mobs:
            if alive[0][i]:
                mob.rect.topleft = (mob.rect.left - step, mob.rect.top)
                mob.image = row1sp2
            i += 1
        i = 0
        for mob in r2mobs:
            if alive[1][i]:
                mob.rect.topleft = (mob.rect.left + step, mob.rect.top)
                mob.image = row2sp2
            i += 1
        i = 0
        for mob in r3mobs:
            if alive[2][i]:
                mob.rect.topleft = (mob.rect.left - step, mob.rect.top)
                mob.image = row3sp2
            i += 1
        tickn = 4

    elif tickn == 4:
        i = 0
        for mob in r1mobs:
            if alive[0][i]:
                mob.rect.topleft = (mob.rect.left + step, mob.rect.top)
                mob.image = row1sp1
            i += 1
        i = 0
        for mob in r2mobs:
            if alive[1][i]:
                mob.rect.topleft = (mob.rect.left - step, mob.rect.top)
                mob.image = row2sp1
            i += 1
        i = 0
        for mob in r3mobs:
            if alive[2][i]:
                mob.rect.topleft = (mob.rect.left + step, mob.rect.top)
                mob.image = row3sp1
            i += 1

        tickn = 5

    elif tickn == 5:
        i = 0
        for mob in r1mobs:
            if alive[0][i]:
                mob.rect.topleft = (mob.rect.left, mob.rect.top + vstep)
            i += 1
        i = 0
        for mob in r2mobs:
            if alive[1][i]:
                mob.rect.topleft = (mob.rect.left, mob.rect.top + vstep)
            i += 1
        i = 0
        for mob in r3mobs:
            if alive[2][i]:
                mob.rect.topleft = (mob.rect.left, mob.rect.top + vstep)
            i += 1
        tickn = 1


pygame.init()
pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption('Space Invaders Rebuild')
clock = pygame.time.Clock()

row1sp1 = load_image('mob1.png')
row1sp2 = load_image('mob12.png')
mob11 = pygame.sprite.Sprite(r1mobs)
mob12 = pygame.sprite.Sprite(r1mobs)
mob13 = pygame.sprite.Sprite(r1mobs)
mob14 = pygame.sprite.Sprite(r1mobs)
mob15 = pygame.sprite.Sprite(r1mobs)
mob16 = pygame.sprite.Sprite(r1mobs)
mob11.image = row1sp1
mob12.image = row1sp1
mob13.image = row1sp1
mob14.image = row1sp1
mob15.image = row1sp1
mob16.image = row1sp1
mob11.rect = mob11.image.get_rect()
mob12.rect = mob12.image.get_rect()
mob13.rect = mob13.image.get_rect()
mob14.rect = mob14.image.get_rect()
mob15.rect = mob15.image.get_rect()
mob16.rect = mob16.image.get_rect()

row2sp1 = load_image('mob2.png')
row2sp2 = load_image('mob22.png')
mob21 = pygame.sprite.Sprite(r2mobs)
mob22 = pygame.sprite.Sprite(r2mobs)
mob23 = pygame.sprite.Sprite(r2mobs)
mob24 = pygame.sprite.Sprite(r2mobs)
mob25 = pygame.sprite.Sprite(r2mobs)
mob26 = pygame.sprite.Sprite(r2mobs)
mob21.image = row2sp1
mob22.image = row2sp1
mob23.image = row2sp1
mob24.image = row2sp1
mob25.image = row2sp1
mob26.image = row2sp1
mob21.rect = mob21.image.get_rect()
mob22.rect = mob22.image.get_rect()
mob23.rect = mob23.image.get_rect()
mob24.rect = mob24.image.get_rect()
mob25.rect = mob25.image.get_rect()
mob26.rect = mob26.image.get_rect()

row3sp1 = load_image('mob3.png')
row3sp2 = load_image('mob32.png')
mob31 = pygame.sprite.Sprite(r3mobs)
mob32 = pygame.sprite.Sprite(r3mobs)
mob33 = pygame.sprite.Sprite(r3mobs)
mob34 = pygame.sprite.Sprite(r3mobs)
mob35 = pygame.sprite.Sprite(r3mobs)
mob36 = pygame.sprite.Sprite(r3mobs)
mob31.image = row3sp1
mob32.image = row3sp1
mob33.image = row3sp1
mob34.image = row3sp1
mob35.image = row3sp1
mob36.image = row3sp1
mob31.rect = mob31.image.get_rect()
mob32.rect = mob32.image.get_rect()
mob33.rect = mob33.image.get_rect()
mob34.rect = mob34.image.get_rect()
mob35.rect = mob35.image.get_rect()
mob36.rect = mob36.image.get_rect()

ded = load_image('void.png')

ship_im = load_image('ship.png')
ship = pygame.sprite.Sprite(ships)
ship.image = ship_im
ship.rect = ship.image.get_rect()

bullet_im1 = load_image('ship_piu3.png')
bullet_im2 = load_image('ship_piu4.png')
bullet_im3 = load_image('mob_piu1.png')
bullet_im4 = load_image('mob_piu2.png')
ship_piu = pygame.sprite.Sprite(ship_bullets)
mob_piu = pygame.sprite.Sprite(mob_bullets)
mob_piu.image = bullet_im3
mob_piu.rect = mob_piu.image.get_rect()
ship_piu.image = bullet_im1
ship_piu.rect = ship.image.get_rect()

start_screen()
