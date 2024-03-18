# _*_ condinf: utf-8 _*_
"""
client0udp.py
Usage $python3 client0udp.py
"""

import socket

HOST = "localhost"
PORT = 50000
BUFSIZE = 4096

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto(b"Hi!", (HOST, PORT))

data = client.recv(BUFSIZE)
print(data.decode("UTF-8"))

client.close()
