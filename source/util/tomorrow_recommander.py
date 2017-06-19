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
    def __init__(self):
        print('tomorrow_recommander')
        self.stationarity_tester = stationarity_tester()
        self.stock_updater = stock_updater()

    def tomorrow_recommand_stock(self, end=None, is_update_stock=True, last_month=6, window=20):
        if end is None:
            end = datetime.datetime.today()
        start = end - relativedelta(months=last_month)
        print('Tomorrow trade stock: %s ~ %s' % (end, start))

        code_list = []
        if is_update_stock is True:
            self.stock_updater.download_kospi_data()
            code_list = self.stock_updater.update_kospi_200()
        else:
            data = load_yaml('kospi200')
            for company_code, value in data.iterItems():
                code_list.append(company_code)

        stocks_trade_list = self.stationarity_tester.show_stationarity(code_list, False, start, end, window)
        # print(stocks_trade_list)

        df = get_df_from_file('000030', start, end)
        last_stock_trade_day = df.iloc[len(df) - 1].name
        print('last_stock_trade_day: %s' % (last_stock_trade_day))


        save_stocks = {'date': str(last_stock_trade_day), 'last_month': last_month, 'window': window, 'SELL_list': [],'BUY_list': []}

        print('================tomorrow trade===================')
        for stock in stocks_trade_list:
            if len(stock['sell']) > 0:
                sell_last_day = stock['sell'][len(stock['sell']) - 1].name
                if last_stock_trade_day == sell_last_day:
                    save_stocks['SELL_list'].append(stock['code'])
                    print('SELL code:%s %s' % (stock['code'], stock['sell'][len(stock['sell']) - 1]))

            if len(stock['buy']) > 0:
                buy_last_day = stock['buy'][len(stock['buy']) - 1].name
                if last_stock_trade_day == buy_last_day:
                    save_stocks['BUY_list'].append(stock['code'])
                    print('BUY code:%s %s' % (stock['code'], stock['buy'][len(stock['buy']) - 1]))

        print('TOMORROW SELL LIST [%s][last_month:%s, window:%s] SELL list: %s' % (
        last_stock_trade_day, last_month, window, save_stocks['SELL_list']))
        print('TOMORROW BUY LIST [%s][last_month:%s, window:%s] BUY list: %s' % (
        last_stock_trade_day, last_month, window, save_stocks['BUY_list']))

        saved_data = load_yaml('daily_trade')
        if saved_data == None:
            saved_data = {'daily_trade': []}
            saved_data['daily_trade'].append(save_stocks)
        else:
            if saved_data['daily_trade'] == None:
                save_list = {'daily_trade': []}
                save_list.append(save_stocks)
            else:
                for index, v in enumerate(saved_data['daily_trade'], start=0):
                    if str(v['date']) == str(last_stock_trade_day):
                        del saved_data['daily_trade'][index]

                saved_data['daily_trade'].append(save_stocks)

        write_yaml('daily_trade', saved_data)

        for code in save_stocks['BUY_list']:
            print('StockList.add("%s");' % (code))

    def recommand_draw(self, date=get_trade_last_day()):
        draw = load_yaml('daily_trade')
        # last_day = get_trade_last_day()
        for v in draw['daily_trade']:
            print(v['date'])
            print(v)
            print(date)
            # if str(v['date']) != str(last_day):
            if str(date) in str(v['date']):
                end = datetime.datetime.today()
                start = end - relativedelta(months=v['last_month'])
                df = get_df_from_file('000030', start, end)
                last_stock_trade_day = df.iloc[len(df) - 1].name
                print('last_stock_trade_day: %s' % (last_stock_trade_day))
                for code in v['BUY_list']:
                    print(code)
                    self.stationarity_tester.stationarity_per_day(code, start, end, True, v['window'])
                for code in v['SELL_list']:
                    print(code)
                    self.stationarity_tester.stationarity_per_day(code, start, end, True, v['window'])
