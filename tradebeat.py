#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
from trade import *
import sys
import time
import random
import json
import yaml
import os
import order

#trade_word = [u"kr\u00F3tka po rynkowej", u"kr\u00F3tka po cenie rynkowej",
#              u"d\u0142uga po rynkowej", u"d\u0142uga po cenie rynkowej",
#              u"zamkni\u0119ta"]

trade_word = {"buy": [u"long at market", u"long on market", 
		      u"buy at market", u"buy on market"],
              "sell": [u"short at market", u"short on market",
		       u"sell at market", u"sell on marker"]}

trade_action = {"TP" : ["take profit", "tp:"],
                "SL" : ["stop loss", "sl:"]}

url = "http://tradebeat.com/"
useragent = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:44.0) Gecko/20100101 Firefox/44.0"
instruments = './instruments.yaml'


class get_idea_trade():

    def __init__(self):
        self.user = sys.argv[1]
        self.password = sys.argv[2]
        self.timeframe = sys.argv[3]
        self.base_url = "%simportant" %(url)
        self.try_num = 0
        self.found_list = {}
        self.art_list = {}
        self.art_data = {}
	self.instruments_dict = {}
	self.trades = {}
	
    def check_page(self):
        with requests.Session() as c:
            self.main_page = c.get(self.base_url, headers={"User-Agent": useragent})
            self.do_soup(self.main_page, "article")

    def import_instruments(self):
	try:
	    with open(instruments, 'r') as f:
		self.instruments_dict = yaml.load(f)
	    print('Instruments imported!')
	except:
	    print('Instruments import failed')

    def check_instrument(self, title):
	print('checking instruments...')
	for i in self.instruments_dict.keys():
	    if i.lower() in title:
		return i.lower()

    def find_tp_sl(self, info):
	print('finding TP and SL...')
	#print info
	for action in trade_action.keys():
	    for t in trade_action.get(action):
		try:
		    self._art_data.add_takestop(action, self.outer(info.lower().index(t)))
		except ValueError:
		    pass

    def do_soup(self, page, option):
        self._art_data = {} #internal variable to hold article data
        self.soup = BeautifulSoup(page.content, "lxml")
        if option == "article":
            for art in self.soup.find_all(option):
                self.do_article(art)
        else:
            self.art = self.soup.find('article', option)
            print "Let's start with ", self.art.find("h1").text.lower()
	    self._art_data = tradeClass()
	    self._art_data.title = self.art.find("h1").text.lower().encode('ascii', 'ignore')
	    self._art_data.add_time(self.art.find("time").get("datetime"))
	    self._art_data.page_adr = page.url.encode('ascii', 'ignore')
	    self._art_data.ID = self.art.get("id")
	    self._art_data.instrument = self.check_instrument(self._art_data.title)
	    self._art_data.description = self.art.find('div').text.encode('ascii', 'ignore')
            self.find_tp_sl(self._art_data.description) # find take profit and sl values
	    self._art_data.add_trade(self._art_data.takestop)
	    self._art_data.author = self.art.find('section', {'class' : 'autor'}).text.encode('ascii', 'ignore')
	    self._art_data.do_all_data()
	    self.trades.update({self._art_data.ID : self._art_data.all_data})
	    self.save_to_yaml(self._art_data.ID, self._art_data.all_data)
	    self.save_to_file(self._art_data.ID, self.trades)
	   # self.place_order(self._art_data.all_data)

    def do_article(self, art): # check articles from /important page and find keywords from trade_word
        for trade_list in trade_word.values():
	    for trade in trade_list:
                try:
                    assert trade in art.text.lower()
                    if self.check_mem(art.contents[5].find_all("a")[0].get("href")):
                        print "\nFound something!\n"
	#		print art
                        self.art_data["action"] = self.get_action(trade)
                        self.login(art.contents[5].find_all("a")[0].get("href"))
                        self.try_num += 1
                    else:
                        self.try_num += 1
                except AssertionError:
                    pass

    def get_action(self, action):
	for t in trade_word.keys():
	    if action in trade_word.get(t):
		return t

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
            self.do_soup(page, {"class": "news urgent"})

    def save_to_file(self, fname, data):
        self._time = time.ctime().split(' ')
        self._dir_name = "./%s-%s/" % (self._time[2], self._time[1])
        self._file_name = self._dir_name + fname
        try:
            with open(self._file_name, "ab") as f:
                json.dump(data, f)
        except IOError:
            os.makedirs(self._dir_name)
            with open(self._file_name, "ab") as f:
                json.dump(data, f)

    def save_to_yaml(self, fname,data):
        self._time = time.ctime().split(' ')
        self._dir_name = "./%s-%s/" % (self._time[2], self._time[1])
        self._file_name = self._dir_name + fname + '.yaml'
        try:
            with open(self._file_name, "ab") as f:
                yaml.dump(data, f)
        except IOError:
            os.makedirs(self._dir_name)
            with open(self._file_name, "ab") as f:
                yaml.dump(data, f)


    def place_order(self, data):
	print('Placing order...')
        self._instr = self.instruments_dict.get(data.get('instrument').upper())[0].get('instrument')
	self._unit = self.instruments_dict.get(data.get('instrument').upper())[3].get('tradeUnit')
	self._action = data.get('action')
	self._tp = data.get("TP")
	self._sl = data.get("SL")
	print self._instr, self._unit, self._action, self._tp, self._sl
	self.ordr = order.MyOanda(self._instr, self._unit, self._action, self._sl, self._tp)
	try:
	    self._response = self.ordr.create_order()
	    print self._response
	except:
	    print('Place order failed')
	    pass
# Find take profit and stop loss values from description section:
    def inner(self, z):
        if z.isdigit():
            return True
        else:
            return False

    def inner2(self, z):
        if z.isdigit() or z == ".": # or z == ",":
            return True
        else:
            return False

    def outer(self, u):
        self._value = str()
        if self.inner(self.ble(u)):
            while self.inner2(self.ble(u)):
                self._value += self._value.join(self.ble(u))
                u +=1
            return (self._value).encode('ascii', 'ignore')
        else:
            return self.outer(u+1)

    def ble(self, x):
        self.txt = self._art_data.description
        return self.txt[x:(x+1)]
# end of section

    def check_time(self):
        self._mytime = time.ctime().split(' ')[3][:5]
        return self.timeframe >= self._mytime

try:
    p1 = get_idea_trade()
    p1.import_instruments()
    while  p1.check_time():
        p1.check_page()
        time.sleep(random.randint(300,400))
    p1.save_to_yaml("trade-ideas", p1.trades) # save all info to one file
except KeyboardInterrupt:
    p1.save_to_yaml("trade-ideas", p1.trades) # save all info to one file
    sys.exit(1)

