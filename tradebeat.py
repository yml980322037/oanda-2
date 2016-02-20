#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import sys
import time
import random
import json

trade_word = [u"kr\u00F3tka po rynkowej", u"d\u0142uga po rynkowej",
              u"kr\u00F3tka po cenie rynkowej", u"d\u0142uga po cenie rynkowej",	      u"take profit", u"stop loss", u"zamkni\u0119ta", u"st:", u"tp:"]

url = "http://tradebeat.pl/"
useragent = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:44.0) Gecko/20100101 Firefox/44.0"

class get_idea_trade():
    def __init__(self):
        self.user = sys.argv[1]
        self.password = sys.argv[2]
        self.base_url = "%simportant" %(url)
        self.try_num = 0
        self.found_list = {}
	self.value = str()
	self.art_list = {}
	self.art_data = {}

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
            self.art = self.soup.find_all('article', option)
	    self.art_data["title"]= self.art[0].find("h1").text.lower()
	    self.art_data["time"]= self.art[0].find("time").get("datetime")
            for item in self.art:
	#	self.art_obj[str(self.art[0].get("id"))] = {"title": self.art[0].find("h1").text.lower()}
		self.art_data['description'] = item.contents[3].text.lower() # description from page (save to database)
	#	print self.text.get(self.art_id, "error")
	    self.art_list[self.art[0].get("id")] = self.art_data
	    print self.art_list
    
    def do_article(self, art):
        for trade in trade_word:
            try:
                assert trade in art.text.lower()
                if self.check_mem(art.contents[5].find_all("a")[0].get("href")):
                    print "\nFound something!"
		    print art.contents[5].find_all("a")[0].get("href")
                    self.login(art.contents[5].find_all("a")[0].get("href"))
                    self.try_num += 1
                else:
                    print('\nNothing new!')
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
            self.do_soup(page, {'class': 'news urgent'})

    def save_to_file(self, data):
        self.time = time.ctime().split(' ')
        self.file_name = "trade-ideas."+self.time[2]+"."+self.time[1]
        with open(self.file_name, "ab") as f:
            json.dump(data, f)




try:
    p1 = get_idea_trade()
    while True:
        p1.check_page()
        time.sleep(random.randint(300,400))
except KeyboardInterrupt:
#    for e in p1.found_list.keys():
#        p1.save_to_file(str(e))
#        p1.save_to_file(str(p1.found_list[e]))
    p1.save_to_file(p1.art_list)
    sys.exit(1)

