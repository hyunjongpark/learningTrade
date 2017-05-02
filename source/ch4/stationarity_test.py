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


def get_half_life(df):
    price = pd.Series(df)
    lagged_price = price.shift(1).fillna(method="bfill")
    delta = price - lagged_price
    beta = np.polyfit(lagged_price, delta, 1)[0]
    half_life = (-1 * np.log(2) / beta)

    return half_life


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


def adf():
    # Calculate and output the CADF test on the residuals
    # http://statsmodels.sourceforge.net/devel/generated/statsmodels.tsa.stattools.adfuller.html
    df_samsung = load_stock_data('samsung.data')
    adf_result = ts.adfuller(df_samsung["Close"])
    print('----- Samsung ADF -----')
    pprint.pprint(adf_result)

    df_hanmi = load_stock_data('hanmi.data')
    adf_result = ts.adfuller(df_hanmi["Close"])
    print('----- hanmi ADF -----')
    pprint.pprint(adf_result)


def hurst_exponent():
    df_samsung = load_stock_data('samsung.data')
    df_hanmi = load_stock_data('hanmi.data')
    hurst_samsung = get_hurst_exponent(df_samsung['Close'])
    hurst_hanmi = get_hurst_exponent(df_hanmi['Close'])
    print("Hurst Exponent : Samsung=%s, Hanmi=%s" % (hurst_samsung, hurst_hanmi))


def half_life():
    df_samsung = load_stock_data('samsung.data')
    df_hanmi = load_stock_data('hanmi.data')
    half_life_samsung = get_half_life(df_samsung['Close'])
    half_life_hanmi = get_half_life(df_hanmi['Close'])
    print("Half_life : Samsung=%s, Hanmi=%s" % (half_life_samsung, half_life_hanmi))


def rolling_mean():
    df_samsung = load_stock_data('066570_LG전자.data')
    # print (df_samsung['Close'])
    draw_moving_average(df_samsung['Close'])
    # do_mean_reversion(df_samsung['Close'],10,100)


if __name__ == "__main__":
    adf()
    hurst_exponent()
    half_life()
    rolling_mean()
