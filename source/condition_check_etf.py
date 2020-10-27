# -*- coding: utf-8 -*-
from __future__ import division
import os
import pandas as pd
from source.util.StockManager import stockManager
from util.StockManager import *

LOG_FOLDER = 'log'

def file_test(TODAY, SHOW_CHART, DEBUG_LOG):
    log_folder = ('%s/%s' % (LOG_FOLDER, TODAY))
    if not os.path.exists(log_folder):
        return

    total_profit = 0
    total_money = 0
    skip_total_money = 0
    files = os.listdir(log_folder)

    for file in files:
        df = pd.read_csv('%s/%s/%s' % (LOG_FOLDER, TODAY, file),
                         names=['시간', '한글명', '코드', '현재가', '등락율', '누적거래량', '거래량차', '거래대금'])
        code = df['코드'][0]
        if int(code) == int(233740) or int(code) == int(251340):

            print('SKIP [%s][%s] ' % (df['한글명'][0], code))

            continue

        stockManager.ini_stock_code(code)
        for i in df.index:
            # print('. ', end='', flush=True)
            stockManager.register(code, df.iloc[i])
            trade, log = stockManager.get_stock_code(code).is_trade(debug=DEBUG_LOG)

        profit, money, skip_money = stockManager.get_stock_code(code).test_profit()
        total_profit += profit
        total_money += money
        skip_total_money += skip_money
        if SHOW_CHART:
            stockManager.get_stock_code(code).show_graph()
    print('>>>>>>>>DAY[%s] - Profit[%s] total_money[%s] skip_total_money[%s]' % (TODAY, total_profit, total_money, skip_total_money))
    print('======================================================')
    return total_profit, total_money, skip_total_money


class Trade():
    def all_file_test(self, SHOW_CHART, DEBUG_LOG):
        total_profit = 0
        total_money = 0
        skip_total_money = 0
        folders = os.listdir(LOG_FOLDER)
        for folder in folders:
            profit, money, skip_money = file_test(folder, SHOW_CHART, DEBUG_LOG)
            total_profit += profit
            total_money += money
            skip_total_money += skip_money
        print('TOTAL Profit[%s] money[%s] skip_money[%s]' % (total_profit, total_money, skip_total_money))


if __name__ == "__main__":
    all_days_check = False
    Trade = Trade()
    if all_days_check:
        Trade.all_file_test(SHOW_CHART=False, DEBUG_LOG=False)
    else:
        file_test(TODAY='20200604', SHOW_CHART=False, DEBUG_LOG=False)
