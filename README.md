<h1>Introduction</h1>

Let me introduce to you amazing spider script for oanda broker! :)

Generally this script does check trade ideas from tradebeat.com/important page (every 5-10 min) and place order to oanda broker practice account.

<h1>Requirements:</h1>
- account on tradebeat.com with market access
- database MySQL:
    - database name: forexdb
    - table name: trades
    - user name: forex
    - user pass: pass123
    - grand access for fores: add, select, update
- oandapy, json, yaml, BeautifulSoup

<h1>How to run in:</h1>
python tradebeat.py 'login' 'pass' 'end_time'

- login - it's login to tradebeat.com
- pass - your password to tradebeat.com
- end_time - at what local time script should end (please keep in mind that guys from tradebeat.com works till 21:00 GMT+1)

<h1>Logging</h1>
logger.py is responsible for logging. All logs are in ./logs folder
 
