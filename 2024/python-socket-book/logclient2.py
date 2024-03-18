# _*_ coding: utf-8 _*_
"""
logclient2.py
Usage $python logclient2.py
"""

import socket
import sys

HOST = "localhost"
PORT = 50000
DATAFILE = "data.txt"

fin = open(DATAFILE, "rt")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))
except:
    print("接続できません")
    sys.exit()

msg = fin.read()
client.sendall(msg.encode("utf-8"))
client.close()
