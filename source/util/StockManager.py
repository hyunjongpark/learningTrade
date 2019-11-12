# -*- coding: utf-8 -*-
from __future__ import division
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

class StockCode():
    def __init__(self, code):
        self.df = pd.DataFrame()
        self.code = code

        self.거래량_차이_리스트 = []
        self.현재_시간_매수_매도_차이_리스트 = []
        self.이전시간_현재시간_매수_매도_차이_리스트 = []
        self.거래량_차이_리스트.append(0)
        self.현재_시간_매수_매도_차이_리스트.append(0)
        self.이전시간_현재시간_매수_매도_차이_리스트.append(0)

        self.buy_list = []
        self.max_volume = 0
        self.is_buy = False
        self.real_buy_percent = 50

        self.index = 0
        self.등략율_list = []
        self.test_success_sell_price_list = []
        self.test_success_sell_index_list = []
        self.test_fail_sell_price_list = []
        self.test_fail_sell_index_list = []

    def register(self, df):
        self.df = self.df.append(df, ignore_index=True)

    def is_trade(self, debug):
        is_trade = ''
        if self.index == 0:
            self.index += 1
            return

        시간차이 = int(self.df['시간'][self.index]) - int(self.df['시간'][self.index - 1])
        거래량차이 = int(self.df['거래량'][self.index]) - int(self.df['거래량'][self.index - 1])
        이전_시간_매수_매도_차이 = int(self.df['매수잔량'][self.index - 1]) - int(self.df['매도잔량'][self.index - 1])
        현재_시간_매수_매도_차이 = int(self.df['매수잔량'][self.index]) - int(self.df['매도잔량'][self.index])
        이전시간_현재시간_매수_매도_차이 = 현재_시간_매수_매도_차이 - 이전_시간_매수_매도_차이

        self.거래량_차이_리스트.append(거래량차이)
        self.현재_시간_매수_매도_차이_리스트.append(현재_시간_매수_매도_차이)
        self.이전시간_현재시간_매수_매도_차이_리스트.append(이전시간_현재시간_매수_매도_차이)

        if 거래량차이 > self.max_volume:
            self.max_volume = 거래량차이;

        남은매수대금 = (현재_시간_매수_매도_차이 * 거래량차이) / 100000000

        if debug is True:
            print('[%s] [%s] 거래량차이[%s] 남은매수대금[%s] 현재_차이[%s] 이전_차이[%s] DIFF_차이[%s] 시간차이[%s]' % (self.df['시간'][self.index], self.df['등락율'][self.index], 거래량차이, 남은매수대금, 현재_시간_매수_매도_차이, 이전_시간_매수_매도_차이, 이전시간_현재시간_매수_매도_차이, 시간차이))

        if 이전시간_현재시간_매수_매도_차이 > 0 \
                and 현재_시간_매수_매도_차이 > 0 \
                and 거래량차이 >= self.max_volume / 2 \
                and self.df['등락율'][self.index] > self.df['등락율'][self.index - 1] \
                and self.df['등락율'][self.index] > 0 and 남은매수대금 > 2 \
                and int(self.df['등락율'][self.index]) <= 20 \
                and self.이전시간_현재시간_매수_매도_차이_리스트[self.index] > self.이전시간_현재시간_매수_매도_차이_리스트[self.index - 1]:
            if debug is True:
                print('============== Buy')
            self.buy_list.append([self.index])
            self.real_buy_percent = float(self.df['등락율'][self.index])
            self.등략율_list.append(self.df['등락율'][self.index])
            self.is_buy = True
            if self.index == len(self.df.index)-1:
                is_trade = 'buy'

        if self.is_buy is True and float(self.df['등락율'][self.index]) > self.real_buy_percent + 1.0:
            if debug is True:
                print('============== Sell')
            self.real_buy_percent = 50
            self.is_buy = False
            self.test_success_sell_index_list.append(self.index)
            self.test_success_sell_price_list.append(self.df['등락율'][self.index])

            if self.index == len(self.df.index)-1:
                is_trade = 'sell_success'

        if self.is_buy is True and float(self.df['등락율'][self.index]) < self.real_buy_percent - 1.0:
            if debug is True:
                print('============== Failed Sell')
            self.real_buy_percent = 50
            self.is_buy = False
            self.test_fail_sell_index_list.append(self.index)
            self.test_fail_sell_price_list.append(self.df['등락율'][self.index])

            if self.index == len(self.df.index)-1:
                is_trade = 'sell_failed'

        self.index += 1
        return is_trade


    def show_graph(self):
        fig, axs = plt.subplots(4)

        ax = axs[0]
        ax.plot(self.df['등락율'])
        ax.scatter(self.buy_list, self.등략율_list, c='r')
        ax.scatter(self.test_success_sell_index_list, self.test_success_sell_price_list, c='b')
        ax.scatter(self.test_fail_sell_index_list, self.test_fail_sell_price_list, c='y')
        ax.grid(True)

        ax = axs[1]
        ax.plot(self.거래량_차이_리스트)
        ax.grid(True)

        ax = axs[2]
        ax.plot(self.현재_시간_매수_매도_차이_리스트)
        ax.grid(True)

        ax = axs[3]
        ax.plot(self.이전시간_현재시간_매수_매도_차이_리스트)
        ax.grid(True)

        plt.title(self.code)
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
            code.show_graph()



stockManager = StockManager()
