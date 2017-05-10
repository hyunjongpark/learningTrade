# -*- coding: utf-8 -*-
from __future__ import division
from dateutil.relativedelta import relativedelta

import os, sys
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *
from util.stationarity import Stationarity


class stationarity_tester():
    def __init__(self, last_month=6, window=20):
        print('stationarity_tester')
        self.end = datetime.datetime.today()
        self.start = self.end - relativedelta(months=last_month)

    def run_stationarity(self, code_list=None, view_chart=True, start='20160101', end='20170101', windows=20):
        print(code_list)
        result_list = []
        total_profit = 0
        stock_trade = []
        for row_index, code in enumerate(code_list, start=0):
            profit_result, title, rank, sell_list, buy_list = self.stationarity_per_day(code, start, end, view_chart, windows)
            if rank != 3:
                continue
            if profit_result == 0:
                continue
            title = str('profit:[%s], %s' % (row_index, title))
            total_profit += profit_result
            result_list.append(str('%s, %s' % (row_index, title)))

            stock_trade.append({'code': code, 'sell': sell_list, 'buy': buy_list})

        for v in result_list:
            print(v)
        print('Total profit:%s, count:%s %s~%s' % (total_profit / len(result_list), len(result_list), start, end))
        return stock_trade


    def show_stationarity(self, view_chart=True, start='20160101', end='20170101', windows=20):
        s_list = load_yaml('stationarity_kospi100')
        print(s_list)
        rank_sorted = s_list.sort_values(by='rank', ascending=False)
        aa = rank_sorted.set_index('rank')
        print(aa)
        result_list = []
        total_profit = 0

        stock_trade = []
        for row_index in range(rank_sorted.shape[0]):
            print(aa.iloc[row_index])
            code = aa.iloc[row_index]['code']
            profit_result, title, rank, sell_list, buy_list = self.stationarity_per_day(code, start, end, view_chart, windows)
            # if rank != 3:
            #     continue
            if profit_result == 0:
                continue
            title = str('profit:[%s], %s' % (row_index, title))
            total_profit += profit_result
            result_list.append(str('%s, %s' % (row_index, title)))

            stock_trade.append({'code': code, 'sell': sell_list, 'buy': buy_list})

        for v in result_list:
            print(v)
        print('Total profit:%s, count:%s %s~%s' % (total_profit / len(result_list), len(result_list), start, end))
        return stock_trade

    def stationarity_per_day(self, code, start, end, view_chart=True, window=20):
        current_df = get_df_from_file(code, start, end)
        sell_list = []
        buy_list = []
        isBuy = False
        profit = 0
        profit_sum = 0

        for index, date in enumerate(current_df.index, start=0):
            today = date
            ago_month = today - relativedelta(days=(end - start).days)
            df = get_df_from_file(code, ago_month, today)
            # print('[%s] %s ~ %s' % (str(index), ago_month, date))
            tomorrow_trade_result = self.tomorrow_trade(df, isBuy, window)
            if tomorrow_trade_result == 1:
                sell_list.append(current_df.iloc[index])
                isBuy = False
                profit_sum += current_df.iloc[index]['Close'] - profit
            elif tomorrow_trade_result == -1:
                buy_list.append(current_df.iloc[index])
                isBuy = True
                profit = current_df.iloc[index]['Close']
            else:
                continue

        # if isBuy == True:
        #     sell_list.append(current_df.iloc[len(current_df) - 1])
        #     profit_sum += current_df.iloc[len(current_df) - 1]['Close'] - profit

        profit_result = (profit_sum / current_df['Close'].mean() * 100)

        df_stationarity = self.doStationarityTestFromFileCode(code=code, start=start, end=end)
        df_rank = self.rankStationarity(df_stationarity)
        title = str(
            'profit:[%s], code:%s, halflife:%s, hurst:%s, rank_adf:%s, rank_hurst:%s, rank_halflife:%s ' % (
                profit_result,
                code,
                df_rank[
                    'halflife'].values,
                df_rank[
                    'hurst'].values,
                df_rank[
                    'rank_adf'].values,
                df_rank[
                    'rank_hurst'].values,
                df_rank[
                    'rank_halflife'].values))
        print('Result %s' % (title))

        if view_chart is True:
            stationarity = Stationarity(df=current_df, code=code, start=start, end=end)
            stationarity.show_rolling_mean(title=title, sell_df=pd.DataFrame(sell_list), buy_df=pd.DataFrame(buy_list),
                                           trade_df=None, window=window)
        return profit_result, title, df_rank['rank_adf'].values, sell_list, buy_list

    def tomorrow_trade(self, df, isBuy, window):
        df_ma = pd.rolling_mean(df['Close'], window)
        df_std = pd.rolling_std(df['Close'], window)
        diff = df['Close'] - df_ma
        check_diff_std = np.abs(diff) - df_std
        last_index = len(df) - 1
        today_price = df.iloc[last_index]['Close']
        if str(float(today_price)).lower() == 'nan':
            return 0
        if check_diff_std[last_index] < 0:
            return 0
        if diff[last_index] > 0:
            # if isBuy == True and df.iloc[last_index]['Close'] > df['Close'].mean():
            if isBuy is True and df.iloc[last_index]['Close'] > df_ma.iloc[last_index]:
                return 1
            else:
                return 0
        else:
            # if isBuy == False and df.iloc[last_index]['Close'] < df['Close'].mean():
            if isBuy is False and df.iloc[last_index]['Close'] < df_ma.iloc[last_index]:
                return -1
            else:
                return 0

    def doStationarityTestFromFileCode(self, code, start, end):
        test_result = {'code': [], 'company': [], 'adf_statistic': [], 'adf_1': [], 'adf_5': [], 'adf_10': [],
                       'hurst': [], 'halflife': []}
        try:
            df = get_df_from_file(code, start, end)
            # print(df)
            stationarity = Stationarity(df=df, code=code, start=start, end=end)
            test_stat, adf_1, adf_5, adf_10, hurst, halflifes = stationarity.get_result()
            test_result['adf_statistic'].append(test_stat)
            test_result['adf_1'].append(adf_1)
            test_result['adf_5'].append(adf_5)
            test_result['adf_10'].append(adf_10)
            test_result['code'].append(code)
            test_result['company'].append(code)
            test_result['hurst'].append(hurst)
            test_result['halflife'].append(halflifes)
        except:
            print('except %s' %(code))
        print(test_result)
        df_result = pd.DataFrame(test_result)
        return df_result

    def buildUniverse(self, df_stationarity, column, ratio):
        percentile_column = np.percentile(df_stationarity[column], np.arange(0, 100, 10))
        ratio_index = np.trunc(ratio * len(percentile_column))
        print(df_stationarity)
        universe = {}

        for row_index in range(df_stationarity.shape[0]):
            percentile_index = getPercentileIndex(percentile_column, df_stationarity.loc[row_index, column])
            if percentile_index >= ratio_index:
                universe[df_stationarity.loc[row_index, 'code']] = df_stationarity.loc[row_index, 'company']

        return universe

    def rankStationarity(self, df_stationarity):
        df_stationarity['rank_adf'] = 0
        df_stationarity['rank_hurst'] = 0
        df_stationarity['rank_halflife'] = 0

        halflife_percentile = np.percentile(df_stationarity['halflife'], np.arange(0, 100, 10))  # quartiles

        # print halflife_percentile

        for row_index in range(df_stationarity.shape[0]):
            df_stationarity.loc[row_index, 'rank_adf'] = self.assessADF(df_stationarity.loc[row_index, 'adf_statistic'],
                                                                        df_stationarity.loc[row_index, 'adf_1'],
                                                                        df_stationarity.loc[row_index, 'adf_5'],
                                                                        df_stationarity.loc[row_index, 'adf_10'])
            df_stationarity.loc[row_index, 'rank_hurst'] = self.assessHurst(df_stationarity.loc[row_index, 'hurst'])
            df_stationarity.loc[row_index, 'rank_halflife'] = self.assessHalflife(halflife_percentile,
                                                                                  df_stationarity.loc[
                                                                                      row_index, 'halflife'])

            print('code:%s, adf: %s, hurst:%s, halflife:%s ' % (
            df_stationarity.loc[row_index, 'company'], df_stationarity.loc[row_index, 'rank_adf'],
            df_stationarity.loc[row_index, 'rank_hurst'], df_stationarity.loc[row_index, 'rank_halflife']))

        df_stationarity['rank'] = df_stationarity['rank_adf'] + df_stationarity['rank_hurst'] + df_stationarity[
            'rank_halflife']
        print(df_stationarity['rank'])

        # print(df_stationarity['rank'])
        # print(df_stationarity['rank_adf'])
        # print(df_stationarity['rank_hurst'])
        # print(df_stationarity['rank_halflife'])
        return df_stationarity

    def assessADF(self, test_stat, adf_1, adf_5, adf_10):
        if test_stat < adf_10:
            return 3
        elif test_stat < adf_5:
            return 2
        elif test_stat < adf_1:
            return 1

        return 0

    def assessHurst(self, hurst):
        if hurst > 0.4:
            return 0

        if hurst < 0.1:
            return 3
        elif hurst < 0.2:
            return 2

        return 1

    def assessHalflife(self, percentile, halflife):
        for index in range(len(percentile)):

            # print "assessHalflife : %s , half=%s : percentile=%s" % (index, halflife, percentile[index])

            if halflife <= percentile[index]:

                # print "assessHalflife : %s , half=%s : percentile=%s" % (index, halflife, percentile[index])

                if index < 2:
                    return 3
                elif index < 3:
                    return 2
                elif index < 4:
                    return 1

        return 0

    def assessMachineLearning(self, percentile, halflife):
        for index in range(len(percentile)):

            print("assessHalflife : %s , half=%s : percentile=%s" % (index, halflife, percentile[index]))

            if halflife <= percentile[index]:

                print("assessHalflife : %s , half=%s : percentile=%s" % (index, halflife, percentile[index]))

                if index < 2:
                    return 3
                elif index < 3:
                    return 2
                elif index < 4:
                    return 1

        return 0
