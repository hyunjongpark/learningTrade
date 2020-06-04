# -*- coding: utf-8 -*-
from __future__ import division
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

from source.common import get_percent_price_etf, RIDE_TRADE_COUNT, DEFAULT_BUY_COUNT, \
    FAILED_SELL_PROFIT, SUCCESS_SELL_PROFIT, RIDE_1_PROFIT
import numpy
from source.common import get_percent

# from util.ta_tester import ta_tester

TAX = 0.0015


class StockCode():
    def __init__(self, code):
        self.df = pd.DataFrame()
        self.code = code

        self.success_trade_count = 0
        self.failed_trade_count = 0
        self.period_top_price = 0
        self.period_min_price = 10000000
        self.period_index = 0

        self.거래량_차이_리스트 = []
        self.현재_시간_매수_매도_차이_리스트 = []
        self.이전시간_현재시간_매수_매도_차이_리스트 = []
        self.남은매수대금 = []
        self.매수매도체결건수_리스트 = []

        self.거래량_차이_리스트.append(0)
        self.현재_시간_매수_매도_차이_리스트.append(0)
        self.이전시간_현재시간_매수_매도_차이_리스트.append(0)
        self.매수매도체결건수_리스트.append(0)

        self.누적거래량차이 = []
        self.누적거래량차이.append(0)

        self.현재가차이 = []
        self.현재가차이.append(0)

        self.거래대금차이 = []
        self.거래대금차이.append(0)

        self.등락율차이 = []
        self.등락율차이.append(0)

        self.등략율 = []
        self.등략율.append(0)

        self.period_buy_count = 0
        self.period_물타기_index = 0

        self.buy_list = []
        self.pattern_list = []
        self.pattern_list_price = []
        self.max_volume = 0
        self.is_buy = False
        self.real_buy_percent = 50

        self.index = 0
        self.등략율_list = []
        self.test_success_sell_price_list = []
        self.test_success_sell_index_list = []
        self.물타기_index_list = []
        self.물타기_price_list = []
        self.test_fail_sell_price_list = []
        self.test_fail_sell_index_list = []

        self.profit = 0
        self.preBuyPrice = 0
        self.preSellPrice = 0
        self.buy_count = 0
        self.total_money_profit = 0
        self.skip_total_money_profit = 0
        self.buy_top_price = 0
        self.today_min_percent = 1

        self.isSellEqBuyPrice = False


        # self.ta_tester = ta_tester()

    def register(self, df):
        self.df = self.df.append(df, ignore_index=True)

    def set_not_buy(self, debug):
        self.is_buy = False
        print('code[%s] - Rollback Buy Status' % (self.code))

    def is_trade(self, debug):
        is_trade = ''
        if self.index == 0:
            self.index += 1
            self.남은매수대금.append(0)
            return ('', '')

        시간 = int(self.df['시간'][self.index]) - int(self.df['시간'][self.index - 1])
        현재가차이 = int(self.df['현재가'][self.index]) - int(self.df['현재가'][self.index - 1])
        등락율차이 = round(float(self.df['등락율'][self.index]) - float(self.df['등락율'][self.index - 1]), 3)
        누적거래량차이 = int(self.df['누적거래량'][self.index]) - int(self.df['누적거래량'][self.index - 1])
        거래량차이 = int(self.df['거래량차'][self.index]) - int(self.df['거래량차'][self.index - 1])
        거래대금차이 = int(self.df['거래대금'][self.index]) - int(self.df['거래대금'][self.index - 1])
        시간차이 = int(self.df['시간'][self.index]) - int(self.df['시간'][self.index - 1])

        print_log = 'index[%s] 코드[%s] 시간[%s] 현재가[%s] 등락율[%s] 등락율차이[%s] ' \
                    '현재가차이[%s] 거래대금차이[%s]' % (
                        self.index, self.df['코드'][self.index], self.df['시간'][self.index], self.df['현재가'][self.index],
                        self.df['등락율'][self.index], 등락율차이, 현재가차이, 거래대금차이)

        self.등락율차이.append(등락율차이)
        self.현재가차이.append(현재가차이)
        self.거래대금차이.append(거래대금차이)
        self.등략율.append(self.df['등락율'][self.index])
        self.누적거래량차이.append(누적거래량차이)

        if self.today_min_percent > self.df['등락율'][self.index]:
            self.today_min_percent = self.df['등락율'][self.index]

        if self.is_buy is True and self.period_top_price < self.df['현재가'][self.index]:
            self.period_top_price = self.df['현재가'][self.index]

        if self.is_buy is True and self.period_min_price > self.df['현재가'][self.index]:
            self.period_min_price = self.df['현재가'][self.index]

        if debug is True:
            print(print_log)

        if int(self.code) != int('122630') and int(self.code) != int('252670'):
            return 0, 0

        if self.is_buy is False \
                and 1 <= self.df['등락율'][self.index] <= 4 \
                and int(self.df['시간'][self.index]) < 1430000 \
                and self.현재가차이[self.index - 1] == self.현재가차이[self.index]:

            # 100 -> 약 2분
            is_up = False
            if len(self.등략율) > 500:
                if float(self.등략율[self.index - 500]) < float(self.등략율[self.index - 300]) < float(self.등략율[self.index - 150]) < float(self.등략율[self.index - 50]) < float(self.등략율[self.index]):
                    is_up = True

            if is_up and self.preSellPrice == 0:
                self.isSellEqBuyPrice = True
            else:
                if self.preSellPrice == int(self.df['현재가'][self.index]):
                    self.isSellEqBuyPrice = True
                else:
                    self.isSellEqBuyPrice = False

            if is_up:
                self.buy_list.append([self.index])
                self.real_buy_percent = float(self.df['등락율'][self.index])
                self.등략율_list.append(self.df['등락율'][self.index])
                self.is_buy = True
                self.buy_count += 1
                self.preBuyPrice = int(self.df['현재가'][self.index])
                self.period_top_price = self.preBuyPrice
                self.period_min_price = self.preBuyPrice
                self.period_index = self.index
                self.period_물타기_index = self.index
                self.period_buy_count = 1
                if self.buy_top_price < self.preBuyPrice:
                    self.buy_top_price = self.preBuyPrice

                print('code[%s][%s][%s] - Buy buy_price[%s] total_profit[%s] percent[%s]' % (self.df['코드'][self.index], self.index, self.df['시간'][self.index], int(self.df['현재가'][self.index]), self.profit,  self.df['등락율'][self.index]))
                if self.index == len(self.df.index) - 1:
                    if self.isSellEqBuyPrice is True:
                        is_trade = 'buy'
                    else:
                        is_trade = 'skip_buy'

        if self.is_buy is True \
                and float(self.df['현재가'][self.index]) >= get_percent_price_etf(self.preBuyPrice, SUCCESS_SELL_PROFIT):
            self.real_buy_percent = 50
            self.is_buy = False
            self.test_success_sell_index_list.append(self.index)
            self.test_success_sell_price_list.append(self.df['등락율'][self.index])
            profit = ((get_percent(self.preBuyPrice, int(self.df['현재가'][self.index])) - TAX) * self.period_buy_count)
            self.preSellPrice = int(self.df['현재가'][self.index])
            self.success_trade_count = self.success_trade_count + 1
            if self.isSellEqBuyPrice:
                self.profit += profit
                self.total_money_profit += ((int(self.df['현재가'][self.index]) - self.preBuyPrice) * self.period_buy_count)
            else:
                print('code[%s][%s][%s] -        Skip - different sell price' % (self.df['코드'][self.index], self.index, self.df['시간'][self.index]))
                self.profit += 0.001
                self.total_money_profit += 0
            self.skip_total_money_profit += ((int(self.df['현재가'][self.index]) - self.preBuyPrice) * self.period_buy_count)
            print('code[%s][%s][%s] - SUCCESS Sell buy_price[%s] sell_price[%s] profit[%s] total_profit[%s] total_money[%s] skip_total_money_profit[%s] 성공[%s] 실패[%s] 구간최고가격[%s] 구간최저가격[%s] index[%s]' % (
                    self.df['코드'][self.index], self.index, self.df['시간'][self.index], self.preBuyPrice,
                    int(self.df['현재가'][self.index]), profit,
                    self.profit, self.total_money_profit, self.skip_total_money_profit, self.success_trade_count, self.failed_trade_count,
                    self.period_top_price - self.preBuyPrice, self.period_min_price - self.preBuyPrice,
                    self.index - self.period_index))
            if self.index == len(self.df.index) - 1:
                is_trade = 'sell_success'

        elif self.is_buy is True and float(self.df['현재가'][self.index]) <= get_percent_price_etf(self.preBuyPrice, FAILED_SELL_PROFIT):
            self.real_buy_percent = 50
            self.is_buy = False
            self.test_fail_sell_index_list.append(self.index)
            self.test_fail_sell_price_list.append(self.df['등락율'][self.index])
            profit = ((get_percent(self.preBuyPrice, int(self.df['현재가'][self.index])) - TAX - 0.2) * self.period_buy_count)
            self.preSellPrice = int(self.df['현재가'][self.index])

            if self.isSellEqBuyPrice:
                self.profit += profit
                self.total_money_profit += ((int(self.df['현재가'][self.index]) - self.preBuyPrice - 20) * self.period_buy_count)
            else:
                print('code[%s][%s][%s] - Skip NOT Same Price' % (self.df['코드'][self.index], self.index, self.df['시간'][self.index]))
                self.profit += -0.001
                self.total_money_profit += 0
            self.skip_total_money_profit += ((int(self.df['현재가'][self.index]) - self.preBuyPrice - 20) * self.period_buy_count)
            self.failed_trade_count = self.failed_trade_count + 1
            print('code[%s][%s][%s] - FAILED Sell buy_price[%s] sell_price[%s] profit[%s] total_profit[%s] skip_total_money_profit[%s] money[%s] 성공[%s] 실패[%s] 구간최고가격[%s] 구간최저가격[%s] index[%s]' % (
                    self.df['코드'][self.index], self.index, self.df['시간'][self.index], self.preBuyPrice,
                    int(self.df['현재가'][self.index]), profit,
                    self.profit, self.total_money_profit, self.skip_total_money_profit, self.success_trade_count, self.failed_trade_count,
                    self.period_top_price - self.preBuyPrice, self.period_min_price - self.preBuyPrice,
                    self.index - self.period_index))
            if self.index == len(self.df.index) - 1:
                is_trade = 'sell_failed'

        # elif self.is_buy is True and float(self.df['현재가'][self.index]) <= get_percent_price_etf(self.preBuyPrice, -1.5) \
        #         and self.period_buy_count == 2:
        #     self.물타기_index_list.append(self.index)
        #     self.물타기_price_list.append(self.df['등락율'][self.index])
        #     self.period_buy_count = self.period_buy_count + self.period_buy_count
        #
        #     ride_price = int((self.preBuyPrice + self.df['현재가'][self.index]) / 2)
        #
        #     print('>>> 2 ride code[%s][%s] buy[%s] now[%s] ride_price[%s] buy_count[%s] money[%s] index[%s] buy_index[%s]' % (
        #             self.code, self.df['시간'][self.index], self.preBuyPrice, self.df['현재가'][self.index], ride_price,
        #             self.period_buy_count, ride_price * self.period_buy_count, self.index - self.period_물타기_index,
        #             self.index - self.period_index))
        #     self.preBuyPrice = ride_price
        #     self.period_물타기_index = self.index

        elif self.is_buy is True and float(self.df['현재가'][self.index]) <= get_percent_price_etf(self.preBuyPrice, RIDE_1_PROFIT) \
                and self.period_buy_count == 1:
            self.물타기_index_list.append(self.index)
            self.물타기_price_list.append(self.df['등락율'][self.index])
            self.period_buy_count = self.period_buy_count + self.period_buy_count

            ride_price = int((self.preBuyPrice + self.df['현재가'][self.index]) / 2)

            print('>>> 1 ride code[%s][%s] buy[%s] now[%s] ride_price[%s] buy_count[%s] money[%s] index[%s] buy_index[%s]' % (
                    self.code, self.df['시간'][self.index], self.preBuyPrice, self.df['현재가'][self.index], ride_price,
                    self.period_buy_count, ride_price * self.period_buy_count, self.index - self.period_물타기_index,
                    self.index - self.period_index))
            self.preBuyPrice = ride_price
            self.period_물타기_index = self.index

        self.index += 1
        return (is_trade, print_log)

    def test_profit(self):
        if self.is_buy:
            last_index = len(self.df['현재가']) - 1
            if self.isSellEqBuyPrice:
                profit = ((get_percent(self.preBuyPrice,int(self.df['현재가'][last_index])) - TAX - 0.2) * self.period_buy_count)
                self.total_money_profit += ((int(self.df['현재가'][last_index]) - self.preBuyPrice - 20) * self.period_buy_count)
            else:
                profit = 0
                print('code[%s]- Skip NOT Same Price' % (self.df['코드'][last_index]))
            self.skip_total_money_profit += ((int(self.df['현재가'][last_index]) - self.preBuyPrice - 20) * self.period_buy_count)

            print(
                'END NOT SELL code[%s][%s] - Sell buy_price[%s] sell_price[%s] profit[%s] total_profit[%s] total_money[%s] skip_total_money_profit[%s] 성공[%s] 실패[%s] 구간최고가격[%s] 구간최저가격[%s] index[%s]' % (
                    self.df['코드'][last_index], self.index, self.preBuyPrice, int(self.df['현재가'][last_index]), profit,
                    self.profit, self.total_money_profit, self.skip_total_money_profit, self.success_trade_count, self.failed_trade_count,
                    self.period_top_price - self.preBuyPrice, self.period_min_price - self.preBuyPrice,
                    self.index - self.period_index))
        print('END 종목[%s] 수익률[%s] 현금[%s]' % (self.code, self.profit, self.total_money_profit))
        return int(self.profit), self.total_money_profit, self.skip_total_money_profit

    def show_graph(self):
        fig, axs = plt.subplots(4)

        ax = axs[0]
        ax.plot(self.df['등락율'])
        ax.scatter(self.buy_list, self.등략율_list, c='r')
        ax.scatter(self.pattern_list, self.pattern_list_price, c='g')

        ax.scatter(self.test_success_sell_index_list, self.test_success_sell_price_list, c='b')
        ax.scatter(self.test_fail_sell_index_list, self.test_fail_sell_price_list, c='y')
        ax.scatter(self.물타기_index_list, self.물타기_price_list, c='k')

        ax.grid(True)

        ax = axs[1]
        ax.plot(self.등락율차이)
        ax.grid(True)

        ax = axs[2]
        ax.plot(self.현재가차이)
        ax.grid(True)

        ax = axs[3]
        ax.plot(self.거래대금차이)
        ax.grid(True)

        #
        # ax = axs[3]
        # ax.plot(self.이전시간_현재시간_매수_매도_차이_리스트)
        # ax.grid(True)

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

    def ini_stock_code(self, code):
        self.stocks.get(code).__init__(code)

    def get_stock_code(self, code):
        return self.stocks.get(code)

    def all_print_stock(self):
        for stockCode in self.stocks.keys():
            code = self.stocks.get(stockCode)
            code.show_graph()

    def is_buy_another_stock(self, code):
        isBuy = False
        buy_code = ''
        for stockCode in self.stocks.keys():
            if stockCode == code:
                continue
            stock = self.stocks.get(stockCode)
            if stock.is_buy:
                isBuy = True
                buy_code = stockCode
                break
        return isBuy, buy_code


stockManager = StockManager()
