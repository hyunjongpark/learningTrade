import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt

start = datetime.datetime(2016,1,19)
end = datetime.datetime(2017,12,31)
gs = web.DataReader("005930.ks", "yahoo", start, end)
plt.plot(gs.index, gs['Close'])
plt.title('TEST')
plt.show()
