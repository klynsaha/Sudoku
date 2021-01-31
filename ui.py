import pygame
from sudoku_solver import solve, valid, find_empty
from boards import boards
import random
import time
pygame.font.init()

MAX_STRIKES = 5
winner = False


class Grid:
    def __init__(self, rows, cols, width, height):
        random.shuffle(boards)
        self.board = boards[random.randint(0, len(boards)-1)].copy()
        for i in range(random.randint(20, 27)):
            x = random.randint(0, 8)
            y = random.randint(0, 8)
            self.board[x][y] = 0
        self.rows = rows
        self.cols = cols
        self.squares = [[Box(self.board[i][j], i, j, width, height)
                         for j in range(cols)] for i in range(rows)]
        self.width = width
        self.height = height
        self.model = None
        self.selected = None

    def update_model(self):
        self.model = [[self.squares[i][j].value for j in range(
            self.cols)] for i in range(self.rows)]

    def place(self, val):
        row, col = self.selected
        if self.squares[row][col].value == 0:
            self.squares[row][col].set(val)
            self.update_model()

            if valid(self.model, val, (row, col)) and solve(self.model):
                self.squares[row][col].set_temp(0)
                return True
            else:
                self.squares[row][col].set(0)
                self.squares[row][col].set_temp(0)
                self.update_model()
                return False

    def sketch(self, val):
        row, col = self.selected
        self.squares[row][col].set_temp(val)

    def draw(self, win):
        # Draw Grid Lines
        gap = self.width / 9
        for i in range(self.rows+1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(win, (0, 0, 0), (0, i*gap),
                             (self.width, i*gap), thick)
            pygame.draw.line(win, (0, 0, 0), (i * gap, 0),
                             (i * gap, self.height), thick)

        # Draw squares
        for i in range(self.rows):
            for j in range(self.cols):
                self.squares[i][j].draw(win)

    def select(self, row, col):

        if(row in range(0, self.rows) and col in range(0, self.cols)):
            for i in range(self.rows):
                for j in range(self.cols):
                    self.squares[i][j].selected = False

            self.squares[row][col].selected = True
            self.selected = (row, col)

    def clear(self):
        row, col = self.selected
        if self.squares[row][col].value == 0:
            self.squares[row][col].set_temp(0)

    def click(self, pos):
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y), int(x))
        else:
            return None

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.squares[i][j].value == 0:
                    return False
        return True


class Box:
    rows = 9
    cols = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, (128, 128, 128))
            win.blit(text, (x+5, y+5))
        elif not(self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + (gap/2 - text.get_width()/2),
                            y + (gap/2 - text.get_height()/2)))

        if self.selected:
            if self.value == 0:
                pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)
            else:
                pygame.draw.rect(win, (0, 255, 0), (x, y, gap, gap), 3)
            if self.temp != 0:
                pygame.draw.rect(win, (0, 0, 255), (x, y, gap, gap), 3)

    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val


def redraw_window(win, board, time, strikes):
    win.fill((255, 255, 255))
    # Win or lose
    loseFont = pygame.font.SysFont("comicsans", 100)
    if(strikes == MAX_STRIKES):
        loseText = loseFont.render("You Lose!", 1, (255, 0, 0))
        win.blit(loseText, (540/2-160, 600/2-90))
    if(winner):
        loseText = loseFont.render("You Won!", 1, (0, 255, 0))
        win.blit(loseText, (540/2-160, 600/2-90))

    # Draw time
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (0, 0, 0))
    win.blit(text, (540 - 160, 560))
    # Draw Strikes
    text = fnt.render("X " * strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    # Draw grid and board
    board.draw(win)


def format_time(secs):
    sec = secs % 60
    minute = secs//60
    hour = minute//60

    mat = " " + str(minute) + ":" + str(sec)
    return mat


if __name__ == "__main__":
    board = Grid(9, 9, 540, 540)
    i, j = find_empty(board.board)
    board.select(i, j)
    key = None
    run = True
    start = time.time()
    strikes = 0

    win = pygame.display.set_mode((540, 600))
    pygame.display.set_caption("Sudoku")

    pause = False
    while run:
        play_time = round(time.time() - start)

        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pause = False
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pause = False
                        board = Grid(9, 9, 540, 540)
                        i, j = find_empty(board.board)
                        board.select(i, j)
                        key = None
                        run = True
                        start = time.time()
                        strikes = 0
                        winner = False
            pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                # Move keys
                if event.key in [pygame.K_LEFT, pygame.K_a]:
                    i, j = board.selected
                    board.select(i, j-1)
                    key = None
                if event.key == [pygame.K_RIGHT, pygame.K_d]:
                    i, j = board.selected
                    board.select(i, j+1)
                    key = None
                if event.key == [pygame.K_UP, pygame.K_w]:
                    i, j = board.selected
                    board.select(i-1, j)
                    key = None
                if event.key == [pygame.K_DOWN, pygame.K_s]:
                    i, j = board.selected
                    board.select(i+1, j)
                    key = None
                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None
                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.squares[i][j].temp != 0:
                        if not board.place(board.squares[i][j].temp):
                            strikes += 1
                        key = None
                        if board.is_finished():
                            winner = True
                            pause = True
                # New Game
                if event.key == pygame.K_r:
                    pause = False
                    board = Grid(9, 9, 540, 540)
                    i, j = find_empty(board.board)
                    board.select(i, j)
                    key = None
                    run = True
                    start = time.time()
                    strikes = 0
                    winner = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key != None:
            board.sketch(key)
        if strikes == MAX_STRIKES or winner:
            pause = True

        redraw_window(win, board, play_time, strikes)
        pygame.display.update()

    pygame.quit()
