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
            code_list = [k for k, v in codes.iterItems()]
            print(code_list)
            write_yaml('kospi_200_code', code_list)


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
        start = end - relativedelta(months=48)
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
        # try:
            # df = web.DataReader("%s.KS" % (company_code), "yahoo", start, end)
        df = web.DataReader("KRX:%s" % (company_code), "google", start, end)
        df_fe = get_df_from_file_fe(company_code, start, end)
        if df_fe is None:
            df_fe = get_foreigner_info(company_code, start, end)
        else:
            df_fe.append(get_foreigner_info(company_code, start, end))
        save_stock_data_fe(df_fe, file_name)
        df['foreigner_count'] = df_fe['foreigner_count']
        df['institution_trading'] = df_fe['institution_trading']
        # print(df)
        save_stock_data(df, file_name)
        # except Exception as ex:
        #     print('except [%s] %s' % (company_code, ex))
        #     return None
        return df

    def download_kospi_data(self):
        end = datetime.datetime.today()
        start = end - relativedelta(months=48)
        try:
            df = web.DataReader("KRX:KOSPI", "google", start, end)
            print(df)
            save_stock_data(df, 'kospi.data')
            # web.DataReader("KRX:KOSPI", "google", start, end).to_csv('kospi.csv')
        except Exception as ex:
            print('except [%s] %s' % ('kospi', ex))
            return None
        return df
