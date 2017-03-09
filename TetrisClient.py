import socket
import sys
from TetrisObject import *
import json, threading
import Menu




def draw(board, x,y):
    BSURFACE = board.draw_game_board()
    SURFACE.blit(BSURFACE,(x,y))

#TODO 告诉服务器退出，服务器应该也要有心跳测试
def terminate(sock):
    # send_key_data(sock, request('quit'))
    pygame.quit()
    send_key_data(sock, request('quit'))
    #TODO 如果在matching页面退出，会因为recv阻塞而不能退出.
    # sock.close() #TODO 直接close，服务端也会出错。而且并没有删掉在服务端的匹配用户
    sys.exit()


def request(opr):
    data = '{"game_id":"' + str(cli_player.game_id) + '","player_id":"' + str(cli_player.player_id) + '","opr":"' + opr + '"}'
    return data.encode('utf-8')


def get_board(sock):
    sock.sendall(request('show'))
    raw = sock.recv(8000)
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

def send_key_data(sock, data):
    sock.send(data)
    get_board(sock)

def m(sock):
    global cli_player, svr_player
    sock.send(request("match"))
    cli_player.status = player_status.matching
    cli_player, svr_player = load_basic_info(sock)
    # 第一个玩家遇到matching状态,需要再等待一个playing状态
    if cli_player.player_status == player_status.matching:
        m(sock)

def match(sock):
    if cli_player.status == player_status.init:
        threading.Thread(target=m, args=(sock,)).start()


f = 0
# TODO 修改代码
def menu_screen(menu, sock):
    global f
    menu.draw_menu()
    r = menu.process_key_event()
    if r == 'match':
        match(sock)
        f = 1
    elif r == 'terminate':
        terminate(sock)
    if f == 0:
        menu.update_menu()
    else:
        menu.matching_screen()

# 匹配画面
def match_screen():
    pass

# 加载这局游戏的基本数据
def load_basic_info(sock):
    game_info_json = json.loads(sock.recv(1024).decode('utf-8'))
    print(game_info_json)
    game_id = game_info_json["game_id"]
    player_id = int(game_info_json["player_id"])
    status = player_status[game_info_json["player_status"]]
    c,s = Player(game_id, player_id, sock, Board(16,28)),Player(game_id, player_id, sock, Board(16,28)) #TODO board参数
    c.player_status = status
    return c,s

# 每隔4帧数处理一次
def process_key_event(sock, frames=4):
    global key_dir,frame_count
    frame_count += 1
    for event in pygame.event.get():
        key_dir = None
        if event.type == QUIT:
            terminate(sock)
        pressed_keys = pygame.key.get_pressed()
        if event.type == KEYDOWN:
            if event.key == K_UP:
                send_key_data(sock, request('up'))
        if pressed_keys[K_LEFT]:
            key_dir = K_LEFT
        elif pressed_keys[K_RIGHT]:
            key_dir = K_RIGHT
        elif pressed_keys[K_DOWN]:
            key_dir = K_DOWN
        elif pressed_keys[K_SPACE]:
            key_dir = K_SPACE

    if key_dir == K_SPACE:
        send_key_data(sock, request('bottom'))


    # 每4帧
    if key_dir is not None and frame_count > frames:
        frame_count = 0
        if key_dir == K_LEFT:
            send_key_data(sock, request('left'))
        elif key_dir == K_RIGHT:
            send_key_data(sock, request('right'))
        elif key_dir == K_DOWN:
            send_key_data(sock, request('down'))



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
frame_count = 0


menu = Menu.Menu(SURFACE)

while True:

    if cli_player.player_status in [player_status.init, player_status.matching]:
        menu_screen(menu, sock)
        continue

    SURFACE.fill(WHITE)
    get_board(sock)
    process_key_event(sock)
    draw(cli_player.board,0,0)
    draw(svr_player.board,280,0)
    pygame.display.update()
    fpsClock.tick(FPS)

sock.close()

