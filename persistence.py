import pymysql
import time

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASS = 'qwqwqw'
DB_NAME = 'tetris'
DB_PORT = 3306
DB_CHARSET = 'utf8'


def now(format="%Y-%m-%d %H:%M:%S"):
    timeArray = time.localtime(int(time.time()))
    formatTime = time.strftime(format, timeArray)
    return formatTime

def execute(sql, args, host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME, port=DB_PORT, charset=DB_CHARSET):
    conn = pymysql.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset=charset)
    cur = conn.cursor()  # 获取一个游标
    cur.execute(sql, args)
    conn.commit()
    cur.close()  # 关闭游标
    conn.close()  # 释放数据库资源

def select(sql, args=None, host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME, port=DB_PORT, charset=DB_CHARSET):
    conn = pymysql.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset=charset)
    cur = conn.cursor()  # 获取一个游标
    cur.execute(sql, args)
    data = cur.fetchall()
    # conn.commit()
    cur.close()  # 关闭游标
    conn.close()  # 释放数据库资源
    return data

def add_game(game):
    player1,player2 = game.player.values()
    sql = 'INSERT INTO game (game_id,start_time,end_time,player1,player2,player1_score,player2_score) ' \
          'VALUES (%s,%s,%s,%s,%s,%s,%s)'
    ssql = 'SELECT * FROM game WHERE game_id=%s'
    if select(sql=ssql, args=game.game_id) is ():
        args = (game.game_id,game.start_time,game.end_time,player1.username,player2.username,player1.score,player2.score)
        execute(sql=sql,args=args)



def add_player(username, password, email, phone):
    sql = 'INSERT INTO player (username,password,email,phone,register_time,score,won_games,games)' \
          'VALUES (%s,PASSWORD(%s),%s,%s,now(),0,0,0)'
    args = (username, password, email, phone)
    execute(sql=sql, args=args)


def update_score(username, score, won):
    won = 1 if won == True else 0
    sql = 'UPDATE player SET score = score+%s, won_games = won_games + %s, games = games + 1 WHERE username = %s'
    args = (score, won, username)
    print(sql % args)
    execute(sql=sql, args=args)

def login(username,password):
    sql = 'SELECT * FROM player WHERE username = %s AND password = PASSWORD(%s)'
    args = (username,password)
    return True if select(sql=sql, args=args) is not () else False
