# -*- coding: utf-8 -*-
from __future__ import division
import os, sys, datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statsmodels.tsa.stattools as ts

from stock_common import *

from data_model import *
from data_handler import *
from services import *
from alpha_model import *

from common import *
from stationarity import Stationarity

class PortfolioBuilder():
    def __init__(self):
        print('PortfolioBuilder')
        # self.dbhandler = services.get('dbhandler')
        # self.dbreader = services.get('dbreader')
        # self.predictor = services.get('predictor')
        # self.config = services.get('configurator')
        # self.mean_reversion_model = services.get('mean_reversion_model')
        self.machine_learning_model = services.get('machine_learning_model')

    """
    def setTimePeriod(self,start,end):
        self.start_date = start
        self.end_date = end
    """

    def loadDataFrame(self, code):
        sql = "select * from prices"
        sql += " where code='%s'" % (code)
        sql += " and price_date between '%s' and '%s' " % (self.config.get('start_date'), self.config.get('end_date'))

        # print sql

        df = pd.read_sql(sql, self.dbhandler.conn)

        return df

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

            print ("assessHalflife : %s , half=%s : percentile=%s" % (index, halflife, percentile[index]))

            if halflife <= percentile[index]:

                print ("assessHalflife : %s , half=%s : percentile=%s" % (index, halflife, percentile[index]))

                if index < 2:
                    return 3
                elif index < 3:
                    return 2
                elif index < 4:
                    return 1

        return 0

    def doStationarityTestFromFile(self, start, end):
        test_result = {'code': [], 'company': [], 'adf_statistic': [], 'adf_1': [], 'adf_5': [], 'adf_10': [],
                       'hurst': [], 'halflife': []}

        dataList = get_data_list()
        print(dataList)
        index = 0;
        for file_name in dataList:

            index = index + 1
            try:
                code_split = str(file_name).split("_")
                code = code_split[0]
                print('    %s/%s: %s' % (index, len(dataList), file_name))
                df = get_df_from_file(code, start, end)
                # print(df)
                stationarity = Stationarity(df=df, code=code, start=start, end=end)
                test_stat, adf_1, adf_5, adf_10, hurst, halflifes = stationarity.get_result()
                test_result['adf_statistic'].append(test_stat)
                test_result['adf_1'].append(adf_1)
                test_result['adf_5'].append(adf_5)
                test_result['adf_10'].append(adf_10)
                test_result['code'].append(code)
                test_result['company'].append(file_name)
                test_result['hurst'].append(hurst)
                test_result['halflife'].append(halflifes)
            except:
                print('except %s' %file_name)
            # if index > 3:
            #     break
        print(test_result)
        df_result = pd.DataFrame(test_result)
        return df_result

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


    def doStationarityTest(self, column, lags_count=100):
        rows_code = self.dbreader.loadCodes(limit=self.config.get('data_limit'))

        test_result = {'code': [], 'company': [], 'adf_statistic': [], 'adf_1': [], 'adf_5': [], 'adf_10': [],
                       'hurst': [], 'halflife': []}

        deleteCode = []

        index = 1
        for a_row_code in rows_code:
            code = a_row_code[0]
            company = a_row_code[1]
            if code == str('001440'):
                self.dbreader.deleteCode(code)

            print("... %s of %s : Testing Stationarity on %s %s" % (index, len(rows_code), code, company))

            a_df = self.loadDataFrame(code)
            a_df_column = a_df[column]
            # print (a_df_column)

            if a_df_column.shape[0] > 0:
                try:
                    test_stat, adf_1, adf_5, adf_10 = self.mean_reversion_model.calcADF(a_df_column)
                    test_result['adf_statistic'].append(test_stat)
                    test_result['adf_1'].append(adf_1)
                    test_result['adf_5'].append(adf_5)
                    test_result['adf_10'].append(adf_10)
                    test_result['code'].append(code)
                    test_result['company'].append(company)
                    test_result['hurst'].append(self.mean_reversion_model.calcHurstExponent(a_df_column, lags_count))
                    test_result['halflife'].append(self.mean_reversion_model.calcHalfLife(a_df_column))
                    # print(test_result)
                except:
                    print('except mean_reversion_model')

            else:
                deleteCode.append(rows_code)
                self.dbreader.deleteCode(a_row_code[0])


            index += 1

        print(test_result)

        df_result = pd.DataFrame(test_result)

        return df_result

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

            print('code:%s, adf: %s, hurst:%s, halflife:%s ' %(df_stationarity.loc[row_index, 'company'], df_stationarity.loc[row_index, 'rank_adf'], df_stationarity.loc[row_index, 'rank_hurst'], df_stationarity.loc[row_index, 'rank_halflife']))

        df_stationarity['rank'] = df_stationarity['rank_adf'] + df_stationarity['rank_hurst'] + df_stationarity['rank_halflife']
        print(df_stationarity['rank'])

        # print(df_stationarity['rank'])
        # print(df_stationarity['rank_adf'])
        # print(df_stationarity['rank_hurst'])
        # print(df_stationarity['rank_halflife'])
        return df_stationarity

    def buildUniverse(self, df_stationarity, column, ratio):
        percentile_column = np.percentile(df_stationarity[column], np.arange(0, 100, 10))
        ratio_index = np.trunc(ratio * len(percentile_column))

        print(df_stationarity)

        # rank_sorted = df_stationarity.sort_values(by='total_score', ascending=False)




        universe = {}

        for row_index in range(df_stationarity.shape[0]):
            percentile_index = getPercentileIndex(percentile_column, df_stationarity.loc[row_index, column])
            if percentile_index >= ratio_index:
                universe[df_stationarity.loc[row_index, 'code']] = df_stationarity.loc[row_index, 'company']

        return universe

    def doMachineLearningTest(self, split_ratio=0.75, lags_count=10):
        return self.machine_learning_model.calcScore(split_ratio=split_ratio, time_lags=lags_count)

    def rankMachineLearning(self, df_machine_learning):
        def listed_columns(arr, prefix):
            result = []
            for a_item in arr:
                result.append(prefix % (a_item))
            return result

        mr_models = ['logistic', 'rf', 'svm']

        for a_predictor in mr_models:
            df_machine_learning['rank_%s' % (a_predictor)] = 0

        percentiles = {}
        for a_predictor in mr_models:
            percentiles[a_predictor] = np.percentile(df_machine_learning[a_predictor], np.arange(0, 100, 10))

            for row_index in range(df_machine_learning.shape[0]):
                df_machine_learning.loc[row_index, 'rank_%s' % (a_predictor)] = self.assessMachineLearning(
                    percentiles[a_predictor], df_machine_learning.loc[row_index, a_predictor])

        df_machine_learning['total_score'] = df_machine_learning[mr_models].sum(axis=1)
        df_machine_learning['rank'] = df_machine_learning[listed_columns(mr_models, 'rank_%s')].sum(axis=1)

        return df_machine_learning
