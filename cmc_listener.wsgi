#!/usr/bin/python
import sys

path = "/home/itdtin/CoinmarketcapListener"
if path not in sys.path:
    sys.path.insert(0, path)

from CoinmarketcapListener.app import app as application
