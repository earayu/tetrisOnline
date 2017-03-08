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




#TODO player_id参数可以去掉
def show_str(player_id):
    return '{"game_id":"' + str(game_id) + '","player_id":"' + str(player_id) + '","opr":"show"}'

def up_str(player_id):
    return '{"game_id":"' + str(game_id) + '","player_id":"' + str(player_id) + '","opr":"up"}'

def left_str(player_id):
    return '{"game_id":"' + str(game_id) + '","player_id":"' + str(player_id) + '","opr":"left"}'

def down_str(player_id):
    return '{"game_id":"' + str(game_id) + '","player_id":"' + str(player_id) + '","opr":"down"}'

def right_str(player_id):
    return '{"game_id":"' + str(game_id) + '","player_id":"' + str(player_id) + '","opr":"right"}'




def get_board(sock):
    sock.sendall(bytes(show_str(player_id), 'utf-8'))
    raw = sock.recv(4024)
    print(raw)
    raw_recv_data = json.loads(raw.decode('utf-8'))
    # TODO 多人游戏，要按照player_id分离json
    for j in raw_recv_data:
        if j["player_id"] == player_id:
            recv_data = j
            board.board = recv_data["board"]
            board.active_shape.shape = recv_data["active_shape"]
            board.active_shape.x = recv_data["x"]
            board.active_shape.y = recv_data["y"]
        else:
            recv_data = j
            board2.board = recv_data["board"]
            board2.active_shape.shape = recv_data["active_shape"]
            board2.active_shape.x = recv_data["x"]
            board2.active_shape.y = recv_data["y"]

#TODO 图形界面配置服务器和端口
HOST, PORT = "localhost", 9999
game_id = 0
player_id = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    # sock.sendall('{"opr":"info"}'.encode('utf-8'))
    game_info_json = json.loads(sock.recv(1024).decode('utf-8'))
    game_id = game_info_json["game_id"]
    player_id = int(game_info_json["player_id"])

    pygame.init()
    SURFACE = pygame.display.set_mode((WINDOW_WIDTH*2+50,WINDOW_HEIGHT))
    SURFACE.fill(WHITE)
    pygame.display.set_caption("俄罗斯方块")
    fpsClock = pygame.time.Clock()

    board = Board(WIDTH,HEIGHT)

    board2 = Board(WIDTH,HEIGHT)

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
                    sock.sendall(bytes(up_str(player_id), 'utf-8'))
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
                sock.sendall(bytes(left_str(player_id), 'utf-8'))
            if key_dir == K_RIGHT:
                sock.sendall(bytes(right_str(player_id), 'utf-8'))
            if key_dir == K_DOWN:
                sock.sendall(bytes(down_str(player_id), 'utf-8'))

        draw(board,0,0)
        draw(board2,280,0)
        # 渲染一帧
        pygame.display.update()
        fpsClock.tick(FPS)


