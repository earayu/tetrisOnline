from TetrisObject import *
import json
import socket
import selectors
import threading

def get_init_player(player_id):
    player = init_player.pop(player_id)
    player.status = player_status.playing
    return player


def send_info(game_id, player_id, conn):
    data = {
        "game_id": game_id,
        "player_id": player_id
    }
    conn.send(json.dumps(data).encode('utf-8'))


def accept(s):
    conn,addr = s.accept()
    conn.setblocking(False)
    selector.register(conn, selectors.EVENT_READ, read)

    player_id = conn.fileno()
    init_player[player_id] = Player(0, player_id, conn, Board(16, 28))
    print(player_id)

    send_info(0, player_id, conn) #给刚建立连接的玩家发送的game_id为0


def match(conn, player_id):
    if len(pending_game) == 0:
        pending_game.append(Game(1))

    game = pending_game[0]
    game.add_player(get_init_player(conn.fileno()))

    playing_games[game.game_id] = game

    if len(game.player) == 2:
        pending_game.remove(game)
        for p in game.player.values():
            send_info(game_id=game.game_id, player_id=p.player_id, conn=p.conn)

def read(conn):
    raw_request_jsons = conn.recv(1024).decode("utf-8")
    request_jsons = split_json(raw_request_jsons) #TODO 很奇怪，要改成一次只发送1个json吗
    print(request_jsons)
    for j in request_jsons:
        js = json.loads(j)

        player_id = int(js["player_id"])
        if js["opr"] == "match":
            match(conn, player_id)
            continue

        game = playing_games[int(js["game_id"])]
        if js["opr"] == "quit":
            game.quit(player_id)
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
            l.append(e + "}")
    return l


HOST, PORT = "localhost", 9999
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(10)

selector = selectors.DefaultSelector()
selector.register(s, selectors.EVENT_READ, accept)

#TODO 同步问题
#正在进行的游戏
playing_games = {}
#刚建立连接，还没开始游戏的玩家
init_player = {}
#正在匹配中的游戏
pending_game = []

#TODO 方块速率下降调整，或许下降速度应该跟帧数和水平挂钩，而不只是时间
def schedule_move_down(interval=0.02):
    def move_down():
        while True:
            for game in playing_games.values():
                if game.should_update():
                    for p in game.player.values():
                        p.board.move_down()
            time.sleep(interval)
    threading.Thread(target=move_down).start()


schedule_move_down()
while True:
    events = selector.select()
    for key, mask in events:
        callback = key.data  # 掉accept函数
        callback(key.fileobj)  # key.fileobj = 文件句柄 （相当于上个例子中检测的自己）











