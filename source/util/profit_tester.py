# -*- coding: utf-8 -*-
from __future__ import division
import os, sys
from util.stationarity_tester import stationarity_tester
from util.stock_updater import stock_updater

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *
import datetime
from dateutil.relativedelta import relativedelta


class profit_tester():
    def __init__(self):
        print('profit_tester')

    def profit_print_all_today(self):
        draw = load_yaml('daily_trade')
        print(draw)
        profit_sum = 0
        end = datetime.datetime.today()
        index = 0
        for v in draw['daily_trade']:
            for code in v['BUY_list']:
                start = str(v['date'])
                profit = self.code_profit(code, start, end)
                profit_sum += profit
                print('[%s] total: %s, profit: %s, [%s ~ %s]' % (code, profit_sum, profit, start, end))
                index += 1
        print('TOTAL:%s' % (profit_sum / index))
        return profit_sum

    def profit_print_kospi200(self, start, end=None):
        stock_list = load_yaml('kospi200')
        end = datetime.datetime.today()
        profit_sum = 0
        index = 0
        for code, value in stock_list.iterItems():
            profit = self.code_profit(code, start, end)
            profit_sum += profit
            print('[%s][%s/%s] total: %s, profit: %s, [%s ~ %s]' % (
            code, index, len(stock_list.iterItems()), profit_sum, profit, start, end))
            index += 1
        print('TOTAL:%s' % (profit_sum / len(stock_list.iterItems())))
        return profit_sum

    def profit_print_all_with_sell(self):
        draw = load_yaml('daily_trade')
        print(draw)
        profit_sum = 0
        check_codes = []
        for v in draw['daily_trade']:
            for code in v['BUY_list']:
                if code in check_codes:
                    continue
                check_codes.append(code)

        index = 0
        for code in check_codes:
            buy_date = self.get_buy_date(code)
            sell_date = self.get_sell_date(code)

            for i in range(len(buy_date)):
                start = buy_date[i]
                if len(sell_date) == 0 or len(sell_date) < i:
                    continue
                end = sell_date[i]
                profit = self.code_profit(code, start, end)
                profit_sum += profit
                print('[%s] total: %s, profit: %s, [%s ~ %s]' % (code, profit_sum, profit, start, end))
                index += 1
        print('TOTAL:%s' % (profit_sum / index))
        return profit_sum

    def profit_print_all_with_sell_today(self):
        draw = load_yaml('daily_trade')
        print(draw)
        profit_sum = 0
        check_codes = []
        for v in draw['daily_trade']:
            for code in v['BUY_list']:
                if code in check_codes:
                    continue
                check_codes.append(code)

        index = 0
        for code in check_codes:
            buy_date = self.get_buy_date(code)
            sell_date = self.get_sell_date(code)

            for i in range(len(buy_date)):
                start = buy_date[i]
                end = datetime.datetime.today()
                if len(sell_date) != 0 and len(sell_date) >= i:
                    end = sell_date[i]
                profit = self.code_profit(code, start, end)
                profit_sum += profit
                print('[%s] total: %s, profit: %s, [%s ~ %s]' % (code, profit_sum, profit, start, end))
                index += 1
        print('TOTAL:%s' % (profit_sum / index))
        return profit_sum

    def code_profit(self, code='023530', start=20170510, end=get_trade_last_day()):
        current_df = get_df_from_file(code, start, end)
        start_price = current_df.iloc[0]['Close']
        end_price = current_df.iloc[len(current_df) - 1]['Close']
        profit = (end_price - start_price) / start_price * 100
        # print('[%s] profit: %s' %(start, profit))
        return profit

    def get_buy_date(self, code):
        draw = load_yaml('daily_trade')
        dates = []
        for v in draw['daily_trade']:
            for code_in in v['BUY_list']:
                if code_in == code:
                    dates.append(v['date'])
        return dates

    def get_sell_date(self, code):
        draw = load_yaml('daily_trade')
        dates = []
        for v in draw['daily_trade']:
            for code_in in v['SELL_list']:
                if code_in == code:
                    dates.append(v['date'])
        return dates
