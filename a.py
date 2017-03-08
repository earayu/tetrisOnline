import socketserver
import pygame, sys, random, time, re
from pygame.locals import *
import json
import socket
import selectors

HOST, PORT = "localhost", 9999

# 游戏基本设置
WIDTH = 16
HEIGHT = 28

BLOCK_SIZE = 15

WINDOW_WIDTH = WIDTH*BLOCK_SIZE
WINDOW_HEIGHT = HEIGHT*BLOCK_SIZE

FPS = 60

SPEED = [1,0.8,0.6,0.4,0.3,0.2,0.1]


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

    def __init__(self, width, height):
        self.width, self.height = width, height
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
        print(self.active_shape.y)

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

class Player():
    player_id = 0
    conn = None
    board = None
    score = 0

    def __init__(self, player_id, conn, board):
        self.player_id = player_id
        self.conn = conn
        self.board = board


class Game(object):
    game_id = 0
    # TODO 这些都要N个，支持N人同一局游戏
    # conn = None
    # board = None
    player = {}


    ticks = 0
    factor = 4
    frame_rate = 60.0
    is_paused = False
    starting_level = 1
    level = 1

    def __init__(self, starting_level=1):
        self.game_id = len(games)+1
        self.starting_level = int(starting_level)
        self.reset()

    def reset(self):
        self.level = self.starting_level

    def should_update(self):
        if self.is_paused:
            return False

        self.ticks += 1
        # level越高，刷新速度越快
        if self.ticks >= (self.frame_rate - (self.level * self.factor)):
            self.ticks = 0
            return True
        return False

    def send_info(self, conn):
        p = self.get_player(conn.fileno()) #TODO 直接传fd，而不是conn
        data = {
            "game_id":self.game_id,
            "player_id":p.player_id
        }
        conn.send(json.dumps(data).encode('utf-8'))

    # 添加一个玩家进入这局游戏
    def add_player(self, conn):
        # TODO 暂时把socket fd当作player_id, Board最后也要改掉
        player_id = conn.fileno()
        self.player[player_id] = Player(player_id, conn, Board(16,28))

    def get_player(self, player_id):
        return self.player[player_id]

    # 将游戏状态发送给同一局游戏中的所有玩家
    def show(self, player_id):
        dd = []
        # 遍历map
        for p in self.player.values():
            dd.append(
                {
                    "player_id":p.player_id,
                    "board": p.board.board,
                    "active_shape": p.board.active_shape.shape,
                    "x": p.board.active_shape.x,
                    "y": p.board.active_shape.y
                }
            )

        data = json.dumps(dd).encode('utf-8')
        for p in self.player.values():
            if p.player_id == player_id:
                p.conn.send(data)

    # 响应相应玩家的操作
    def up(self, player_id):
        self.player.get(player_id).board.move_piece(K_UP)

    def left(self, player_id):
        self.player.get(player_id).board.move_piece(K_LEFT)

    def right(self, player_id):
        self.player.get(player_id).board.move_piece(K_RIGHT)

    def down(self, player_id):
        self.player.get(player_id).board.move_piece(K_DOWN)



def accept(s, mask):
    conn,addr = s.accept()
    conn.setblocking(False)
    selector.register(conn, selectors.EVENT_READ, read)

    game = Game(1)
    game.add_player(conn)
    games[game.game_id] = game

    game.send_info(conn)


def read(conn, mask):
    raw_request_jsons = conn.recv(1024).decode("utf-8")
    print(raw_request_jsons)
    request_jsons = split_json(raw_request_jsons) #TODO 很奇怪，要改成一次只发送1个json吗
    for j in request_jsons:
        js = json.loads(j)

        game = games[int(js["game_id"])]
        player_id = int(js["player_id"])
        if js["opr"] == "show":
            game.show(player_id)
        if js["opr"] == "up":
            game.up(player_id)
        if js["opr"] == "left":
            game.left(player_id)
        if js["opr"] == "right":
            game.right(player_id)
        if js["opr"] == "down":
            game.down(player_id)

#TODO 垃圾实现
def split_json(str):
    l = []
    for e in str.split("}"):
        if e.startswith("{"):
            l.append(e+"}")
    return l


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(10)

selector = selectors.DefaultSelector()
selector.register(s, selectors.EVENT_READ, accept)

#TODO 同步问题
games = {}

while True:
    events = selector.select(SPEED[4])
    for key, mask in events:
        callback = key.data  # 掉accept函数
        callback(key.fileobj, mask)  # key.fileobj = 文件句柄 （相当于上个例子中检测的自己）

        for fd in games:
            game = games[fd]
            if game.should_update():
                for pid in game.player:
                    p = game.player[pid]
                    p.board.move_down()









