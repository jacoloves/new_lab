# _*_ coding: utf-8 _*_
"""
logclient1.py
Usage $python logclient1.py
"""

import socket
import sys

HOST = "localhost"
PORT = 50000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))
except:
    print("接続できません")
    sys.exit()

while True:
    msg = input()
    if msg == "q":
        break
    client.sendall(msg.encode("utf-8"))

client.close()
