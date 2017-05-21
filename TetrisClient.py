import socket
from TetrisObject import *
import json, threading
import Menu


def restart():
    global cli_player, svr_player, FINISH, key_dir, frame_count, f
    FINISH = False
    sock.send(request('restart'))
    cli_player,svr_player = load_basic_info(sock)
    key_dir = None
    frame_count = 0
    f = 0


def finish_wait():
    global FINISH
    if FINISH is True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate(sock)
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    restart()


def finish_game():
    global FINISH
    if FINISH is False:
        sock.send(request("finish"))
        FINISH = True

def draw(board, x,y):
    BSURFACE = board.draw_game_board()
    if cli_player.board.dead:
        result_screen("lose", SURFACE)
        finish_game()
    elif svr_player.board.dead:
        result_screen("win", SURFACE)
        finish_game()
    SURFACE.blit(BSURFACE,(x,y))

def terminate(sock):
    sock.send(request('quit'))
    pygame.quit()
    sys.exit()


def request(opr):
    data = '{"game_id":"%s","player_id":"%s","opr":"%s","username":"%s"}' \
           % (str(cli_player.game_id), str(cli_player.player_id), opr, cli_player.username)
    # data = '{"game_id":"' + str(cli_player.game_id) + '","player_id":"' + str(cli_player.player_id) + '","opr":"' + opr + '"}'
    print(data)
    return data.encode('utf-8')


def get_board(sock):
    if cli_player.player_status in [player_status.win, player_status.lose]:
        return

    sock.sendall(request('show'))
    raw = sock.recv(18000)
    print(raw)
    raw_recv_data = json.loads(raw.decode('utf-8'))
    # TODO 支持更多人游戏，要按照player_id分离json
    for recv_data in raw_recv_data:
        if recv_data["player_id"] == cli_player.player_id:
            cli_player.board.board = recv_data["board"]
            cli_player.board.active_shape.shape = recv_data["active_shape"]
            cli_player.board.active_shape.x = recv_data["x"]
            cli_player.board.active_shape.y = recv_data["y"]
            cli_player.board.dead = recv_data["dead"]
            cli_player.board.username = recv_data["username"]
        else:
            svr_player.board.board = recv_data["board"]
            svr_player.board.active_shape.shape = recv_data["active_shape"]
            svr_player.board.active_shape.x = recv_data["x"]
            svr_player.board.active_shape.y = recv_data["y"]
            svr_player.board.dead = recv_data["dead"]
            svr_player.board.username = recv_data["username"]

        if cli_player.board.dead:
            cli_player.player_status = player_status.lose
        if svr_player.board.dead:
            cli_player.player_status = player_status.win

def send_key_data(sock, data):
    if cli_player.player_status in [player_status.win, player_status.lose]:
        return
    sock.send(data)
    get_board(sock)

def m(sock):
    global cli_player, svr_player
    sock.send(request("match"))
    # cli_player.status = player_status.matching
    cli_player, svr_player = load_basic_info(sock)
    # 第一个玩家遇到matching状态,需要再等待一个playing状态
    if cli_player.player_status == player_status.matching:
        m(sock)

def match(sock):
    if cli_player.status == player_status.init:
        threading.Thread(target=m, args=(sock,)).start()

def single():
    return single_game()

# TODO 响应页面
def about():
    global f
    SURFACE.fill(BLACK)
    center_x = WINDOW_WIDTH
    center_y = WINDOW_HEIGHT/2
    show_text("SimHei", 16, "Author: earayu", (255, 255, 255), (center_x,center_y-20) , SURFACE)
    show_text("SimHei", 16, "E-mail: earayu@gmail.com", (255, 255, 255), (center_x, center_y), SURFACE)
    show_text("SimHei", 16, "site: https://github.com/earayu/tetrisOnline", (255, 255, 255), (center_x, center_y+20), SURFACE)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate(sock)
        if event.type == KEYDOWN:
            if event.key == K_RETURN:
                f = 0


f = 0

# TODO 修改代码
def menu_screen(menu, sock):
    global f
    menu.draw_menu()
    r = menu.process_key_event()
    if r == 'match':
        match(sock)
        f = 1
    elif r == 'single':
        f = 2
        if single()==0:
            f = 0
    elif r == 'about':
        about()
        f = 3
    elif r == 'terminate':
        terminate(sock)

    if f == 0:
        menu.update_menu()
    elif f==1:
        menu.matching_screen()
    elif f==3:
        about()



# 加载这局游戏的基本数据
def load_basic_info(sock):#TODO 代码冗余
    sss = sock.recv(1024).decode('utf-8')
    print(sss)
    game_info_json = json.loads(sss)
    game_id = game_info_json["game_id"]
    player_id = int(game_info_json["player_id"])
    c,s = Player(game_id, player_id, sock, Board(16,28)),Player(game_id, player_id, sock, Board(16,28)) #TODO board参数
    c.player_status = player_status[game_info_json["player_status"]]
    if c.username is None:
        c.set_username(USERNAME)
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

USERNAME = input('username:')
FINISH = False

# 123.206.180.79   192.168.130.128
HOST, PORT = "127.0.0.1", 9999

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

a = 0

while True:
    a += 1
    if cli_player.player_status in [player_status.init, player_status.matching]:
        menu_screen(menu, sock)
        continue
    SURFACE.fill(WHITE)
    if a > 10:
        get_board(sock)
        a = 0
    process_key_event(sock)
    draw(cli_player.board,0,0)
    draw(svr_player.board,280,0)
    finish_wait()
    pygame.display.update()
    fpsClock.tick(FPS)

sock.close()

