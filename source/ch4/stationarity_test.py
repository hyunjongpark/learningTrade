# -*- coding: utf-8 -*-

import os, sys, datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import pprint
import statsmodels.tsa.stattools as ts

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *


def get_hurst_exponent(df, lags_count=100):
    lags = range(2, lags_count)
    ts = np.log(df)

    tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
    poly = np.polyfit(np.log(lags), np.log(tau), 1)

    result = poly[0] * 2.0

    return result

import pandas as pd

def get_half_life(df):
    price = pd.Series(df)
    lagged_price = price.shift(1).fillna(method="bfill")
    delta = price - lagged_price
    beta = np.polyfit(lagged_price, delta, 1)[0]
    return (-1 * np.log(2) / beta)


def random_walk(seed=1000, mu=0.0, sigma=1, length=1000):
    """ this function creates a series of independent, identically distributed values
    with the form of a random walk. Where the best prediction of the next value is the present
    value plus some random variable with mean and variance finite 
    We distinguish two types of random walks: (1) random walk without drift (i.e., no constant
    or intercept term) and (2) random walk with drift (i.e., a constant term is present).  
    The random walk model is an example of what is known in the literature as a unit root process.
    RWM without drift: Yt = YtÃ¢ÂÂ1 + ut
    RWM with drift: Yt = ÃÂ´ + YtÃ¢ÂÂ1 + ut
    """

    ts = []
    for i in range(length):
        if i == 0:
            ts.append(seed)
        else:
            ts.append(mu + ts[i - 1] + random.gauss(0, sigma))

    return ts


def draw_moving_average(df):
    df.plot(style='k--')
    pd.rolling_mean(df, 20).plot(style='k')

    plt.show()


def do_mean_reversion(df, window_size, index):
    df_ma = pd.rolling_mean(df, window_size)
    df_std = pd.rolling_std(df, window_size)

    diff = df.loc[index, 0] - df_ma.loc[index, 0]
    print(diff)


def adf(df):
    # Calculate and output the CADF test on the residuals
    # http://statsmodels.sourceforge.net/devel/generated/statsmodels.tsa.stattools.adfuller.html
    # df = load_stock_data('005930_삼성전자.data')
    # end = datetime.datetime.today()
    # start = end - relativedelta(months=12)
    # df_samsung = df[start:end]

    adf_result = ts.adfuller(df["Close"])
    pprint.pprint(adf_result)
    # df_hanmi = load_stock_data('hanmi.data')
    # adf_result = ts.adfuller(df_hanmi["Close"])
    # print('----- hanmi ADF -----')
    # pprint.pprint(adf_result)


def hurst_exponent(df):
    hurst_samsung = get_hurst_exponent(df['Close'])
    print("Hurst Exponent: %s " % (hurst_samsung))


def half_life(df):
    half_life = get_half_life(df['Close'])
    print("Half_life: %s" % (half_life))


def rolling_mean(df):
    # df_samsung = load_stock_data('005930_삼성전자.data')
    # print (df_samsung['Close'])
    # draw_moving_average(df['Close'])
    df['Close'].plot()
    plt.axhline(df['Close'].mean(), color='red')
    plt.show()

    # do_mean_reversion(df_samsung['Close'],10,100)


if __name__ == "__main__":

    end = datetime.datetime.today()
    # end = datetime.datetime.strptime('20160601', '%Y%m%d')
    start = end - relativedelta(months=24)

    # data = load_yaml('kospi100')
    # for code, value in data.iterItems():
    #     df = get_df_from_file(code, start, end)
    #     print(code)
    #     adf(df)
    #     hurst_exponent(df)
    #     half_life(df)
    #     # rolling_mean(df)


    # df = load_stock_data('145990_삼양사.data')
    df = load_stock_data('003520_영진약품.data')
    df_samsung = df[start:end]
    print(df_samsung.describe())
    adf(df_samsung)
    hurst_exponent(df_samsung)
    half_life(df_samsung)
    rolling_mean(df_samsung)
