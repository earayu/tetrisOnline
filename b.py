import socket
import pygame, sys, random, time
from pygame.locals import *
import json


# 游戏基本设置
WIDTH = 16
HEIGHT = 28

BLOCK_SIZE = 15

WINDOW_WIDTH = WIDTH*BLOCK_SIZE
WINDOW_HEIGHT = HEIGHT*BLOCK_SIZE

FPS = 60




# 颜色
WHITE = (255,255,255)
RED = (255,0,0)


class Shape(object):
    _shapes = [
        [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]],
        [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]],
        [[0, 0, 0, 0], [0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0]],
        [[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 1, 1, 0]],
        [[0, 0, 0, 0], [0, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 0]],
        [[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0]],]

    def __init__(self, x=0, y=0):
        self.shape = random.choice(self._shapes)
        self.shape = self.copy_shape()

        for i in range(random.choice(range(4))):
            self.rotate()

        self.x = x
        self.y = y

    def copy_shape(self):
        new_shape = []
        for row in self.shape:
            new_shape.append(row[:])
        return new_shape

    def clone(self):
        cloned = Shape()
        cloned.shape = self.copy_shape()
        cloned.x = self.x
        cloned.y = self.y
        return cloned

    def rotate(self):
        new_shape = self.copy_shape()
        for j in range(0, 4):
            for i in range(0, 4):
                new_shape[i][j] = self.shape[4 - j - 1][i]
        self.shape = new_shape

    @property
    def left_edge(self):
        for x in range(0, 4):
            for y in range(0, 4):
                if self.shape[y][x] == 1:
                    return x

    @property
    def right_edge(self):
        for x in range(3, -1, -1):
            for y in range(0, 4):
                if self.shape[y][x] == 1:
                    return x

    @property
    def bottom_edge(self):
        for y in range(3, -1, -1):
            for x in range(0, 4):
                if self.shape[y][x] == 1:
                    return y


class Board():
    active_shape = None
    pending_shape = None
    board = None

    def __init__(self, width, height, block):
        self.width, self.height = width, height
        self.block = block
        self.calculated_height = self.height * BLOCK_SIZE
        self.calculated_width = self.width * BLOCK_SIZE
        self.reset()

    # 初始化窗口为全部空白
    def reset(self):
        self.board = []
        for row in range(self.height):
            self.board.append([0] * self.width)

        self.pending_shape = Shape()
        self.add_shape()

    def add_shape(self):
        self.active_shape = self.pending_shape.clone()
        self.active_shape.x = self.width // 2 - self.active_shape.left_edge
        self.active_shape.y = -1
        self.pending_shape = Shape()

        if self.is_collision():
            self.reset()
            #TODO 输了
            # self.dispatch_event('on_game_over')

    # 旋转方块，S和Z形方块好像有点问题，旋转位置不对。需要碰撞检测，查看能否旋转
    def rotate_shape(self):
        rotated_shape = self.active_shape.clone()
        rotated_shape.rotate()

        if rotated_shape.left_edge + rotated_shape.x < 0:
            rotated_shape.x = -rotated_shape.left_edge
        elif rotated_shape.right_edge + rotated_shape.x >= self.width:
            rotated_shape.x = self.width - rotated_shape.right_edge - 1

        if rotated_shape.bottom_edge + rotated_shape.y > self.height:
            return False

        if not self.is_collision(rotated_shape):
            self.active_shape = rotated_shape

    def move_left(self):
        self.active_shape.x -= 1
        if self.out_of_bounds() or self.is_collision():
            self.active_shape.x += 1
            return False
        return True

    def move_right(self):
        self.active_shape.x += 1
        if self.out_of_bounds() or self.is_collision():
            self.active_shape.x -= 1
            return False
        return True

    def move_down(self):
        self.active_shape.y += 1

        if self.check_bottom() or self.is_collision():
            self.active_shape.y -= 1
            # 着陆
            self.shape_to_board()
            self.add_shape()
            return False
        return True

    #查看是否出界
    def out_of_bounds(self, shape=None):
        shape = shape or self.active_shape
        if shape.x + shape.left_edge < 0:
            return True
        elif shape.x + shape.right_edge >= self.width:
            return True
        return False

    def check_bottom(self, shape=None):
        shape = shape or self.active_shape
        # TODO 检查一下这个方法
        if shape.y + shape.bottom_edge + 1 >= self.height:
            return True
        return False

    # 碰撞检测，不计算边界
    def is_collision(self, shape=None):
        shape = shape or self.active_shape
        for y in range(4):
            for x in range(4):
                if y + shape.y < 0:
                    continue
                if shape.shape[y][x] and self.board[y + shape.y][x + shape.x]:
                    return True
        return False

    #
    def test_for_line(self):
        for y in range(self.height - 1, -1, -1):
            counter = 0
            for x in range(self.width):
                if self.board[y][x] == 1:
                    counter += 1
            if counter == self.width:
                self.process_line(y)
                return True
        return False

    def process_line(self, y_to_remove):
        for y in range(y_to_remove - 1, -1, -1):
            for x in range(self.width):
                self.board[y + 1][x] = self.board[y][x]

    def shape_to_board(self):
        # transpose onto board
        # while test for line, process & increase score
        for y in range(4):
            for x in range(4):
                dx = x + self.active_shape.x
                dy = y + self.active_shape.y
                if self.active_shape.shape[y][x] == 1:
                    self.board[dy][dx] = 1

        lines_found = 0
        while self.test_for_line():
            lines_found += 1

        # TODO 计分
        # if lines_found:
        #     self.dispatch_event('on_lines', lines_found)

    def move_piece(self, motion_state):
        if motion_state == K_LEFT:
            self.move_left()
        elif motion_state == K_RIGHT:
            self.move_right()
        elif motion_state == K_UP:
            self.rotate_shape()
        elif motion_state == K_DOWN:
            self.move_down()
        elif motion_state == K_d:
            self.move_right()
        elif motion_state == K_w:
            self.rotate_shape()
        elif motion_state == K_s:
            self.move_down()
        elif motion_state == K_a:
            self.move_left()

    def draw_game_board(self):
        bsurface = pygame.Surface((WINDOW_WIDTH,WINDOW_HEIGHT))

        for y, row in enumerate(self.board):
            for x, col in enumerate(row):
                if col == 1 or col == 1:
                    self.draw_block(bsurface, x, y)

        for y in range(4):
            for x in range(4):
                dx = x + self.active_shape.x
                dy = y + self.active_shape.y
                if self.active_shape.shape[y][x] == 1:
                    self.draw_block(bsurface, dx, dy)

        return bsurface


    def draw_block(self, surface, x, y):
        y += 1  # since calculated_height does not account for 0-based index
        # self.block.blit(x * WINDOW_WIDTH, self.calculated_height - y * WINDOW_HEIGHT)
        rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE,BLOCK_SIZE)
        pygame.draw.rect(surface,RED,rect)


class Game(object):
    ticks = 0
    factor = 4
    frame_rate = 60.0

    is_paused = False

    def __init__(self, window_ref, board, starting_level=1):
        self.window_ref = window_ref
        self.board = board
        self.starting_level = int(starting_level)
        # self.register_callbacks()
        self.reset()

    def register_callbacks(self):
        self.board.push_handlers(self)

    def reset(self):
        self.level = self.starting_level
        self.lines = 0
        self.score = 0

    def should_update(self):
        if self.is_paused:
            return False

        self.ticks += 1
        # level越高，刷新速度越快
        if self.ticks >= (self.frame_rate - (self.level * self.factor)):
            self.ticks = 0
            return True
        return False

    # 我自定义的方法
    def draw(self,x,y):
        BSURFACE = self.board.draw_game_board()
        SURFACE.blit(BSURFACE,(x,y))


def terminate():
    pygame.quit()
    sys.exit()


HOST, PORT = "localhost", 9999

show_str = """{
	"game_id":"0",
	"player_id":"0",
	"opr":""
}"""

bb = Board(16,28,None)
dd = {}
dd["board"] = bb.board
dd["active_shape"] = bb.active_shape


def get_board(sock):
    sock.sendall(bytes(show_str, 'utf-8'))
    raw_recv_data = sock.recv(40240)
    print(raw_recv_data)
    recv_data = json.loads(str(raw_recv_data, 'utf-8'))
    board.board = recv_data["board"]
    board.active_shape.shape = recv_data["active_shape"]
    # board.pending_shape.shape = recv_data["pending_shape"]
    board.active_shape.x = recv_data["x"]
    board.active_shape.y = recv_data["y"]


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))

    pygame.init()
    SURFACE = pygame.display.set_mode((WINDOW_WIDTH*2+50,WINDOW_HEIGHT))
    SURFACE.fill(WHITE)
    pygame.display.set_caption("俄罗斯方块")
    fpsClock = pygame.time.Clock()

    board = Board(WIDTH,HEIGHT,None)
    game = Game(SURFACE, board, 1)

    board2 = Board(WIDTH,HEIGHT,None)
    game2 = Game(SURFACE, board2, 1)

    key_dir = None
    frameCount = 0

    while True:
        get_board(sock)
        frameCount += 1
        for event in pygame.event.get():
            key_dir = None
            if event.type == QUIT:
                terminate()

            pressed_keys = pygame.key.get_pressed()

            if event.type == KEYDOWN:
                if event.key == K_UP:
                    sock.sendall(bytes('{"opr":"up"}', 'utf-8'))
                if event.key == K_w:
                    board2.move_piece(K_UP)

            if pressed_keys[K_LEFT]:
                key_dir = K_LEFT
            if pressed_keys[K_a]:
                key_dir2 = K_a
            if pressed_keys[K_RIGHT]:
                key_dir = K_RIGHT
            if pressed_keys[K_d]:
                key_dir2 = K_d
            if pressed_keys[K_DOWN]:
                key_dir = K_DOWN
            if pressed_keys[K_s]:
                key_dir2 = K_s

        if key_dir in [K_LEFT,K_RIGHT,K_DOWN] and frameCount > 4:
            frameCount = 0
            # board.move_piece(key_dir)
            if key_dir == K_LEFT:
                sock.sendall(bytes('{"opr":"left"}', 'utf-8'))
            if key_dir == K_RIGHT:
                sock.sendall(bytes('{"opr":"right"}', 'utf-8'))
            if key_dir == K_DOWN:
                sock.sendall(bytes('{"opr":"down"}', 'utf-8'))


        game.draw(0,0)
        game2.draw(280,0)


        # 渲染一帧
        pygame.display.update()

        fpsClock.tick(FPS)


