# _*_ coding: utf-8 _*_
"""
client1.py
Usage $python3 client1.py
"""

import socket
import sys

PORT = 50000
BUFSIZE = 4096

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = input("接続サーバー:")
try:
    client.connect((host, PORT))
except:
    print("接続できません")
    sys.exit()

msg = input("メッセージを入力:")
client.sendall(msg.encode("utf-8"))

data = client.recv(BUFSIZE)
print("サーバからのメッセージ:")
print(data.decode("UTF-8"))

client.close()
