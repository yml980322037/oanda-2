#!/usr/bin/env python

import MySQLdb
import json

class MySQL():
    def __init__(self):
	self.db = MySQLdb.connect('db_server', 'forex', 'pass123', 'forexdb')
	self.cursor= self.db.cursor()
	self.insert_query = ("INSERT INTO trades " "(artID, author, description, instrument, oanda, page_adr, time, title, trade) " "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" )
	self.update_query = ("UPDATE trades SET {0} = '{1}' " "WHERE artID = %s")
	self.select_query = ("SELECT {} FROM trades " "WHERE artID=%s")

    def insert(self, dane):
	try:	
	    self.cursor.execute(self.insert_query, (dane.get('artID', 'NULL'), dane.get('author', ''), json.dumps(dane.get('description', '')), dane.get('instrument', 'NULL'), json.dumps(dane.get('oanda', '')), dane.get('page_adr', ''), json.dumps(dane.get('time', 'NULL')), dane.get('title', 'NULL'), json.dumps(dane.get('trade', ''))))
	    self.db.commit()
	    print('Insert OK!')
	    return 0
	except:
	    print('Inset to databse failed')
	    return 1
	
    
    def update(self, what, onwhat, artID):
	try:
	    print self.update_query.format(what, onwhat, artID)
	    self.cursor.execute(self.update_query.format(what, json.dumps(onwhat)), artID)
	    self.db.commit()
	    print('Update OK!')
	    return 1
	except:
	    print('Update to databse failed')
	    print(what, onwhat, artID)
	    return 0
	 

    def select(self, what, artID):
	self.cursor.execute(self.select_query.format(what), artID)
	return self.cursor.fetchone()

    def __exit__(self):
	self.db.close()

# from database import MySQL
# t = MySQL()
# r = t.select('a105424')
# r = t.select('time', 'a105424')
# t.update('time', '{"1": "2016-02-24 07:08:30", "2": "4016-02-24 17:08:30"}', 'a105424')

