# _*_ coding: utf-8 _*_
"""
server2.py
Usage $python server2.py
"""

import socket
import datetime

PORT = 50000
BUFSIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("", PORT))

server.listen()

while True:
    client, addr = server.accept()
    msg = str(datetime.datetime.now())
    print(msg, "接続要求あり")
    print(client)

    data = client.recv(BUFSIZE)
    print(data.decode("UTF-8"))

    client.sendall(msg.encode("utf-8"))
    client.close()
