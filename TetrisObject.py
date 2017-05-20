import random, pygame, json, time, sys
from pygame.locals import *
from enum import Enum


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
BLACK = (0,0,0)

#TODO 同步问题
#正在进行的游戏
playing_games = {}
#刚建立连接，还没开始游戏的玩家
init_player = {}
#正在匹配中的游戏
pending_game = []

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


class Board:
    active_shape = None
    pending_shape = None
    board = None

    def __init__(self, width, height):
        self.dead = False
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
            self.dead = True
            # self.reset()
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
            # 着陆y
            n = self.shape_to_board()
            self.add_shape()
            return (False, n)
        return (True, 0)

    # 还可以更快点，瞬间到底
    def move_bottom(self):
        at_bottom = self.check_bottom() or self.is_collision()
        while at_bottom is False and self.dead is False:
            at_bottom = self.move_down()[0]

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

    #测试每一行是否被填满
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

    #删除第Y行
    def process_line(self, y_to_remove):
        for y in range(y_to_remove - 1, -1, -1):
            for x in range(self.width):
                self.board[y + 1][x] = self.board[y][x]

    def shape_to_board(self):
        for y in range(4):
            for x in range(4):
                dx = x + self.active_shape.x
                dy = y + self.active_shape.y
                if self.active_shape.shape[y][x] == 1:
                    self.board[dy][dx] = 1

        lines_found = 0
        while self.test_for_line():
            lines_found += 1
        return lines_found

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
        elif motion_state == K_SPACE:
            self.move_bottom()

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
        y += 1
        pic = pygame.image.load("block.png")
        surface.blit(pic,(x * BLOCK_SIZE, y * BLOCK_SIZE))
        # rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE,BLOCK_SIZE)
        # pygame.draw.rect(surface,RED,rect)


# 玩家状态:init(建立和服务器的链接)  -> matching(正在匹配)  ->  playing  ->  win/lose   ->quit
player_status = Enum("player_status", ("init", "matching", "playing", "win", "lose", "quit"))
game_status = Enum("game_status", ("init", "matching", "playing", "finish"))

class Player:
    game_id = 0
    player_id = 0
    conn = None
    board = None

    def __init__(self, game_id, player_id, conn, board):
        self.game_id = game_id
        self.player_id = player_id
        self.conn = conn
        self.board = board
        self.status = player_status.init
        self.username = None
        self.score = 0

    def set_username(self, username):
        self.username = username

    def add_score(self,n):
        self.score += n

class Game(object):
    game_id = 0
    ticks = 0
    factor = 4
    frame_rate = 60
    is_paused = False
    starting_level = 1
    level = 1
    # start_time
    # end_time
    # score1
    # score2

    def __init__(self, starting_level=1):
        self.game_status = game_status.init
        self.game_id = int(time.time()*1000000)
        self.player = {}
        self.starting_level = int(starting_level)
        self.reset()

    def reset(self):
        self.level = self.starting_level

    #TODO 引入游戏状态, len(self.player)<2这行代码改掉
    def should_update(self):
        if self.is_paused or self.game_status != game_status.playing:
            return False

        self.ticks += 1
        # level越高，刷新速度越快
        if self.ticks >= (self.frame_rate - (self.level * self.factor)):
            self.ticks = 0
            return True
        return False


    def has_player_id(self, player_id):
        return self.player.get(player_id) is not None

    # 添加一个玩家进入这局游戏
    def add_player(self, player):
        # TODO 暂时把socket fd当作player_id, Board最后也要改掉
        self.player[player.player_id] = player

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
                    "score":p.score,
                    "board": p.board.board,
                    "active_shape": p.board.active_shape.shape,
                    "x": p.board.active_shape.x,
                    "y": p.board.active_shape.y,
                    "dead": p.board.dead
                }
            )

        data = json.dumps(dd).encode('utf-8')
        for p in self.player.values():
            if p.player_id == player_id:
                p.conn.send(data)

    # TODO 有一个玩家退出游戏
    def quit(self, player_id):
        self.get_player(player_id).status = player_status.quit
        if len(self.player) == 1:
            pending_game.pop(self)
        # elif len(self.player) == 2:
        # TODO 另一方胜利


    # 响应相应玩家的操作
    def up(self, player_id):
        self.player.get(player_id).board.move_piece(K_UP)

    def left(self, player_id):
        self.player.get(player_id).board.move_left()

    def right(self, player_id):
        self.player.get(player_id).board.move_right()

    def down(self, player_id):
        player = self.player.get(player_id)
        b = player.board
        n = b.move_down()[1]
        if b.dead:
            playing_games.pop(self.game_id)
            self.game_status = game_status.finish
            for p in self.player.values():
                p.player_status = player_status.lose if p.player_id == player_id else player_status.win #python 3元表达式
        elif n > 0:
            player.add_score(n)


    def bottom(self, player_id):
        player = self.player.get(player_id)
        n = self.player.get(player_id).board.move_down()[1]
        if n > 0:
            player.add_score(n)


def show_text(font, size, text, color, center, screen, bold=0, alias = 1):
    try:
        tetris_font = pygame.font.Font(font, size)
    except:
        tetris_font = pygame.font.SysFont(font, size)
    tetris_font.set_bold(bold)

    label_1 = tetris_font.render(text, alias, color)
    label_1_rect = label_1.get_rect()
    label_1_rect.center = center

    screen.blit(label_1, label_1_rect)

#TODO 位置不要写死
def result_screen(result, screen):
    show_text("freesansbold.ttf", 64, result, (0,0,255), (100,100), screen)


def _draw2(SURFACE, board, x,y):
    BSURFACE = board.draw_game_board()
    SURFACE.blit(BSURFACE,(x,y))

#本地的游戏就简单写一下，用了以前的代码
def single_game():
    pygame.init()
    SURFACE = pygame.display.set_mode((WINDOW_WIDTH * 2 + 50, WINDOW_HEIGHT))
    SURFACE.fill(WHITE)
    pygame.display.set_caption("俄罗斯方块")
    fpsClock = pygame.time.Clock()

    board = Board(WIDTH, HEIGHT)
    game = Game(1)
    game.game_status = game_status.playing

    board2 = Board(WIDTH, HEIGHT)

    key_dir = None
    key_dir2 = None
    frameCount = 0
    frameCount2 = 0

    while True:
        frameCount += 1
        frameCount2 += 1

        for event in pygame.event.get():
            key_dir = None
            key_dir2 = None

            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            pressed_keys = pygame.key.get_pressed()

            if event.type == KEYDOWN:
                if event.key == K_UP:
                    board.move_piece(K_UP)
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

        if key_dir in [K_LEFT, K_RIGHT, K_DOWN] and frameCount > 4 and not board.dead and not board2.dead:
            frameCount = 0
            board.move_piece(key_dir)
        if key_dir2 in [K_s, K_a, K_d] and frameCount2 > 4 and not board.dead and not board2.dead:
            frameCount2 = 0
            board2.move_piece(key_dir2)

        _draw2(SURFACE, board, 0, 0)
        _draw2(SURFACE, board2, 280, 0)

        # 每隔一定帧数下降一格
        if game.should_update() and not board.dead and not board2.dead:
            board.move_down()
            board2.move_down()

        if board.dead:
            result_screen("lose", SURFACE)
        if board2.dead:
            result_screen("win", SURFACE)

        # 渲染一帧
        pygame.display.update()

        fpsClock.tick(FPS)

