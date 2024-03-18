# _*_ coding: utf-8 _*_
"""
server1v6.py
Usage $python server1v6.py
"""

import socket
import datetime

PORT = 50000

server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

server.bind(("", PORT))
server.listen()

while True:
    client, addr = server.accept()
    msg = str(datetime.datetime.now())
    client.sendall(msg.encode("utf-8"))
    print(msg, "接続要求あり")
    print(client)
    client.close()
