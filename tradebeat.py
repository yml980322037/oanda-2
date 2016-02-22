#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import sys
import time
import random
import json
import ipdb
import os


trade_word = [u"kr\u00F3tka po rynkowej", u"kr\u00F3tka po cenie rynkowej",
              u"d\u0142uga po rynkowej", u"d\u0142uga po cenie rynkowej",
              u"zamkni\u0119ta"]

trade_action = {"TP" : ["take profit", "tp:"],
		"SL" : ["stop loss", "sl:"]}

url = "http://tradebeat.pl/"
useragent = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:44.0) Gecko/20100101 Firefox/44.0"

class get_idea_trade():
    def __init__(self):
        self.user = sys.argv[1]
        self.password = sys.argv[2]
        self.timeframe = sys.argv[3]
        self.base_url = "%simportant" %(url)
        self.try_num = 0
        self.found_list = {}
	iself.art_list = {}
	self.art_data = {}

    def check_page(self):
        with requests.Session() as c:
            self.main_page = c.get(self.base_url, headers={"User-Agent": useragent})
            self.do_soup(self.main_page, "article")

    def do_soup(self, page, option):
	self._temp = [] #internal temporary veriable, used to find intrument's symbol
	self._art_data = {} #internal variable to hold article data
	self._art_list = {}
        self.soup = BeautifulSoup(page.content, "lxml")
        if option == "article":
            for art in self.soup.find_all(option):
                self.do_article(art)
        else:
            self.art = self.soup.find_all('article', option)
        print "Let's start with ", self.art[0].find("h1").text.lower()
        self._art_data["title"]= self.art[0].find("h1").text.lower()
        self._art_data["time"]= self.art[0].find("time").get("datetime")
        self._art_data['page'] = page.url
            for item in self.art[0].find_all("li"): # this one is to find tags and take instrument symbol from it
		self._temp.append(item.text)
        self._art_data["instrument"] = self._temp[1]
        print "Instrument: ", self._temp[1]
        for item in self.art: # take description
		self._art_data['description'] = item.contents[3].text.lower() # description from page (save to database)
        for action in trade_action.keys(): # find action keywords from trade_action list words
            for t in trade_action.get(action):
            try:
			self._art_data[action] = self.outer(self._art_data.get('description', '').index((t)))
			print "%s, value: %s" % (t, self._value)
                except ValueError:
			pass
        print "action: ", self.art_data["action"]
        self._art_list[self.art[0].get("id")] = self._art_data
        self._art_list[self.art[0].get("id")].update(self.art_data)
        self.art_list.update(self._art_list)
        self.save_to_file(self.art[0].get("id"), self._art_list)

    def do_article(self, art): # check articles from /important page and find keywords from trade_word
        for trade in trade_word:
            try:
                assert trade in art.text.lower()
                if self.check_mem(art.contents[5].find_all("a")[0].get("href")):
                    print "\nFound something!"
            self.art_data["action"] = self.get_action(trade)
                    self.login(art.contents[5].find_all("a")[0].get("href"))
                    self.try_num += 1
                else:
                  #  print('\nNothing new!')
                    self.try_num += 1
            except AssertionError:
                pass
    def get_action(self, action):
	if action in trade_word[:2]:
        return "sell"
	elif action in trade_word[2:4]:
        return "buy"
	else:
        return "error"

    def check_mem(self, data): # section to check if trade idea has been found before (need change to use art_id)
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

    def save_to_file(self, fname, data):
        self.time = time.ctime().split(' ')
	self.dir_name = "./%s-%s/" % (self.time[2], self.time[1])
        self.file_name = self.dir_name + fname
	try:
            with open(self.file_name, "ab") as f:
                json.dump(data, f)
	except IOError:
        os.makedirs(self.dir_name)
        with open(self.file_name, "ab") as f:
		json.dump(data, f)


# Find take profit and stop loss values from description section:
    def inner(self, z):
        if z.isdigit():
                return True
        else:
                return False

    def inner2(self, z):
        if z.isdigit() or z == "." or z == ",":
                return True
        else:
                return False

    def outer(self, u):
	self._value = str()
        if self.inner(self.ble(u)):
                while self.inner2(self.ble(u)):
                        self._value += self._value.join(self.ble(u))
                        u +=1
                return self._value
        else:
                return self.outer(u+1)

    def ble(self, x):
	self.txt = self._art_data.get('description', '')
        return self.txt[x:(x+1)]
# end of section

    def check_time(self):
        self._mytime = time.ctime().split(' ')[3][:5]
        return self.timeframe in self._mytime


try:
    p1 = get_idea_trade()
    while not p1.check_time():
        p1.check_page()
        time.sleep(random.randint(300,400))
    p1.save_to_file("trade-ideas", p1.art_list) # save all info to one file
except KeyboardInterrupt:
    p1.save_to_file("trade-ideas", p1.art_list) # save all info to one file
    sys.exit(1)

