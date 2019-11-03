# -*- coding: utf-8 -*-
from __future__ import division
import os, sys

import matplotlib.pyplot as plt

class Stock():
    def __init__(self, log):
        list = log.split(',')


        self.time = list[0].split(':')[1].strip() #시간
        self.hname = list[1].split(':')[1].strip() #이름
        self.code = list[2].split(':')[1].strip() #코드
        self.price = list[3].split(':')[1].strip() #가격
        self.sign = list[4].split(':')[1].strip() #전일대비구분
        self.change = list[5].split(':')[1].strip() #전일대비
        self.diff = list[6].split(':')[1].strip() #등락율
        self.volume = list[7].split(':')[1].strip() #누적거래량
        self.recprice = list[8].split(':')[1].strip() #기준가
        self.avg = list[9].split(':')[1].strip() #가중평균
        self.vol = list[10].split(':')[1].strip() #회전율
        self.volumediff = list[11].split(':')[1].strip() #거래량차
        self.jvolume = list[12].split(':')[1].strip() #전일동시간거래량
        self.ftradmdvag = list[13].split(':')[1].strip()  # 외국계매도평단가
        self.ftradmsavg = list[14].split(':')[1].strip()  # 외국계매수평단가
        self.fwdvl = list[15].split(':')[1].strip()  # 외국계매도합계수량
        self.ftradmdcha = list[16].split(':')[1].strip()  # 외국계매도직전대비
        self.ftradmddiff = list[17].split(':')[1].strip()  # 외국계매도비율
        self.fwsvl = list[18].split(':')[1].strip()  # 외국계매수합계수량
        self.ftradmscha = list[19].split(':')[1].strip()  # 외국계매수직전대비
        self.ftradmsdiff = list[20].split(':')[1].strip()  # 외국계매수비율

        self.dvol1 = list[21].split(':')[1].strip()  # 총매도수량1
        self.svol1 = list[22].split(':')[1].strip()  # 총매수수량1
        self.dcha1 = list[23].split(':')[1].strip()  # 매도비율1
        self.scha1 = list[24].split(':')[1].strip()  # 매수증감1
        self.ddiff1 = list[25].split(':')[1].strip()  # 매도비율1
        self.sdiff1 = list[26].split(':')[1].strip()  # 매수비율1


        self.dvol2 = list[27].split(':')[1].strip()  # 총매도수량2
        self.svol2 = list[28].split(':')[1].strip()  # 총매수수량2
        self.dcha2 = list[29].split(':')[1].strip()  # 매도비율2
        self.scha2 = list[30].split(':')[1].strip()  # 매수증감2
        self.ddiff2 = list[31].split(':')[1].strip()  # 매도비율2
        self.sdiff2 = list[32].split(':')[1].strip()  # 매수비율2



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
            print(
                '[%s]시간:%s, 이름:%s, 코드:%s, 가격:%s, 전일대비구분:%s, 전일대비:%s, 등락율:%s, 누적거래량:%s, 기준가:%s, 가중평균:%s, 회전율:%s, 거래량차:%s, 전일동시간거래량:%s, 외국계매도평단가:%s, 외국계매수평단가:%s, 외국계매도합계수량:%s, 외국계매도직전대비:%s, 외국계매도비율:%s, 외국계매수합계수량:%s, 외국계매수직전대비:%s, 외국계매수비율:%s, 총매도수량1:%s, 총매수수량1:%s, 매도증감1:%s, 매수증감1:%s, 매도비율1:%s, 매수비율1:%s, 총매도수량2:%s, 총매수수량2:%s, 매도증감2:%s, 매수증감2:%s, 매도비율2:%s, 매수비율2:%s' % (
                index, stock.time, stock.hname, stock.code, stock.price, stock.sign, stock.change, stock.diff, stock.volume, stock.recprice, stock.avg, stock.vol, stock.volumediff,
                stock.jvolume, stock.ftradmdvag, stock.ftradmsavg, stock.fwdvl, stock.ftradmdcha, stock.ftradmddiff, stock.fwsvl, stock.ftradmscha, stock.ftradmsdiff, stock.dvol1,
                stock.svol1, stock.dcha1, stock.scha1, stock.ddiff1, stock.sdiff1, stock.dvol2, stock.svol2,stock.dcha2, stock.scha2, stock.ddiff2, stock.sdiff2))
            index = index + 1


    def show_graph(self):
        fig, axs = plt.subplots(5)
        ax = axs[0]
        ax.plot([stock.diff for stock in self.list])
        ax.grid(True)


        # ax2 = ax.twinx()
        # ax2.plot(get_foreigner_info(code, start, end), 'r')

        ax = axs[1]
        ax.plot([stock.volumediff for stock in self.list])
        ax.get_yaxis().set_visible(False)
        ax.grid(True)

        ax = axs[2]
        ax.plot([stock.dvol1 for stock in self.list], 'b')
        ax.plot([stock.svol1 for stock in self.list], 'r')
        ax.get_yaxis().set_visible(False)
        ax.grid(True)

        ax = axs[3]
        ax.plot([stock.dcha1 for stock in self.list], 'b')
        ax.plot([stock.scha1 for stock in self.list], 'r')
        ax.get_yaxis().set_visible(False)
        ax.grid(True)
        #
        ax = axs[4]
        ax.plot([stock.ddiff1 for stock in self.list], 'b')
        ax.plot([stock.sdiff1 for stock in self.list], 'r')
        ax.get_yaxis().set_visible(False)
        ax.grid(True)


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
