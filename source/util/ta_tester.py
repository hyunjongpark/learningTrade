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


    def add_pattern(self, df):
        output = talib.CDL2CROWS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output > 0, 1, output)
        output = talib.CDL3BLACKCROWS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 2, result)
        output = talib.CDL3INSIDE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 3, result)
        output = talib.CDL3LINESTRIKE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 4, result)
        output = talib.CDL3OUTSIDE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 5, result)
        output = talib.CDL3STARSINSOUTH(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 6, result)
        output = talib.CDL3WHITESOLDIERS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 7, result)
        output = talib.CDLABANDONEDBABY(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 8, result)
        output = talib.CDLADVANCEBLOCK(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 9, result)
        output = talib.CDLBELTHOLD(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 10, result)
        output = talib.CDLBREAKAWAY(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 11, result)
        output = talib.CDLCLOSINGMARUBOZU(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 12, result)
        output = talib.CDLCONCEALBABYSWALL(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 13, result)
        output = talib.CDLCOUNTERATTACK(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 14, result)
        output = talib.CDLDARKCLOUDCOVER(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 15, result)
        output = talib.CDLDOJI(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 16, result)
        output = talib.CDLDOJISTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 17, result)
        output = talib.CDLDRAGONFLYDOJI(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 18, result)
        output = talib.CDLENGULFING(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 19, result)
        output = talib.CDLEVENINGDOJISTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 20, result)
        output = talib.CDLEVENINGSTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 21, result)
        output = talib.CDLGAPSIDESIDEWHITE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 22, result)
        output = talib.CDLGRAVESTONEDOJI(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 23, result)
        output = talib.CDLHAMMER(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 24, result)
        output = talib.CDLHANGINGMAN(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 25, result)
        output = talib.CDLHARAMI(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 26, result)
        output = talib.CDLHARAMICROSS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 27, result)
        output = talib.CDLHIGHWAVE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 28, result)
        output = talib.CDLHIKKAKE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 29, result)
        output = talib.CDLHIKKAKEMOD(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 30, result)
        output = talib.CDLHOMINGPIGEON(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 31, result)
        output = talib.CDLIDENTICAL3CROWS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 32, result)
        output = talib.CDLINNECK(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 33, result)
        output = talib.CDLINVERTEDHAMMER(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 34, result)
        output = talib.CDLKICKING(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 35, result)
        output = talib.CDLKICKINGBYLENGTH(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 36, result)
        output = talib.CDLLADDERBOTTOM(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 37, result)
        output = talib.CDLLONGLEGGEDDOJI(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 38, result)
        output = talib.CDLLONGLINE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 39, result)
        output = talib.CDLMARUBOZU(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 40, result)
        output = talib.CDLMATCHINGLOW(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 41, result)
        output = talib.CDLMATHOLD(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 42, result)
        output = talib.CDLMATCHINGLOW(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 43, result)
        output = talib.CDLMORNINGDOJISTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 44, result)
        output = talib.CDLMORNINGSTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 45, result)
        output = talib.CDLONNECK(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 46, result)
        output = talib.CDLPIERCING(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 47, result)
        output = talib.CDLRICKSHAWMAN(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 48, result)
        output = talib.CDLRISEFALL3METHODS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 49, result)
        output = talib.CDLSEPARATINGLINES(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 50, result)
        output = talib.CDLSHOOTINGSTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 51, result)
        output = talib.CDLSHORTLINE(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 52, result)
        output = talib.CDLSPINNINGTOP(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 53, result)
        output = talib.CDLSTALLEDPATTERN(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 54, result)
        output = talib.CDLSTICKSANDWICH(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 55, result)
        output = talib.CDLTAKURI(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 56, result)
        output = talib.CDLTASUKIGAP(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 57, result)
        output = talib.CDLTHRUSTING(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 58, result)
        output = talib.CDLTRISTAR(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 59, result)
        output = talib.CDLUNIQUE3RIVER(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 60, result)
        output = talib.CDLUPSIDEGAP2CROWS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 61, result)
        output = talib.CDLXSIDEGAP3METHODS(df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values)
        result = np.where(output == 100, 62, result)
        df['PATTERN'] = result
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

