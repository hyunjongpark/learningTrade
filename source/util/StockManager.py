# -*- coding: utf-8 -*-
from __future__ import division
import os, sys

import matplotlib.pyplot as plt

class Stock():
    def __init__(self, log):
        list = log.split('|')
        self.time = list[0].strip()
        self.name = list[1].strip()
        self.code = list[2].strip()
        self.price = list[3].strip()
        self.diff = list[4].strip()
        self.volume = list[5].strip()
        self.vol = list[6].strip()
        self.dvol1 = list[7].strip()
        self.svol1 = list[8].strip()
        self.dcha1 = list[9].strip()
        self.scha1 = list[10].strip()
        self.ddiff1 = list[11].strip()
        self.sdiff1 = list[12].strip()


class StockCode():
    def __init__(self, code):
        # print('StockCode[%s]' % (code))
        self.list = []
        self.code = code

    def register(self, log):
        stock = Stock(log)
        self.list.append(stock)

    def print(self):
        index = 0
        for stock in self.list:
            print('[%s][%s][%s-%s] 가격:%s, 전일대비:%s, 누적거래량:%s, 회전율:%s, 총매도수량1:%s, 총매수수량1:%s, 매도증감1:%s, 매수증감1:%s, 매도비율1:%s, 매수비율1:%s'
                  % (index, stock.time, stock.name, stock.code, stock.price, stock.diff, stock.volume, stock.vol, stock.dvol1, stock.svol1, stock.dcha1, stock.scha1, stock.ddiff1, stock.sdiff1))
            index = index + 1

    def getDataList(self):
        ret = []
        for stock in self.list:
            ret.append(stock.price)
        return ret

    def show_graph(self):
        fig, axs = plt.subplots(6)
        ax = axs[0]
        ax.plot(self.getDataList())
        # ax.plot([stock.volume for stock in self.list])
        ax.grid(True)

        # ax2 = ax.twinx()
        # ax2.plot(get_foreigner_info(code, start, end), 'r')

        ax = axs[1]
        ax.plot([stock.volume for stock in self.list])
        ax.grid(True)

        ax = axs[2]
        ax.plot([stock.dcha1 for stock in self.list])
        ax.grid(True)

        ax = axs[3]
        ax.plot([stock.scha1 for stock in self.list])
        ax.grid(True)
        #
        ax = axs[4]
        ax.plot([stock.ddiff1 for stock in self.list])
        ax.grid(True)

        ax = axs[5]
        ax.plot([stock.sdiff1 for stock in self.list])
        ax.grid(True)
        #
        # ax = axs[5]
        # ax.plot([stock.volume for stock in self.list])
        # ax.grid(True)

        plt.show()

class StockManager:
    def __init__(self):
        self.stocks = dict()

    def register(self, code, log):

        stockCode = self.stocks.get(code)
        if stockCode == None:
            stockCode = StockCode(code)
            stockCode.register(log)
            self.stocks[code] = stockCode
        else:
            stockCode.register(log)

        # stockCode.print()

    def all_print_stock(self):
        for stockCode in self.stocks.keys():
            code = self.stocks.get(stockCode)
            code.print()
            code.show_graph()
            # self.stocks.get(stockCode)



stockManager = StockManager()
