#!/usr/bin/env python

class tradeClass():
    def __init__(self):
        self.ID = None
        self.description = None
        self.time = {}
        self.trade = {}
        self.title = None
        self.author = None
        self.page_adr = None
        self.instrument = None
        self.oanda_respond = {}
	self.takestop = {}


    def add_trade(self, action, data):
	self.trade.update({len(self.trade)+1 : {action : data}})

    def add_time(self, new_time):
	self.time.update({len(self.time)+1 : new_time})

    def add_takestop(self, action, data):
	self.takestop.update({action : data})

    def add_oanda(self, data):
	self.oanda_respond.update({data})

    def do_all_data(self):
        self.all_data = {'artID' : self.ID,
                         'instrument' : self.instrument,
                         'trade': self.trade,
                         'page_adr' : self.page_adr,
                         'time' : self.time,
                         'title' : self.title,
                         'description': self.description,
                         'author' : self.author,
			 'oanda' : self.oanda_respond }


    def show_all(self):
	print self.all_data

"""
from trade import *
orderek = tradeClass()
orderek.ID = 'a1234'
orderek.description = 'lalal lala'
orderek.add_time(['Mon', '21:21'])
orderek.title = 'trade idea na buziaki'
orderek.add_trade({'buy' : {'ST' : 1500, 'TP' : 1908}})
orderek.instrument = 'EURUSD'
orderek.page_adr = 'www.wp.pl'
orderek.author = 'Stefan W.'
orderek.do_all_data()
orderek.add_trade({'buy' : {'ST' : 91500, 'TP' : 91908}})

"""
