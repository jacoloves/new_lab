# _*_ coding: utf-8 *_
"""
urlopen.py
Usage $python urlopen.py
"""

import urllib.request

DURL = "http://localhost:8080/"

url = input("取得先URL:")
if url == "":
    url = DURL

chcode = input("文字コード:")
if chcode == "":
    chcode = "UTF-8"

urlinfo = urllib.request.urlopen(url)

html = urlinfo.read()

print(html.decode(chcode))
