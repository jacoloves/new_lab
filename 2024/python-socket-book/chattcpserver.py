# _*_ coding: utf-8 _*_
"""
chattcpserver.py
Usage $python chattcpserver.py
"""

import socket
import datetime
import threading

PORT = 50000
BUFSIZE = 4096


def client_handler(client, addr):
    while True:
        try:
            data = client.recv(BUFSIZE)
        except:
            clist.remove(client)
            break
        if (not data) or (data.decode("UTF-8") == "q"):
            clist.remove(client)
            break
        msg = str(addr) + ">" + data.decode("UTF-8")
        print(msg)
        for c in clist:
            c.sendall(msg.encode("UTF-8"))
    client.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", PORT))
server.listen()

clist = []
while True:
    client, addr = server.accept()
    clist.append(client)

    p = threading.Thread(target=client_handler, args=(client, addr))
    p.start()
