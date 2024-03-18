# _*_ coding: utf-8 _*_
"""
chatserv.py
Usage $python chatserv.py
"""

import socket

PORT = 50000
BUFSIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind(("", PORT))

clist = []
while True:
    data, client = server.recvfrom(BUFSIZE)
    if not (client in clist):
        clist.append(client)
    if data.decode("UTF-8") == "q":
        clist.remove(client)
    else:
        msg = str(client) + ">"
        msg += data.decode("UTF-8")
        print(msg)
        for c in clist:
            server.sendto(msg.encode("UTF-8"), c)
