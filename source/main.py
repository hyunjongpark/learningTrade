# -*- coding: utf-8 -*-
from __future__ import division
from flask import Flask, render_template, request, Response, send_file
from util.services import *
from util.tomorrow_recommander import tomorrow_recommander

from common import *
import datetime
from dateutil.relativedelta import relativedelta
from util.back_tester import back_tester
from util.stationarity_tester import stationarity_tester

app = Flask(__name__)


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

    # services.register('dbhandler', DataHandler())
    # services.register('dbwriter', DataWriter())
    # services.register('dbreader', DataReader())
    # services.register('charter', Charter())
    # services.register('configurator', Configurator())
    # services.register('crawler', DataCrawler())
    #
    # services.register('predictor', Predictors())
    # services.register('trader', MessTrader())
    # services.register('mean_reversion_model', MeanReversionModel())
    # services.register('machine_learning_model', MachineLearningModel())
    #
    # services.register('portfolio', Portfolio())
    # services.register('portfolioBuilder', PortfolioBuilder())
    #
    # services.get('configurator').register('start_date', '20110101')
    # services.get('configurator').register('end_date', '20150601')
    # services.get('configurator').register('data_limit', 100)
    # services.get('configurator').register('input_column', ['Close', 'Colume'])
    # services.get('configurator').register('output_column', 'Close_Direction')



def test_show_machineLearning():
    start = '20160101'
    end = '20170501'
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


        # stationarity = Stationarity(df=df, code=code, start=start, end=end)
        # stationarity.show_rolling_mean()

        machine_backtester = MachineLearningBackTester(df)
        print('------------------------back tester: %s' % (code))
        machine_backtester.getConfusionMatrix('rf', code, start, end, lags_count=5)
        machine_backtester.printClassificationReport('rf', code, start, end, lags_count=5)
        # machine_backtester.showROC('rf', code, start, end, lags_count=5)
        # machine_backtester.showROC('rf', code, start, end, lags_count=5)
        machine_backtester.getHitRatio('rf', code, start, end, lags_count=1)
        machine_backtester.getHitRatio('rf', code, start, end, lags_count=5)
        machine_backtester.getHitRatio('rf', code, start, end, lags_count=10)
        # machine_backtester.drawHitRatio('rf', code, start, end, lags_count=1)


if __name__ == "__main__":
    init()
    end = datetime.datetime.today()
    start = end - relativedelta(months=3)

    # start = datetime.datetime.strptime('20160101', '%Y%m%d')
    # end = datetime.datetime.strptime('20160101', '%Y%m%d')
    # start = end - relativedelta(months=6)

    tomorrow_recommander = tomorrow_recommander()
    # tomorrow_recommander.tomorrow_recommand_stock(end=None, is_update_stock=False, last_month=3, window=10)
    tomorrow_recommander.recommand_draw('2017-05-10')

    stationarity_tester = stationarity_tester()
    # stationarity_tester.stationarity_per_day(code='011780', start=start, end=end, view_chart=True, window=10)
    # stationarity_tester.stationarity_per_day(code='012330', start=start, end=end, view_chart=True, window=10)

    back_tester = back_tester()
    # back_tester.run()
    back_tester.run_series()

    # machineLearning()
    # test_show_machineLearning()

    # app.debug = True
    # app.run(host='0.0.0.0', port=services.get('configurator').get('trbs_master_port'))
