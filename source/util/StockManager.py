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

    def register(self, df):
        self.df = self.df.append(df, ignore_index=True)

    def is_trade(self):
        is_trade = ''
        if self.index == 0:
            self.index += 1
            return


        거래량차이 = int(self.df['거래량'][self.index]) - int(self.df['거래량'][self.index - 1])
        이전_시간_매수_매도_차이 = int(self.df['매수잔량'][self.index - 1]) - int(self.df['매도잔량'][self.index - 1])
        현재_시간_매수_매도_차이 = int(self.df['매수잔량'][self.index]) - int(self.df['매도잔량'][self.index])
        이전시간_현재시간_매수_매도_차이 = 현재_시간_매수_매도_차이 - 이전_시간_매수_매도_차이

        self.거래량_차이_리스트.append(거래량차이)
        self.현재_시간_매수_매도_차이_리스트.append(현재_시간_매수_매도_차이)
        self.이전시간_현재시간_매수_매도_차이_리스트.append(이전시간_현재시간_매수_매도_차이)

        if 거래량차이 > self.max_volume:
            self.max_volume = 거래량차이;

        남은매수대금대금 = (현재_시간_매수_매도_차이 * 거래량차이) / 100000000

        if 이전시간_현재시간_매수_매도_차이 > 0 \
                and 현재_시간_매수_매도_차이 > 0 \
                and 거래량차이 >= self.max_volume / 2 \
                and self.df['등락율'][self.index] > self.df['등락율'][self.index - 1] and self.df['등락율'][self.index] > 0 \
                and 남은매수대금대금 > 2 \
                and self.이전시간_현재시간_매수_매도_차이_리스트[self.index] > self.이전시간_현재시간_매수_매도_차이_리스트[self.index - 1]:
            # print('============== Buy')
            self.buy_list.append([self.index])
            self.real_buy_percent = float(self.df['등락율'][self.index])
            self.is_buy = True
            if self.index == len(self.df.index)-1:
                is_trade = 'buy'

        if self.is_buy is True and float(self.df['등락율'][self.index]) > self.real_buy_percent + 1.0:
            # print('============== Sell')
            self.real_buy_percent = 50
            self.is_buy = False

            if self.index == len(self.df.index)-1:
                is_trade = 'sell_success'

        if self.is_buy is True and float(self.df['등락율'][self.index]) < self.real_buy_percent - 1.0:
            # print('============== Failed Sell')
            self.real_buy_percent = 50
            self.is_buy = False
            if self.index == len(self.df.index)-1:
                is_trade = 'sell_failed'

        self.index += 1
        return is_trade


    def show_graph(self):
        거래량_차이_리스트 = []
        현재_시간_매수_매도_차이_리스트 = []
        이전시간_현재시간_매수_매도_차이_리스트 = []

        등략율_리스트 = []
        buy_list = []

        test_success_sell_price_list = []
        test_success_sell_index_list = []

        test_fail_sell_price_list = []
        test_fail_sell_index_list = []

        거래대금_리스트 = []
        max_volume = 0
        is_buy = False
        real_buy_percent = 50

        for i in self.df.index:
            if 0 == i:
                거래량_차이_리스트.append(0)
                현재_시간_매수_매도_차이_리스트.append(0)
                이전시간_현재시간_매수_매도_차이_리스트.append(0)
                거래대금_리스트.append(0)
                continue

            시간차이 = int(self.df['시간'][i]) - int(self.df['시간'][i - 1])
            거래량차이 = int(self.df['거래량'][i]) - int(self.df['거래량'][i - 1])
            이전_시간_매수_매도_차이 = int(self.df['매수잔량'][i - 1]) - int(self.df['매도잔량'][i - 1])
            현재_시간_매수_매도_차이 = int(self.df['매수잔량'][i]) - int(self.df['매도잔량'][i])
            이전시간_현재시간_매수_매도_차이 = 현재_시간_매수_매도_차이 - 이전_시간_매수_매도_차이

            거래량_차이_리스트.append(거래량차이)
            현재_시간_매수_매도_차이_리스트.append(현재_시간_매수_매도_차이)
            이전시간_현재시간_매수_매도_차이_리스트.append(이전시간_현재시간_매수_매도_차이)

            if 거래량차이 > max_volume:
                max_volume = 거래량차이;

            남은매수대금대금 = (현재_시간_매수_매도_차이 * 거래량차이) / 100000000
            거래대금_리스트.append(남은매수대금대금)

            print('[%s] [%s] [%s] [%s] [%s] [%s]' % (
            self.df['시간'][i], self.df['등락율'][i], 현재_시간_매수_매도_차이, 이전시간_현재시간_매수_매도_차이, 거래량차이, 시간차이))

            if 이전시간_현재시간_매수_매도_차이 > 0 \
                    and 현재_시간_매수_매도_차이 > 0 \
                    and 거래량차이 >= max_volume / 2 \
                    and self.df['등락율'][i] > self.df['등락율'][i - 1] and self.df['등락율'][i] > 0 \
                    and 남은매수대금대금 > 2 \
                    and 이전시간_현재시간_매수_매도_차이_리스트[i] > 이전시간_현재시간_매수_매도_차이_리스트[i - 1]:
                print('============== Buy')
                buy_list.append([i])
                등략율_리스트.append(self.df['등락율'][i])
                real_buy_percent = float(self.df['등락율'][i])
                is_buy = True

            if is_buy is True and float(self.df['등락율'][i]) > real_buy_percent + 1.0:
                print('============== Sell')
                test_success_sell_index_list.append([i])
                test_success_sell_price_list.append(self.df['등락율'][i])
                real_buy_percent = 50
                is_buy = False

            if is_buy is True and float(self.df['등락율'][i]) < real_buy_percent - 1.0:
                print('============== Failed Sell')
                test_fail_sell_index_list.append([i])
                test_fail_sell_price_list.append(self.df['등락율'][i])
                real_buy_percent = 50
                is_buy = False

        fig, axs = plt.subplots(5)

        ax = axs[0]
        ax.plot(self.df['등락율'])
        ax.scatter(buy_list, 등략율_리스트, c='r')
        ax.scatter(test_success_sell_index_list, test_success_sell_price_list, c='b')
        ax.scatter(test_fail_sell_index_list, test_fail_sell_price_list, c='y')
        ax.grid(True)

        ax = axs[1]
        ax.plot(거래량_차이_리스트)
        ax.grid(True)

        ax = axs[2]
        ax.plot(현재_시간_매수_매도_차이_리스트)
        ax.grid(True)

        ax = axs[3]
        ax.plot(이전시간_현재시간_매수_매도_차이_리스트)
        ax.grid(True)

        ax = axs[4]
        ax.plot(거래대금_리스트)
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
