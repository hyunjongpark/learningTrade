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


class tomorrow_recommander():
    def __init__(self, stock_list_file_name='kospi100', last_month=6, window=20):
        print('tomorrow_recommander')
        self.stationarity_tester = stationarity_tester()
        self.stock_updater = stock_updater()
        self.end = datetime.datetime.today()
        self.start = self.end - relativedelta(months=last_month)

    def tomorrow_recommand_stock(self, stock_list_file_name='kospi100', last_month=6, window=20):
        print('Tomorrow trade stock')

        # self.stock_updater.update_kospi_100()

        stocks_trade_list = self.stationarity_tester.show_stationarity(False, self.start, self.end, window)
        print(stocks_trade_list)

        df = get_df_from_file('042670', self.start, self.end)
        last_stock_trade_day = df.iloc[len(df) - 1].name
        print('last_stock_trade_day: %s' % (last_stock_trade_day))

        sell_list = []
        buy_list = []

        print('================tomorrow trade===================')
        for stock in stocks_trade_list:
            sell_last_day = stock['sell'][len(stock['sell']) - 1].name
            buy_last_day = stock['buy'][len(stock['buy']) - 1].name

            if last_stock_trade_day == sell_last_day:
                sell_list.append({'code': stock['code'], 'Close': stock['sell'][len(stock['sell']) - 1]['Close']})
                print('SELL code:%s %s' % (stock['code'], stock['sell'][len(stock['sell']) - 1]))
            elif last_stock_trade_day == buy_last_day:
                buy_list.append({'code': stock['code'], 'Close': stock['buy'][len(stock['buy']) - 1]['Close']})
                print('BUY code:%s %s' % (stock['code'], stock['buy'][len(stock['buy']) - 1]))

        print('[%s][last_month:%s, window:%s] SELL list: %s' % (last_stock_trade_day, last_month, window, sell_list))
        print('[%s][last_month:%s, window:%s] BUY list: %s' % (last_stock_trade_day, last_month, window, buy_list))
        write_yaml('daily_trade',
                   {'date': last_stock_trade_day, 'sell': sell_list, 'buy': buy_list, 'last_month': last_month,
                    'window': window})
        return 'END'

    def tomorrow_recommand_draw(self):
        draw = load_yaml('daily_trade')

        start = self.end - relativedelta(months=draw['last_month'])
        df = get_df_from_file('042670', start, self.end)
        last_stock_trade_day = df.iloc[len(df) - 1].name
        print('last_stock_trade_day: %s' % (last_stock_trade_day))

        for sell_list in draw['sell']:
            print(sell_list)
            self.stationarity_tester.stationarity_per_day(sell_list['code'], start, self.end, True, draw['window'])

        for sell_list in draw['buy']:
            print(sell_list)
            self.stationarity_tester.stationarity_per_day(sell_list['code'], start, self.end, True, draw['window'])
