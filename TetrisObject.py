import random,pygame
from pygame.locals import *


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
        for y in range(4):
            for x in range(4):
                dx = x + self.active_shape.x
                dy = y + self.active_shape.y
                if self.active_shape.shape[y][x] == 1:
                    self.board[dy][dx] = 1

        lines_found = 0
        while self.test_for_line():
            lines_found += 1

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
        y += 1
        rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE,BLOCK_SIZE)
        pygame.draw.rect(surface,RED,rect)