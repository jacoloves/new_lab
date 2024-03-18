# _*_ coding: utf-8 _*_
"""
client0v6.py
usage python client0v6.py
"""

import socket

HOST = "localhost"
PORT = 50000
BUFSIZE = 4096

client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

client.connect((HOST, PORT))

data = client.recv(BUFSIZE)
print(data.decode("UTF-8"))

client.close()
