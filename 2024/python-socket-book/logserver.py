# _*_ coding: utf-8 _*_
"""
logserver.py
Usage $python logserver.py
"""

import socket
import datetime

from server3 import client_handler

PORT = 50000
BUFSIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", PORT))
server.listen()

while True:
    client, addr = server.accept()
    d = datetime.datetime.now()
    fname = d.strftime("%m%d%H%M%S%f")
    print(fname, "接続要求あり")
    print(client)
    fout = open(fname + ".txt", "wt")
    try:
        while True:
            data = client.recv(BUFSIZE)
            if not data:
                break
            print(data.decode("UTF-8"))
            print(data.decode("UTF-8"), file=fout)
    except:
        print("エラー発生しました（接続終了）")
    client.close()
    fout.close()
