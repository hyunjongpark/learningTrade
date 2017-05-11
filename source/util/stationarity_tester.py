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
    def __init__(self):
        print('stationarity_tester')

    def show_stationarity(self, stock_list=None, view_chart=True, start='20160101', end='20170101', windows=20):
        result_list = []
        total_profit = 0
        stock_trade = []
        row_index = 0
        code_list = []
        if stock_list == None:
            stock_list = load_yaml('kospi200')
            for company_code, value in stock_list.iterItems():
                code_list.append(company_code)
        else:
            code_list = stock_list
        for code in code_list:
            row_index += 1
            if code == '042660':
                continue

            print('%s/%s code:%s ==================================' %(row_index, len(code_list), code))
            profit_result, title, df_rank, sell_list, buy_list = self.stationarity_per_day(code, start, end, view_chart, windows)
            if profit_result == 0:
                continue

            # if df_rank['score'].values < 8:
            #     continue
            # if df_rank['rank_adf'].values < 1:
            #     continue
            # if df_rank['rank_hurst'].values < 1:
            #     continue
            # if df_rank['rank_halflife'].values < 1:
            #     continue

            if df_rank['rank_adf'].values < 1 and  df_rank['rank_hurst'].values < 1 and df_rank['rank_halflife'].values < 1:
                continue


            total_profit += profit_result
            result_list.append(str('%s, %s' % (row_index, title)))

            stock_trade.append({'code': code, 'sell': sell_list, 'buy': buy_list})

            # if row_index > 10:
            #     break

        for v in result_list:
            print(v)
        print('Total profit:%s, count:%s %s~%s windows:%s' % (total_profit / len(result_list), len(result_list), start, end, windows))
        return stock_trade

    def stationarity_per_day(self, code, start, end, view_chart=True, window=20):
        print('stationarity_per_day: %s, %s~%s' %(code, start, end))
        current_df = get_df_from_file(code, start, end)
        # print(current_df)
        if current_df is None:
            return 0, None, None, None, None
        sell_list = []
        buy_list = []
        trade_list = []
        isBuy = False
        profit = 0
        profit_sum = 0

        for index, date in enumerate(current_df.index, start=0):
            today = date
            ago_month = today - relativedelta(days=(end - start).days)
            # ago_month = today - relativedelta(days=window)
            df = get_df_from_file(code, ago_month, today)
            # print('[%s] %s ~ %s' % (str(index), ago_month, date))
            # print(df)
            tomorrow_trade_result = self.tomorrow_trade(df, isBuy, window)
            if tomorrow_trade_result == 1:

                # TEST CODE
                df_stationarity = self.doStationarityTestFromFileCode(code=code, start=ago_month, end=today)
                df_rank = self.rankStationarity(df_stationarity)
                # if df_rank['rank_adf'].values < 1:
                #     continue
                if df_rank['rank_adf'].values < 1 and df_rank['rank_hurst'].values < 1 and df_rank[
                    'rank_halflife'].values < 1:
                    continue
                # TEST CODE


                sell_list.append(current_df.iloc[index])
                isBuy = False
                sell_profit = current_df.iloc[index]['Close'] - profit
                profit_sum += sell_profit
            elif tomorrow_trade_result == -1:

                #TEST CODE
                df_stationarity = self.doStationarityTestFromFileCode(code=code, start=ago_month, end=today)
                df_rank = self.rankStationarity(df_stationarity)
                # if df_rank['rank_adf'].values < 1:
                #     continue
                if df_rank['rank_adf'].values < 1 and df_rank['rank_hurst'].values < 1 and df_rank[
                    'rank_halflife'].values < 1:
                    continue
                # TEST CODE

                buy_list.append(current_df.iloc[index])
                isBuy = True
                profit = current_df.iloc[index]['Close']
            else:
                continue

        if isBuy == True:
            trade_list.append(current_df.iloc[len(current_df) - 1])
            sell_profit = current_df.iloc[len(current_df) - 1]['Close'] - profit
            profit_sum += sell_profit

        profit_result = (profit_sum / current_df['Close'].mean() * 100)

        df_stationarity = self.doStationarityTestFromFileCode(code=code, start=start, end=end)
        df_rank = self.rankStationarity(df_stationarity)
        title = str(
            'profit:[%s], code:%s, score=%s, rank_adf:%s, rank_hurst:%s, rank_halflife:%s ' % (
                profit_result,
                code,
                df_rank['score'].values,
                df_rank['rank_adf'].values,
                df_rank['rank_hurst'].values,
                df_rank['rank_halflife'].values))
        print('==== Result %s' % (title))
        # title = str('profit:[%s], code:%s, ' % (profit_result, code))

        if view_chart is True:
            stationarity = Stationarity(df=current_df, code=code, start=start, end=end)
            stationarity.show_rolling_mean(title=title, sell_df=pd.DataFrame(sell_list), buy_df=pd.DataFrame(buy_list),
                                           trade_df=pd.DataFrame(trade_list), window=window)
        return profit_result, title, df_rank, sell_list, buy_list

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
        # print(test_result)
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

            # print('code:%s, adf: %s, hurst:%s, halflife:%s ' % (
            # df_stationarity.loc[row_index, 'company'], df_stationarity.loc[row_index, 'rank_adf'],
            # df_stationarity.loc[row_index, 'rank_hurst'], df_stationarity.loc[row_index, 'rank_halflife']))

        df_stationarity['score'] = df_stationarity['rank_adf'] + df_stationarity['rank_hurst'] + df_stationarity['rank_halflife']
        # print(df_stationarity['score'].values)
        # print(df_stationarity['rank_adf'].values)
        # print(df_stationarity['rank_hurst'].values)
        # print(df_stationarity['rank_halflife'].values)
        return df_stationarity

    # def assessADF(self, test_stat, adf_1, adf_5, adf_10):
    #     if test_stat < adf_10:
    #         return 3
    #     elif test_stat < adf_5:
    #         return 2
    #     elif test_stat < adf_1:
    #         return 1
    #     return 0

    def assessADF(self, test_stat, adf_1, adf_5, adf_10):
        sum = 0
        if test_stat < adf_10:
            sum += 1
        if test_stat < adf_5:
            sum += 1
        if test_stat < adf_1:
            sum += 1
        return sum

    def assessHurst(self, hurst):
        sum = 0
        if hurst < 0.4:
            sum += 1
        if hurst < 0.25:
            sum += 1
        if hurst < 0.1:
            sum += 1
        return sum


    # def assessHurst(self, hurst):
    #     if hurst > 0.4:
    #         return 0
    #     if hurst < 0.1:
    #         return 3
    #     elif hurst < 0.2:
    #         return 2
    #     return 1

    # def assessHalflife(self, percentile, halflife):
    #     print(percentile)
    #     for index in range(len(percentile)):
    #
    #         print ("assessHalflife : %s , half=%s : percentile=%s" % (index, halflife, percentile[index]))
    #
    #         if halflife <= percentile[index]:
    #
    #             print ("assessHalflife : %s , half=%s : percentile=%s" % (index, halflife, percentile[index]))
    #
    #             if index < 2:
    #                 return 3
    #             elif index < 3:
    #                 return 2
    #             elif index < 4:
    #                 return 1
    #
    #     return 0

    def assessHalflife(self, percentile, halflife):
        sum = 0
        if halflife < 50:
            sum += 1
        if halflife < 10:
            sum += 1
        if halflife < 5:
            sum += 1
        return sum


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
