#!/usr/env/ python
import oandapy


class MyOanda():
    def __init__(self, instrument, units, side, stopLoss, takeProfit):
	self.accountID = "8098814"
	self.token = "651c24e0df293921aa1d299195f42d9a-fb0a7be5c893a749d4593c2bef6e8730"
	self.response = dict()
	self.oanda = oandapy.API(environment="practice", access_token=self.token)
	self.instrument = instrument
	self.units = units
	self.side = side
	self.stopLoss = stopLoss
	self.takeProfit= takeProfit

    def create_order(self):

	self.response = self.oanda.create_order(account_id=self.accountID,
    				      instrument=self.instrument,
    				      units=self.units,
    				      side=self.side,
    				      type='market',
				      stopLoss=self.stopLoss,
				      takeProfit=self.takeProfit)

	if self.response:
	    print('Order placed with success')
	    return self.response
	else:
	    print('error with order')
	    return False
