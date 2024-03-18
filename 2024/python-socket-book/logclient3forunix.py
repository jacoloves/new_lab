# _*_ coding: utf-8 _*_
"""
logclient3forunix.py
Usage $python logclient3forunix.py
"""

import socket
import sys
import os
import time

PORT = 50000
SLEEPTIME = 10

if os.name != "posix":
    print("本プログラムは、unix系OS以外では稼働しません")
    sys.exit()

host = input("接続先サーバ:")
while True:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, PORT))
    except:
        print("接続できません")
        sys.exit()
    loadave = os.getloadavg()
    print(loadave)
    client.sendall(str(loadave).encode("utf-8"))
    client.close()
    time.sleep(SLEEPTIME)
