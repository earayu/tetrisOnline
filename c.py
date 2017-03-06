import selectors
import socket

sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()  # 开始连接
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)  # 连接设为非阻塞模式
    sel.register(conn, selectors.EVENT_READ, read)  # 把conn注册到sel对象里
    # 新连接回调read函数

def read(conn, mask):
    data = conn.recv(1024)  # 接收数据
    if data:
        print('echoing', repr(data), 'to', conn)
        conn.send(data)  # Hope it won't block
    else:
        print('closing', conn)
        sel.unregister(conn)  # 取消注册
        conn.close()

sock = socket.socket()
sock.bind(('localhost', 9000))
sock.listen(100)
sock.setblocking(False)

conn = None

while True:
    try:
        conn = sock.accept()
        print(conn)
    except:
        pass

# data = conn.recv(1024)
