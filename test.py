from PyQt5 import QtCore, QtGui, QtWidgets
import pyautogui
import copy
import numpy as np
import cv2
import datetime
import math
import time

win = pyautogui.getWindowsWithTitle("BlueStacks")[0]
win.moveTo(1500, 130)
win.resizeTo(700, 1176)

# for screenshot:
center_x, center_y = win.centerx, win.centery
left = center_x - 335
up = center_y - 99
width = 612
height = 612
squareSize = 88
top_left_x = left + squareSize // 2
top_left_y = up + squareSize // 2

# colors:

# base colors templates:
red = cv2.imread('assets/general/red.png', 0)
green = cv2.imread('assets/general/green.png', 0)
yellow = cv2.imread('assets/general/yellow.png', 0)
purple = cv2.imread('assets/general/purple.png', 0)
blue = cv2.imread('assets/general/blue.png', 0)
orange = cv2.imread('assets/general/orange.png', 0)

color_templates = [blue, green, yellow, purple, red, orange]

# special templates:
horizonal_purple_arrow = cv2.imread('assets/general/horizonal_purple_arrow.png', 0)
vertical_blue_arrow = cv2.imread('assets/general/vertical_blue_arrow.png', 0)
green_bomb = cv2.imread('assets/general/green_bomb.png', 0)
green_lightning = cv2.imread('assets/general/green_lightning.png', 0)

special_templates = [
    horizonal_purple_arrow,
    vertical_blue_arrow,
    green_bomb,
    green_lightning
]

# modes templates:
# bounty mode
bounty = cv2.imread('assets/modes/bounty/bounty.png', 0)

# leafs mode
leaf = cv2.imread('assets/modes/leafs/leaf.png', 0)

# purple gem mode
purple_gem_4 = cv2.imread('assets/modes/purple_gem/purple_gem_4.png', 0)
purple_gem_5 = cv2.imread('assets/modes/purple_gem/purple_gem_5.png', 0)

# red and blue mode
red_blue = cv2.imread('assets/modes/red_blue/red_blue.png', 0)

# chest mode
chest = cv2.imread('assets/modes/chest/chest.png', 0)
chest2 = cv2.imread('assets/modes/chest/chest2.png', 0)


# frozen mode
frozen_horizonal_red_arrow = cv2.imread('assets/modes/frozen/frozen_horizonal_red_arrow.png', 0)
frozen_vertical_purple_arrow = cv2.imread('assets/modes/frozen/frozen_vertical_purple_arrow.png', 0)
frozen_blue_bomb = cv2.imread('assets/modes/frozen/frozen_blue_bomb.png', 0)
frozen_red_lightning = cv2.imread('assets/modes/frozen/frozen_red_lightning.png', 0)

# fireworks mode
left_firework = cv2.imread('assets/modes/fireworks/left_firework.png', 0)
right_firework = cv2.imread('assets/modes/fireworks/right_firework.png', 0)
down_firework = cv2.imread('assets/modes/fireworks/down_firework.png', 0)
up_firework = cv2.imread('assets/modes/fireworks/up_firework.png', 0)

frozen_mode_templates = [
                     frozen_horizonal_red_arrow,
                     frozen_vertical_purple_arrow,
                     frozen_blue_bomb,
                     frozen_red_lightning,
                     ]

firework_mode_templates = [
                     left_firework,
                     right_firework,
                     up_firework,
                     down_firework
                     ]


colors = [(0, 151, 224), (42, 214, 44), (255, 239, 16), (201, 106, 251), (251, 46, 76), (255, 138, 44)]
firework_color = [(0, 151, 224), (25, 187, 26), (255, 241, 91), (209, 110, 248), (251, 46, 76), (255, 104, 28)]
board_length = 7
color_acc = 10
min_detect_range = 2  # min square size for check color in square
max_detect_range = 30  # max square size for check color in square
pixel_color_detect_range = 60  # color percision

# combos:
special_color = 1
special_color_three_score = 2.5
three_score = 1

color_dict = {
    1: "blue",
    2: "green",
    3: "yellow",
    4: "purple",
    5: "red",
    6: "orange"
}


def square_color_detect(im, x, y, fireworks=False):
    for curr_range in range(min_detect_range, max_detect_range, 4):
        color_count = [0, 0, 0, 0, 0, 0]
        curr_left = x - curr_range // 2
        curr_top = y - curr_range // 2
        for i in range(curr_range):
            for j in range(curr_range):
                pixel = im.getpixel((int(curr_left + i), int(curr_top + j)))
                if not fireworks:
                    curr_pixel = pixel_color_detect(pixel)
                else:
                    curr_pixel = pixel_color_detect(pixel, True)
                if curr_pixel != -1:
                    color_count[curr_pixel] += 1
        max_count = max(color_count)
        if max_count != 0:
            return color_count.index(max_count) + 1
    return 0


def pixel_color_detect(pixel, fireworks=False):
    r = pixel[0]
    g = pixel[1]
    b = pixel[2]
    curr_colors = firework_color if fireworks else colors
    for i in range(len(curr_colors)):
        curr_color = curr_colors[i]
        if math.sqrt((curr_color[0] - r) ** 2 + (curr_color[1] - g) ** 2 + (curr_color[2] - b) ** 2) < pixel_color_detect_range:
            return i
    return -1


def create_board():
    return [[0 for i in range(board_length)] for j in range(board_length)]


# scans screen and updates board
def update_board(board, special_board):
    curr_time = str(datetime.datetime.now())[:19].replace(':', '_')  # DEBUG
    im = pyautogui.screenshot(("Debug/" + curr_time + ".png"), region=(left, up, width, height))  # DEBUG
    for i in range(board_length):
        for j in range(board_length):
            x = j * squareSize + squareSize // 2
            y = i * squareSize + squareSize // 2
            # board[i][j] = estimate_each_color(im.getpixel((x, y)))
            board[i][j] = square_color_detect(im, x, y)
            special_board[i][j] = estimate_special_color(im, x, y)
    return board, special_board


def get_board_locations(locations):
    board = create_board()
    for pt in zip(*locations[::-1]):
        i = (pt[1] + squareSize // 2) // squareSize
        j = (pt[0] + squareSize // 2) // squareSize
        board[i][j] = 1
    return board


def update_board_2(board, special_board):
    curr_time = str(datetime.datetime.now())[:19].replace(':', '_')  # DEBUG
    img_color = pyautogui.screenshot(("Debug/" + curr_time + ".png"), region=(left, up, width, height))  # DEBUG
    img_gray = cv2.cvtColor(np.array(img_color), cv2.COLOR_RGB2GRAY)

    curr_time = datetime.datetime.now()

    for index in range(len(color_templates)):
        res = cv2.matchTemplate(img_gray, color_templates[index], cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            i = (pt[1] + squareSize // 2) // squareSize
            j = (pt[0] + squareSize // 2) // squareSize
            board[i][j] = index + 1

    if check_fill(board):
        return board, special_board


    for index in range(len(special_templates)):
        res = cv2.matchTemplate(img_gray, special_templates[index], cv2.TM_CCOEFF_NORMED)
        threshold = 0.75
        loc = np.where(res >= threshold)
        board_locations = get_board_locations(loc)
        for i in range(board_length):
            for j in range(board_length):
                if board_locations[i][j] == 1:
                    if board[i][j] == 0:
                        x = j * squareSize + squareSize // 2
                        y = i * squareSize + squareSize // 2
                        board[i][j] = square_color_detect(img_color,  x, y)
                        special_board[i][j] = index + 1

    if check_fill(board):
        return board, special_board

    print("Base shapes time: ", datetime.datetime.now() - curr_time)
    curr_time = datetime.datetime.now()

    if curr_mode == "Fireworks Mode":
        for index in range(len(firework_mode_templates)):
            w, h = firework_mode_templates[index].shape[::-1]
            res = cv2.matchTemplate(img_gray, firework_mode_templates[index], cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            loc = np.where(res >= threshold)
            board_locations = get_board_locations(loc)
            for i in range(board_length):
                for j in range(board_length):
                    if board_locations[i][j] == 1:
                        x = j * squareSize + squareSize // 2
                        y = i * squareSize + squareSize // 2
                        board[i][j] = square_color_detect(img_color, x, y, True)
                        special_board[i][j] = index + 5

    elif curr_mode == "Frozen Mode":
        for index in range(len(frozen_mode_templates)):
            res = cv2.matchTemplate(img_gray, frozen_mode_templates[index], cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            loc = np.where(res >= threshold)
            board_locations = get_board_locations(loc)
            for i in range(board_length):
                for j in range(board_length):
                    if board_locations[i][j] == 1:
                        x = j * squareSize + squareSize // 2
                        y = i * squareSize + squareSize // 2
                        board[i][j] = square_color_detect(img_color, x, y)
                        special_board[i][j] = index + 5

    elif curr_mode == "Chest Mode":
        w, h = chest.shape[::-1]
        res = cv2.matchTemplate(img_gray, chest, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            i = (pt[1] + squareSize // 2) // squareSize
            j = (pt[0] + squareSize // 2) // squareSize
            board[i][j] = 7
            special_board[i][j] = 9

    elif curr_mode == "Red and Blue Mode":
        w, h = red_blue.shape[::-1]
        res = cv2.matchTemplate(img_gray, red_blue, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            i = (pt[1] + squareSize // 2) // squareSize
            j = (pt[0] + squareSize // 2) // squareSize
            board[i][j] = 1

    elif curr_mode == "Purple Gem Mode":
        w, h = purple_gem_4.shape[::-1]
        res = cv2.matchTemplate(img_gray, purple_gem_4, cv2.TM_CCOEFF_NORMED)
        threshold = 0.7
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            i = (pt[1] + squareSize // 2) // squareSize
            j = (pt[0] + squareSize // 2) // squareSize
            board[i][j] = 4
            special_board[i][j] = 9

    elif curr_mode == "Green Leaf Mode":
        w, h = leaf.shape[::-1]
        res = cv2.matchTemplate(img_gray, leaf, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            i = (pt[1] + squareSize // 2) // squareSize
            j = (pt[0] + squareSize // 2) // squareSize
            board[i][j] = 2
            special_board[i][j] = 9

    elif curr_mode == "Bounty Mode":
        w, h = bounty.shape[::-1]
        res = cv2.matchTemplate(img_gray, bounty, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            i = (pt[1] + squareSize // 2) // squareSize
            j = (pt[0] + squareSize // 2) // squareSize
            board[i][j] = 6
            special_board[i][j] = 9

    if check_fill(board):
        return board, special_board

    print("Mode time: ", datetime.datetime.now() - curr_time)
    curr_time = datetime.datetime.now()

    for i in range(board_length):
        for j in range(board_length):
            if board[i][j] == 0:
                board[i][j] = square_color_detect(img_color, j * squareSize + squareSize // 2, i * squareSize + squareSize // 2)
    print("color detection time: ", datetime.datetime.now() - curr_time)

    return board, special_board


def check_fill(board):
    for i in range(board_length):
        for j in range(board_length):
            if board[i][j] == 0:
                return False
    return True


def estimate_special_color(im, x, y):
    if sum(im.getpixel((x - 15, y))) < 200:
        return 1
    elif sum(im.getpixel((x, y - 15))) < 200:
        return 2
    elif sum(im.getpixel((x - 10, y - 10))) > 650:
        return 3
    else:
        return 0


# exchanges each square to four directions and checks the best
def check_best_exchange(board, special_board):
    highest_score = 0
    highest_score_spot = (0, 0)
    highest_score_dir = "up"
    for i in range(board_length):
        for j in range(board_length):
            score_up, score_down, score_left, score_right = 0, 0, 0, 0
            if i > 0:
                boards = exchange_boards(board, special_board, i, j, "up")
                score_up = check_board_score(boards[0], boards[1])
            if i < board_length - 1:
                boards = exchange_boards(board, special_board, i, j, "down")
                score_down = check_board_score(boards[0], boards[1])
            if j > 0:
                boards = exchange_boards(board, special_board, i, j, "left")
                score_left = check_board_score(boards[0], boards[1])
            if j < board_length - 1:
                boards = exchange_boards(board, special_board, i, j, "right")
                score_right = check_board_score(boards[0], boards[1])
            curr_high_score = max(score_up, score_down, score_left, score_right)
            if curr_high_score >= highest_score:
                highest_score, highest_score_dir = check_best_direction(score_up, score_down, score_left, score_right)
                highest_score_spot = (i, j)
    return (highest_score, highest_score_spot, highest_score_dir)


def exchange_boards(board, special_board, i, j, direction):
    if direction == "up":
        exchange_board = copy.deepcopy(board)
        temp = exchange_board[i][j]
        exchange_board[i][j] = exchange_board[i - 1][j]
        exchange_board[i - 1][j] = temp
        exchange_special_board = copy.deepcopy(special_board)
        temp = exchange_special_board[i][j]
        exchange_special_board[i][j] = exchange_special_board[i - 1][j]
        exchange_special_board[i - 1][j] = temp
    elif direction == "down":
        exchange_board = copy.deepcopy(board)
        temp = exchange_board[i][j]
        exchange_board[i][j] = exchange_board[i + 1][j]
        exchange_board[i + 1][j] = temp
        exchange_special_board = copy.deepcopy(special_board)
        temp = exchange_special_board[i][j]
        exchange_special_board[i][j] = exchange_special_board[i + 1][j]
        exchange_special_board[i + 1][j] = temp
    elif direction == "left":
        exchange_board = copy.deepcopy(board)
        temp = exchange_board[i][j]
        exchange_board[i][j] = exchange_board[i][j - 1]
        exchange_board[i][j - 1] = temp
        exchange_special_board = copy.deepcopy(special_board)
        temp = exchange_special_board[i][j]
        exchange_special_board[i][j] = exchange_special_board[i][j - 1]
        exchange_special_board[i][j - 1] = temp
    else:  # right
        exchange_board = copy.deepcopy(board)
        temp = exchange_board[i][j]
        exchange_board[i][j] = exchange_board[i][j + 1]
        exchange_board[i][j + 1] = temp
        exchange_special_board = copy.deepcopy(special_board)
        temp = exchange_special_board[i][j]
        exchange_special_board[i][j] = exchange_special_board[i][j + 1]
        exchange_special_board[i][j + 1] = temp
    return exchange_board, exchange_special_board


# checks highest direction score
def check_best_direction(score_up, score_down, score_left, score_right):
    if score_up >= score_down and score_up >= score_left and score_up >= score_right:
        return score_up, "up"
    if score_down >= score_up and score_down >= score_left and score_down >= score_right:
        return score_down, "down"
    if score_left >= score_up and score_left >= score_down and score_left >= score_right:
        return score_left, "left"
    if score_right >= score_up and score_right >= score_down and score_right >= score_left:
        return score_right, "right"


# checks score after exchange
# Possible matches: three - 1, four - 5, L - 7, T - 7, cross - 7, five - 12
def check_board_score(board, special_board):
    score = 0
    not_special = True
    match = False
    # horizonal:
    for i in range(board_length):
        for j in range(board_length - 2):
            if board[i][j] == board[i][j + 1] == board[i][j + 2] and board[i][j] != 0:
                match = True
                horizonal_special_score = is_special_horizonal(board, special_board, (i, j))
                if horizonal_special_score >= 5:
                    not_special = False
                    score += horizonal_special_score
                if horizonal_special_score < 5:
                    if board[i][j] == 1:
                        score += special_color_three_score
                    else:
                        score += three_score
                    explode_line(board, i, j, "horizonal")
    # vertical:
    for i in range(board_length - 2):
        for j in range(board_length):
            if board[i][j] == board[i + 1][j] == board[i + 2][j] and board[i][j] != 0:
                match = True
                vertical_special_score = is_special_vertical(board, special_board, (i, j))
                if vertical_special_score >= 5:
                    not_special = False
                    score += vertical_special_score
                if vertical_special_score < 5:
                    if board[i][j] == 1:
                        score += special_color_three_score
                    else:
                        score += three_score
                    explode_line(board, i, j, "vertical")
    if not_special and match:
        board, special_board = drop_boards(board, special_board)
        score += check_board_score(board, special_board)
    return score


# Possible matches: three - 1, four - 5, L - 7, T - 7, cross - 7, five - 12
def is_special_horizonal(board, special_board, left_c):
    blue_bonus = board[left_c[0]][left_c[1]] == 1
    special_score = 0
    if 1 <= special_board[left_c[0]][left_c[1]] <= 4 or 1 <= special_board[left_c[0]][left_c[1] + 1] <= 4 or 1 <= \
            special_board[left_c[0]][left_c[1] + 2] <= 4:
        special_score += 5
    for j in range(left_c[1], left_c[1] + 3):
        if left_c[0] > 1:
            if board[left_c[0] - 2][j] == board[left_c[0] - 1][j] == board[left_c[0]][j]:
                return 20 + special_score if blue_bonus else 12 + special_score
        if 0 < left_c[0] < 6:
            if board[left_c[0] - 1][j] == board[left_c[0]][j] == board[left_c[0] + 1][j]:
                return 20 + special_score if blue_bonus else 12 + special_score
        if left_c[0] < 5:
            if board[left_c[0]][j] == board[left_c[0] + 1][j] == board[left_c[0] + 2][j]:
                return 20 + special_score if blue_bonus else 12 + special_score
    if 0 < left_c[1] < 4:
        if board[left_c[0]][left_c[1] - 1] == board[left_c[0]][left_c[1]] == board[left_c[0]][left_c[1] + 3]:
            return 30 + special_score if blue_bonus else 22 + special_score
    if left_c[1] > 0:
        if board[left_c[0]][left_c[1] - 1] == board[left_c[0]][left_c[1]]:
            return 15 + special_score if blue_bonus else 10 + special_score
    if left_c[1] + 3 <= 6:
        if board[left_c[0]][left_c[1]] == board[left_c[0]][left_c[1] + 3]:
            return 15 + special_score if blue_bonus else 10 + special_score
    return special_score


def is_special_vertical(board, special_board, top_c):
    blue_bonus = board[top_c[0]][top_c[1]] == 1
    special_score = 0
    if 0 < special_board[top_c[0]][top_c[1]] <= 3 or 0 < special_board[top_c[0] + 1][top_c[1]] <= 3 or 0 < special_board[top_c[0] + 2][top_c[1]] <= 3:
        special_score += 5
    for i in range(top_c[0], top_c[0] + 3):
        if top_c[1] > 1:
            if board[i][top_c[1] - 2] == board[i][top_c[1] - 1] == board[i][top_c[1]]:
                return 20 + special_score if blue_bonus else 12 + special_score
        if 0 < top_c[1] < 6:
            if board[i][top_c[1] - 1] == board[i][top_c[1]] == board[i][top_c[1] + 1]:
                return 20 + special_score if blue_bonus else 12 + special_score
        if top_c[1] < 5:
            if board[i][top_c[1]] == board[i][top_c[1] + 1] == board[i][top_c[1] + 2]:
                return 20 + special_score if blue_bonus else 12 + special_score
    if 0 < top_c[0] < 4:
        if board[top_c[0] - 1][top_c[1]] == board[top_c[0]][top_c[1]] == board[top_c[0] + 3][top_c[1]]:
            return 30 + special_score if blue_bonus else 22 + special_score
    if top_c[0] > 0:
        if board[top_c[0] - 1][top_c[1]] == board[top_c[0]][top_c[1]]:
            return 15 + special_score if blue_bonus else 10 + special_score
    if top_c[0] + 3 <= 6:
        if board[top_c[0]][top_c[1]] == board[top_c[0] + 3][top_c[1]]:
            return 15 + special_score if blue_bonus else 10 + special_score
    return special_score


# try
def explode_line(board, i, j, direction):
    if direction == "horizonal":
        board[i][j] = 0
        board[i][j + 1] = 0
        board[i][j + 2] = 0
    if direction == "vertical":
        board[i][j] = 0
        board[i + 1][j] = 0
        board[i + 2][j] = 0


def drop_boards(board, special_board):
    board = np.rot90(board)
    board = board.tolist()
    for i in range(board_length):
        for j in range(board_length):
            if board[i][j] == 0:
                board[i].insert(0, board[i].pop(j))
                special_board[i].insert(0, special_board[i].pop(j))
    board = np.rot90(board, 3)
    board = board.tolist()
    return board, special_board


def swipe(direction):
    if direction == "left":
        pyautogui.drag(-40, 0, 0.2, button='left')
    if direction == "right":
        pyautogui.drag(40, 0, 0.2, button='left')
    if direction == "up":
        pyautogui.drag(0, -40, 0.2, button='left')
    if direction == "down":
        pyautogui.drag(0, 40, 0.2, button='left')

curr_mode = "Fireworks Mode"

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(457, 402)
        MainWindow.setAutoFillBackground(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.ModeBox = QtWidgets.QComboBox(self.centralwidget)
        self.ModeBox.setGeometry(QtCore.QRect(140, 20, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ModeBox.setFont(font)
        self.ModeBox.setObjectName("ModeBox")
        self.ModeBox.addItem("")
        self.ModeBox.addItem("")
        self.ModeBox.addItem("")
        self.ModeBox.addItem("")
        self.ModeBox.addItem("")
        self.ModeBox.addItem("")
        self.ModeBox.addItem("")
        self.ModeBox.addItem("")
        self.ActiveButton = QtWidgets.QToolButton(self.centralwidget)
        self.ActiveButton.setGeometry(QtCore.QRect(120, 280, 201, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.ActiveButton.setFont(font)
        self.ActiveButton.setObjectName("ActiveButton")
        self.BestMove = QtWidgets.QLabel(self.centralwidget)
        self.BestMove.setGeometry(QtCore.QRect(10, 80, 311, 51))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.BestMove.setFont(font)
        self.BestMove.setObjectName("BestMove")
        self.Score = QtWidgets.QLabel(self.centralwidget)
        self.Score.setGeometry(QtCore.QRect(80, 130, 211, 51))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.Score.setFont(font)
        self.Score.setObjectName("Score")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 457, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.ActiveButton.clicked.connect(self.button_clicked)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.ModeBox.setItemText(0, _translate("MainWindow", "Fireworks Mode"))
        self.ModeBox.setItemText(1, _translate("MainWindow", "Frozen Mode"))
        self.ModeBox.setItemText(2, _translate("MainWindow", "Chest Mode"))
        self.ModeBox.setItemText(3, _translate("MainWindow", "Red and Blue Mode"))
        self.ModeBox.setItemText(4, _translate("MainWindow", "Purple Gem Mode"))
        self.ModeBox.setItemText(5, _translate("MainWindow", "Green Leaf Mode"))
        self.ModeBox.setItemText(6, _translate("MainWindow", "Bounty Mode"))
        self.ModeBox.setItemText(7, _translate("MainWindow", "None"))
        self.ActiveButton.setText(_translate("MainWindow", "Check Best Move"))
        self.BestMove.setText(_translate("MainWindow", "Best Move:"))
        self.Score.setText(_translate("MainWindow", "Score: "))

    def button_clicked(self, MainWindow):
        self.check_best_move()

    def check_best_move(self):
        global curr_mode
        curr_mode = self.ModeBox.currentText()
        game_board = create_board()
        special_game_board = create_board()
        game_board, special_game_board = update_board_2(game_board, special_game_board)
        best_move = check_best_exchange(game_board, special_game_board)

        self.BestMove.setText("Best Move: " + str(best_move[1]) + ", " + str(best_move[2]))
        self.Score.setText("Score: " + str(best_move[0]))

        for line in game_board:
            print(line)
        print()
        for line in special_game_board:
            print(line)
        print()
        print(best_move)

        pyautogui.moveTo(top_left_x + squareSize * best_move[1][1], top_left_y + squareSize * best_move[1][0])
        if best_move[0] > 15:
            swipe(best_move[2])


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
