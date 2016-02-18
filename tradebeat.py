#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import sys
import time

trade_word = [u"Kr\u00F3tka po rynkowej", u"D\u0142uga po rynkowej"]
url = "http://tradebeat.pl/"

class get_idea_trade():
    def __init__(self):
        self.user = sys.argv[1]
        self.password = sys.argv[2]
        self.base_url = "%simportant" %(url)
        self.try_num = 0
        self.found_list = {}

    def check_page(self):
        with requests.Session() as c:
            self.main_page = c.get(self.base_url)
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
                    print art.contents[5].find_all("a")[0].get("href")
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
            print page.url
            self.do_soup(page, "p")

try:
    p1 = get_idea_trade()
    while True:
        p1.check_page()
        time.sleep(300)
except KeyboardInterrupt:
    sys.exit(1)

    #url = "http://tradebeat.pl/user"
    #user = "maciej.szopinski@gmail.com"
    #c.get(url)
    #coockie = c.cookies["PHPSESSID"]
    #login_data = {"PHPSESSID": coockie,"T[_U]": user, "T[_P]": password, "T[_A]":0, "T[_A]":1, "Action[login]":1, "T[_B]":''}
    #c.post(url, data=login_data, headers={"Referer": "http://tradebeat.pl/user"})
    #page = c.get("http://tradebeat.pl/dax-trade-idea-16-02-zamkniEta/")
    #soup = BeautifulSoup(page.content, "lxml")
    #for p in soup.find_all("p"):
    #    print p.text
    # u"Kr\u00F3tka po rynkowej"
    # u"D\u0142uga po rynkowej" in article[3].text
