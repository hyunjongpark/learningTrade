# -*- coding: utf-8 -*-
from __future__ import division
import os, sys
import pandas_datareader.data as web
parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *
import datetime
import os, sys, datetime
import requests, json
# import BeautifulSoup
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import pandas_datareader.data as web
from dateutil.relativedelta import relativedelta
from data_model import *

class stock_updater():
    def __init__(self):
        print('stock_updater')

    def update_kospi_100(self):
        self.update_stock_list(file_name='kospi100', whereCode=61)
        return self.download_stock_datas(stock_list_file_name='kospi100')

    def update_kospi_200(self):
        self.update_stock_list(file_name='kospi200', whereCode=51)
        return self.download_stock_datas(stock_list_file_name='kospi200')

    def update_stock_list(self, file_name, whereCode=51):
        for market_type in ['kospiVal']:
            html = self.downloadCode(market_type,whereCode)
            codes = self.parseCodeHTML(html, market_type)
            print('code len %s' %(len(codes.iterItems())))
            delete_file(file_name)
            write_yaml(file_name, codes)

    def downloadCode(self, market_type,whereCode):
        url = 'http://datamall.koscom.co.kr/servlet/infoService/SearchIssue'
        html = requests.post(url, data={'flag': 'SEARCH', 'marketDisabled': 'null', 'marketBit': market_type, 'where':'1', 'whereCode':whereCode})
        return html.content

    def parseCodeHTML(self, html, market_type):
        soup = BeautifulSoup(html, "lxml")
        options = soup.findAll('option')

        codes = StockCode()

        for a_option in options:
            # print a_tr
            if len(a_option) == 0:
                continue

            code = a_option.text[1:7]
            company = a_option.text[8:]
            full_code = a_option.get('value')

            if company == '':
                continue;

            if "폐지" in str(company):
                continue

            codes.add(market_type, code, full_code, company)

        return codes


    def download_stock_datas(self, stock_list_file_name):
        data = load_yaml(stock_list_file_name)
        index = 0
        end = datetime.datetime.today()
        start = end - relativedelta(months=24)
        code_list = []
        for company_code, value in data.iterItems():
            print("%s : %s - key=%s, Full Code=%s, Company=%s" % (
            index, value.market_type, company_code, value.full_code, value.company))
            index += 1
            find_name = '%s_%s.data' % (company_code, value.company)
            if self.download_stock_data(file_name=find_name, company_code=company_code, start=start, end=end) is not None:
                code_list.append(company_code)

        return code_list

    def download_stock_data(self, file_name, company_code, start, end):
        try:
            df = web.DataReader("%s.KS" % (company_code), "yahoo", start, end)
            print(df)
            save_stock_data(df, file_name)
        except:
            print("!!! Fatal Error Occurred %s" % (company_code))
            return None
        return df

