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


description ='''NZDUSD - short at market {0}{1}{2}Justification (04/03/2016):We believe that the market is underpricing the
possibility for the RBNZ to deliver further monetary policy easing in first half of 2016. Subdued inflation growth, deteriorating inflation expectations and weak commodities pri
ces are likely to overshadow scarce signs of economic rebound in New Zealand. Furthermore looming risks in China are going to drive the market sentiment in the months come. We s
ee scope for further NZD sell-off, especially in pairs with USD.Any person acting on this information does so entirely at their own risk. Any research provided does not have reg
ard to the specific investment objectives, financial situation and needs of any specific person who may receive it.'''

trade_action = {"TP" : ["take profit", "tp:"],
                "SL" : ["stop loss", "sl:"]}



class FindInTesxTest(unittest.TestCase):

    def setUp(self):
        self._art_takestop = {}
	
   

    def find_tp_sl(self, info):
	print('finding TP and SL...')
	for action in trade_action.keys():
	    for t in trade_action.get(action):
		try:
		    log.print_green('index %s of %s' % (info.lower().index(t), t))
		    self._tmp = self.outer(info.lower().index(t))
		    #self._art_takestop.update({action} : {self._tmp.split(',')})
		    self._art_takestop.update({action : self._tmp.split(',')})
		except ValueError:
		    pass
	log.print_green(self._art_takestop)

    def outer(self, u, value = str()):
	log.print_warning('!!wchodze z u: ', u)
	if self.find_digit(u).isdigit():
	    while (self.find_digit(u).isdigit() or self.find_digit(u) == '.' or self.find_digit(u) == ','):
                value += value.join(self.find_digit(u))
		log.print_warning("na poczatku while: ", self.find_digit(u))
	        if self.find_digit(u) == ',':
		    log.print_warning("if self.find_digit(u) == ',' ", self.find_digit(u))
		    if (self.find_digit(u+1).isdigit() or self.find_digit(u+2).isdigit()):
			log.print_warning("if self.find_digit(u+1).isdigit() ", value)
			value += value.join(self.find_digit(u+1))
			#value = value.replace(',','.')
			u += 1
		    else:
			#value = value.replace(',','.')
			return value[:-1].encode('ascii', 'ignore')
		log.print_warning("na koncu while ", value)
		value = value.replace(',','.')
		u +=1
            return value.encode('ascii', 'ignore')
        else:
            return self.outer(u+1)

    def find_digit(self, x):
        self._txt = self.description
        return self._txt[x:(x+1)]

    def test_01_value_with_one_comma(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200', 'Stop Loss:0,7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050']}, self._art_takestop) 

    def test_02_value_with_two_comma_sl(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200', 'Stop Loss:0,7050, 0,7150')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050, 0.7150']}, self._art_takestop) 

    def test_03_value_with_two_comma(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200, 0,6500', 'Stop Loss:0,7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200', '0,6500'], 'SL': ['0.7050']}, self._art_takestop)

    def test_04_value_with_three_comma(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200, 0,6500, 0,6700', 'Stop Loss:0,7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200', '0,6500', '0,6700'], 'SL': ['0.7050']}, self._art_takestop)

    def test_05_value_with_three_comma_sl(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200', 'Stop Loss:0,7050, 0,7150, 0,7350')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050, 0.7150, 0.7350']}, self._art_takestop) 

    def test_06_value_with_one_dot(self):
	self.description = description.format('(open price 0.67580)','Take profit: 0.6200', 'Stop Loss:0.7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050']}, self._art_takestop)

    def test_07_value_with_two_dot(self):
	self.description = description.format('(open price 0.67580)','Take profit: 0.6200, 0.6500', 'Stop Loss:0.7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200', '0.6500'], 'SL': ['0.7050']}, self._art_takestop)

    def test_08_value_with_three_dot(self):
	self.description = description.format('(open price 0.67580)','Take profit: 0.6200, 0.6500, 0.6700', 'Stop Loss:0.7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200', '0.6500', '0.6700'], 'SL': ['0.7050']}, self._art_takestop)

    def test_09_no_tp_dot(self):
	self.description = description.format('(open price 0.67580)','Take profit,', 'Stop Loss:0.7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': [], 'SL': ['0.7050']}, self._art_takestop)

    def test_10_no_sl_dot(self):
	self.description = description.format('(open price 0.67580)','Take profit: 0.6200', 'Stop Loss')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': []}, self._art_takestop)

    def test_11_no_sl_and_tp(self):
	self.description = description.format('(open price 0.67580)','Take profit:', 'Stop Loss:')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': [], 'SL': []}, self._art_takestop)

    def test_12_value_with_one_comma_short(self):
	self.description = description.format('(open price 0,67580)','TP: 0,6200', 'SL:0,7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050']}, self._art_takestop) 

    def test_13_value_with_two_comma_short(self):
	self.description = description.format('(open price 0,67580)','TP: 0,6200', 'SL:0,7050, 0,7150')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050, 0.7150']}, self._art_takestop) 

    def test_14_value_with_one_comma_mixed(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200', 'sl: 0,7050')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050']}, self._art_takestop) 

    def test_15_value_with_two_comma_mixed(self):
	self.description = description.format('(open price 0,67580)','Take profit: 0,6200', 'SL:0,7050, 0,7150')
	print self.description
	self.find_tp_sl(self.description)
	self.assertEqual(self._art_takestop, {'TP': ['0.6200'], 'SL': ['0.7050, 0.7150']}, self._art_takestop) 


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(FindInTesxTest)
    unittest.TextTestRunner(verbosity=3).run(suite)
