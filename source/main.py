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
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

@app.route("/write/stock/list/<file_name>")
def write_stock_list(file_name):
    crawler = services.get('crawler')
    crawler.write_kospi(file_name=file_name)
    return ''

@app.route("/write/stock/datas/<stock_list_file_name>")
def download_stock_datas(stock_list_file_name):
    data = load_yaml(stock_list_file_name)
    # download_stock_data('249420_일동제약.data','249420',2016,1,1,2017,4,30)
    # data.dump()
    index = 0
    end = datetime.today()
    start = today - relativedelta(months=24)
    for company_code, value in data.iterItems():
        print("%s : %s - key=%s, Full Code=%s, Company=%s" % (index, value.market_type, company_code, value.full_code, value.company))
        index += 1
        find_name = '%s_%s.data' %(company_code, value.company)
        # download_stock_data(file_name=find_name, company_code=company_code, start='20170101', end='20170428')
        download_stock_data(file_name=find_name, company_code=company_code, start=start, end=end)

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
    end_date = datetime.today()
    start_date = today - relativedelta(months=24)
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
def show_stock(code, start, end, window):
    print('Show stock: %s %s~%s' % (code, start, end))
    # df = get_df_from_file(code, start, end)
    # close = df['Close']
    # print(close)
    # fig, axs = plt.subplots(2)
    # ax = axs[0]
    # ax.plot(df['Close'])
    # ax.axhline(df['Close'].mean(), color='red')
    # ax.grid(True)
    # ax = axs[1]
    # ax.plot(df['Volume'], 'b')
    # ax.grid(True)
    # plt.show()

    test_stationarity_per_day(code, start, end, True, window)

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
    services.get('configurator').register('input_column', ['Close', 'Colume'])
    services.get('configurator').register('output_column', 'Close_Direction')


def test_show_stationarity(view_chart=True, start='20160101', end='20170101', windows=20):
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
        # profit_result, title, rank = test_stationarity(code, start, end, view_chart, windows)
        profit_result, title, rank, sell_list, buy_list = test_stationarity_per_day(code, start, end, view_chart, windows)
        if rank != 3 or profit_result == 0:
            continue
        title = str('profit:[%s], %s' %(row_index, title))
        total_profit += profit_result
        result_list.append(str('%s, %s' % (row_index, title)))

        stock_trade.append({'code':code, 'sell':sell_list, 'buy':buy_list})

    for v in result_list:
        print(v)
    print('Total profit:%s, count:%s %s~%s' %(total_profit/len(result_list), len(result_list), start, end))
    return stock_trade

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

def tomorrow_trade(df, isBuy, window):
    # print('[%s] ~ [%s]' %(df.iloc[0], df.iloc[len(df)-1]))
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


def test_stationarity_per_day(code, start, end, view_chart=True, window=20):
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
        tomorrow_trade_result = tomorrow_trade(df, isBuy, window)
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

    if isBuy == True:
        sell_list.append(current_df.iloc[len(current_df)-1])
        profit_sum += current_df.iloc[len(current_df)-1]['Close'] - profit

    profit_result = (profit_sum / current_df['Close'].mean() * 100)

    portfolioBuilder = services.get('portfolioBuilder')
    df_stationarity = portfolioBuilder.doStationarityTestFromFileCode(code=code, start=start, end=end)
    df_rank = portfolioBuilder.rankStationarity(df_stationarity)
    title = str(
        'profit:[%s], code:%s, halflife:%s, hurst:%s, rank_adf:%s, rank_hurst:%s, rank_halflife:%s ' % (profit_result,
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

    # print(pd.DataFrame(sell_list))
    # print(pd.DataFrame(buy_list))
    if view_chart is True:
        stationarity = Stationarity(df=current_df, code=code, start=start, end=end)
        stationarity.show_rolling_mean(title=title, sell_df=pd.DataFrame(sell_list), buy_df=pd.DataFrame(buy_list), trade_df=None, window=window)
    return profit_result, title, df_rank['rank_adf'].values, sell_list, buy_list

def test_stationarity(code, start, end, view_chart=True, window=20):

    df = get_df_from_file(code, start, end)

    df_ma = pd.rolling_mean(df['Close'], window)
    df_std = pd.rolling_std(df['Close'], window)
    diff = df['Close'] - df_ma
    check_diff_std = np.abs(diff) - df_std
    sell_list = []
    buy_list = []
    trade_list = []
    isBuy = False
    profit = 0
    profit_sum = 0
    for index, v in enumerate(check_diff_std, start=0):
        if str(float(v)).lower() == 'nan':
            continue
        if v < 0:
            continue
        if diff[index] > 0:
            sell_list.append(df.iloc[index])
            # if isBuy == True and df.iloc[index]['Close'] > df['Close'].mean():
            if isBuy == True and df.iloc[index]['Close'] > df_ma.iloc[index]:
                isBuy = False
                trade_list.append(df.iloc[index])
                profit_sum += df.iloc[index]['Close'] - profit
        else:
            buy_list.append(df.iloc[index])
            # if isBuy == False and df.iloc[index]['Close'] < df['Close'].mean():
            if isBuy == False and df.iloc[index]['Close'] < df_ma.iloc[index]:
                isBuy = True
                trade_list.append(df.iloc[index])
                profit = df.iloc[index]['Close']

    if isBuy == True:
        trade_list.append(df.iloc[index])
        profit_sum += df.iloc[index]['Close'] - profit

    profit_result = (profit_sum / df['Close'].mean() * 100)

    portfolioBuilder = services.get('portfolioBuilder')
    df_stationarity = portfolioBuilder.doStationarityTestFromFileCode(code=code, start=start, end=end)
    df_rank = portfolioBuilder.rankStationarity(df_stationarity)
    print(df_rank)
    title = str(
        'profit:[%s], code:%s, halflife:%s, hurst:%s, rank_adf:%s, rank_hurst:%s, rank_halflife:%s ' % (profit_result,
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
        stationarity = Stationarity(df=df, code=code, start=start, end=end)
        stationarity.show_rolling_mean(title, pd.DataFrame(sell_list), pd.DataFrame(buy_list), pd.DataFrame(trade_list), window)
    return profit_result, title, df_rank['rank_adf'].values

def daemon_trade(stock_list_file_name='kospi100', last_month=6, window=20):
    print('Tomorrow trade stock')
    download_stock_datas(stock_list_file_name)

    end = datetime.today()
    start = today - relativedelta(months=last_month)
    stocks_trade_list = test_show_stationarity(False, start, end, window)
    print(stocks_trade_list)

    df = get_df_from_file('042670', start, end)
    last_stock_trade_day = df.iloc[len(df)-1].name
    print('last_stock_trade_day: %s' %(last_stock_trade_day))

    sell_list = []
    buy_list = []

    print('================tomorrow trade===================')
    for stock in stocks_trade_list:
        # print(stock['code'])
        # print(stock['sell'][len(stock['sell']) - 1])
        # print(stock['sell'][len(stock['sell']) - 1].name)
        sell_last_day = stock['sell'][len(stock['sell']) - 1].name
        buy_last_day = stock['buy'][len(stock['buy']) - 1].name


        if last_stock_trade_day == sell_last_day:
            sell_list.append({'code':stock['code'], 'Close':stock['sell'][len(stock['sell']) - 1]['Close']})
            print('SELL code:%s %s' % (stock['code'], stock['sell'][len(stock['sell']) - 1]))
        elif last_stock_trade_day == buy_last_day:
            buy_list.append({'code': stock['code'], 'Close': stock['buy'][len(stock['buy']) - 1]['Close']})
            print('BUY code:%s %s' % (stock['code'], stock['buy'][len(stock['buy']) - 1]))


    print('[%s][last_month:%s, window:%s] SELL list: %s' %(last_stock_trade_day, last_month, window, sell_list))
    print('[%s][last_month:%s, window:%s] BUY list: %s' % (last_stock_trade_day, last_month, window, buy_list))
    write_yaml('daily_trade',{'date': last_stock_trade_day, 'sell': sell_list, 'buy': buy_list, 'last_month': last_month,'window': window})
    return 'END'

def tomorrow_recommand_draw():
    draw = load_yaml('daily_trade')
    # print(draw)

    end = datetime.today()
    start = today - relativedelta(months=draw['last_month'])
    df = get_df_from_file('042670', start, end)
    last_stock_trade_day = df.iloc[len(df) - 1].name
    print('last_stock_trade_day: %s' % (last_stock_trade_day))

    for sell_list in draw['sell']:
        print(sell_list)
        test_stationarity_per_day(sell_list['code'], start, end, True, draw['window'])

    for sell_list in draw['buy']:
        print(sell_list)
        test_stationarity_per_day(sell_list['code'], start, end, True, draw['window'])

if __name__ == "__main__":
    init()
    today = datetime.today()
    month_ago = today - relativedelta(months=3)
    # write_stock_list('kospi100')
    # download_stock_datas('kospi100')

    # stock_update()
    # test();
    # print(load_yaml('daily_trade'))

    # daemon_trade(stock_list_file_name='kospi100', last_month=6, window=20)
    tomorrow_recommand_draw()

    # show_stock('010140', month_ago, today, 5)
    # test_stationarity('042670', month_ago, today, True, 5)
    # test_stationarity_per_day('042670', month_ago, today, True, 10)
    # stationarity()
    # for index in [24,15,12,20,8, 6,4,3,2]:
    # for index in [6]:
    # for window in [5,10,15,20]:
    # for window in [10]:
    #     month_ago = today - relativedelta(months=3)
    #     test_show_stationarity(False, month_ago, today, window)

    # machineLearning()
    # test_show_machineLearning()

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
