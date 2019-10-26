# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *
# import BeautifulSoup
import pandas_datareader.data as web
from dateutil.relativedelta import relativedelta
from util.data_model import *
from util.services import *
import re

class stock_updater():
    def __init__(self):
        print('stock_updater')

    def update_kospi_200(self):
        services.get('configurator').register('stock_list', 'kospi200')
        self.download_kospi_200_stock_list(file_name=services.get('configurator').get('stock_list'))
        return self.download_stock_datas(stock_list_file_name=services.get('configurator').get('stock_list'))

    def update_kospi(self, end_index):
        services.get('configurator').register('stock_list', 'kospi')
        self.download_kospi_stock_list(file_name=services.get('configurator').get('stock_list'), end_index=end_index)
        return self.download_stock_datas(stock_list_file_name=services.get('configurator').get('stock_list'))


    def download_kospi_200_stock_list(self, file_name):
        code_list = []
        base_url = 'http://finance.naver.com/sise/entryJongmok.nhn?&page='
        for i in range(1,20):
            url = base_url + str(i);
            html = requests.post(url).content
            soup = BeautifulSoup(html, "lxml")
            items = soup.find_all('td', {'class': 'ctg'})
            for item in items:
                txt = item.a.get('href')
                k = re.search('[\d]+', txt)
                if k:
                    code = k.group()
                    name = item.text
                    data = code, name
                    code_list.append(data)
                    print(data)
        write_yaml(file_name, code_list)

    def download_kospi_stock_list(self, file_name, end_index=200):
        code_list = []
        base_url = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0&page='
        for i in range(1, end_index):
            url = base_url + str(i);
            html = requests.post(url).content
            soup = BeautifulSoup(html, "lxml")
            items = soup.find_all("a", {"class": "tltle"})
            for item in items:
                txt = item.get('href')
                k = re.search('[\d]+', txt)
                if k:
                    code = k.group()
                    name = item.text
                    data = code, name
                    code_list.append(data)
                    print(data)
        write_yaml(file_name, code_list)

    def download_stock_datas(self, stock_list_file_name):
        data = load_yaml(stock_list_file_name)
        index = 0
        end = datetime.datetime.today()
        start = end - relativedelta(months=48)
        code_list = []
        for company_code, value in data:
            print("%s/%s : Code=%s, Company=%s" % (index, len(data), company_code, value))
            index += 1
            find_name = 'data/%s_%s.data' % (company_code, value)
            if self.download_stock_data(file_name=find_name, company_code=company_code, start=start, end=end) is not None:
                code_list.append(company_code)
        return code_list

    def download_stock_data(self, file_name, company_code, start, end):
        try:
            df = web.DataReader('%s.KS' %(company_code), 'yahoo', start, end)
            df.to_pickle(file_name)
        except Exception as ex:
            print('except [%s] %s' % ('download_stock_data', ex))
            return None
        return df