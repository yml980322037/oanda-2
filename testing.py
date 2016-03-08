#!/usr/bin/env python

import logger as log
import unittest
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
import re


description ='''NZDUSD - short at market {0}{1}{2}Justification (04/03/2016):We believe that the market is underpricing the
possibility for the RBNZ to deliver further monetary policy easing in first half of 2016. Subdued inflation growth, deteriorating inflation expectations and weak commodities pri
ces are likely to overshadow scarce signs of economic rebound in New Zealand. Furthermore looming risks in China are going to drive the market sentiment in the months come. We s
ee scope for further NZD sell-off, especially in pairs with USD.Any person acting on this information does so entirely at their own risk. Any research provided does not have reg
ard to the specific investment objectives, financial situation and needs of any specific person who may receive it.'''

trade_word = {"buy": [u"long at market", u"long on market", 
		      u"buy at market", u"buy on market"],
              "sell": [u"short at market", u"short on market",
		       u"sell at market", u"sell on marker"]}

trade_action = {"TP" : ["take profit", "tp:"],
                "SL" : ["stop loss", "sl:"]}

url = "http://tradebeat.com/"
useragent = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:44.0) Gecko/20100101 Firefox/44.0"
instruments = './instruments.yaml'

test_page = './main_page.html'
#test_page = './test_page2.yaml'

class FindInTextTest(unittest.TestCase):

    def setUp(self):
        self.user = ''
        self.password = ''
        self._art_takestop = {}
	self.test_page = test_page
	self.test_page_cont = None
	self.art_data = {}
	self.trades = {}
	self.all_trade_ideas = {}
	self.db = MySQL()


    def check_page(self):
	'''
	Main function which is called every time.
	It's some kind of start process function.
	'''
        with requests.Session() as c:
	    self.do_soup(self.test_page_cont, "article")
	
    def check_instrument(self, title):
	log.print_green('checking instruments...')
	for i in self.instruments_dict.keys():
	    print title
	    print 'i.lower() ', i.lower()
	    if i.lower() in title:
		print '2: ', title
		print '2: i.lower() ', i.lower()
		log.print_green('Found: ', i.lower())
		return i.lower()

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


    def do_article(self, art):
	'''
	check articles from /important page and find keywords from trade_word
	'''
        for trade_list in trade_word.values():
	    for trade in trade_list:
                try:
                    assert trade in art.text.lower()
                    self.art_data["action"] = self.get_action(trade)
		    self.check_artid(self.test_page, {"class": "news urgent"})
                except AssertionError:
                    pass


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
	self.soup = BeautifulSoup(self.test_page_cont, "lxml")
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
	self.soup = BeautifulSoup(page, "lxml")
        if option == "article":
            for art in self.soup.find_all(option):
                #self.do_article(art)
		print art
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
	   


    def import_test_page(self):
	'''
	Importing test_page from mainpage.yaml file
	'''
	try:
	    with open(self.test_page, 'r') as f:
		self.test_page_cont = f.read()
	    log.print_green('Test page imported!')
	except:
	    log.print_error('Test page import failed')

    def import_instruments(self):
	'''
	Importing list of indtrument from instruments.yaml file
	'''
	try:
	    with open('./instruments.yaml', 'r') as f:
		self.instruments_dict = yaml.load(f)
	    log.print_green('Instruments imported!')
	except:
	    log.print_error('Instruments import failed')

    def find_tp_sl(self, info):
	print('finding TP and SL...')
	for action in trade_action.keys():
	    for t in trade_action.get(action):
		try:
		    if t in info.lower():
			self._tmp = self.find_digits(t, info.lower())
			self._art_takestop.update({action : self._tmp})
		except ValueError:
		    pass
	log.print_green(self._art_takestop)

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
	    print 'new result: ', self._result
	    return self._result
	except IndexError:
	    return []


    @unittest.skip("skipping")
    def test_01_value_with_one_comma(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200', 'Stop Loss:0,7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050']}, self._art_takestop) 

    @unittest.skip("skipping")
    def test_02_value_with_two_comma_sl(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200', 'Stop Loss:0,7050, 0,7150')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050', '0.7150']}, self._art_takestop) 

    @unittest.skip("skipping")
    def test_03_value_with_two_comma(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200, 0,6500', 'Stop Loss:0,7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200', '0.6500'], 'SL': ['0.7050']}, self._art_takestop)

    @unittest.skip("skipping")
    def test_04_value_with_three_comma(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200, 0,6500, 0,6700', 'Stop Loss:0,7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200', '0.6500', '0.6700'], 'SL': ['0.7050']}, self._art_takestop)

    @unittest.skip("skipping")
    def test_05_value_with_three_comma_sl(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200', 'Stop Loss:0,7050, 0,7150, 0,7350')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050', '0.7150', '0.7350']}, self._art_takestop) 

    @unittest.skip("skipping")
    def test_06_value_with_one_dot(self):
	self.description = description.format('(open price 0.67580)','Take profit: 0.6200', 'Stop Loss:0.7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050']}, self._art_takestop)

    @unittest.skip("skipping")
    def test_07_value_with_two_dot(self):
	self.description = description.format('(open price 0.67580)','Take profit: 0.6200, 0.6500', 'Stop Loss:0.7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200', '0.6500'], 'SL': ['0.7050']}, self._art_takestop)

    @unittest.skip("skipping")
    def test_08_value_with_three_dot(self):
	self.description = description.format('(open price 0.67580)','Take profit: 0.6200, 0.6500, 0.6700', 'Stop Loss:0.7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200', '0.6500', '0.6700'], 'SL': ['0.7050']}, self._art_takestop)

    @unittest.skip("skipping")
    def test_09_no_tp_dot(self):
	self.description = description.format('(open price 0.67580)','Take profit,', 'Stop Loss:0.7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': [], 'SL': ['0.7050']}, self._art_takestop)

    @unittest.skip("skipping")
    def test_10_no_sl_dot(self):
	self.description = description.format('(open price 0.67580)','Take profit: 0.6200', 'Stop Loss')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': []}, self._art_takestop)

    @unittest.skip("skipping")
    def test_11_no_sl_and_tp(self):
	self.description = description.format('(open price 0.67580)','Take profit:', 'Stop Loss:')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': [], 'SL': []}, self._art_takestop)

    @unittest.skip("skipping")
    def test_12_value_with_one_comma_short(self):
	self.description = description.format('(open price 0,67580)','TP: 0,6200', 'SL:0,7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050']}, self._art_takestop) 

    @unittest.skip("skipping")
    def test_13_value_with_two_comma_short(self):
	self.description = description.format('(open price 0,67580)','TP: 0,6200', 'SL:0,7050, 0,7150')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050', '0.7150']}, self._art_takestop) 

    @unittest.skip("skipping")
    def test_14_value_with_one_comma_mixed(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200', 'sl: 0,7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050']}, self._art_takestop) 

    @unittest.skip("skipping")
    def test_15_value_with_two_comma_mixed(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200', 'SL:0,7050, 0,7150')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050', '0.7150']}, self._art_takestop) 

    @unittest.skip("skipping")
    def test_16_title(self):
	self.instruments_dict = {}
	self.import_instruments()
	self._title = 'caduiyjpy - trade idea 02/03'
	self._instr = self.check_instrument(self._title)
	self.assertEqual(self._instr, 'cadjpy' , self._instr)

    def test_17_check_page(self):
    	self.import_instruments()
        self.import_test_page()
	self.do_soup(self.test_page_cont, 'article')


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(FindInTextTest)
    unittest.TextTestRunner(verbosity=3).run(suite)
