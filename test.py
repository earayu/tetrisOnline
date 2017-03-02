import pygame, sys
from pygame.locals import *


# 游戏基本设置
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 600

FPS = 30

# 颜色
WHITE = (255,255,255)


def terminate():
    pygame.quit()
    sys.exit()


pygame.init()
SURFACE = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
pygame.display.set_caption("俄罗斯方块")

fpsClock = pygame.time.Clock()



while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()

    pressed_keys = pygame.key.get_mods()

    for i in range(len(pressed_keys)):
        if pressed_keys[i] != 0:
            print(pygame.key.name(i))



    SURFACE.fill(WHITE)
    pygame.display.update()
    fpsClock.tick(FPS)