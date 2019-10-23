# -*- coding: utf-8 -*-
from __future__ import division

import os, sys
import matplotlib.pyplot as plt
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC, SVC
from sklearn.model_selection import cross_validate
#https://github.com/mrjbq7/ta-lib
#https://mrjbq7.github.io/ta-lib/doc_index.html
#https://booja.blogspot.com/2017/12/python-ta-lib.html

#http://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
#https://pip.pypa.io/en/latest/user_guide/#installing-from-wheels
import talib
from talib import MA_Type


parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *
from util.services import *


class ta_tester():
    def __init__(self):
        print('ta_tester')
        self.code = None
        self.fastperiod = 12
        self.slowperiod = 26
        self.signalperiod = 9
        self.profit = 0

    def set_code(self, code):
        self.code = code

    def test(self, code='004990'):
        end = datetime.datetime.today()
        start = end - relativedelta(months=24)
        df = get_df_from_file(code, start, end)

        df = self.add_sma(df)
        df = self.add_bbands(df)
        df = self.add_mom(df)
        # df = self.add_stoch(df)
        df = self.add_macd(df)
        df = self.add_pattern(df)


        # print(df)

        fig, axs = plt.subplots(6)
        ax = axs[0]
        ax.plot(df["Close"])

        ax.plot(df['SMA'])
        ax.grid(True)

        ax2 = ax.twinx()
        ax2.plot(get_foreigner_info(code, start, end), 'r')


        ax = axs[1]
        ax.plot(df["Close"])
        ax.plot(df['BBANDS_upper'])
        ax.plot(df['BBANDS_middle'])
        ax.plot(df['BBANDS_lower'])
        ax.grid(True)

        ax = axs[2]
        ax.plot(df["MOM"], 'r')
        ax.grid(True)

        # ax = axs[3]
        # ax.plot(df["STOCH_slowk"])
        # ax.plot(df["STOCH_slowd"])
        # ax.grid(True)

        ax = axs[3]
        ax.plot(df["MACD_macd"])
        ax.plot(df["MACD_signal"])
        ax.plot(df["MACD_hist"])
        ax.grid(True)

        ax = axs[4]
        ax.plot(df["Volume"])
        ax.grid(True)

        ax = axs[5]
        ax.plot(df['SMA'])
        ax.grid(True)


        plt.show()

    def get_pattern(self, src, new, pattern_index):
        for i in range(len(new)):
            if new[i] > 0:
                if 0 == src[i]:
                    src[i] = pattern_index
                else:
                    src[i] = '%s : %s ' %(src[i], pattern_index)
                    # print('[%s] src[%s] add[%s]' % (i, src[i], pattern_index))
            elif new[i] < 0:
                if 0 == src[i]:
                    src[i] = -pattern_index
                else:
                    src[i] = '%s : %s ' %(src[i], -pattern_index)
                    # print('[%s] src[%s] add[%s]' % (i, src[i], -pattern_index))
        return src

    def add_pattern(self, df):
        result = []
        output = talib.CDL2CROWS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        for i in range(len(output)):
            result.append(0)

        result = self.get_pattern(result, output, 1)
        output = talib.CDL3BLACKCROWS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 2)
        output = talib.CDL3INSIDE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 3)
        output = talib.CDL3LINESTRIKE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 4)
        output = talib.CDL3OUTSIDE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 5)
        output = talib.CDL3STARSINSOUTH(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 6)
        output = talib.CDL3WHITESOLDIERS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 7)
        output = talib.CDLABANDONEDBABY(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 8)
        output = talib.CDLADVANCEBLOCK(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 9)
        output = talib.CDLBELTHOLD(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 10)
        output = talib.CDLBREAKAWAY(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 11)
        output = talib.CDLCLOSINGMARUBOZU(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 12)
        output = talib.CDLCONCEALBABYSWALL(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 13)
        output = talib.CDLCOUNTERATTACK(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 14)
        output = talib.CDLDARKCLOUDCOVER(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 15)
        output = talib.CDLDOJI(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 16)
        output = talib.CDLDOJISTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 17)
        output = talib.CDLDRAGONFLYDOJI(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 18)
        output = talib.CDLENGULFING(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 19)
        output = talib.CDLEVENINGDOJISTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 20)
        output = talib.CDLEVENINGSTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 21)
        output = talib.CDLGAPSIDESIDEWHITE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 22)
        output = talib.CDLGRAVESTONEDOJI(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 23)
        output = talib.CDLHAMMER(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 24)
        output = talib.CDLHANGINGMAN(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 25)
        output = talib.CDLHARAMI(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 26)
        output = talib.CDLHARAMICROSS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 27)
        output = talib.CDLHIGHWAVE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 28)
        output = talib.CDLHIKKAKE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 29)
        output = talib.CDLHIKKAKEMOD(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 30)
        output = talib.CDLHOMINGPIGEON(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 31)
        output = talib.CDLIDENTICAL3CROWS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 32)
        output = talib.CDLINNECK(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 33)
        output = talib.CDLINVERTEDHAMMER(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 34)
        output = talib.CDLKICKING(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 35)
        output = talib.CDLKICKINGBYLENGTH(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 36)
        output = talib.CDLLADDERBOTTOM(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 37)
        output = talib.CDLLONGLEGGEDDOJI(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 38)
        output = talib.CDLLONGLINE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 39)
        output = talib.CDLMARUBOZU(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 40)
        output = talib.CDLMATCHINGLOW(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 41)
        output = talib.CDLMATHOLD(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 42)
        output = talib.CDLMATCHINGLOW(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 43)
        output = talib.CDLMORNINGDOJISTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 44)
        output = talib.CDLMORNINGSTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 45)
        output = talib.CDLONNECK(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 46)
        output = talib.CDLPIERCING(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 47)
        output = talib.CDLRICKSHAWMAN(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 48)
        output = talib.CDLRISEFALL3METHODS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 49)
        output = talib.CDLSEPARATINGLINES(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 50)
        output = talib.CDLSHOOTINGSTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 51)
        output = talib.CDLSHORTLINE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 52)
        output = talib.CDLSPINNINGTOP(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 53)
        output = talib.CDLSTALLEDPATTERN(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 54)
        output = talib.CDLSTICKSANDWICH(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 55)
        output = talib.CDLTAKURI(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 56)
        output = talib.CDLTASUKIGAP(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 57)
        output = talib.CDLTHRUSTING(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 58)
        output = talib.CDLTRISTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 59)
        output = talib.CDLUNIQUE3RIVER(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 60)
        output = talib.CDLUPSIDEGAP2CROWS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 61)
        output = talib.CDLXSIDEGAP3METHODS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = self.get_pattern(result, output, 62)
        df['PATTERN'] = result
        for i in range(len(result)):
            print('[%s]: [%s][%s][%s][%s]  %s' % (i, df.iloc[i].name, df['High'].values[i],  df['Close'].values[i],  df['Low'].values[i], result[i]))

        return df

    def add_sma(self, df):
        output = talib.SMA(df['Close'].values, timeperiod=25)
        df['SMA'] = output
        return df

    def add_bbands(self, df):
        upper, middle, lower = talib.BBANDS(df['Close'].values, 20, 2, 2)
        df['BBANDS_upper'] = upper
        df['BBANDS_middle'] = middle
        df['BBANDS_lower'] = lower
        return df

    def add_mom(self, df):
        output = talib.MOM(df['Close'].values)
        df['MOM'] = output
        return df

    def add_stoch(self, df):
        slowk, slowd = talib.STOCH(df['High'].values,
                                   df['Low'].values,
                                   df['Open'].values,
                                   fastk_period=5,
                                   slowk_period=3,
                                   slowk_matype=0,
                                   slowd_period=3,
                                   slowd_matype=0)
        df['STOCH_slowk'] = slowk
        df['STOCH_slowd'] = slowd
        return df

    def add_macd(self, df):

        success, profit, fastperiod, slowperiod, signalperiod = get_best_macd_value(self.code)
        if success != True:
            self.fastperiod = 12
            self.slowperiod = 26
            self.signalperiod = 9
        self.profit = profit


        macd, signal, hist = talib.MACD(df['Close'].values,
                                        self.fastperiod,
                                        self.slowperiod,
                                        self.signalperiod)
        df['MACD_macd'] = macd
        df['MACD_signal'] = signal
        df['MACD_hist'] = hist
        return df

    def add_macd_foreigner_count(self, df):

        success, profit, fastperiod, slowperiod, signalperiod = get_best_macd_value(self.code)
        if success != True:
            self.fastperiod = 12
            self.slowperiod = 26
            self.signalperiod = 9
        self.profit = profit

        macd, signal, hist = talib.MACD(df['foreigner_count'].values,
                                        self.fastperiod,
                                        self.slowperiod,
                                        self.signalperiod)
        df['MACD_foreigner_count_macd'] = macd
        df['MACD_foreigner_count_signal'] = signal
        df['MACD_foreigner_count_hist'] = hist
        return df

    def get_best_value(self, code):
        load_yaml()

