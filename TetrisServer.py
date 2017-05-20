from TetrisObject import *
import json
import socket
import selectors
import threading

def get_init_player(player_id):
    player = init_player.pop(player_id)
    player.status = player_status.playing
    return player


def send_info(game_id, player_id, conn, player_status):
    data = {
        "game_id": game_id,
        "player_id": player_id,
        "player_status":player_status
    }
    conn.send(json.dumps(data).encode('utf-8'))


def accept(s):
    conn,addr = s.accept()
    conn.setblocking(False)
    selector.register(conn, selectors.EVENT_READ, read)

    player_id = conn.fileno()
    #TODO 并不是每个玩家都要加入init_player。单机玩的就可以不要。当然单机玩也可以通过init_player获取数据
    init_player[player_id] = Player(0, player_id, conn, Board(16, 28))
    all_players[player_id] = init_player[player_id]

    send_info(0, player_id, conn, player_status="init") #给刚建立连接的玩家发送的game_id为0

# 匹配游戏，2种情况：能匹配到；不能匹配到，等待下一个玩家
def match(conn, player_id):#TODO conn.fileno()就是player_id
    if len(pending_game) == 0:
        pending_game.append(Game(1))

    game = pending_game[0]

    if game.has_player_id(player_id):#客户端重复发送匹配请求
        return

    player = get_init_player(conn.fileno())
    game.add_player(player)


    if len(game.player) == 2:
        playing_games[game.game_id] = game
        pending_game.remove(game)
        game.game_status = game_status.playing
        for p in game.player.values():
            send_info(game_id=game.game_id, player_id=p.player_id, conn=p.conn, player_status="playing")
        return

    send_info(game_id=game.game_id, player_id=player.player_id, conn=player.conn, player_status="matching")



def read(conn):
    try:
        raw_request_jsons = conn.recv(8000).decode("utf-8")
    except ConnectionResetError as e: #客户端异常退出
        # 客户端在匹配中异常退出
        for game in pending_game:
            for p in game.player.values():
                if p.player_id == conn.fileno():
                    pending_game.remove(game)
        selector.unregister(conn)
        conn.close()
        return

    request_jsons = split_json(raw_request_jsons) #TODO 很奇怪，要改成一次只发送1个json吗
    for j in request_jsons:
        print(j)
        js = json.loads(j)
        print(js)

        player_id = int(js["player_id"])

        if all_players[player_id].username is None:
            all_players[player_id].set_username(js["username"])

        if js["opr"] == "match":
            match(conn, player_id)
            continue
        if js["opr"] == "quit": #客户端退出（非异常）
            for game in pending_game:
                if game.game_id == int(js["game_id"]):
                    pending_game.remove(game)
                    selector.unregister(conn)
                    conn.close()
            return

        game = playing_games[int(js["game_id"])]
        if js["opr"] == "up":
            game.up(player_id)
        if js["opr"] == "left":
            game.left(player_id)
        if js["opr"] == "right":
            game.right(player_id)
        if js["opr"] == "down":
            game.down(player_id)
        if js["opr"] == "show":
            game.show(player_id)
        if js["opr"] == "bottom":
            game.down(player_id)
        if js["opr"] == "finish":
            game.finish()

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



#TODO 方块速率下降调整，或许下降速度应该跟帧数和水平挂钩，而不只是时间
def schedule_move_down(interval=0.02):
    def move_down():
        while True:
            for game in playing_games.values():
                if game.should_update():
                    for p in game.player.values():
                        if not p.board.dead:
                            game.down(p.player_id)
            time.sleep(interval)
    threading.Thread(target=move_down).start()


schedule_move_down()

while True:
    events = selector.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj)










