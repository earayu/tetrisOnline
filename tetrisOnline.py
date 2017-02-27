import pygame, sys, random, time
from pygame.locals import *


# 游戏基本设置
WINDOW_WIDTH = 270
WINDOW_HEIGHT = 450

BOX_SIZE = 15

assert WINDOW_WIDTH % BOX_SIZE ==0 and WINDOW_HEIGHT % BOX_SIZE ==0, '窗口大小不合适'

FPS = 5

# 颜色
WHITE = (255,255,255)
RED = (255,0,0)


class Shape(object):
    _shapes = [
        [
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0]
        ],
        [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0]],
        [
            [0, 0, 0, 0],
            [0, 1, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0]
        ],
        [
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 0],
            [0, 1, 1, 0]
        ],
        [
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 1, 0],
            [0, 1, 0, 0]
        ],
        [
            [0, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0]
        ],
    ]

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



def terminate():
    pygame.quit()
    sys.exit()

def drawShape(SURFACE, shape):
    for i in range(len(shape.shape)):
        for j in range(len(shape.shape[i])):
            if shape.shape[i][j]==1:
                rect = pygame.Rect((shape.x+i)*BOX_SIZE,(shape.y+j)*BOX_SIZE,BOX_SIZE,BOX_SIZE)
                pygame.draw.rect(SURFACE,RED,rect)




pygame.init()
SURFACE = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
pygame.display.set_caption("俄罗斯方块")

fpsClock = pygame.time.Clock()

shape = Shape(5,0)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()

    SURFACE.fill(WHITE)

    drawShape(SURFACE,shape)
    pygame.display.update()

    time.sleep(3)

    shape.rotate()

    fpsClock.tick(FPS)