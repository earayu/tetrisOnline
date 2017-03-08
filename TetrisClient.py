import socket
import sys
from TetrisObject import *
import json


def draw(board, x,y):
    BSURFACE = board.draw_game_board()
    SURFACE.blit(BSURFACE,(x,y))


def terminate():
    pygame.quit()
    sys.exit()


def request(opr):
    data = '{"game_id":"' + str(cli_player.game_id) + '","player_id":"' + str(cli_player.player_id) + '","opr":"' + opr + '"}'
    return data.encode('utf-8')



def get_board(sock):
    sock.sendall(request('show'))
    raw = sock.recv(4024)
    raw_recv_data = json.loads(raw.decode('utf-8'))
    # TODO 多人游戏，要按照player_id分离json
    for recv_data in raw_recv_data:
        if recv_data["player_id"] == cli_player.player_id:
            cli_player.board.board = recv_data["board"]
            cli_player.board.active_shape.shape = recv_data["active_shape"]
            cli_player.board.active_shape.x = recv_data["x"]
            cli_player.board.active_shape.y = recv_data["y"]
        else:
            svr_player.board.board = recv_data["board"]
            svr_player.board.active_shape.shape = recv_data["active_shape"]
            svr_player.board.active_shape.x = recv_data["x"]
            svr_player.board.active_shape.y = recv_data["y"]

# 加载这局游戏的基本数据
def load_basic_info(sock):
    game_info_json = json.loads(sock.recv(1024).decode('utf-8'))
    game_id = game_info_json["game_id"]
    player_id = int(game_info_json["player_id"])
    return Player(game_id, player_id, sock, Board(16,28)),Player(game_id, player_id, sock, Board(16,28)) #TODO board参数


HOST, PORT = "localhost", 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

cli_player, svr_player = load_basic_info(sock) #cli_player为本方,svr_player为对方

pygame.init()
SURFACE = pygame.display.set_mode((WINDOW_WIDTH*2+50,WINDOW_HEIGHT)) #窗口大小
SURFACE.fill(WHITE)
pygame.display.set_caption("俄罗斯方块")
fpsClock = pygame.time.Clock()

key_dir = None
frameCount = 0

while True:
    get_board(sock)
    # 渲染
    frameCount += 1
    for event in pygame.event.get():
        key_dir = None
        if event.type == QUIT:
            terminate()
        pressed_keys = pygame.key.get_pressed()
        if event.type == KEYDOWN:
            if event.key == K_UP:
                sock.sendall(request('up'))
            if event.key == K_w:
                svr_player.board.move_piece(K_UP)
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
        if key_dir == K_LEFT:
            sock.sendall(request('left'))
        if key_dir == K_RIGHT:
            sock.sendall(request('right'))
        if key_dir == K_DOWN:
            sock.sendall(request('down'))

    draw(cli_player.board,0,0)
    draw(svr_player.board,280,0)
    # 渲染一帧
    pygame.display.update()
    fpsClock.tick(FPS)

sock.close()

