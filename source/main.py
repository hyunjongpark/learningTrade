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

from common import load_yaml, download_stock_data, get_df_from_file
from portfolio_builder import *
from predictor import *
from backtester import *
from alpha_model import *


app = Flask(__name__)

@app.route("/write/stock/list/<file_name>")
def write_stock_list(file_name):
    crawler = services.get('crawler')
    crawler.write_kospi(file_name=file_name)
    return ''

@app.route("/write/stock/datas/<stock_list_file_name>")
def download_stock_datas(stock_list_file_name):
    data = load_yaml(stock_list_file_name)
    #download_stock_data('lg.data','066570',2015,1,1,2015,11,30)
    # data.dump()
    index = 0
    for company_code, value in data.iterItems():
        print("%s : %s - key=%s, Full Code=%s, Company=%s" % (index, value.market_type, company_code, value.full_code, value.company))
        index += 1
        find_name = '%s_%s.data' %(company_code, value.company)
        download_stock_data(file_name=find_name, company_code=company_code, start='20110101', end='20170428')

    return 'END'


@app.route("/stock/update",methods=['POST'])
def stock_update():
    """
    curl -d "start_date=20110101&end_data=20170421" http://172.21.110.174:8088/stock/update
    :return:
    """
    # start_date = request.form.get('start_date', default='20110101', type=str)
    # end_date = request.form.get('end_data', default='20170501', type=str)
    start_date = '20110101'
    end_date = '20170428'
    crawler = services.get('crawler')
    # crawler.updateAllCodes()
    crawler.updateKospiCodes(write_file=True)

    year1=str(start_date)[0:4]
    month1=str(start_date)[4:6]
    date1=str(start_date)[6:8]
    year2=str(end_date)[0:4]
    month2=str(end_date)[4:6]
    date2=str(end_date)[6:8]

    crawler.updateAllStockData(1, year1, month1, date1, year2, month2, date2, start_index=90)


@app.route("/stationarity/")
def stationarity():
    portfolioBuilder = services.get('portfolioBuilder')
    df_stationarity = portfolioBuilder.doStationarityTestFromFile(start = '20150101', end = '20161230')
    df_rank = portfolioBuilder.rankStationarity(df_stationarity)
    stationarity_codes = portfolioBuilder.buildUniverse(df_rank, 'rank', 0.8)
    print('stationarity top 80 list %s' % stationarity_codes)
    print('stationarity %s' %(stationarity_codes))
    write_yaml('stationarity_kospi100', df_rank)
    return 'END'

@app.route("/machineLearning")
def machineLearning():
    portfolioBuilder = services.get('portfolioBuilder')
    df_machine_result = portfolioBuilder.doMachineLearningTest(split_ratio=0.75, lags_count=1)
    df_machine_rank = portfolioBuilder.rankMachineLearning(df_machine_result)
    print('df_machine_rank: %s' %(df_machine_rank))
    machine_codes = portfolioBuilder.buildUniverse(df_machine_rank, 'rank', 0.8)
    print('rank_sorted: %s' %(machine_codes))
    write_yaml('machineLearning_kospi100', df_machine_rank)
    return 'END'

@app.route("/show/stock/<code>/<start>/<end>")
def show_stock(code, start, end):
    print('Show stock: %s %s~%s' % (code, start, end))
    # portfolioBuilder = services.get('portfolioBuilder')
    # df_dataset = portfolioBuilder.predictor.makeLaggedDataset(code, services.get('configurator').get('start_date'),
    #                                                           services.get('configurator').get('end_date'),
    #                                                           services.get('configurator').get('input_column'),
    #                                                           services.get('configurator').get('output_column'), 5)
    # print(df_dataset['price_open'])
    # df_dataset['price_open'].plot()
    # plt.axhline(df_dataset['price_open'].mean(), color='red')
    # plt.show()

    # dir_list = get_data_list()
    # name = [name for name in dir_list if code in name]
    # df = load_stock_data(name[0])
    # print(df.describe())
    # df = df[start:end]

    df = get_df_from_file(code, start, end)


    #test
    # date = df['Date']
    # print(date)
    close = df['Close']
    print(close)


    fig, axs = plt.subplots(2)
    # axs[1].xaxis.set_visible(False)
    ax = axs[0]
    ax.plot(df['Close'])
    # ax.plot(['20150106', '20150128', '2015-02-20'], [97800, 99000, 110000], 'bo')
    # ax.plot(['2015-01-02', '2015-02-04',], [101000,  97400], 'ro')
    ax.axhline(df['Close'].mean(), color='red')
    ax.grid(True)

    ax = axs[1]
    ax.plot(df['Volume'], 'b')
    ax.grid(True)
    plt.show()

    return 'END'


@app.route("/rank/code/<stationarity_codes>/<machine_codes>")
def get_rank_close(stationarity_codes, machine_codes):
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
    services.get('configurator').register('end_date', '20150601')
    services.get('configurator').register('data_limit', 100)
    services.get('configurator').register('input_column', ['price_close', 'price_volume'])
    services.get('configurator').register('output_column', 'price_close_Direction')


def test_show_stationarity():
    start = '20150101'
    end = '20151230'
    s_list = load_yaml('stationarity_kospi100')
    print(s_list)
    rank_sorted = s_list.sort_values(by='rank', ascending=False)
    aa = rank_sorted.set_index('rank')
    print(aa)
    for row_index in range(rank_sorted.shape[0]):
        print(aa.iloc[row_index])
        code = aa.iloc[row_index]['code']
        # code = rank_sorted.loc[row_index, 'code']
        print('code: %s' % (code))
        df = get_df_from_file(code, start, end)
        stationarity = Stationarity(df=df, code=code, start=start, end=end)
        stationarity.show_rolling_mean()

def test_show_machineLearning():
    start = '20150101'
    end = '20151230'
    s_list = load_yaml('machineLearning_kospi100')
    rank_sorted = s_list.sort_values(by='total_score', ascending=False)
    print(rank_sorted)
    aa = rank_sorted.set_index('total_score')
    print(aa)
    for row_index in range(aa.shape[0]):
        print(aa.iloc[row_index])
        file_name = aa.iloc[row_index]['company']
        print('Index %s, %s, %s' %(row_index, file_name,rank_sorted.loc[row_index, 'total_score']))
        code = str(file_name).split('_')[0]
        print('code: %s' % (code))
        df = get_df_from_file(code, start, end)
        stationarity = Stationarity(df=df, code=code, start=start, end=end)
        stationarity.show_rolling_mean()

if __name__ == "__main__":
    init()
    # write_stock_list('kospi100')
    # download_stock_datas('kospi100')

    # stock_update()
    # test();

    # show_stock('000030', '20150201','20150401')
    # stationarity()
    test_show_stationarity()

    # machineLearning()
    test_show_machineLearning()

    # chart_close('097950')

    # stationarity_codes = {'102780': 'KODEX 삼성그룹', '114800': 'KODEX 인버스', '091170': 'KODEX 은행', '130730': 'KOSEF 단기자금',
    #                       '104530': 'KOSEF 고배당',
    #                       '069660': 'KOSEF 200'}
    # machine_codes = {'117680': 'KODEX 철강', '104530': 'KOSEF 고배당', '114800': 'KODEX 인버스', '102780': 'KODEX 삼성그룹',
    #                  '144600': 'KODEX 은선물(H)', '138920': 'KODEX 콩선물(H)'}
    # get_rank_close(stationarity_codes, machine_codes)

    #[['144600', 'KODEX 은선물(H)'], ['102780', 'KODEX 삼성그룹'], ['138920', 'KODEX 콩선물(H)'], ['104530', 'KOSEF 고배당'], ['117680', 'KODEX 철강'], ['114800', 'KODEX 인버스'], ['104530', 'KOSEF 고배당'], ['114800', 'KODEX 인버스'], ['091170', 'KODEX 은행'], ['130730', 'KOSEF 단기자금'], ['102780', 'KODEX 삼성그룹'], ['069660', 'KOSEF 200']]
    # backtester(144600, 20150501, 20150601)

    # app.debug = True
    # app.run(host='0.0.0.0', port=services.get('configurator').get('trbs_master_port'))
