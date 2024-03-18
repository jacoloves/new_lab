# _*_ coding: utf-8 _*_
"""
server1UDP.py
Usage $python server1UDP.py
"""

import socket
import datetime

PORT = 50000
BUFSIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind(("", PORT))

while True:
    data, client = server.recvfrom(BUFSIZE)
    msg = str(datetime.datetime.now())
    server.sendto(msg.encode("utf-8"), client)
    print(msg, "接続要求あり")
    print(client)
