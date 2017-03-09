import requests
import os, sys
from bs4 import BeautifulSoup
import datetime
import pandas_datareader.data as web

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *


class StockCodeItem:
    def __init__(self, market_type, code, full_code, company):
        self.market_type = market_type
        self.code = code
        self.full_code = full_code
        self.company = company


class StockCode:
    def __init__(self):
        self.items = {}

    def count(self):
        return len(self.items)

    def clear(self):
        self.items.clear()

    def add(self, market_type, code, full_code, company):
        a_item = StockCodeItem(market_type, code, full_code, company)
        self.items[company] = a_item

    def remove(self, company):
        del self.items[company]

    def find(self, company):
        return self.items[company]

    def iterItems(self):
        return self.items.items()

    def dump(self):
        index = 0
        for key, value in self.items.items():
            print("%s : %s - key=%s, Full Code=%s, Company=%s" % (
            index, value.market_type, key, value.full_code, value.company))
            index += 1


class LearningTrade(object):
    def __init__(self):
        print('init')
        dataList = get_data_list()
        print(dataList)

        self.codes = StockCode()
        for company in dataList:
            self.codes.add('market_type', 'code', 'full_code', str(company).replace('.data', ''))
        self.codes.dump()



LearningTrade()
