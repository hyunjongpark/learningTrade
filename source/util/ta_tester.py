# -*- coding: utf-8 -*-
from __future__ import division

import os, sys
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC, SVC
from sklearn import cross_validation
#https://github.com/mrjbq7/ta-lib

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

    def test(self, code='004990'):
        end = datetime.datetime.today()
        start = end - relativedelta(months=24)
        df = get_df_from_file(code, start, end)

        df = self.add_sma(df)
        df = self.add_bbands(df)
        df = self.add_mom(df)
        df = self.add_stoch(df)
        df = self.add_macd(df)


        # print(df)

        fig, axs = plt.subplots(6)
        ax = axs[0]
        ax.plot(df["Close"])
        ax.plot(df['SMA'])
        ax.grid(True)


        ax = axs[1]
        ax.plot(df["Close"])
        ax.plot(df['BBANDS_upper'])
        ax.plot(df['BBANDS_middle'])
        ax.plot(df['BBANDS_lower'])
        ax.grid(True)

        ax = axs[2]
        ax.plot(df["MOM"], 'r')
        ax.grid(True)

        ax = axs[3]
        ax.plot(df["STOCH_slowk"])
        ax.plot(df["STOCH_slowd"])
        ax.grid(True)

        ax = axs[4]
        ax.plot(df["MACD_macd"])
        ax.plot(df["MACD_signal"])
        ax.plot(df["MACD_hist"])
        ax.grid(True)

        ax = axs[5]
        ax.plot(df["Volume"])
        ax.grid(True)

        plt.show()


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
        macd, signal, hist = talib.MACD(df['Close'].values,
                                        fastperiod=12,
                                        slowperiod=26,
                                        signalperiod=9)
        df['MACD_macd'] = macd
        df['MACD_signal'] = signal
        df['MACD_hist'] = hist
        return df

