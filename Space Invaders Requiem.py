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
now_score = 0
wave = 1
FPS = 10
SIZE = W, H = 450, 750
buttons = pygame.sprite.Group()
mobs = pygame.sprite.Group()
fons = pygame.sprite.Group()
status = 'm'
tickn = 1
alive = [[False, False, False, False, False, False], [False, False, False, False, False, False], [False, False, False, False, False, False]]
# Обозначение глобальных переменных


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


def terminate():
    print(pygame.font.get_fonts())
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
                if event.pos[0] >= 138 and event.pos[1] >= 441 and event.pos[0] <= 324 and event.pos[1] <= 534 and status == 'm':
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

    #textinput.initial_string = False
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
    else:                        # Если игрок оставил поле пустым, то называем его default_player и устанавливаем счёт на 0
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
    global status, wave, now_score
    screen = pygame.display.set_mode((450, 750))
    screen.fill((225, 225, 225))
    status = 'g'
    aa = False

    ded = load_image('void.png')

    row1sp = load_image('mob1.png')
    mob11 = pygame.sprite.Sprite(mobs)
    mob12 = pygame.sprite.Sprite(mobs)
    mob13 = pygame.sprite.Sprite(mobs)
    mob14 = pygame.sprite.Sprite(mobs)
    mob15 = pygame.sprite.Sprite(mobs)
    mob16 = pygame.sprite.Sprite(mobs)
    mob11.image = row1sp
    mob12.image = row1sp
    mob13.image = row1sp
    mob14.image = row1sp
    mob15.image = row1sp
    mob16.image = row1sp
    mob11.rect = mob11.image.get_rect()
    mob12.rect = mob12.image.get_rect()
    mob13.rect = mob13.image.get_rect()
    mob14.rect = mob14.image.get_rect()
    mob15.rect = mob15.image.get_rect()
    mob16.rect = mob16.image.get_rect()

    row2sp = load_image('mob2.png')
    mob21 = pygame.sprite.Sprite(mobs)
    mob22 = pygame.sprite.Sprite(mobs)
    mob23 = pygame.sprite.Sprite(mobs)
    mob24 = pygame.sprite.Sprite(mobs)
    mob25 = pygame.sprite.Sprite(mobs)
    mob26 = pygame.sprite.Sprite(mobs)
    mob21.image = row2sp
    mob22.image = row2sp
    mob23.image = row2sp
    mob24.image = row2sp
    mob25.image = row2sp
    mob26.image = row2sp
    mob21.rect = mob21.image.get_rect()
    mob22.rect = mob22.image.get_rect()
    mob23.rect = mob23.image.get_rect()
    mob24.rect = mob24.image.get_rect()
    mob25.rect = mob25.image.get_rect()
    mob26.rect = mob26.image.get_rect()

    row3sp = load_image('mob3.png')
    mob31 = pygame.sprite.Sprite(mobs)
    mob32 = pygame.sprite.Sprite(mobs)
    mob33 = pygame.sprite.Sprite(mobs)
    mob34 = pygame.sprite.Sprite(mobs)
    mob35 = pygame.sprite.Sprite(mobs)
    mob36 = pygame.sprite.Sprite(mobs)
    mob31.image = row3sp
    mob32.image = row3sp
    mob33.image = row3sp
    mob34.image = row3sp
    mob35.image = row3sp
    mob36.image = row3sp
    mob31.rect = mob31.image.get_rect()
    mob32.rect = mob32.image.get_rect()
    mob33.rect = mob33.image.get_rect()
    mob34.rect = mob34.image.get_rect()
    mob35.rect = mob35.image.get_rect()
    mob36.rect = mob36.image.get_rect()

    running = True
    while running:
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

        clock.tick(FPS)
        pygame.display.flip()
    return


def new_wave():
    global wave, now_score
    wave += 1
    now_score += 1
    now_score *= 3


class Leaderboard(QWidget):  # Окно с таблицей лидеров
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):

        self.setMinimumSize(QSize(600, 400))
        self.setWindowTitle("Вы проиграли")

        self.table = QTableWidget(self)
        self.table.resize(600, 400)

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


class MainGame(QWidget):    # Окно с самой игрой
    def __init__(self):
        super().__init__()

        self.ship_pixmap = QPixmap('ship.png')
        self.back_pixmap = QPixmap('back.png')
        self.bullet_pixmap = QPixmap('piu.png')
        self.mob1_pixmap = QPixmap('data/mob1.png')    # Импортируем PNG как пиксмапы
        self.mob2_pixmap = QPixmap('mob2.png')
        self.mob3_pixmap = QPixmap('mob3.png')
        self.void_pixmap = QPixmap('void.png')

        self.setGeometry(600, 160, 500, 800)
        self.setMinimumSize(QSize(500, 800))
        self.setMaximumSize(QSize(500, 800))
        self.setWindowTitle('Space Invaders Requiem')
        self.wave = 1   # Номер волны
        self.movet = 0   # Переменная, используемая функцией движения мобов для определения следующего шага
        self.game = True  # Переменная, показывающая, идёт игра или закончилась
        self.wave_obj = sa.WaveObject.from_wave_file("peng.wav")
        self.play_obj = self.wave_obj.play()  # Запуск музычки(АП на неё у меня нет, но продавать этот проект я не собираюсь, так что ,думаю, всё нормально)

        self.initUi()  # Вызов первой волны

    def initUi(self):
        global now_score, p_name, best_score

        if self.wave == 1:
            self.back = QLabel(self)  # Создание фона
            self.back.setPixmap(self.back_pixmap)

            self.score_show = QLabel(self)   # Отображение счёта
            self.score_show.move(10, 0)
            self.score_show.resize(100, 20)
            self.score_show.setText("Score: {}".format(str(now_score)))
            self.score_show.setStyleSheet("color: rgb(255, 255, 255)")
            self.score_show.show()

            self.wave_show = QLabel(self)   # Отображение волны
            self.wave_show.move(10, 11)
            self.wave_show.resize(100, 20)
            self.wave_show.setText("Wave: {}".format(str(self.wave)))
            self.wave_show.setStyleSheet("color: rgb(255, 255, 255)")
            self.wave_show.show()

            self.ship = QLabel(self)  # Создание корабля
            self.ship.move(226, 755)
            self.ship.setPixmap(self.ship_pixmap)

            self.bullet = QLabel(self)  # Создание пульки
            self.bullet.move(1000, 1000)
            self.bullet.setPixmap(self.bullet_pixmap)

            self.mob11 = QLabel(self)
            self.mob11.setPixmap(self.mob1_pixmap)
            self.mob12 = QLabel(self)
            self.mob12.setPixmap(self.mob1_pixmap)
            self.mob13 = QLabel(self)
            self.mob13.setPixmap(self.mob1_pixmap)  # Создание мобов первого ряда
            self.mob14 = QLabel(self)
            self.mob14.setPixmap(self.mob1_pixmap)
            self.mob15 = QLabel(self)
            self.mob15.setPixmap(self.mob1_pixmap)
            self.mob16 = QLabel(self)
            self.mob16.setPixmap(self.mob1_pixmap)

            self.mob21 = QLabel(self)
            self.mob21.setPixmap(self.mob2_pixmap)
            self.mob22 = QLabel(self)
            self.mob22.setPixmap(self.mob2_pixmap)
            self.mob23 = QLabel(self)
            self.mob23.setPixmap(self.mob2_pixmap)  # Создание мобов второго ряда
            self.mob24 = QLabel(self)
            self.mob24.setPixmap(self.mob2_pixmap)
            self.mob25 = QLabel(self)
            self.mob25.setPixmap(self.mob2_pixmap)
            self.mob26 = QLabel(self)
            self.mob26.setPixmap(self.mob2_pixmap)

            self.mob31 = QLabel(self)
            self.mob31.setPixmap(self.mob3_pixmap)
            self.mob32 = QLabel(self)
            self.mob32.setPixmap(self.mob3_pixmap)
            self.mob33 = QLabel(self)
            self.mob33.setPixmap(self.mob3_pixmap)  # Создание мобов третьего ряда
            self.mob34 = QLabel(self)
            self.mob34.setPixmap(self.mob3_pixmap)
            self.mob35 = QLabel(self)
            self.mob35.setPixmap(self.mob3_pixmap)
            self.mob36 = QLabel(self)
            self.mob36.setPixmap(self.mob3_pixmap)

            self.step = 10  # Скорость корабля
            self.game_speed = 5  # Скорость противников
            self.piu_exist = False
            self.show()
            self.dialog = AddPlayer()
            self.dialog.show()
            self.l = Leaderboard()
            self.l.upd()
            self.l.show()  # Вызов таблицы лидеров для того, чтобы это окно находилось в одном потоке с основным и не возникало ошибки
            self.l.hide()  # Скрытие таблицы до момента проигрыша

        else:
            self.mob11.setPixmap(self.mob1_pixmap)
            self.mob12.setPixmap(self.mob1_pixmap)
            self.mob13.setPixmap(self.mob1_pixmap)
            self.mob14.setPixmap(self.mob1_pixmap)  # Воскрешение мобов первого ряда
            self.mob15.setPixmap(self.mob1_pixmap)
            self.mob16.setPixmap(self.mob1_pixmap)

            self.mob21.setPixmap(self.mob2_pixmap)
            self.mob22.setPixmap(self.mob2_pixmap)
            self.mob23.setPixmap(self.mob2_pixmap)
            self.mob24.setPixmap(self.mob2_pixmap)  # Воскрешение мобов второго рада
            self.mob25.setPixmap(self.mob2_pixmap)
            self.mob26.setPixmap(self.mob2_pixmap)

            self.mob31.setPixmap(self.mob3_pixmap)
            self.mob32.setPixmap(self.mob3_pixmap)
            self.mob33.setPixmap(self.mob3_pixmap)
            self.mob34.setPixmap(self.mob3_pixmap)  # Воскрешение мобов третьего ряда
            self.mob35.setPixmap(self.mob3_pixmap)
            self.mob36.setPixmap(self.mob3_pixmap)

            self.t.cancel()  # Сброс таймера во избежание ошибок и накладок

            self.score_show.setText("Score: {}".format(str(now_score)))  # Обновление отображаемого счёта

            if self.game_speed <= 19:
                self.game_speed += 2

            if not self.play_obj.is_playing():
                self.play_obj = wave_obj.play()

            self.wave_show.setText("Wave: {}".format(str(self.wave)))  # Обновление Счётчика волн

        self.mob11.move(4, 20)
        self.mob11e = True
        self.mob12.move(84, 20)
        self.mob12e = True
        self.mob13.move(164, 20)
        self.mob13e = True
        self.mob14.move(244, 20)  # Перемещение мобов на начальные позиции
        self.mob14e = True
        self.mob15.move(324, 20)
        self.mob15e = True
        self.mob16.move(404, 20)
        self.mob16e = True

        self.mob21.move(28, 84)
        self.mob21e = True
        self.mob22.move(108, 84)
        self.mob22e = True
        self.mob23.move(188, 84)
        self.mob23e = True
        self.mob24.move(268, 84)
        self.mob24e = True
        self.mob25.move(348, 84)
        self.mob25e = True
        self.mob26.move(428, 84)
        self.mob26e = True

        self.mob31.move(4, 148)
        self.mob31e = True
        self.mob32.move(84, 148)
        self.mob32e = True
        self.mob33.move(164, 148)
        self.mob33e = True
        self.mob34.move(244, 148)
        self.mob34e = True
        self.mob35.move(324, 148)
        self.mob35e = True
        self.mob36.move(404, 148)
        self.mob36e = True

        if best_score < now_score:
            self.con = sqlite3.connect("leaderboard.sqlite")  # Обновление рекорда в таблице
            cur = self.con.cursor()
            cur.execute("""UPDATE leaders SET Score={}, Date='{}' WHERE Name='{}'""".format(now_score, str(time.ctime(time.time())), str(p_name),))
            self.con.commit()

        self.wave += 1
        self.movet = 0
        self.mob_move()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.game = False  # Выход из приложения
            self.cl()

        if event.key() == Qt.Key_Left:
            if not self.ship.x() - self.step < 0:
                self.ship.move(self.ship.x() - self.step, self.ship.y())  # Движение корабля влево и вправо
        elif event.key() == Qt.Key_Right:
            if not self.ship.x() + self.step > 455:
                self.ship.move(self.ship.x() + self.step, self.ship.y())

        if event.key() == Qt.Key_Space or event.key() == Qt.Key_Up:  # Инициация стрельбы
            self.bullet.move(self.ship.x(), self.ship.y() - 10)
            self.bullet.setPixmap(self.bullet_pixmap)
            self.piu_exist = True
            self.bullet_move()
            self.update()

    def mob_move(self):  # Движение мобов

        global now_score
        if self.game:

            if self.movet == 0:  # Движение вниз и вправо
                if self.mob11e:
                    self.mob11.move(self.mob11.x() + 12, self.mob11.y() + self.game_speed)
                if self.mob12e:
                    self.mob12.move(self.mob12.x() + 12, self.mob12.y() + self.game_speed)
                if self.mob13e:
                    self.mob13.move(self.mob13.x() + 12, self.mob13.y() + self.game_speed)
                if self.mob14e:
                    self.mob14.move(self.mob14.x() + 12, self.mob14.y() + self.game_speed)
                if self.mob15e:
                    self.mob15.move(self.mob15.x() + 12, self.mob15.y() + self.game_speed)
                if self.mob16e:
                    self.mob16.move(self.mob16.x() + 12, self.mob16.y() + self.game_speed)

                if self.mob21e:
                    self.mob21.move(self.mob21.x() - 12, self.mob21.y() + self.game_speed)
                if self.mob22e:
                    self.mob22.move(self.mob22.x() - 12, self.mob22.y() + self.game_speed)
                if self.mob23e:
                    self.mob23.move(self.mob23.x() - 12, self.mob23.y() + self.game_speed)
                if self.mob24e:
                    self.mob24.move(self.mob24.x() - 12, self.mob24.y() + self.game_speed)
                if self.mob25e:
                    self.mob25.move(self.mob25.x() - 12, self.mob25.y() + self.game_speed)
                if self.mob26e:
                    self.mob26.move(self.mob26.x() - 12, self.mob26.y() + self.game_speed)

                if self.mob31e:
                    self.mob31.move(self.mob31.x() + 12, self.mob31.y() + self.game_speed)
                if self.mob32e:
                    self.mob32.move(self.mob32.x() + 12, self.mob32.y() + self.game_speed)
                if self.mob33e:
                    self.mob33.move(self.mob33.x() + 12, self.mob33.y() + self.game_speed)
                if self.mob34e:
                    self.mob34.move(self.mob34.x() + 12, self.mob34.y() + self.game_speed)
                if self.mob35e:
                    self.mob35.move(self.mob35.x() + 12, self.mob35.y() + self.game_speed)
                if self.mob36e:
                    self.mob36.move(self.mob36.x() + 12, self.mob36.y() + self.game_speed)

                self.movet = 1

            elif self.movet == 1:  # Движение вправо
                if self.mob11e:
                    self.mob11.move(self.mob11.x() + 12, self.mob11.y())
                if self.mob12e:
                    self.mob12.move(self.mob12.x() + 12, self.mob12.y())
                if self.mob13e:
                    self.mob13.move(self.mob13.x() + 12, self.mob13.y())
                if self.mob14e:
                    self.mob14.move(self.mob14.x() + 12, self.mob14.y())
                if self.mob15e:
                    self.mob15.move(self.mob15.x() + 12, self.mob15.y())
                if self.mob16e:
                    self.mob16.move(self.mob16.x() + 12, self.mob16.y())

                if self.mob21e:
                    self.mob21.move(self.mob21.x() - 12, self.mob21.y())
                if self.mob22e:
                    self.mob22.move(self.mob22.x() - 12, self.mob22.y())
                if self.mob23e:
                    self.mob23.move(self.mob23.x() - 12, self.mob23.y())
                if self.mob24e:
                    self.mob24.move(self.mob24.x() - 12, self.mob24.y())
                if self.mob25e:
                    self.mob25.move(self.mob25.x() - 12, self.mob25.y())
                if self.mob26e:
                    self.mob26.move(self.mob26.x() - 12, self.mob26.y())

                if self.mob31e:
                    self.mob31.move(self.mob31.x() + 12, self.mob31.y())
                if self.mob32e:
                    self.mob32.move(self.mob32.x() + 12, self.mob32.y())
                if self.mob33e:
                    self.mob33.move(self.mob33.x() + 12, self.mob33.y())
                if self.mob34e:
                    self.mob34.move(self.mob34.x() + 12, self.mob34.y())
                if self.mob35e:
                    self.mob35.move(self.mob35.x() + 12, self.mob35.y())
                if self.mob36e:
                    self.mob36.move(self.mob36.x() + 12, self.mob36.y())

                self.movet = 2

            elif self.movet == 2:  # Движение влево
                if self.mob11e:
                    self.mob11.move(self.mob11.x() - 12, self.mob11.y())
                if self.mob12e:
                    self.mob12.move(self.mob12.x() - 12, self.mob12.y())
                if self.mob13e:
                    self.mob13.move(self.mob13.x() - 12, self.mob13.y())
                if self.mob14e:
                    self.mob14.move(self.mob14.x() - 12, self.mob14.y())
                if self.mob15e:
                    self.mob15.move(self.mob15.x() - 12, self.mob15.y())
                if self.mob16e:
                    self.mob16.move(self.mob16.x() - 12, self.mob16.y())

                if self.mob21e:
                    self.mob21.move(self.mob21.x() + 12, self.mob21.y())
                if self.mob22e:
                    self.mob22.move(self.mob22.x() + 12, self.mob22.y())
                if self.mob23e:
                    self.mob23.move(self.mob23.x() + 12, self.mob23.y())
                if self.mob24e:
                    self.mob24.move(self.mob24.x() + 12, self.mob24.y())
                if self.mob25e:
                    self.mob25.move(self.mob25.x() + 12, self.mob25.y())
                if self.mob26e:
                    self.mob26.move(self.mob26.x() + 12, self.mob26.y())

                if self.mob31e:
                    self.mob31.move(self.mob31.x() - 12, self.mob31.y())
                if self.mob32e:
                    self.mob32.move(self.mob32.x() - 12, self.mob32.y())
                if self.mob33e:
                    self.mob33.move(self.mob33.x() - 12, self.mob33.y())
                if self.mob34e:
                    self.mob34.move(self.mob34.x() - 12, self.mob34.y())
                if self.mob35e:
                    self.mob35.move(self.mob35.x() - 12, self.mob35.y())
                if self.mob36e:
                    self.mob36.move(self.mob36.x() - 12, self.mob36.y())

                self.movet = 3

            else:              # Движение влево
                if self.mob11e:
                    self.mob11.move(self.mob11.x() - 12, self.mob11.y())
                if self.mob12e:
                    self.mob12.move(self.mob12.x() - 12, self.mob12.y())
                if self.mob13e:
                    self.mob13.move(self.mob13.x() - 12, self.mob13.y())
                if self.mob14e:
                    self.mob14.move(self.mob14.x() - 12, self.mob14.y())
                if self.mob15e:
                    self.mob15.move(self.mob15.x() - 12, self.mob15.y())
                if self.mob16e:
                    self.mob16.move(self.mob16.x() - 12, self.mob16.y())

                if self.mob21e:
                    self.mob21.move(self.mob21.x() + 12, self.mob21.y())
                if self.mob22e:
                    self.mob22.move(self.mob22.x() + 12, self.mob22.y())
                if self.mob23e:
                    self.mob23.move(self.mob23.x() + 12, self.mob23.y())
                if self.mob24e:
                    self.mob24.move(self.mob24.x() + 12, self.mob24.y())
                if self.mob25e:
                    self.mob25.move(self.mob25.x() + 12, self.mob25.y())
                if self.mob26e:
                    self.mob26.move(self.mob26.x() + 12, self.mob26.y())

                if self.mob31e:
                    self.mob31.move(self.mob31.x() - 12, self.mob31.y())
                if self.mob32e:
                    self.mob32.move(self.mob32.x() - 12, self.mob32.y())
                if self.mob33e:
                    self.mob33.move(self.mob33.x() - 12, self.mob33.y())
                if self.mob34e:
                    self.mob34.move(self.mob34.x() - 12, self.mob34.y())
                if self.mob35e:
                    self.mob35.move(self.mob35.x() - 12, self.mob35.y())
                if self.mob36e:
                    self.mob36.move(self.mob36.x() - 12, self.mob36.y())

                self.movet = 0

            self.t = threading.Timer(0.5, self.mob_move)  # Установка таймера для следующего движения
            self.t.start()
            self.check_all_deads()  # Проверка на уничтожение всех мобов
            self.check_lose()   # Проверка проигрыша
            self.update()
            self.score_show.setText("Score: {}".format(str(now_score)))  # Обновление отображаемого счёта

    def bullet_move(self):   # Движение пули
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

    def check_all_deads(self):  # Проверка существуют ли мобы
        global now_score
        if not (self.mob11e or self.mob12e or self.mob13e or self.mob14e or self.mob15e or self.mob16e
                or self.mob21e or self.mob22e or self.mob23e or self.mob24e or self.mob25e or self.mob26e
                or self.mob31e or self.mob32e or self.mob33e or self.mob34e or self.mob35e or self.mob36e):
            now_score += 10
            self.initUi()  # Вызов новой волны если все мобы убиты

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
                cur.execute("""UPDATE leaders SET Score={}, Date='{}' WHERE Name='{}'""".format(now_score, str(time.ctime(time.time())), str(p_name),))
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
# заставка
start_screen()
enter_name(screen)
game_start()
terminate()

# if __name__ == '__main__':
    #app = QApplication(sys.argv)
    #game = MainGame()
    # game.show()
    # sys.exit(app.exec())
 #   ['arial', 'arialblack', 'bahnschrift', 'calibri', 'cambriacambriamath', 'cambria', 'candara', 'comicsansms', 'consolas', 'constantia', 'corbel', 'couriernew', 'ebrima', 'franklingothicmedium', 'gabriola', 'gadugi', 'georgia', 'impact', 'inkfree', 'javanesetext', 'leelawadeeui', 'leelawadeeuisemilight', 'lucidaconsole', 'lucidasans', 'malgungothic', 'malgungothicsemilight', 'microsofthimalaya', 'microsoftjhengheimicrosoftjhengheiui', 'microsoftjhengheimicrosoftjhengheiuibold', 'microsoftjhengheimicrosoftjhengheiuilight', 'microsoftnewtailue', 'microsoftphagspa', 'microsoftsansserif', 'microsofttaile', 'microsoftyaheimicrosoftyaheiui', 'microsoftyaheimicrosoftyaheiuibold', 'microsoftyaheimicrosoftyaheiuilight', 'microsoftyibaiti', 'mingliuextbpmingliuextbmingliuhkscsextb', 'mongolianbaiti', 'msgothicmsuigothicmspgothic', 'mvboli', 'myanmartext', 'nirmalaui', 'nirmalauisemilight', 'palatinolinotype', 'segoemdl2assets', 'segoeprint', 'segoescript', 'segoeui', 'segoeuiblack', 'segoeuiemoji', 'segoeuihistoric', 'segoeuisemibold', 'segoeuisemilight', 'segoeuisymbol', 'simsunnsimsun', 'simsunextb', 'sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner', 'sitkasmallsitkatextboldsitkasubheadingboldsitkaheadingboldsitkadisplayboldsitkabannerbold', 'sitkasmallsitkatextbolditalicsitkasubheadingbolditalicsitkaheadingbolditalicsitkadisplaybolditalicsitkabannerbolditalic', 'sitkasmallsitkatextitalicsitkasubheadingitalicsitkaheadingitalicsitkadisplayitalicsitkabanneritalic', 'sylfaen', 'symbol', 'tahoma', 'timesnewroman', 'trebuchetms', 'verdana', 'webdings', 'wingdings', 'yugothicyugothicuisemiboldyugothicuibold', 'yugothicyugothicuilight', 'yugothicmediumyugothicuiregular', 'yugothicregularyugothicuisemilight', 'holomdl2assets', 'acaslonproboldopentype', 'acaslonprobolditalicopentype', 'acaslonproitalicopentype', 'acaslonproregularopentype', 'acaslonprosemiboldopentype', 'acaslonprosemibolditalicopentype', 'adobefangsongstdregularopentype', 'adobefanheitistdboldopentype', 'adobegothicstdboldopentype', 'adobeheitistdregularopentype', 'adobekaitistdregularopentype', 'adobenaskhmediumopentype', 'agaramondproboldopentype', 'agaramondprobolditalicopentype', 'agaramondproitalicopentype', 'agaramondproregularopentype', 'birchstdopentype', 'blackoakstdopentype', 'brushscriptstdopentype', 'chaparralproboldopentype', 'chaparralprobolditopentype', 'chaparralproitalicopentype', 'chaparralprolightitopentype', 'chaparralproregularopentype', 'charlemagnestdboldopentype', 'hobostdopentype', 'kozgoproboldopentype', 'kozgoproextralightopentype', 'kozgoproheavyopentype', 'kozgoprolightopentype', 'kozgopromediumopentype', 'kozgoproregularopentype', 'kozminproboldopentype', 'kozminproextralightopentype', 'kozminproheavyopentype', 'kozminprolightopentype', 'kozminpromediumopentype', 'kozminproregularopentype', 'lithosproblackopentype', 'lithosproregularopentype', 'minionproboldcnopentype', 'minionproboldcnitopentype', 'minionpromediumopentype', 'minionpromediumitopentype', 'minionprosemiboldopentype', 'minionprosemibolditopentype', 'myriadarabicopentype', 'nuevastdboldopentype', 'nuevastdboldcondopentype', 'nuevastdcondopentype', 'nuevastditalicopentype', 'ocrastdopentype', 'oratorstdopentype', 'poplarstdopentype', 'prestigeelitestdbdopentype', 'sourcesansproblackopentype', 'sourcesansproopentype', 'sourcesansproextralightopentype', 'sourcesansprosemiboldopentype', 'tektonproboldopentype', 'tektonproboldcondopentype', 'tektonproboldextopentype', 'tektonproboldoblopentype', 'trajanpro3opentype', 'adobearabicboldopentype', 'adobearabicbolditalicopentype', 'adobearabicitalicopentype', 'adobearabicregularopentype', 'adobedevanagariboldopentype', 'adobedevanagaribolditalicopentype', 'adobedevanagariitalicopentype', 'adobedevanagariregularopentype', 'adobegurmukhiopentype', 'adobehebrewboldopentype', 'adobehebrewbolditalicopentype', 'adobehebrewitalicopentype', 'adobehebrewregularopentype', 'adobemingstdlightopentype', 'adobemyungjostdmediumopentype', 'adobesongstdlightopentype', 'kozgopr6nboldopentype', 'kozgopr6nextralightopentype', 'kozgopr6nheavyopentype', 'kozgopr6nlightopentype', 'kozgopr6nmediumopentype', 'kozgopr6nregularopentype', 'kozminpr6nboldopentype', 'kozminpr6nextralightopentype', 'kozminpr6nheavyopentype', 'kozminpr6nlightopentype', 'kozminpr6nmediumopentype', 'kozminpr6nregularopentype', 'lettergothicstdboldopentype', 'lettergothicstdboldslantedopentype', 'lettergothicstdslantedopentype', 'lettergothicstdopentype', 'minionproboldopentype', 'minionprobolditopentype', 'minionproitopentype', 'minionproregularopentype', 'myriadhebrewopentype', 'myriadproboldopentype', 'myriadproboldcondopentype', 'myriadproboldconditopentype', 'myriadprobolditopentype', 'myriadprocondopentype', 'myriadproconditopentype', 'myriadproitopentype', 'myriadproregularopentype', 'myriadprosemiboldopentype', 'myriadprosemibolditopentype', 'lato', 'latobolditalic', 'latolightitalic', 'latosemibold', 'latosemibolditalic', '18thcentury', 'acmefontregular', 'alfredoregular', 'alienencounters', 'almontesnow', 'amethystregular', 'asimov', 'autumnregular', 'babykruffy', 'balthazarregular', 'bastionregular', 'bnjinx', 'bnmachine', 'bobcat', 'bolsterbold', 'borealisregular', 'boutoninternationalsymbols', 'brandishregular', 'brusselsregular', 'calligraphicregular', 'calvinregular', 'candles', 'chinyennormal', 'clarendonregular', 'colbertregular', 'commonsregular', 'coolsvilleregular', 'corporateregular', 'crackedjohnnie', 'creepygirl', 'daytonregular', 'deneaneregular', 'detenteregular', 'digifit', 'distantgalaxy', 'dominicanregular', 'emmettregular', 'enlivenregular', 'ethnocentric', 'fingerpop', 'flubber', 'frankfurtervenetiantt', 'gazzarelli', 'geotypett', 'glockenspielregular', 'goodtimes', 'greekdinerinlinett', 'handmedownsbrk', 'hansenregular', 'harvestitalregular', 'harvestregular', 'haxtonlogostt', 'heavyheap', 'hollywoodhills', 'hombreregular', 'huxleytitling', 'induction', 'italianateregular', 'limousineregular', 'littlelordfontleroy', 'letteromatic', 'mael', 'manorlyregular', 'martinaregular', 'melodbold', 'minervaregular', 'moonbeamregular', 'mycalcregular', 'prceltic', 'nasalization', 'neonlights', 'notramregular', 'novemberregular', 'opineheavyregular', 'parryhotter', 'penultimatelightitalregular', 'penultimatelightregular', 'phrasticmediumregular', 'pirateregular', 'quiveritalregular', 'rolandregular', 'rondaloregular', 'rowdyheavyregular', 'russelwritett', 'salinaregular', 'sfmovieposter', 'skinnyregular', 'snowdrift', 'splashregular', 'stephenregular', 'steppestt', 'tarzanregular', 'terminatortwo', 'toledoregular', 'valkenregular', 'vivianregular', 'waverlyregular', 'whimsytt', 'woodcut', 'xfiles', 'yearsupplyoffairycakes', 'agencyfbполужирный', 'agencyfb', 'algerian', 'bookantiquaполужирный', 'bookantiquaполужирныйкурсив', 'bookantiquaкурсив', 'arialполужирный', 'arialполужирныйкурсив', 'arialкурсив', 'arialrounded', 'baskervilleoldface', 'bauhaus93', 'bell', 'bellполужирный', 'bellкурсив', 'bernardcondensed', 'bookantiqua', 'bodoniполужирный', 'bodoniполужирныйкурсив', 'bodoniblackкурсив', 'bodoniblack', 'bodonicondensedполужирный', 'bodonicondensedполужирныйкурсив', 'bodonicondensedкурсив', 'bodonicondensed', 'bodoniкурсив', 'bodonipostercompressed', 'bodoni', 'bookmanoldstyle', 'bookmanoldstyleполужирный', 'bookmanoldstyleполужирныйкурсив', 'bookmanoldstyleкурсив', 'bradleyhanditc', 'britannic', 'berlinsansfbполужирный', 'berlinsansfbdemiполужирный', 'berlinsansfb', 'broadway', 'brushscriptкурсив', 'bookshelfsymbol7', 'californianfbполужирный', 'californianfbкурсив', 'californianfb', 'calisto', 'calistoполужирный', 'calistoполужирныйкурсив', 'calistoкурсив', 'castellar', 'centuryschoolbook', 'centaur', 'century', 'chiller', 'colonna', 'cooperblack', 'copperplategothic', 'curlz', 'dubai', 'dubaimedium', 'dubairegular', 'elephant', 'elephantкурсив', 'engravers', 'erasitc', 'erasdemiitc', 'erasmediumitc', 'felixtitling', 'forte', 'franklingothicbook', 'franklingothicbookкурсив', 'franklingothicdemi', 'franklingothicdemicond', 'franklingothicdemiкурсив', 'franklingothicheavy', 'franklingothicheavyкурсив', 'franklingothicmediumcond', 'freestylescript', 'frenchscript', 'footlight', 'garamond', 'garamondполужирный', 'garamondкурсив', 'gigi', 'gillsansполужирныйкурсив', 'gillsansполужирный', 'gillsanscondensed', 'gillsansкурсив', 'gillsansultracondensed', 'gillsansultra', 'gillsans', 'gloucesterextracondensed', 'gillsansextcondensed', 'centurygothic', 'centurygothicполужирный', 'centurygothicполужирныйкурсив', 'centurygothicкурсив', 'goudyoldstyle', 'goudyoldstyleполужирный', 'goudyoldstyleкурсив', 'goudystout', 'harlowsolid', 'harrington', 'haettenschweiler', 'hightowertext', 'hightowertextкурсив', 'imprintshadow', 'informalroman', 'blackadderitc', 'edwardianscriptitc', 'kristenitc', 'jokerman', 'juiceitc', 'kunstlerscript', 'widelatin', 'lucidabright', 'lucidacalligraphy', 'leelawadee', 'leelawadeeполужирный', 'lucidafaxregular', 'lucidafax', 'lucidahandwriting', 'lucidasansregular', 'lucidasansroman', 'lucidasanstypewriterregular', 'lucidasanstypewriter', 'lucidasanstypewriteroblique', 'magnetoполужирный', 'maiandragd', 'maturascriptcapitals', 'mistral', 'modernno20', 'microsoftuighurполужирный', 'microsoftuighur', 'monotypecorsiva', 'extra', 'niagaraengraved', 'niagarasolid', 'ocraextended', 'oldenglishtext', 'onyx', 'msoutlook', 'palacescript', 'papyrus', 'parchment', 'perpetuaполужирныйкурсив', 'perpetuaполужирный', 'perpetuaкурсив', 'perpetuatitlingполужирный', 'perpetuatitling', 'perpetua', 'playbill', 'poorrichard', 'pristina', 'rage', 'ravie', 'msreferencesansserif', 'msreferencespecialty', 'rockwellcondensedполужирный', 'rockwellcondensed', 'rockwell', 'rockwellполужирный', 'rockwellполужирныйкурсив', 'rockwellextra', 'rockwellкурсив', 'centuryschoolbookполужирный', 'centuryschoolbookполужирныйкурсив', 'centuryschoolbookкурсив', 'script', 'showcardgothic', 'snapitc', 'stencil', 'twcenполужирныйкурсив', 'twcenполужирный', 'twcencondensedполужирный', 'twcencondensedextra', 'twcencondensed', 'twcenкурсив', 'twcen', 'tempussansitc', 'vinerhanditc', 'vivaldiкурсив', 'vladimirscript', 'wingdings2', 'wingdings3', 'zwadobef', 'adobedevanagariitalic', 'adobedevanagaribolditalic', 'adobedevanagaribold', 'adobedevanagariregular']
