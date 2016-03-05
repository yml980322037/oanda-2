#!/usr/bin/env python

from oandapy import OandaError
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
from database import MySQL
import logger as log
import re

#log.print_error
#log.print_green
#log.print_warning


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
        self.art_data = {}
	self.instruments_dict = {}
	self.trades = {}
	self.all_trade_ideas = {}
	self.db = MySQL()

    def import_instruments(self):
	'''
	Importing list of indtrument from instruments.yaml file
	'''
	try:
	    with open(instruments, 'r') as f:
		self.instruments_dict = yaml.load(f)
	    log.print_green('Instruments imported!')
	except:
	    log.print_error('Instruments import failed')

    def check_page(self):
	'''
	Main function which is called every time.
	It's some kind of start process function.
	'''
        with requests.Session() as c:
            self.main_page = c.get(self.base_url, headers={"User-Agent": useragent})
            self.do_soup(self.main_page, "article")

    def do_article(self, art):
	'''
	check articles from /important page and find keywords from trade_word
	'''
        for trade_list in trade_word.values():
	    for trade in trade_list:
                try:
                    assert trade in art.text.lower()
                    self.art_data["action"] = self.get_action(trade)
                    self.login(art.contents[5].find_all("a")[0].get("href"))
                except AssertionError:
                    pass

    def login(self, link):
	'''
	Login function. This function use detailes passed into tadebeat.py
	'''
        with requests.Session() as l:
            l.get(url+"user")
            self.phpid= l.cookies["PHPSESSID"]  #save token
            self.login_data = {"PHPSESSID": self.phpid, #create login dictionary with details
                               "T[_U]": self.user,
                               "T[_P]": self.password,
                               "T[_A]":0, "T[_A]":1,
                               "Action[login]":1, "T[_B]":''}
            l.post(url+"user", data=self.login_data, headers={"Referer": url+"user"}) # send post request to login page
            page = l.get(url+link[1:]) # send get request to article page
	    self.check_artid(page, {"class": "news urgent"}) # pass page content for checking process

    def ask_database(self, what, artID):
	self._result = self.db.select(what, artID)
	if self._result:
	    for data in self._result:
		self._result_dict = yaml.load(data)
	    return self._result_dict
	else:
	    log.print_warning('Nothing found!')
	    return 0

    def check_artid(self, page, option):
	self.soup = BeautifulSoup(page.content, "lxml")
	self.art = self.soup.find('article', option)
	if self.ask_database('time', self.art.get("id")):
	    log.print_green('Found something with has same articleID in database already...')
	    self.check_timestamp(self.art.get("id"), self.art) #  checking if article is an update, or old one
	    return
	else:
	    log.print_warning('Found something new!')
	    self.do_soup(page, option)

    def check_timestamp(self, artID, content):
	'''
	compare timestamp of last entry in time key
	'''
	print('I am going to compare timestamps')
	#self._old_time = self.all_trade_ideas.get(artID).get('time')[len(self.all_trade_ideas.get(artID).get('time'))]
	self._old_time = self.ask_database('time', artID)
	print artID
	print self._old_time
	print len(self._old_time)
	self._old_time = self._old_time.values()[-1]
	self._new_time = content.find("time").get("datetime")
	if self._old_time == self._new_time:
	    print('No updates')
	    return
	else:
	    print('Update of article has been detected!')
	    return self.do_update(self._new_time)

    def do_soup(self, page, option):
        self.soup = BeautifulSoup(page.content, "lxml")
	#self.save_to_yaml('mainpage', self.soup.prettify())
        if option == "article":
            for art in self.soup.find_all(option):
                self.do_article(art)
        else:
            self.art = self.soup.find('article', option)
	    self.do_collect_info(self.art, page.url.encode('ascii', 'ignore'))

    def do_collect_info(self, art, pageurl):
	self.save_to_yaml('page', str(art))
        self._art_data = {} #internal variable to hold article data	
	log.print_green("Let's start with ", art.find("h1").text.lower())
	self._art_data = tradeClass()
	self._art_data.title = art.find("h1").text.lower().encode('ascii', 'ignore')
	self._art_data.add_time(art.find("time").get("datetime"))
	self._art_data.ID = art.get("id")
	self._art_data.page_adr = pageurl
	self._art_data.instrument = self.check_instrument(self._art_data.title)
	for p in art.find('div').find_all('p'): #.text.encode('ascii', 'ignore')
	    self._art_data.description += p.text.encode('ascii', 'ignore')
	log.print_warning('###### description ##### ', self._art_data.description)
        self.find_tp_sl(self._art_data.description) # find take profit and sl values
	self._art_data.author = art.find('section', {'class' : 'autor'}).find('div', {'class' : 'about'}).find('h1').text.encode('ascii', 'ignore')
	#self._art_data.add_trade(self.art_data['action'], self._art_data.takestop)
	#log.print_warning(art.find('div').find('p').text.encode('ascii', 'ignore'))
	self._art_data.do_all_data()
	self.do_trade(self._art_data.takestop)
	if self._art_data.trade: self.place_order(self._art_data.all_data, len(self._art_data.trade))
	#log.print_warning('trade: ', self._art_data.trade)
	#log.print_warning('len: ', len(self._art_data.trade))
	self._art_data.do_all_data()
	self.trades.update({self._art_data.ID : self._art_data.all_data})
	self.save_to_yaml(self._art_data.ID, self._art_data.all_data)
	self.save_to_yaml_all(self.trades)
	self.db.insert(self._art_data.all_data) #insert all data to database
	self.trades = {}
	return

    def do_trade(self, value):
	log.print_green('Do trade with value: ', value)
	try:
    	    for i in range(0,max(len(value.get('SL')), len(value.get('TP')))):
	        log.print_green(i)
    	        try:
		    self._temp = {}
            	    self._temp.update({'SL' : value.get('SL')[0], 'TP': value.get('TP')[i]})
            	    log.print_green('temp1: ', self._temp)
		    self._art_data.add_trade(self.art_data['action'], self._temp)
    	    	except IndexError:
		    self._temp = {}
		    log.print_green('temp2: ', self._temp)
        	    self._temp.update({'SL' : value.get('SL')[i], 'TP': value.get('TP')[0]})
		    self._art_data.add_trade(self.art_data['action'], self._temp)
	except TypeError:
	    self._art_data.trade = ''
	    

    def check_instrument(self, title):
	log.print_green('checking instruments...')
	for i in self.instruments_dict.keys():
	    if i.lower() in title:
		log.print_green('Found: ', i.lower())
		return i.lower()


    def find_tp_sl(self, info):
	log.print_green('finding TP and SL...')
	for action in trade_action.keys():
	    for t in trade_action.get(action):
		try:
		    if t in info.lower():
			self._tmp = self.find_digits(t, info.lower())
			self._art_data.add_takestop(action, self._tmp)
		except ValueError:
		    pass
	log.print_green('takestop: ', self._art_data.takestop)

    def do_update(self,new_time):
	'''
	do update for article
	'''
	print("Let's check what has been updated")
	self._art_data.add_time(new_time)
	return

    def get_action(self, action):
	'''
	get action like, buy or sell
	'''
	for t in trade_word.keys():
	    if action in trade_word.get(t):
		return t

    def find_digits(self, what, where):
	self._result = 0
	self._compile = "{}.[0-9\s.,]+".format(what)
	try:
	    self._result = re.findall(self._compile, where)[0]
	    self._result = self._result.split(':')[1]
	    self._result = self._result.split(', ')
	    for i in range(0, len(self._result)):
		self._result[i] = self._result[i].replace(' ', '')
		self._result[i] = self._result[i].replace(',', '.')
	    return self._result
	except IndexError:
	    return []


    def save_to_yaml_all(self, data):
        self._time = time.ctime().split(' ')
	self._time.remove('')
        self._dir_name = "./%s-%s/" % (self._time[2], self._time[1])
        self._file_name = 'all_trade_ideas.yaml'
        try:
            with open(self._file_name, "ab") as f:
                yaml.dump(data, f)
		log.print_green('All data has been saved to: ', self._file_name)
        except IOError:
	    log.print_error('Error during saving: ', self._file_name)

    def save_to_yaml(self, fname,data):
        self._time = time.ctime().split(' ')
	self._time.remove('')
        self._dir_name = "./%s-%s/" % (self._time[2], self._time[1])
        self._file_name = self._dir_name + fname + '.yaml'
        try:
            with open(self._file_name, "ab") as f:
                yaml.dump(data, f)
        except IOError:
            os.makedirs(self._dir_name)
            with open(self._file_name, "ab") as f:
                yaml.dump(data, f)

    def place_order(self, data, i):
	'''
	Funtion to place an order with ST and TP parameters
	'''
	log.print_green('Placing an order...')
        self._instr = self.instruments_dict.get(data.get('instrument').upper())[0].get('instrument')
	self._unit = self.instruments_dict.get(data.get('instrument').upper())[3].get('tradeUnit')
	for x in range(1,(i+1)):
	    self._action = data.get('trade')[x].keys()[0]
    	    self._tp = data.get('trade')[x][self._action]['TP'] 
    	    self._sl = data.get('trade')[x][self._action]['SL']
	    log.print_warning(self._instr, self._unit, self._action, self._tp, self._sl)
	    self.ordr = order.MyOanda(self._instr, self._unit, self._action, self._sl, self._tp)
	    try:
	    	self._art_data.add_oanda(self.ordr.create_order())
	    except OandaError:
	    	log.print_error('Placing a order failed')
	return
# Find take profit and stop loss values from description section:
    def outer(self, u, value = str()):
	log.print_warning('!!wchodze z u: ', u)
	if self.find_digit(u).isdigit():
	    while (self.find_digit(u).isdigit() or self.find_digit(u) == '.' or self.find_digit(u) == ','):
                value += value.join(self.find_digit(u))
		log.print_warning("na poczatku while: ", self.find_digit(u))
	        if self.find_digit(u) == ',':
		    log.print_warning("if self.find_digit(u) == ',' ", self.find_digit(u))
		    if (self.find_digit(u+1).isdigit() or self.find_digit(u+2).isdigit()):
			#value += value.join(self.find_digit(u))
			log.print_warning("if self.find_digit(u+1).isdigit() ", value)
			u += 1
			#return self.outer(u+1, value.replace(',','.'))
		    else:
			return value[:-1].encode('ascii', 'ignore')
			#return self.outer(u+1, value.replace(',','.'))
			#return self.outer(u+1, value)
		#value += value.join(self.find_digit(u))
		log.print_warning("na koncu while ", value)
		u +=1
            return value.encode('ascii', 'ignore')
        else:
            return self.outer(u+1)

    def find_digit(self, x):
        self._txt = self._art_data.description
        return self._txt[x:(x+1)]
# end of section

    def check_time(self):
        self._mytime = time.ctime().split(' ')
	self._mytime.remove('')
	self._mytime = self._mytime[3][:5]
        return self.timeframe >= self._mytime

try:
    p1 = get_idea_trade()
    p1.import_instruments()
    while  p1.check_time():
        p1.check_page()
        time.sleep(random.randint(300,600))
except KeyboardInterrupt:
    sys.exit(1)

