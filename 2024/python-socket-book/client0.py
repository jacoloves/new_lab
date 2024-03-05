# _*_ coding: utf-8 _*_
"""
client0.py
usage python client0.py
"""

import socket

HOST = "localhost"
#HOST = "127.0.0.1"
PORT = 50000
BUFSIZE = 4096

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

data = client.recv(BUFSIZE)
print(data.decode("UTF_8"))

client.close()
