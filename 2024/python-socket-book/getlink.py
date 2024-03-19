# _*_ coding: utf-8 _*_
"""
getlink.py
Usage $python getlink.py
"""

import urllib.request
from html.parser import HTMLParser

DURL = "http://localhost:8080/"


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            print(attrs)

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass


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
