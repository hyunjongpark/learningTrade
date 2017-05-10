# -*- coding: utf-8 -*-
from __future__ import division
import os, sys
parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *

class stock_updater():
    def __init__(self):
        print('stock_updater')

    def update_kospi_100(self):
        print('stock_updater')

        self.download_stock_datas(stock_list_file_name='kospi100')


    def download_stock_datas(self, stock_list_file_name):
        data = load_yaml(stock_list_file_name)
        index = 0
        end = datetime.today()
        start = end - relativedelta(months=24)
        for company_code, value in data.iterItems():
            print("%s : %s - key=%s, Full Code=%s, Company=%s" % (
            index, value.market_type, company_code, value.full_code, value.company))
            index += 1
            find_name = '%s_%s.data' % (company_code, value.company)
            self.download_stock_data(file_name=find_name, company_code=company_code, start=start, end=end)

        return 'END'

    def download_stock_data(self, file_name, company_code, start, end):
        try:
            df = web.DataReader("%s.KS" % (company_code), "yahoo", start, end)
            save_stock_data(df, file_name)
        except:
            print("!!! Fatal Error Occurred %s" % (company_code))
            return None
        return df

