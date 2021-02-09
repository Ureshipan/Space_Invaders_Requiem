import sys
import sqlite3
import threading
import time
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QMainWindow, QPushButton, QLineEdit
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize
import pygame
import os
import pygame_textinput
from random import randint

# Импорт всех необходимых библиотек

p_name = 'default_player'
best_score = 0
now_score = -10
wave = 0
FPS = 60
SIZE = W, H = 450, 750
buttons = pygame.sprite.Group()
mobs = pygame.sprite.Group()
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
        self.con = sqlite3.connect("leaderboard.sqlite")
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
                    return
        pygame.display.flip()
        clock.tick(FPS)


def enter_name(screen):
    pygame.display.set_caption('Введите имя:')
    global status, p_name, best_score, now_score
    status = 'e'
    screen = pygame.display.set_mode((450, 750))
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

    con = sqlite3.connect("leaderboard.sqlite")
    cur = con.cursor()
    if textinput.get_text() != '':
        p_name = textinput.get_text()
    if p_name != 'default_player':
        result = []
        result = cur.execute("""SELECT Score FROM leaders 
        WHERE Name = '{}'""".format(str(p_name))).fetchone()  # Проверяем, существует ли такое имя в таблице
        if result == None:
            cur.execute("""INSERT INTO leaders
            VALUES('{}', {}, '{}')""".format(str(p_name), '0', str(time.ctime(time.time()))))
            best_score = 0
        else:
            best_score = result[0]
    else:  # Если игрок оставил поле пустым, то называем его default_player и устанавливаем счёт на 0
        result = []
        result = cur.execute("""SELECT Score FROM leaders 
        WHERE Name = '{}'""".format(str(p_name))).fetchone()
        if result == None:
            cur.execute("""INSERT INTO leaders
            VALUES('{}', {}, '{}')""".format(str(p_name), '0', str(time.ctime(time.time()))))
            best_score = 0
        else:
            result = cur.execute("""UPDATE leaders SET Score=0
            WHERE Name='{}'""".format(str(p_name))).fetchone()
            best_score = 0
    con.commit()  # Обновляем БД
    return


def game_start():
    global status, wave, now_score, pal
    screen = pygame.display.set_mode((450, 750))
    screen.fill((225, 225, 225))
    status = 'g'
    frame = 1
    aa = False

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
            if wave >= 5 and (frame == 1 or frame == 13 or frame == 25 or frame == 37 or frame == 49):
                mobs_move()
        else:
            frame = 0

        pygame.display.update()
        screen.fill((0, 0, 0))
        score_str = 'Score: {}'.format(now_score)
        wave_str = 'Wave: {}'.format(wave)
        font = pygame.font.Font(None, 20)

        sc_rendered = font.render(score_str, 1, pygame.Color('Yellow'))
        sc_rect = sc_rendered.get_rect()
        screen.blit(sc_rendered, sc_rect)

        wv_rendered = font.render(wave_str, 1, pygame.Color('Yellow'))
        wv_rect = wv_rendered.get_rect()
        wv_rect.y = 15
        screen.blit(wv_rendered, wv_rect)

        mobs.draw(screen)
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
            if aa:
                break
            for j in range(len(alive[i])):
                if alive[i][j]:
                    aa = True
                    break
        if not aa:
            new_wave()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ship_piu.rect.topleft = ship.rect.topleft
                    pal = True
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            ship_move_right()
        if keys[pygame.K_LEFT]:
            ship_move_left()

        clock.tick(FPS)
        pygame.display.flip()
    return


def check_hit():
    print('Done')


def ship_move_right():
    global ships
    if ship.rect[0] < 400:
        ship.rect.left += 3


def ship_move_left():
    global ships
    if ship.rect[0] > 2:
        ship.rect.left -= 3


def new_wave():
    global alive, mobs
    global wave, best_score, now_score, row1sp1, row2sp1, row3sp1, tickn
    wave += 1
    tickn = 1

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
    mobs.draw(screen)
    now_score += 10
    if best_score < now_score:
        con = sqlite3.connect("leaderboard.sqlite")  # Обновление рекорда в таблице
        cur = con.cursor()
        cur.execute(
            """UPDATE leaders SET Score={}, Date='{}' WHERE Name='{}'""".format(now_score, str(time.ctime(time.time())),
                                                                                str(p_name), ))
        con.commit()


def mobs_move():
    global tickn, mobs
    if tickn == 1:
        if alive[0][0]:
            mob11.rect.topleft = (mob11.rect.left + step, mob11.rect.top)
        if alive[0][1]:
            mob12.rect.topleft = (mob12.rect.left + step, mob12.rect.top)
        if alive[0][2]:
            mob13.rect.topleft = (mob13.rect.left + step, mob13.rect.top)
        if alive[0][3]:
            mob14.rect.topleft = (mob14.rect.left + step, mob14.rect.top)
        if alive[0][4]:
            mob15.rect.topleft = (mob15.rect.left + step, mob15.rect.top)
        if alive[0][5]:
            mob16.rect.topleft = (mob16.rect.left + step, mob16.rect.top)
        mob11.image = row1sp2
        mob12.image = row1sp2
        mob13.image = row1sp2
        mob14.image = row1sp2
        mob15.image = row1sp2
        mob16.image = row1sp2

        if alive[1][0]:
            mob21.rect.topleft = (mob21.rect.left - step, mob21.rect.top)
        if alive[1][1]:
            mob22.rect.topleft = (mob22.rect.left - step, mob22.rect.top)
        if alive[1][2]:
            mob23.rect.topleft = (mob23.rect.left - step, mob23.rect.top)
        if alive[1][3]:
            mob24.rect.topleft = (mob24.rect.left - step, mob24.rect.top)
        if alive[1][4]:
            mob25.rect.topleft = (mob25.rect.left - step, mob25.rect.top)
        if alive[1][5]:
            mob26.rect.topleft = (mob26.rect.left - step, mob26.rect.top)
        mob21.image = row2sp2
        mob22.image = row2sp2
        mob23.image = row2sp2
        mob24.image = row2sp2
        mob25.image = row2sp2
        mob26.image = row2sp2

        if alive[2][0]:
            mob31.rect.topleft = (mob31.rect.left + step, mob31.rect.top)
        if alive[2][1]:
            mob32.rect.topleft = (mob32.rect.left + step, mob32.rect.top)
        if alive[2][2]:
            mob33.rect.topleft = (mob33.rect.left + step, mob33.rect.top)
        if alive[2][3]:
            mob34.rect.topleft = (mob34.rect.left + step, mob34.rect.top)
        if alive[2][4]:
            mob35.rect.topleft = (mob35.rect.left + step, mob35.rect.top)
        if alive[2][5]:
            mob36.rect.topleft = (mob36.rect.left + step, mob36.rect.top)
        mob31.image = row3sp2
        mob32.image = row3sp2
        mob33.image = row3sp2
        mob34.image = row3sp2
        mob35.image = row3sp2
        mob36.image = row3sp2

        tickn = 2

    elif tickn == 2:
        if alive[0][0]:
            mob11.rect.topleft = (mob11.rect.left - step, mob11.rect.top)
        if alive[0][1]:
            mob12.rect.topleft = (mob12.rect.left - step, mob12.rect.top)
        if alive[0][2]:
            mob13.rect.topleft = (mob13.rect.left - step, mob13.rect.top)
        if alive[0][3]:
            mob14.rect.topleft = (mob14.rect.left - step, mob14.rect.top)
        if alive[0][4]:
            mob15.rect.topleft = (mob15.rect.left - step, mob15.rect.top)
        if alive[0][5]:
            mob16.rect.topleft = (mob16.rect.left - step, mob16.rect.top)
        mob11.image = row1sp1
        mob12.image = row1sp1
        mob13.image = row1sp1
        mob14.image = row1sp1
        mob15.image = row1sp1
        mob16.image = row1sp1

        if alive[1][0]:
            mob21.rect.topleft = (mob21.rect.left + step, mob21.rect.top)
        if alive[1][1]:
            mob22.rect.topleft = (mob22.rect.left + step, mob22.rect.top)
        if alive[1][2]:
            mob23.rect.topleft = (mob23.rect.left + step, mob23.rect.top)
        if alive[1][3]:
            mob24.rect.topleft = (mob24.rect.left + step, mob24.rect.top)
        if alive[1][4]:
            mob25.rect.topleft = (mob25.rect.left + step, mob25.rect.top)
        if alive[1][5]:
            mob26.rect.topleft = (mob26.rect.left + step, mob26.rect.top)
        mob21.image = row2sp1
        mob22.image = row2sp1
        mob23.image = row2sp1
        mob24.image = row2sp1
        mob25.image = row2sp1
        mob26.image = row2sp1

        if alive[2][0]:
            mob31.rect.topleft = (mob31.rect.left - step, mob31.rect.top)
        if alive[2][1]:
            mob32.rect.topleft = (mob32.rect.left - step, mob32.rect.top)
        if alive[2][2]:
            mob33.rect.topleft = (mob33.rect.left - step, mob33.rect.top)
        if alive[2][3]:
            mob34.rect.topleft = (mob34.rect.left - step, mob34.rect.top)
        if alive[2][4]:
            mob35.rect.topleft = (mob35.rect.left - step, mob35.rect.top)
        if alive[2][5]:
            mob36.rect.topleft = (mob36.rect.left - step, mob36.rect.top)
        mob31.image = row3sp1
        mob32.image = row3sp1
        mob33.image = row3sp1
        mob34.image = row3sp1
        mob35.image = row3sp1
        mob36.image = row3sp1

        tickn = 3

    elif tickn == 3:
        if alive[0][0]:
            mob11.rect.topleft = (mob11.rect.left - step, mob11.rect.top)
        if alive[0][1]:
            mob12.rect.topleft = (mob12.rect.left - step, mob12.rect.top)
        if alive[0][2]:
            mob13.rect.topleft = (mob13.rect.left - step, mob13.rect.top)
        if alive[0][3]:
            mob14.rect.topleft = (mob14.rect.left - step, mob14.rect.top)
        if alive[0][4]:
            mob15.rect.topleft = (mob15.rect.left - step, mob15.rect.top)
        if alive[0][5]:
            mob16.rect.topleft = (mob16.rect.left - step, mob16.rect.top)
        mob11.image = row1sp2
        mob12.image = row1sp2
        mob13.image = row1sp2
        mob14.image = row1sp2
        mob15.image = row1sp2
        mob16.image = row1sp2

        if alive[1][0]:
            mob21.rect.topleft = (mob21.rect.left + step, mob21.rect.top)
        if alive[1][1]:
            mob22.rect.topleft = (mob22.rect.left + step, mob22.rect.top)
        if alive[1][2]:
            mob23.rect.topleft = (mob23.rect.left + step, mob23.rect.top)
        if alive[1][3]:
            mob24.rect.topleft = (mob24.rect.left + step, mob24.rect.top)
        if alive[1][4]:
            mob25.rect.topleft = (mob25.rect.left + step, mob25.rect.top)
        if alive[1][5]:
            mob26.rect.topleft = (mob26.rect.left + step, mob26.rect.top)
        mob21.image = row2sp2
        mob22.image = row2sp2
        mob23.image = row2sp2
        mob24.image = row2sp2
        mob25.image = row2sp2
        mob26.image = row2sp2

        if alive[2][0]:
            mob31.rect.topleft = (mob31.rect.left - step, mob31.rect.top)
        if alive[2][1]:
            mob32.rect.topleft = (mob32.rect.left - step, mob32.rect.top)
        if alive[2][2]:
            mob33.rect.topleft = (mob33.rect.left - step, mob33.rect.top)
        if alive[2][3]:
            mob34.rect.topleft = (mob34.rect.left - step, mob34.rect.top)
        if alive[2][4]:
            mob35.rect.topleft = (mob35.rect.left - step, mob35.rect.top)
        if alive[2][5]:
            mob36.rect.topleft = (mob36.rect.left - step, mob36.rect.top)
        mob31.image = row3sp2
        mob32.image = row3sp2
        mob33.image = row3sp2
        mob34.image = row3sp2
        mob35.image = row3sp2
        mob36.image = row3sp2

        tickn = 4

    elif tickn == 4:
        if alive[0][0]:
            mob11.rect.topleft = (mob11.rect.left + step, mob11.rect.top)
        if alive[0][1]:
            mob12.rect.topleft = (mob12.rect.left + step, mob12.rect.top)
        if alive[0][2]:
            mob13.rect.topleft = (mob13.rect.left + step, mob13.rect.top)
        if alive[0][3]:
            mob14.rect.topleft = (mob14.rect.left + step, mob14.rect.top)
        if alive[0][4]:
            mob15.rect.topleft = (mob15.rect.left + step, mob15.rect.top)
        if alive[0][5]:
            mob16.rect.topleft = (mob16.rect.left + step, mob16.rect.top)
        mob11.image = row1sp1
        mob12.image = row1sp1
        mob13.image = row1sp1
        mob14.image = row1sp1
        mob15.image = row1sp1
        mob16.image = row1sp1

        if alive[1][0]:
            mob21.rect.topleft = (mob21.rect.left - step, mob21.rect.top)
        if alive[1][1]:
            mob22.rect.topleft = (mob22.rect.left - step, mob22.rect.top)
        if alive[1][2]:
            mob23.rect.topleft = (mob23.rect.left - step, mob23.rect.top)
        if alive[1][3]:
            mob24.rect.topleft = (mob24.rect.left - step, mob24.rect.top)
        if alive[1][4]:
            mob25.rect.topleft = (mob25.rect.left - step, mob25.rect.top)
        if alive[1][5]:
            mob26.rect.topleft = (mob26.rect.left - step, mob26.rect.top)
        mob21.image = row2sp1
        mob22.image = row2sp1
        mob23.image = row2sp1
        mob24.image = row2sp1
        mob25.image = row2sp1
        mob26.image = row2sp1

        if alive[2][0]:
            mob31.rect.topleft = (mob31.rect.left + step, mob31.rect.top)
        if alive[2][1]:
            mob32.rect.topleft = (mob32.rect.left + step, mob32.rect.top)
        if alive[2][2]:
            mob33.rect.topleft = (mob33.rect.left + step, mob33.rect.top)
        if alive[2][3]:
            mob34.rect.topleft = (mob34.rect.left + step, mob34.rect.top)
        if alive[2][4]:
            mob35.rect.topleft = (mob35.rect.left + step, mob35.rect.top)
        if alive[2][5]:
            mob36.rect.topleft = (mob36.rect.left + step, mob36.rect.top)
        mob31.image = row3sp1
        mob32.image = row3sp1
        mob33.image = row3sp1
        mob34.image = row3sp1
        mob35.image = row3sp1
        mob36.image = row3sp1

        tickn = 5

    elif tickn == 5:
        if alive[0][0]:
            mob11.rect.topleft = (mob11.rect.left, mob11.rect.top + vstep)
        if alive[0][1]:
            mob12.rect.topleft = (mob12.rect.left, mob12.rect.top + vstep)
        if alive[0][2]:
            mob13.rect.topleft = (mob13.rect.left, mob13.rect.top + vstep)
        if alive[0][3]:
            mob14.rect.topleft = (mob14.rect.left, mob14.rect.top + vstep)
        if alive[0][4]:
            mob15.rect.topleft = (mob15.rect.left, mob15.rect.top + vstep)
        if alive[0][5]:
            mob16.rect.topleft = (mob16.rect.left, mob16.rect.top + vstep)

        if alive[1][0]:
            mob21.rect.topleft = (mob21.rect.left, mob21.rect.top + vstep)
        if alive[1][1]:
            mob22.rect.topleft = (mob22.rect.left, mob22.rect.top + vstep)
        if alive[1][2]:
            mob23.rect.topleft = (mob23.rect.left, mob23.rect.top + vstep)
        if alive[1][3]:
            mob24.rect.topleft = (mob24.rect.left, mob24.rect.top + vstep)
        if alive[1][4]:
            mob25.rect.topleft = (mob25.rect.left, mob25.rect.top + vstep)
        if alive[1][5]:
            mob26.rect.topleft = (mob26.rect.left, mob26.rect.top + vstep)

        if alive[2][0]:
            mob31.rect.topleft = (mob31.rect.left, mob31.rect.top + vstep)
        if alive[2][1]:
            mob32.rect.topleft = (mob32.rect.left, mob32.rect.top + vstep)
        if alive[2][2]:
            mob33.rect.topleft = (mob33.rect.left, mob33.rect.top + vstep)
        if alive[2][3]:
            mob34.rect.topleft = (mob34.rect.left, mob34.rect.top + vstep)
        if alive[2][4]:
            mob35.rect.topleft = (mob35.rect.left, mob35.rect.top + vstep)
        if alive[2][5]:
            mob36.rect.topleft = (mob36.rect.left, mob36.rect.top + vstep)
        tickn = 1


def bullet_move(self):  # Движение пули
    global now_score
    if self.game:
        if self.piu_exist:
            self.bullet.setPixmap(self.bullet_pixmap)
            self.bullet.move(self.bullet.x(), self.bullet.y() - 16)
            if self.mob11e:
                if 0 < (self.bullet.x() + 22) - (self.mob11.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob11.y() + 32) < 25:  # Проверка попадания по мобам
                        self.mob11e = False
                        self.mob11.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 4
            if self.mob12e:
                if 0 < (self.bullet.x() + 22) - (self.mob12.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob12.y() + 32) < 25:
                        self.mob12e = False
                        self.mob12.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 4
            if self.mob13e:
                if 0 < (self.bullet.x() + 22) - (self.mob13.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob13.y() + 32) < 25:
                        self.mob13e = False
                        self.mob13.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 4
            if self.mob14e:
                if 0 < (self.bullet.x() + 22) - (self.mob14.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob14.y() + 32) < 25:
                        self.mob14e = False
                        self.mob14.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 4
            if self.mob15e:
                if 0 < (self.bullet.x() + 22) - (self.mob15.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob15.y() + 32) < 25:
                        self.mob15e = False
                        self.mob15.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 4
            if self.mob16e:
                if 0 < (self.bullet.x() + 22) - (self.mob16.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob16.y() + 32) < 25:
                        self.mob16e = False
                        self.mob16.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 4

            if self.mob21e:
                if 0 < (self.bullet.x() + 22) - (self.mob21.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob21.y() + 32) < 25:
                        self.mob21e = False
                        self.mob21.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 3
            if self.mob22e:
                if 0 < (self.bullet.x() + 22) - (self.mob22.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob22.y() + 32) < 25:
                        self.mob22e = False
                        self.mob22.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 3
            if self.mob23e:
                if 0 < (self.bullet.x() + 22) - (self.mob23.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob23.y() + 32) < 25:
                        self.mob23e = False
                        self.mob23.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 3
            if self.mob24e:
                if 0 < (self.bullet.x() + 22) - (self.mob24.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob24.y() + 32) < 25:
                        self.mob24e = False
                        self.mob24.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 3
            if self.mob25e:
                if 0 < (self.bullet.x() + 22) - (self.mob25.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob25.y() + 32) < 25:
                        self.mob25e = False
                        self.mob25.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 3
            if self.mob26e:
                if 0 < (self.bullet.x() + 22) - (self.mob26.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob26.y() + 32) < 25:
                        self.mob26e = False
                        self.mob26.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 3

            if self.mob31e:
                if 0 < (self.bullet.x() + 22) - (self.mob31.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob31.y() + 32) < 25:
                        self.mob31e = False
                        self.mob31.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 2
            if self.mob32e:
                if 0 < (self.bullet.x() + 22) - (self.mob32.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob32.y() + 32) < 25:
                        self.mob32e = False
                        self.mob32.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 2
            if self.mob33e:
                if 0 < (self.bullet.x() + 22) - (self.mob33.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob33.y() + 32) < 25:
                        self.mob33e = False
                        self.mob33.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 2
            if self.mob34e:
                if 0 < (self.bullet.x() + 22) - (self.mob34.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob34.y() + 32) < 25:
                        self.mob34e = False
                        self.mob34.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 2
            if self.mob35e:
                if 0 < (self.bullet.x() + 22) - (self.mob35.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob35.y() + 32) < 25:
                        self.mob35e = False
                        self.mob35.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 2
            if self.mob36e:
                if 0 < (self.bullet.x() + 22) - (self.mob36.x() + 16) < 32:
                    if 0 < (self.bullet.y() + 12) - (self.mob36.y() + 32) < 25:
                        self.mob36e = False
                        self.mob36.setPixmap(self.void_pixmap)
                        self.piu_exist = False
                        now_score += 2

            if self.bullet.y() >= -48:
                self.piu_t = threading.Timer(0.2, self.bullet_move)
                self.piu_t.start()
            else:
                self.piu_t.cancel()
                self.piu_exist = False
        else:
            self.bullet.setPixmap(self.void_pixmap)


# Вызов новой волны если все мобы убиты

def check_lose(self):  # проверка проигрыша
    global p_name, best_score, now_score
    if (self.mob11.y() >= 736 or self.mob12.y() >= 736 or self.mob13.y() >= 736 or
        self.mob14.y() >= 736 or self.mob15.y() >= 736 or self.mob16.y() >= 736
        or self.mob21.y() >= 736 or self.mob22.y() >= 736 or self.mob23.y() >= 736
        or self.mob24.y() >= 736 or self.mob25.y() >= 736 or self.mob26.y() >= 736
        or self.mob31.y() >= 736 or self.mob32.y() >= 736 or self.mob33.y() >= 736
        or self.mob34.y() >= 736 or self.mob35.y() >= 736 or self.mob36.y() >= 736) and self.game:
        if best_score < now_score:  # Перезапись рекорда в таблице если этот рекорд побит
            self.con = sqlite3.connect("leaderboard.sqlite")
            cur = self.con.cursor()
            cur.execute("""UPDATE leaders SET Score={}, Date='{}' WHERE Name='{}'""".format(now_score, str(
                time.ctime(time.time())), str(p_name), ))
            self.con.commit()
            self.game = False
        self.l.upd()  # Обновление окна с таблицей
        self.l.show()  # и вывод его на экран


def cl(self):
    self.l.close()
    self.dialog.close()
    self.close()
    if self.play_obj.is_playing():
        self.play_obj = wave_obj.stop()


pygame.init()
pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption('Space Invaders Rebuild')
clock = pygame.time.Clock()

row1sp1 = load_image('mob1.png')
row1sp2 = load_image('mob12.png')
mob11 = pygame.sprite.Sprite(mobs)
mob12 = pygame.sprite.Sprite(mobs)
mob13 = pygame.sprite.Sprite(mobs)
mob14 = pygame.sprite.Sprite(mobs)
mob15 = pygame.sprite.Sprite(mobs)
mob16 = pygame.sprite.Sprite(mobs)
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
mob21 = pygame.sprite.Sprite(mobs)
mob22 = pygame.sprite.Sprite(mobs)
mob23 = pygame.sprite.Sprite(mobs)
mob24 = pygame.sprite.Sprite(mobs)
mob25 = pygame.sprite.Sprite(mobs)
mob26 = pygame.sprite.Sprite(mobs)
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
mob31 = pygame.sprite.Sprite(mobs)
mob32 = pygame.sprite.Sprite(mobs)
mob33 = pygame.sprite.Sprite(mobs)
mob34 = pygame.sprite.Sprite(mobs)
mob35 = pygame.sprite.Sprite(mobs)
mob36 = pygame.sprite.Sprite(mobs)
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

# if __name__ == '__main__':
# app = QApplication(sys.argv)
# l = Leaderboard()
# l.upd()
# l.show()
# sys.exit(app.exec())


start_screen()
enter_name(screen)

game_start()
terminate()