# _*_ coding: utf-8 _*_
"""
server1.py
Usage $python server1.py
"""

import socket
import datetime

PORT = 50000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", PORT))
server.listen()

while True:
    client, addr = server.accept()
    msg = str(datetime.datetime.now())
    client.sendall(msg.encode("UTF-8"))
    print(msg, "接続要求あり")
    print(client)
    client.close()
