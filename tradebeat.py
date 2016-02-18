#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import sys
import time
import random

trade_word = [u"Kr\u00F3tka po rynkowej", u"D\u0142uga po rynkowej"]
url = "http://tradebeat.pl/"
useragent = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:44.0) Gecko/20100101 Firefox/44.0"

class get_idea_trade():
    def __init__(self):
        self.user = sys.argv[1]
        self.password = sys.argv[2]
        self.base_url = "%simportant" %(url)
        self.try_num = 0
        self.found_list = {}

    def check_page(self):
        with requests.Session() as c:
            self.main_page = c.get(self.base_url, headers={"User-Agent": useragent})
            self.do_soup(self.main_page, "article")

    def do_soup(self, page, option):
        self.soup = BeautifulSoup(page.content, "lxml")
        if option == "article":
            for art in self.soup.find_all(option):
                self.do_article(art)
        else:
            for art in self.soup.find_all(option):
                print art.text

    def do_article(self, art):
        for trade in trade_word:
            try:
                assert trade in art.text
                print "Found something!"
                if self.check_mem(art.contents[5].find_all("a")[0].get("href")):
                    print art.contents[5].find_all("a")[0].get("href")
                    self.login(art.contents[5].find_all("a")[0].get("href"))
                    self.try_num += 1
                else:
                    print('Nothing new!')
                    self.try_num += 1
            except AssertionError:
                pass

    def check_mem(self, data):
        if data not in self.found_list.values():
            self.found_list[self.try_num]= data
            return True
        else:
            return False

    def login(self, link):
        with requests.Session() as l:
            l.get(url+"user")
            self.phpid= l.cookies["PHPSESSID"]
            self.login_data = {"PHPSESSID": self.phpid,
                               "T[_U]": self.user,
                               "T[_P]": self.password,
                               "T[_A]":0, "T[_A]":1,
                               "Action[login]":1, "T[_B]":''}
            l.post(url+"user", data=self.login_data, headers={"Referer": url+"user"})
            page = l.get(url+link[1:])
            self.do_soup(page, "p")

    def save_to_file(self, data):
        self.time = time.ctime().split(' ')
        self.file_name = "trade-ideas."+self.time[2]+"."+self.time[1]
        with open(self.file_name, "ab") as f:
            f.write(data+"\n")


try:
    p1 = get_idea_trade()
    while True:
        p1.check_page()
        time.sleep(random.randint(300,400))
except KeyboardInterrupt:
    for e in p1.found_list.keys():
        p1.save_to_file(str(e))
        p1.save_to_file(str(p1.found_list[e]))
    sys.exit(1)

