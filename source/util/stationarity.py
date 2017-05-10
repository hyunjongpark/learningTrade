# -*- coding: utf-8 -*-

import os, sys, datetime
import numpy as np
from scipy.ndimage.filters import uniform_filter1d
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import pprint
import statsmodels.tsa.stattools as ts

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *

class Stationarity():
    def __init__(self, df, code, start, end):
        self.df = df
        self.code = code
        self.start = start
        self.end = end
        self.adf_result = self.adf()
        self.hurst = self.hurst_exponent()
        self.half_life = self.half_life()
        # self.show_rolling_mean()

        self.ciritical_values = self.adf_result[4]
        # print('ciritical_values %s' % ciritical_values)


    def get_result(self):
        return self.adf_result[0], self.ciritical_values['1%'], self.ciritical_values['5%'], self.ciritical_values['10%'], self.hurst, self.half_life

    def get_hurst_exponent(self,df, lags_count=100):
        lags = range(2, lags_count)
        ts = np.log(df)

        tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
        poly = np.polyfit(np.log(lags), np.log(tau), 1)

        result = poly[0] * 2.0

        return result


    def get_half_life(self,df):
        price = pd.Series(df)
        lagged_price = price.shift(1).fillna(method="bfill")
        delta = price - lagged_price
        beta = np.polyfit(lagged_price, delta, 1)[0]
        half_life = (-1 * np.log(2) / beta)

        return half_life


    def random_walk(self,seed=1000, mu=0.0, sigma=1, length=1000):
        ts = []
        for i in range(length):
            if i == 0:
                ts.append(seed)
            else:
                ts.append(mu + ts[i - 1] + random.gauss(0, sigma))

        return ts


    def draw_moving_average(self,df, title, sell_df=None, buy_df=None, trade_df=None, windows=20):
        # df['Close'].plot(style='k--')
        # df[['Open','High','Low','Close','Adj Close']].plot(kind='box')


        # df['Close'].plot()
        # pd.rolling_mean(df['Close'], 20).plot(color='r')
        # plt.axhline(df['Close'].mean(), color='g')
        #
        # if sell_df is not None:
        #     # sell_df['Close'].plot()
        #     df.plot.scatter(sell_df.index, sell_df['Close'], 'ro')
        #
        # if buy_df is not None:
        #     buy_df['Close'].plot()
        # plt.show()

        fig, axs = plt.subplots(2)
        ax = axs[0]
        ax.plot(df['Close'])
        ax.plot(pd.rolling_mean(df['Close'], windows), 'r')
        if sell_df is not None:
            ax.plot(sell_df.index, sell_df['Close'], 'bo')
        if buy_df is not None:
            ax.plot(buy_df.index, buy_df['Close'], 'yo')
        if trade_df is not None:
            ax.plot(trade_df.index, trade_df['Close'], 'ro')
        ax.axhline(df['Close'].mean(), color='red')
        ax.set_title(title)
        ax.grid(True)
        ax = axs[1]
        ax.plot(df['Volume'], 'b')
        ax.grid(True)
        plt.show()


    def do_mean_reversion(self,df, window_size, index):
        df_ma = pd.rolling_mean(df, window_size)
        df_std = pd.rolling_std(df, window_size)
        diff = df.loc[index, 0] - df_ma.loc[index, 0]
        print(diff)


    def adf(self):
        adf_result = ts.adfuller(self.df["Close"])
        pprint.pprint(adf_result)
        return adf_result


    def hurst_exponent(self):
        hurst = self.get_hurst_exponent(self.df['Close'])
        print("Hurst Exponent : %s=%s" % (self.code, hurst))
        return hurst


    def half_life(self):
        half_life = self.get_half_life(self.df['Close'])
        print("Half_life :  %s=%s" % (self.code, half_life))
        return half_life


    def show_rolling_mean(self, title='title', sell_df=None, buy_df=None, trade_df=None, window=20):
        self.draw_moving_average(self.df, title, sell_df, buy_df,trade_df, window)

