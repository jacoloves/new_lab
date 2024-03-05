# _*_ coding: utf-8 _*_
"""
gethostbyname.py

usange pytnon gethostbyname.py
"""

import socket

while True:
    try:
        hostname = input("ホスト名を入力（qで終了）:")
        if hostname == "q":
            break
        print(socket.gethostbyname(hostname))
    except:
        print("変換できませんでした")
        
