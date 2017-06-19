# -*- coding: utf-8 -*-
from __future__ import division

import os, sys
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC, SVC
from sklearn import cross_validation
# https://github.com/mrjbq7/ta-lib

# http://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
# https://pip.pypa.io/en/latest/user_guide/#installing-from-wheels
import talib
from talib import MA_Type

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *
from util.services import *


class macd_tester():
    def __init__(self):
        print('macd_tester')
        self.startTradePrice = 0


    def show(self, code='003300', start='20170101', end='20170531', last_day_sell=True):

        # macd_values = load_yaml('macd_trade')

        df = get_df_from_file(code, start, end)

        # data = [v for v in macd_values['macd_trade'] if v['code'] == code]
        # print(data[0]['top10'])
        # print(data[0]['top10'][0]['value'])
        # for data in data[0]['top10']:
        #     print(data)
        #     macd_split = str(data['value']).split(',')
        #     fastperiod = int(macd_split[0].strip())
        #     slowperiod = int(macd_split[1].strip())
        #     signalperiod = int(macd_split[2].strip())

        # macd_split = str(data[0]['top10'][0]['value']).split(',')
        # fastperiod = int(macd_split[0].strip())
        # slowperiod = int(macd_split[1].strip())
        # signalperiod = int(macd_split[2].strip())


        success, profit, fastperiod, slowperiod, signalperiod = get_best_macd_value(code)

        profit, sell_list, buy_list = self.get_profit(df, fastperiod, slowperiod, signalperiod, last_day_sell)
        print('profit: %s' % (profit))
        df = self.add_macd(df, fastperiod, slowperiod, signalperiod)
        self.show_macd_trading(df, sell_df=pd.DataFrame(sell_list), buy_df=pd.DataFrame(buy_list))

    def show_profit_total_all_kospi(self, start, end, view_chart=True, last_day_sell=True):
        data = load_yaml('kospi200')
        totla_profit = 0
        index = 0
        for code, value in data.iterItems():
            df = get_df_from_file(code, start, end)

            success, profit, fastperiod, slowperiod, signalperiod = get_best_macd_value(code)
            if success != True:
                fastperiod = 6
                slowperiod = 29
                signalperiod = 13
            if profit < 0:
                continue

            profit, sell_list, buy_list = self.get_profit(df, fastperiod, slowperiod, signalperiod, last_day_sell)
            if profit == 0:
                continue
            totla_profit += profit
            index += 1

            print('%s/%s [%s] profit: %s, total profit:%s' % (index, len(data.iterItems()), code, profit, (totla_profit / index)))

            if view_chart == True:
                df = self.add_macd(df, fastperiod, slowperiod, signalperiod)
                self.show_macd_trading(df, sell_df=pd.DataFrame(sell_list), buy_df=pd.DataFrame(buy_list))

        print('total profit:%s ' % (totla_profit / index))

    def tomorrow_macd(self, start, end, view_chart=True, last_day_sell=True, save_file=False):
        data = load_yaml('kospi200')
        totla_profit = 0
        index = 0

        save_stocks = {'date': str(end), 'SELL_list': [], 'BUY_list': []}


        for code, value in data.iterItems():
            df = get_df_from_file(code, start, end)

            success, profit, fastperiod, slowperiod, signalperiod = get_best_macd_value(code)
            if success != True:
                fastperiod = 6
                slowperiod = 29
                signalperiod = 13

            profit, sell_list, buy_list = self.get_profit(df, fastperiod, slowperiod, signalperiod, last_day_sell)


            print('Code: %s, profit:%s' % (code, profit))

            if buy_list[len(sell_list)-1].name == get_trade_last_day():
                save_stocks['BUY_list'].append(code)
            if sell_list[len(sell_list) - 1].name == get_trade_last_day():
                save_stocks['SELL_list'].append(code)



        if save_file == True:
            file_name = 'macd_trade'
            saved_data = load_yaml(file_name)
            if saved_data == None:
                saved_data = {file_name: []}
                saved_data[file_name].append(save_stocks)
            else:
                if saved_data[file_name] == None:
                    save_list = {file_name: []}
                    save_list.append(save_stocks)
                else:
                    for index, v in enumerate(saved_data[file_name], start=0):
                        if str(v['date']) == str(end):
                            del saved_data[file_name][index]

                    saved_data[file_name].append(save_stocks)

            write_yaml(file_name, saved_data)

        print('=========================================')
        print(save_stocks)

        for code in save_stocks['BUY_list']:
            print('StockList.add("%s");' % (code))
        return save_stocks



    def make_best_macd_value_all_kospi(self, start, end, last_day_sell=True):
        data = load_yaml('kospi200')
        index = 0
        for code, value in data.iterItems():
            print('%s/%s , code: %s' % (index, len(data.iterItems()), code))
            success, profit, fastperiod, slowperiod, signalperiod = get_best_macd_value(code)
            if success == True:
                print('fastperiod: %s, slowperiod: %s, signalperiod: %s' %(fastperiod, slowperiod, signalperiod))
                index += 1
                continue
            df = get_df_from_file(code, start, end)
            self.train_macd_value(code=code, df=df, last_day_sell=last_day_sell)
            index += 1

    def train_macd_value(self, code, df, last_day_sell=True):
        index = 0
        test_result = {'profit': [], 'macd': []}
        stop = False
        for fast in range(3, 20):
            if stop == True:
                break
            for slow in range(10, 30):
                if stop == True:
                    break
                if fast >= slow:
                    continue
                for signa in range(10, 30):
                    index += 1
                    profit, sell_list, buy_list = self.get_profit(df, fast, slow, signa, last_day_sell)
                    # print('%s: %s,%s,%s, profit:%s' % (index, fast, slow, signa, profit))
                    test_result['profit'].append(profit)
                    test_result['macd'].append('%s, %s, %s' %(fast, slow, signa))
                    # if len(test_result['profit']) > 10:
                    #     stop = True

        df_result = pd.DataFrame(test_result)
        rank_sorted = df_result.sort_values(by='profit', ascending=False)
        print(rank_sorted)
        start_date = df.iloc[0].name
        end_date = df.iloc[len(df) - 1].name

        save_macd = {'code':code, 'start_date': str(start_date), 'end_date': str(end_date), 'top10':[]}

        for index, v in enumerate(rank_sorted['macd'], start=0):
            macd_split = str(rank_sorted.iloc[index]['macd']).split(',')
            # fast = macd_split[0]
            # slow = macd_split[1]
            # signal = macd_split[2]
            profit = rank_sorted.iloc[index]['profit']
            print(rank_sorted.iloc[index])
            # macd_inof = {'fast':fast, 'slow': slow, 'signal': signal, 'profit':str(profit)}
            macd_inof = {'value': str(rank_sorted.iloc[index]['macd']), 'profit': str(profit)}
            exist = False
            for v in save_macd['top10']:
                if str(v['profit']) == str(profit):
                    exist = True
                    break

            if exist == False:
                save_macd['top10'].append(macd_inof)
            if len(save_macd['top10']) > 10:
                break

        saved_data = load_yaml('macd_trade')
        if saved_data == None:
            saved_data = {'macd_trade': []}
            saved_data['macd_trade'].append(save_macd)
        else:
            if saved_data['macd_trade'] == None:
                save_list = {'macd_trade': []}
                save_list.append(rank_sorted)
            else:
                for index, v in enumerate(saved_data['macd_trade'], start=0):
                    if v['code'] == code and str(v['start_date']) == str(start_date) and str(v['end_date']) == str(
                            end_date):
                        del saved_data['macd_trade'][index]

                saved_data['macd_trade'].append(save_macd)

        # saved_data = {'macd_trade': []}
        # saved_data['macd_trade'].append(save_macd)
        # print(saved_data)
        write_yaml('macd_trade', saved_data)
        print(rank_sorted)


    def get_profit(self, df, fastperiod=12, slowperiod=26, signalperiod=9, last_day_sell=True):
        macd, signal, hist = talib.MACD(df['Close'].values,
                                        fastperiod=fastperiod,
                                        slowperiod=slowperiod,
                                        signalperiod=signalperiod)

        """
        READY: 0
        BUY: 1
        SELL: 2
        HOLD: 3
        """
        TAX_RATE = 0.003
        BUY_CHARGE = 0.00015
        SELL_CHARGE = 0.00015

        status = 0

        preBuyPrice = 0
        mscdProfit = 0
        self.startTradePrice = 0

        sell_list = []
        buy_list = []

        for index, date in enumerate(df.index, start=0):
            # print('[%s] macd:%s, signal:%s' % (date, macd[index], signal[index]))
            closePrice = df.iloc[index]['Close']
            if signal[index - 1] > macd[index - 1] and signal[index] < macd[index] and status == 0:
                status = 1
                preBuyPrice = (closePrice + closePrice * BUY_CHARGE)
                buy_list.append(df.iloc[index])
                self.startTradePrice = closePrice
                # print('BUY [%s] price:%s' % (date, closePrice))
            # elif signal[index - 1] <= macd[index - 1] and signal[index] >= macd[index] and (status == 3 or status == 1):
            elif macd[index - 1] >= 0 and macd[index] <= 0 and (status == 3 or status == 1):
                status = 2
                sellPrice = (closePrice - closePrice * SELL_CHARGE - closePrice * TAX_RATE)
                currentProfit = (sellPrice - preBuyPrice)
                mscdProfit += currentProfit
                preBuyPrice = 0
                sell_list.append(df.iloc[index])
                # print('SELL [%s] total:%s profit:%s price:%s'% (date, self.profitToPercentage(mscdProfit), self.profitToPercentage(currentProfit), closePrice))
            elif status == 1:
                status = 3
            elif status == 2:
                status = 0

        if last_day_sell == True and preBuyPrice > 0 and (status == 3 or status == 1):
            sellPrice = (closePrice - closePrice * SELL_CHARGE - closePrice * TAX_RATE)
            currentProfit = (sellPrice - preBuyPrice)
            mscdProfit += currentProfit

        return self.profitToPercentage(mscdProfit), sell_list, buy_list

    def show_macd_trading(self, df, sell_df=None, buy_df=None):

        fig, axs = plt.subplots(3)
        ax = axs[0]
        ax.plot(df["Close"])
        if len(sell_df.values) > 0:
            ax.plot(sell_df.index, sell_df['Close'], 'ro')
        if len(buy_df.values) > 0:
            ax.plot(buy_df.index, buy_df['Close'], 'bo')
        ax.grid(True)

        ax = axs[1]
        ax.plot(df["MACD_macd"])
        ax.plot(df["MACD_signal"])
        ax.grid(True)

        ax = axs[2]
        ax.plot(df["Volume"])
        ax.grid(True)

        plt.show()

    def add_macd(self, df, fastperiod=12, slowperiod=26, signalperiod=9):
        macd, signal, hist = talib.MACD(df['Close'].values,
                                        fastperiod=fastperiod,
                                        slowperiod=slowperiod,
                                        signalperiod=signalperiod)
        df['MACD_macd'] = macd
        df['MACD_signal'] = signal
        df['MACD_hist'] = hist
        return df

    def profitToPercentage(self, profit):
        if profit == 0:
            return 0.0
        return profit / self.startTradePrice * 100
