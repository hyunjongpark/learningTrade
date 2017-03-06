#-*- coding: utf-8 -*-
import os,sys,datetime
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from pandas.compat import range, lrange, lmap, map, zip
from pandas.tools.plotting import scatter_matrix,autocorrelation_plot

parentPath = os.path.abspath("..")
print(parentPath)
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *


def get_autocorrelation_dataframe(series):
    def r(h):
        return ((data[:n - h] - mean) * (data[h:] - mean)).sum() / float(n) / c0

    n = len(series)
    data = np.asarray(series)

    mean = np.mean(data)
    c0 = np.sum((data - mean) ** 2) / float(n)

    x = np.arange(n) + 1
    y = lmap(r, x)

    df = pd.DataFrame(y, index=x)

    return df


df_samsung = load_stock_data('samsung.data')
df_samsung_corr = get_autocorrelation_dataframe(df_samsung['Close'])

# print df_samsung_corr
#for i in range(df_samsung.shape[0]):
#	arr = df_samsung['Close'].autocorr(lag=i)
#	print "%s, %s" % (i,arr)

#df_samsung_corr = pd.DataFrame(arr,index=arr,columns=arr)

#df_hanmi = load_stock_data('hanmi.data')

#print df_samsung['Close'].cov(df_hanmi['Close'])

#print df_samsung['Close'].corr(df_hanmi['Close'])

fig, axs = plt.subplots(2,1)
axs[1].xaxis.set_visible(False) 

df_samsung['Close'].plot(ax=axs[0])
df_samsung_corr[0].plot(kind='bar',ax=axs[1])
#autocorrelation_plot(df_samsung['Close'],ax=axs[1], kind='box')

plt.show()


