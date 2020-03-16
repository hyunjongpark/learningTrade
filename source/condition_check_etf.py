# -*- coding: utf-8 -*-
from __future__ import division
import os
import pandas as pd
from source.util.StockManager import stockManager
from util.StockManager import *


def file_test(TODAY, SHOW_CHART, DEBUG_LOG):
    log_folder = ('log/%s' % (TODAY))
    if not os.path.exists(log_folder):
        return

    total_profit = 0
    files = os.listdir(log_folder)

    for file in files:
        df = pd.read_csv('log/%s/%s' % (TODAY, file),
                         names=['시간', '한글명', '코드', '현재가', '등락율', '누적거래량', '거래량차', '거래대금'])
        code = df['코드'][0]
        stockManager.ini_stock_code(code)
        for i in df.index:
            stockManager.register(code, df.iloc[i])
            trade, log = stockManager.get_stock_code(code).is_trade(debug=DEBUG_LOG)
            if trade == 'buy':
                print('BUY')
                # print(' %s' % (log))
            elif trade == 'sell_success':
                print('SELL SUCCESS profit[%s]' % (stockManager.get_stock_code(code).test_profit()))
                # print(' %s' % (log))
            elif trade == 'sell_failed':
                print('SELL FAILED profit[%s]' % (stockManager.get_stock_code(code).test_profit()))
                # print(' %s' % (log))

        total_profit += stockManager.get_stock_code(code).test_profit()
        if SHOW_CHART:
            stockManager.get_stock_code(code).show_graph()
    print('>>>>>>>>DAY[%s] - Profit[%s] ' % (TODAY, total_profit))
    print('======================================================')
    return total_profit


class Trade():
    def all_file_test(self, SHOW_CHART, DEBUG_LOG):
        total_profit = 0
        folders = os.listdir('log')
        for folder in folders:
            total_profit += file_test(folder, SHOW_CHART, DEBUG_LOG)
        print('TOTAL Profit[%s]' % (total_profit))


if __name__ == "__main__":
    all_days_check = False
    Trade = Trade()
    if all_days_check:
        Trade.all_file_test(SHOW_CHART=False, DEBUG_LOG=False)
    else:
        file_test(TODAY='20200316', SHOW_CHART=False, DEBUG_LOG=False)
