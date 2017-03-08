from TetrisObject import *
import json
import socket
import selectors
import threading


def accept(s):
    conn,addr = s.accept()
    conn.setblocking(False)
    selector.register(conn, selectors.EVENT_READ, read)

    if len(pending_game) == 0:
        pending_game.append(Game(1))

    game = pending_game[0]
    game.add_player(conn)

    if len(game.player) == 2:
        pending_game.remove(game)

    games[game.game_id] = game

    game.send_info(conn)


def read(conn):
    raw_request_jsons = conn.recv(1024).decode("utf-8")
    request_jsons = split_json(raw_request_jsons) #TODO 很奇怪，要改成一次只发送1个json吗
    for j in request_jsons:
        js = json.loads(j)

        game = games[int(js["game_id"])]
        player_id = int(js["player_id"])
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
games = {}
pending_game = []

#TODO 方块速率下降调整，或许下降速度应该跟帧数和水平挂钩，而不只是时间
def schedule_move_down(interval=0.02):
    def move_down():
        while True:
            for game in games.values():
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











