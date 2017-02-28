import pandas_datareader.data as web
import datetime

start = datetime.datetime(2016,1,19)
end = datetime.datetime(2016,2,19)
gs = web.DataReader("078930.ks", "yahoo", start, end)
print(gs)