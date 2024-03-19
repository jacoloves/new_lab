# _*_ coding: utf-8 _*_
"""
browser.py
Usage $python browser.py
"""

import webbrowser

DURL = "http://localhost:8080/"

url = input("取得先URL:")
if url == "":
    url = DURL

webbrowser.open(url)
