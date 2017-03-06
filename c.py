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
sel.register(sock, selectors.EVENT_READ, accept)  # 注册事件
#      sock注册过来                   新连接调用这个函数

while True:
    events = sel.select()  # 有可能调用epoll，也有可能调用select，看系统支持
    # 默认是阻塞，有活动连接，就返回活动的列表
    for key, mask in events:
        callback = key.data  # 掉accept函数
        callback(key.fileobj, mask)  # key.fileobj = 文件句柄 （相当于上个例子中检测的自己）