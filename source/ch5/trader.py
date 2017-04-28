# -*- coding: utf-8 -*-
from __future__ import division

import os, sys, datetime

from services import *
from charter import *
from data_model import *
from data_handler import *
from data_writer import *
from data_reader import *
from mess_trader import *
from data_crawler import *

from portfolio_builder import *
from predictor import *
from backtester import *
from alpha_model import *


if __name__ == "__main__":
    services.register('dbhandler', DataHandler())
    services.register('dbwriter', DataWriter())
    services.register('dbreader', DataReader())
    services.register('charter', Charter())
    services.register('configurator', Configurator())

    services.register('predictor', Predictors())
    services.register('trader', MessTrader())
    services.register('mean_reversion_model', MeanReversionModel())
    services.register('machine_learning_model', MachineLearningModel())

    crawler = DataCrawler()
    portfolio = Portfolio()
    portfolioBuilder = PortfolioBuilder()
    mean_backtester = MeanReversionBackTester()
    machine_backtester = MachineLearningBackTester()

    # crawler.updateAllCodes()
    # crawler.updateKospiCodes()
    # crawler.updateAllStockData(1,2016,1,1,2016,12,10,start_index=90)


    services.get('configurator').register('start_date', '20110101')
    services.get('configurator').register('end_date', '20170301')

    # services.get('configurator').register('input_column', 'price_adj_close')
    # services.get('configurator').register('output_column', 'indicator')
    services.get('configurator').register('data_limit', 5)
    services.get('configurator').register('input_column', ['price_close', 'price_volume'])
    # services.get('configurator').register('input_column', ['price_close'])
    # services.get('configurator').register('input_column', ['price_volume'])
    services.get('configurator').register('output_column', 'price_close_Direction')

    # finder.setTimePeriod('20150101','20151130')
    df_stationarity = portfolioBuilder.doStationarityTest('price_close')
    df_rank = portfolioBuilder.rankStationarity(df_stationarity)
    stationarity_codes, rank_sorted = portfolioBuilder.buildUniverse(df_rank, 'rank', 0.8)
    print('top 80 list %s' % stationarity_codes)

    print(rank_sorted)



    row_index = 0
    code = rank_sorted.iloc[row_index]['code']
    company = rank_sorted.iloc[row_index]['company']
    print('%s: %s, %s' % (row_index, code, company))

    # df = pd.read_pickle('KODEX 인버스.data')
    # print(df.describe())
    # print(df['Open'])
    # df['Open'].plot()
    # plt.axhline(df['Open'].mean(), color='red')
    # plt.show()

    # df_dataset = portfolioBuilder.predictor.makeLaggedDataset(code, services.get('configurator').get('start_date'),
    #                                                    services.get('configurator').get('end_date'),
    #                                                    services.get('configurator').get('input_column'),
    #                                                    services.get('configurator').get('output_column'), 5)
    # df_dataset['price_open'].plot()
    # plt.axhline(df_dataset['price_open'].mean(), color='red')
    # plt.show()



    df_machine_result = portfolioBuilder.doMachineLearningTest(split_ratio=0.75, lags_count=1)
    df_machine_rank = portfolioBuilder.rankMachineLearning(df_machine_result)
    machine_codes = portfolioBuilder.buildUniverse(df_machine_rank, 'rank', 0.8)

    # print services.get('predictor').dump()
    # print df_machine_rank
    # print machine_codes



   # print(stationarity_codes)
    print(machine_codes)
    portfolio.clear()
    portfolio.makeUniverse('price_close', 'stationarity', stationarity_codes)
    # universe.makeUniverse('price_close', 'machine_learning', machine_codes)
    portfolio.dump()
    codes = portfolio.getCode()

    start = services.get('configurator').get('start_date')
    end = services.get('configurator').get('end_date')

    code = codes[0][0]
    # machine_backtester.drawChart('rf', code, start, end, lags_count=5)
    print('------------------------back tester: %s, %s' %(code, codes[0][1]))
    machine_backtester.drawHitRatio('rf', code, start, end, lags_count=1)

    code = codes[1][0]
    machine_backtester.drawChart('rf', code, start, end, lags_count=5)
    print('------------------------back tester: %s, %s' % (code, codes[1][1]))
    machine_backtester.getConfusionMatrix('rf', code, start, end, lags_count=5)
    machine_backtester.drawHitRatio('rf', code, start, end, lags_count=1)


    for info in codes:
        code = info[0]
        machine_backtester.drawChart('rf', code, start, end, lags_count=5)
        print('------------------------back tester: %s, %s' %(code, info[1]))
        machine_backtester.getConfusionMatrix('rf', code, start, end, lags_count=5)
        machine_backtester.printClassificationReport('rf', code, start, end, lags_count=5)
        # machine_backtester.showROC('rf', code, start, end, lags_count=5)
        # machine_backtester.showROC('rf', code, start, end, lags_count=5)
        machine_backtester.getHitRatio('rf', code, start, end, lags_count=1)
        machine_backtester.getHitRatio('rf', code, start, end, lags_count=5)
        machine_backtester.getHitRatio('rf', code, start, end, lags_count=10)
        machine_backtester.drawHitRatio('rf', code, start, end, lags_count=1)
        # machine_backtester.drawDrawdown('rf', code, start, end, lags_count=5)

        # machine_backtester.optimizeHyperparameter('rf', code, start, end, lags_count=5)
        # machine_backtester.optimizeHyperparameterByRandomSearch('rf', code, start, end, lags_count=5)

        # mean_backtester.setThreshold(1.5)
        # mean_backtester.setWindowSize(20)
        # mean_backtester.doTest('stationarity',universe,'20150101','20151130')

        # services.get('trader').setPortfolio(universe)
        # services.get('trader').simulate()
        # services.get('trader').dump()


        # services.get('charter').drawStationarityTestHistogram(df)
        # services.get('charter').drawStationarityTestBoxPlot(df)
        # services.get('charter').drawStationarityRankHistogram(df_rank)

        # print df_rank
        # print codes
        # plt.title('%s'%(code))
        # plt.show()
