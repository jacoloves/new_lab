# _*_ coding: utf-8 _*_
"""
chattcpclient.py
Usage $python chatcpclient.py
"""

import socket
import sys
import threading

PORT = 50000
BUFSIZE = 4096


# server_handler()
def server_handler(client):
    while True:
        try:
            data = client.recv(BUFSIZE)
        except:
            break
        if (not data) or (data.decode("UTF-8") == "q"):
            break
        print(data.decode("UTF-8"))
