import socketserver
import pygame, sys, random, time, re
from pygame.locals import *
from TetrisObject import *
import json
import socket
import selectors
import threading

HOST, PORT = "localhost", 9999

class Player():
    player_id = 0
    conn = None
    board = None
    score = 0

    def __init__(self, player_id, conn, board):
        self.player_id = player_id
        self.conn = conn
        self.board = board


class Game(object):
    game_id = 0
    ticks = 0
    factor = 4
    frame_rate = 60.0
    is_paused = False
    starting_level = 1
    level = 1

    def __init__(self, starting_level=1):
        self.game_id = len(games)+1
        self.player = {}
        self.starting_level = int(starting_level)
        self.reset()

    def reset(self):
        self.level = self.starting_level

    def should_update(self):
        if self.is_paused:
            return False

        self.ticks += 1
        # level越高，刷新速度越快
        if self.ticks >= (self.frame_rate - (self.level * self.factor)):
            self.ticks = 0
            return True
        return False

    def send_info(self, conn):
        p = self.get_player(conn.fileno()) #TODO 直接传fd，而不是conn
        data = {
            "game_id":self.game_id,
            "player_id":p.player_id
        }
        conn.send(json.dumps(data).encode('utf-8'))

    # 添加一个玩家进入这局游戏
    def add_player(self, conn):
        # TODO 暂时把socket fd当作player_id, Board最后也要改掉
        player_id = conn.fileno()
        self.player[player_id] = Player(player_id, conn, Board(16,28))

    def get_player(self, player_id):
        return self.player[player_id]

    # 将游戏状态发送给同一局游戏中的所有玩家
    def show(self, player_id):
        dd = []
        # 遍历map
        for p in self.player.values():
            dd.append(
                {
                    "player_id":p.player_id,
                    "board": p.board.board,
                    "active_shape": p.board.active_shape.shape,
                    "x": p.board.active_shape.x,
                    "y": p.board.active_shape.y
                }
            )

        data = json.dumps(dd).encode('utf-8')
        for p in self.player.values():
            if p.player_id == player_id:
                p.conn.send(data)

    # 响应相应玩家的操作
    def up(self, player_id):
        self.player.get(player_id).board.move_piece(K_UP)

    def left(self, player_id):
        self.player.get(player_id).board.move_piece(K_LEFT)

    def right(self, player_id):
        self.player.get(player_id).board.move_piece(K_RIGHT)

    def down(self, player_id):
        self.player.get(player_id).board.move_piece(K_DOWN)



def accept(s, mask):
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


def read(conn, mask):
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
            l.append(e+"}")
    return l


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(10)

selector = selectors.DefaultSelector()
selector.register(s, selectors.EVENT_READ, accept)

#TODO 同步问题
games = {}
pending_game = []


#TODO 方块速率下降调整
def schedule_move_down(interval=0.02):
    def move_down():
        while True:
            for game in games.values():
                if game.should_update():
                    for p in game.player.values():
                        p.board.move_down()
            time.sleep(interval)
    t = threading.Thread(target=move_down)
    t.start()


schedule_move_down()
while True:
    events = selector.select()
    for key, mask in events:
        callback = key.data  # 掉accept函数
        callback(key.fileobj, mask)  # key.fileobj = 文件句柄 （相当于上个例子中检测的自己）











