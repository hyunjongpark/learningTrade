# -*- coding: utf-8 -*-
from __future__ import division
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

class StockCode():
    def __init__(self, code):
        # print('StockCode[%s]' % (code))
        self.df = pd.DataFrame()
        self.code = code

    def register(self, df):
        self.df.append(df)

    def print(self):
        for i in self.df.index:
            print(self.df.idoc[i])

    def is_buy_price(self):
        volume_list = []
        buy_list = []
        diff_buy_list = []

        test_buy_price_list = []
        test_buy_index_list = []

        is_buy = False
        test_success_sell_price_list = []
        test_success_sell_index_list = []

        test_fail_sell_price_list = []
        test_fail_sell_index_list = []

        buy_limit_list = []
        max_volume = 0

        real_buy_percent = 50

        index = 0
        for df in self.list:
            # print(df)
            if 0 == index:
                volume_list.append(0)
                buy_list.append(0)
                diff_buy_list.append(0)
                buy_limit_list.append(0)
                index = index + 1
                continue

            diff_time = int(df['시간'][index]) - int(df['시간'][index - 1])
            diff_volume = int(df['거래량'][index]) - int(df['거래량'][index - 1])
            diff_buy_pre_limit = int(df['매수잔량'][index - 1]) - int(df['매도잔량'][index - 1])
            diff_buy_limit = int(df['매수잔량'][index]) - int(df['매도잔량'][index])
            diff_diff_buy = diff_buy_limit - diff_buy_pre_limit

            volume_list.append(diff_volume)
            buy_list.append(diff_buy_limit)
            diff_buy_list.append(diff_diff_buy)

            if diff_volume > max_volume:
                max_volume = diff_volume;

            buy_limit_price = (diff_buy_limit * diff_volume) / 100000000
            buy_limit_list.append(buy_limit_price)

            print('[%s] [%s] [%s] [%s] [%s] [%s]' % (
                df['시간'][index], df['등락율'][index], diff_buy_limit, diff_diff_buy, diff_volume, diff_time))

            if diff_buy_limit > 0 and diff_diff_buy > 0 and diff_volume >= max_volume / 2 and df['등락율'][index] > \
                    df['등락율'][index - 1] and buy_limit_price > 2 and df['등락율'][index] > 0 and diff_buy_list[index] > \
                    diff_buy_list[index - 1]:
                print('============== Buy')
                test_buy_index_list.append([index])
                test_buy_price_list.append(df['등락율'][index])
                real_buy_percent = float(df['등락율'][index])
                is_buy = True

            if is_buy is True and float(df['등락율'][index]) > real_buy_percent + 1.0:
                print('============== Sell')
                test_success_sell_index_list.append([index])
                test_success_sell_price_list.append(df['등락율'][index])
                real_buy_percent = 50
                is_buy = False

            if is_buy is True and float(df['등락율'][index]) < real_buy_percent - 1.0:
                print('============== Failed Sell')
                test_fail_sell_index_list.append([index])
                test_fail_sell_price_list.append(df['등락율'][index])
                real_buy_percent = 50
                is_buy = False

            index = index + 1



    def show_graph(self):
        fig, axs = plt.subplots(4)
        ax = axs[0]
        # Solar = [float(line[1]) for line in I020]
        ax.plot([float(stock.diff)for stock in self.list])
        # ax.plot([float(stock.price) for stock in self.list])
        # plt.gcf().autofmt_xdate()
        ax.grid(True)


        # ax2 = ax.twinx()
        # ax2.plot(get_foreigner_info(code, start, end), 'r')

        # ax = axs[1]
        # ax.plot([float(stock.volumediff) for stock in self.list])
        # ax.grid(True)

        ax = axs[1]
        ax.plot([float(stock.dvol1) for stock in self.list], 'b')
        ax.plot([float(stock.svol1) for stock in self.list], 'r')
        ax.grid(True)
        #
        ax = axs[2]
        ax.plot([float(stock.dcha1)  for stock in self.list], 'b')
        ax.plot([float(stock.scha1)  for stock in self.list], 'r')
        ax.grid(True)
        # #
        ax = axs[3]
        ax.plot([float(stock.ddiff1)  for stock in self.list], 'b')
        ax.plot([float(stock.sdiff1)  for stock in self.list], 'r')
        ax.grid(True)

        # ax = axs[5]
        # ax.plot([float(stock.scha1)  for stock in self.list], 'y')
        # ax.plot([float(stock.scha2)  for stock in self.list], 'r')
        # ax.grid(True)

        # ax = axs[6]
        # ax.plot([float(stock.fwdvl) for stock in self.list], 'b')
        # ax.plot([float(stock.fwsvl) for stock in self.list], 'r')
        # ax.grid(True)


        plt.show()

class StockManager:
    def __init__(self):
        self.stocks = dict()

    def register(self, code, df):
        stockCode = self.stocks.get(code)
        if stockCode == None:
            stockCode = StockCode(code)
            stockCode.register(df)
            self.stocks[code] = stockCode
        else:
            stockCode.register(df)

    def get_stock_code(self, code):
        return self.stocks.get(code)

    def all_print_stock(self):
        for stockCode in self.stocks.keys():
            code = self.stocks.get(stockCode)
            code.print()
            # code.show_graph()
            # self.stocks.get(stockCode)



stockManager = StockManager()
