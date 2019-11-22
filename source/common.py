# -*- coding: utf-8 -*-
import pandas as pd
import yaml
import os, sys
import datetime
import numpy as np
from dateutil.relativedelta import relativedelta
from pandas import Series

import requests
import urllib.request as urllib2
import bs4
from bs4 import BeautifulSoup

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)
data_path = os.path.abspath("data")
data_backup_path = os.path.abspath("data_backup")


# data_path = os.path.abspath("../data")

def load_yaml(filename):
    """
    load a yaml file.

    :param str filename: a yaml filename

    :returns dict: parsed yaml data
    """
    # confDir = os.path.abspath('./conf')
    # fileDir = os.path.dirname(os.path.realpath(__file__))

    filePath = os.path.join(data_path, filename)

    with open(filePath, 'r') as stream:
        data = yaml.load(stream, Loader=yaml.FullLoader)
    return data


def load__data_backup_yaml(filename):
    filePath = os.path.join(data_backup_path, filename)
    with open(filePath, 'r') as stream:
        data = yaml.load(stream)
    return data


def delete_file(filename):
    filePath = os.path.join(data_path, filename)
    if os.path.exists(filePath):
        os.remove(filePath)


def write_yaml(filename, data):
    confParentPath = os.path.abspath("..")
    filePath = os.path.join(data_path, filename)
    with open(filePath, 'w') as stream:
        yaml.dump(data, stream, default_flow_style=False)


def get_data_file_path(file_name):
    full_file_name = "%s/data/%s" % (os.path.dirname(os.path.abspath(__file__)), file_name)
    return full_file_name


def get_data_file_path_fe(file_name):
    full_file_name = "%s/data/fe/%s" % (os.path.dirname(os.path.abspath(__file__)), file_name)
    return full_file_name


def save_stock_data(df, file_name):
    new_file_name = get_data_file_path(file_name)
    df.to_pickle(new_file_name)


def save_stock_data_fe(df, file_name):
    new_file_name = get_data_file_path_fe(file_name)
    df.to_pickle(new_file_name)


def save_stock_csv_data(df, file_name):
    new_file_name = get_data_file_path(file_name)
    df.to(new_file_name)


def load_stock_data(file_name):
    new_file_name = get_data_file_path(file_name)
    df = pd.read_pickle(new_file_name)
    return df


def load_stock_data_fe(file_name):
    new_file_name = get_data_file_path_fe(file_name)
    df = pd.read_pickle(new_file_name)
    return df


def get_data_list():
    dataList = []
    dataPath = os.path.abspath("data")
    # dataPath = os.path.abspath("../data")
    # print(dataPath)
    for i in os.listdir(dataPath):
        # print(i)
        dataList.append(i)
    return dataList


def get_df_from_file(code, start, end):
    dir_list = get_data_list()
    name = [name for name in dir_list if code in name]
    if len(name) == 0:
        return None
    df = load_stock_data(name[0])
    df.sort_index(inplace=True)
    # df = df.drop_duplicates(subset='index')
    df = df.groupby(df.index).first()
    # df = df.set_index('date')
    # print(df)
    # print(df.describe())
    # df_range = df[start:end]
    df = df[df.index > start]
    df = df[df.index <= end]

    # try:
    #     df = load_stock_data(name[0])
    #     print(df)
    #     # print(df.describe())
    #     # df_range = df[start:end]
    #     df = df[df.index > start]
    #     df = df[df.index <= end]
    # except:
    #     return None
    return df


def get_df_from_file_fe(code, start, end):
    dir_list = get_data_list()
    name = [name for name in dir_list if code in name]
    if len(name) == 0:
        return None
    try:
        df = load_stock_data_fe(name[0])
        df = df.set_index('date')
        df = df[df.index > start]
        df = df[df.index <= end]
    except:
        return None
    return df


def get_trade_last_day(code='000030'):
    end = datetime.datetime.today()
    start = end - relativedelta(months=1)
    df = get_df_from_file(code, start, end)
    try:
        return str(df.iloc[len(df) - 1].name).split(' ')[0]
        # return str(df.iloc[0].name).split(' ')[0]
    except:
        return '2015-01-01'


def get_trade_next_day(base_date):
    end = datetime.datetime.today()
    start = end - relativedelta(months=1)
    df = get_df_from_file('000030', start, end)
    df = df[df.index > base_date]
    if len(df) == 0:
        return 'last date'
    return df.iloc[0].name


def getDateByPercent(start_date, end_date, percent):
    days = (end_date - start_date).days
    target_days = np.trunc(days * percent)
    target_date = start_date + relativedelta(days=target_days)
    return target_date


def get_best_macd_value(code):
    try:
        macd_values = load_yaml('macd_trade')
        data = [v for v in macd_values['macd_trade'] if v['code'] == code]
        print(data[0]['top10'])
        profit = str(data[0]['top10'][0]['profit'])
        macd_split = str(data[0]['top10'][0]['value']).split(',')
        fastperiod = int(macd_split[0].strip())
        slowperiod = int(macd_split[1].strip())
        signalperiod = int(macd_split[2].strip())
        return True, profit, fastperiod, slowperiod, signalperiod
    except:
        return False, None, None, None, None


def is_mean_state(code):
    end = datetime.datetime.today()
    start = end - relativedelta(months=1)
    df = get_df_from_file(code, start, end)
    df_ma = Series.rolling(df['Close'], center=False, window=5).mean()
    df_std = Series.rolling(df['Close'], center=False, window=5).std()
    diff = df['Close'] - df_ma
    check_diff_std = np.abs(diff) - df_std
    last_index = len(df) - 1
    today_price = df.iloc[last_index]['Close']
    if str(float(today_price)).lower() == 'nan':
        return 0
    if check_diff_std[last_index] < 0:
        return 0
    if diff[last_index] > 0:
        if df.iloc[last_index]['Close'] > df_ma.iloc[last_index]:
            return -1  # sell
        else:
            return 0
    else:
        if df.iloc[last_index]['Close'] < df_ma.iloc[last_index]:
            return 1  # buy
        else:
            return 0


def get_percent(base, diff):
    if base == 0 or diff == 0:
        return 0
    return (base - diff) / (base / 100) * -1


def get_percent_price(base, p):
    return base + ((base / 100) * p)

def get_buy_count(quote_price, currentPrice):
    step_price = 1
    if currentPrice < 1000:
        step_price = 1
    elif currentPrice < 5000:
        step_price = 5
    elif currentPrice < 10000:
        step_price = 10
    elif currentPrice < 50000:
        step_price = 50
    elif currentPrice < 100000:
        step_price = 100
    elif currentPrice < 500000:
        step_price = 500
    elif currentPrice > 1000000:
        step_price = 10000

    buy_count = quote_price / currentPrice
    minus_count = buy_count % step_price

    if buy_count > minus_count:
        buyCount = buy_count - minus_count

    return buyCount



def get_foreigner_info(code='000660', start=None, end=None):
    dates = []
    closes = []
    volumes = []
    institution_tradings = []
    foreigner_counts = []

    latest_day = get_trade_last_day(code)

    isStop = False
    for i in range(1, 30):
        if isStop == True:
            break
        url = str('http://finance.naver.com/item/frgn.nhn?code=%s&page=%s' % (code, i))
        print(url)
        html = requests.post(url)
        soup = BeautifulSoup(html.content, "lxml")
        table = soup.find("table", {"summary": "외국인 기관 순매매 거래량에 관한표이며 날짜별로 정보를 제공합니다."})
        for row in table.findAll("tr"):
            cells = row.findAll("td")
            if len(cells) == 9:
                if str(cells[0].find(text=True)).strip() == '':
                    isStop = True
                    break

                date = cells[0].find(text=True)
                # print(cells[1].find(text=True))
                close = float(str(cells[1].find(text=True)).replace(',', ''))
                volume = float(str(cells[4].find(text=True)).replace(',', ''))

                institution_trading = cells[5].find(text=True)
                if "+" in institution_trading:
                    a = str(institution_trading).replace('+', '')
                    b = str(a).replace(',', '')
                    institution_trading = float(b)
                else:
                    a = str(institution_trading).replace('-', '')
                    b = str(a).replace(',', '')
                    institution_trading = float(b) * -1
                foreigner_trading = cells[6].find(text=True)
                foreigner_count = cells[7].find(text=True)
                foreigner_percent = cells[8].find(text=True)

                dates.append(datetime.datetime.strptime(date, '%Y.%m.%d'))
                closes.append(close)
                volumes.append(volume)
                institution_tradings.append(institution_trading)
                foreigner_counts.append(float(str(foreigner_count).replace(',', '')))

        if datetime.datetime.strptime(latest_day, '%Y-%m-%d') in dates:
            break;

    data = {'date': dates, 'Close': closes, 'Volume': volumes, 'institution_trading': institution_tradings,
            'foreigner_count': foreigner_counts}
    df = pd.DataFrame(data);
    df = df.set_index('date')
    df = df[df.index > start]
    df = df[df.index <= end]
    print(df)
    return df
