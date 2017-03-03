import socket
import sys

HOST, PORT = "localhost", 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
while True:
    data = input("input:")
    sock.sendall(data.encode('utf-8'))

    # Receive data from the server and shut down
    received = str(sock.recv(1024), "utf-8")
    print("Sent:     {}".format(data))
    print("Received: {}".format(received))
sock.close()