# _*_ coding: utf-8 _*_
"""
getdata.py
Usage $python getdata.py
"""

import urllib.request
from html.parser import HTMLParser

DURL = "http://localhost:8080/"


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        print(data)


url = input("取得先URL:")
if url == "":
    url = DURL

chcode = input("文字コード:")
if chcode == "":
    chcode = "UTF-8"

urlinfo = urllib.request.urlopen(url)
html = urlinfo.read()

parser = MyHTMLParser()
parser.feed(html.decode(chcode))
