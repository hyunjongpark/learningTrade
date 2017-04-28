# -*- coding: utf-8 -*-
from __future__ import division
import os, sys
from flask import Flask, render_template, request, Response, send_file


from services import *
from charter import *
from data_model import *
from data_handler import *
from data_writer import *
from data_reader import *
from mess_trader import *
from data_crawler import *

from util.common import load_yaml, write_yaml, convertTodatetime
from portfolio_builder import *
from predictor import *
from backtester import *
from alpha_model import *


app = Flask(__name__)


@app.route("/stock/update",methods=['POST'])
def stock_update():
    """
    curl -d "start_date=20110101&end_data=20170421" http://172.21.110.174:8088/stock/update
    :return:
    """
    start_date = request.form.get('start_date', default='20160101', type=str)
    end_date = request.form.get('end_data', default='20170101', type=str)

    crawler = services.get('crawler')
    crawler.updateAllCodes()
    crawler.updateKospiCodes()
    crawler.updateAllStockData(1, str(start_date)[0:4], str(start_date)[5:7], str(start_date)[8:10],
                               str(end_date)[0:4], str(end_date)[5:7], str(end_date)[8:10], start_index=90)


@app.route("/stationarity/<count>")
def stationarity(count):
    portfolioBuilder = services.get('portfolioBuilder')
    df_stationarity = portfolioBuilder.doStationarityTest('price_close')
    df_rank = portfolioBuilder.rankStationarity(df_stationarity)
    stationarity_codes, rank_sorted = portfolioBuilder.buildUniverse(df_rank, 'rank', 0.8)
    print('stationarity top 80 list %s' % stationarity_codes)
    return rank_sorted

@app.route("/machineLearning/<count>")
def machineLearning(count):
    portfolioBuilder = services.get('portfolioBuilder')
    df_machine_result = portfolioBuilder.doMachineLearningTest(split_ratio=0.75, lags_count=1)
    df_machine_rank = portfolioBuilder.rankMachineLearning(df_machine_result)
    machine_codes = portfolioBuilder.buildUniverse(df_machine_rank, 'rank', 0.8)
    print(machine_codes)
    return 'END'

@app.route("/chart/close/<code>")
def chart_close(code):
    print('%s' % (code))
    portfolioBuilder = services.get('portfolioBuilder')
    df_dataset = portfolioBuilder.predictor.makeLaggedDataset(code, services.get('configurator').get('start_date'),
                                                              services.get('configurator').get('end_date'),
                                                              services.get('configurator').get('input_column'),
                                                              services.get('configurator').get('output_column'), 5)
    df_dataset['price_open'].plot()
    plt.axhline(df_dataset['price_open'].mean(), color='red')
    plt.show()
    return 'END'


@app.route("/rank/code/<stationarity_codes>/<machine_codes>")
def get_randk_close(stationarity_codes, machine_codes):
    portfolio = Portfolio()
    portfolio.clear()
    portfolio.makeUniverse('price_close', 'stationarity', stationarity_codes)
    portfolio.makeUniverse('price_close', 'machine_learning', machine_codes)
    portfolio.dump()
    codes = portfolio.getCode()
    print(codes)
    return codes


@app.route("/backtester/<code>/<start>/<end>")
def backtester(code, start, end):
    machine_backtester = MachineLearningBackTester()
    print('------------------------back tester: %s' % (code))
    # machine_backtester.drawChart('rf', code, start, end, lags_count=5)
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

def test():
    machine_backtester = MachineLearningBackTester()

    start = 20150501
    end = 20150601
    code = 144600

    print('------------------------back tester: %s' % (code))
    # machine_backtester.drawChart('rf', code, start, end, lags_count=5)
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

    # plt.title('%s'%(code))
    # plt.show()



def init():
    parentPath = os.path.abspath("..")
    if parentPath not in sys.path:
        sys.path.insert(0, parentPath)
    trbsServerConf = os.path.join(parentPath, 'conf/trbs_server.yaml')
    data = load_yaml(trbsServerConf)

    print('init setupe: %s' % (data))

    services.register('configurator', Configurator())

    services.register('dbhandler', DataHandler())
    services.register('dbwriter', DataWriter())
    services.register('dbreader', DataReader())
    services.register('charter', Charter())
    services.register('configurator', Configurator())
    services.register('crawler', DataCrawler())

    services.register('predictor', Predictors())
    services.register('trader', MessTrader())
    services.register('mean_reversion_model', MeanReversionModel())
    services.register('machine_learning_model', MachineLearningModel())

    services.register('portfolio', Portfolio())
    services.register('portfolioBuilder', PortfolioBuilder())

    services.get('configurator').register('start_date', '20110101')
    services.get('configurator').register('end_date', '20170301')
    services.get('configurator').register('data_limit', 10)
    services.get('configurator').register('input_column', ['price_close', 'price_volume'])
    services.get('configurator').register('output_column', 'price_close_Direction')


if __name__ == "__main__":
    init()
    # test();

    # stationarity(10);

    # chart_close(114800)

    # machineLearning(10)

    # stationarity_codes = {'102780': 'KODEX 삼성그룹', '114800': 'KODEX 인버스', '091170': 'KODEX 은행', '130730': 'KOSEF 단기자금',
    #                       '104530': 'KOSEF 고배당',
    #                       '069660': 'KOSEF 200'}
    # machine_codes = {'117680': 'KODEX 철강', '104530': 'KOSEF 고배당', '114800': 'KODEX 인버스', '102780': 'KODEX 삼성그룹',
    #                  '144600': 'KODEX 은선물(H)', '138920': 'KODEX 콩선물(H)'}
    # get_randk_close(stationarity_codes, machine_codes)

    #[['144600', 'KODEX 은선물(H)'], ['102780', 'KODEX 삼성그룹'], ['138920', 'KODEX 콩선물(H)'], ['104530', 'KOSEF 고배당'], ['117680', 'KODEX 철강'], ['114800', 'KODEX 인버스'], ['104530', 'KOSEF 고배당'], ['114800', 'KODEX 인버스'], ['091170', 'KODEX 은행'], ['130730', 'KOSEF 단기자금'], ['102780', 'KODEX 삼성그룹'], ['069660', 'KOSEF 200']]
    backtester(144600, 20150501, 20150601)

    # app.debug = True
    # app.run(host='0.0.0.0', port=services.get('configurator').get('trbs_master_port'))
