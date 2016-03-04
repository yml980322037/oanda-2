#!/usr/bin/env python
import logging
import time
import os


class bcolors:
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    OKGREEN = '\033[92m'

# log file name with date generator
log_file = './logs/tradebeat-' + time.strftime("%Y%m%d-%H%M") + '.log'

# logging config
logg = logging.getLogger('TradeBeat')
logg.setLevel(logging.DEBUG)

# create console handler and set level to debug
try:
    ch = logging.FileHandler(log_file)
    ch.setLevel(logging.DEBUG)
except IOError:
    os.makedirs('./logs')
    ch = logging.FileHandler(log_file)
    ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logg
logg.addHandler(ch)


def print_error(*argv):
    logg.error(argv)
    print bcolors.FAIL + argv + bcolors.ENDC


def print_warning(*argv):
    logg.warning(argv)
    print bcolors.WARNING + argv + bcolors.ENDC


def print_green(*argv):
    logg.info(argv)
    print bcolors.OKGREEN + argv + bcolors.ENDC
