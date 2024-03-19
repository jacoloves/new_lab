# _*_ coding: utf-8 _*_
"""
minihttpd.py
Usage $python nminihttpd.py
"""

import socket

PORT = 8080
BUFSIZE = 4096
INDEX_HTML = "index.html"

fin = open(INDEX_HTML, "rt")
msg = fin.read()
fin.close()
msg = "HTTP/1.0 200 OK\n\n" + msg

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", PORT))
server.listen()

while True:
    client, addr = server.accept()
    data = client.recv(BUFSIZE)
    print(data.decode("UTF-8"))

    client.sendall(msg.encode("cp932"))
    client.close()
