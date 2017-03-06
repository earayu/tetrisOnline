import socket
client = socket.socket()

client.connect(('localhost', 9000))

while True:
    cmd = input('>>> ').strip()
    if len(cmd) == 0 : continue
    client.send(cmd.encode('utf-8'))
    data = client.recv(1024)
    print(data.decode())

client.close()