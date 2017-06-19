# -*- coding: utf-8 -*-
from __future__ import division
from flask import Flask, render_template, request, Response, send_file
from util.services import *
from util.tomorrow_recommander import tomorrow_recommander

from common import *
import datetime
from dateutil.relativedelta import relativedelta

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from util.back_tester import back_tester


from util.machineLearning_tester import machine_learning_tester



app = Flask(__name__)


end = datetime.datetime.today()
start = end - relativedelta(months=6)
# start = datetime.datetime.strptime('20160115', '%Y%m%d')
# end = datetime.datetime.strptime('20170515', '%Y%m%d')

@app.route("/stationarity")
def stationarity():
    from util.stationarity_tester import stationarity_tester
    stationarity_tester = stationarity_tester()
    end = datetime.datetime.today()
    start = datetime.datetime.strptime('20150110', '%Y%m%d')
    stock_list =['000030']
    stationarity_tester.show_stationarity(stock_list=stock_list, view_chart=True, start=start, end=end, windows=10)

    # stationarity_list = stationarity_tester.get_stationarity_list(stock_list=None, view_chart=False, start=start, end=end, windows=10)

    # stationarity_tester.stationarity_per_day(code='000030', start=start, end=end, view_chart=True, window=10)

@app.route("/stationarity/profit")
def stationarity_profit():
    from util.profit_tester import profit_stationarity_tester
    end = datetime.datetime.today()
    start = datetime.datetime.strptime('20170510', '%Y%m%d')
    profit_stationarity_tester = profit_stationarity_tester()
    # profit_stationarity_tester.profit_print_kospi200(start=start, end=end)
    # profit_stationarity_tester.profit_print_all_with_sell_today()
    # profit_stationarity_tester.profit_print_all_with_sell()
    # profit_stationarity_tester.code_profit(code='128940', start='2017-01-01', end=end)

@app.route("/machine")
def machine():

    # end = datetime.datetime.today()
    # end = datetime.datetime.strptime('20170531', '%Y%m%d')
    end = datetime.datetime.strptime(get_trade_last_day(), '%Y-%m-%d')
    start = end - relativedelta(months=6)


    code_list = []
    data = load_yaml('kospi200')
    for company_code, value in data.iterItems():
        code_list.append(company_code)

    machine_learning_recommander = machine_learning_tester()


    # machine_learning_recommander.show_machine_learning(stock_list=code_list, view_chart=False, start=(end - relativedelta(months=6)), end=end,time_lags=1, dataset_ratio=0.8, apply_st=True, two_condition=True)


    # start = datetime.datetime.strptime('20170501', '%Y%m%d')
    # end = datetime.datetime.strptime('20170502', '%Y%m%d')
    # return_str = []
    # df = get_df_from_file('000030', start, end)
    # print(df)
    # for index, date in enumerate(df.index, start=0):
    #     date = str(df.iloc[index].name).split(' ')[0]
    #     print(date)
    #     try:
    #         r = machine_learning_recommander.test_tomorrow_match_count_of_specific_date(date)
    #         return_str.append(r)
    #     except:
    #         print('skip')
    # print('===test_tomorrow_match_count_of_specific_date===')
    # print(return_str)

    # code_list = ['000030','000050','000070','000100','000120','000150','000210','000240','000270','000640','000660','000670','000720','000810','000880','001040',]
    machine_learning_recommander.tomorrow_machine_learning(stock_list=code_list, view_chart=False, start=start, end=end, time_lags=1, dataset_ratio=1, apply_st=True, two_condition=False, save_file=True)

    # machine_learning_recommander.show_machine_learning(stock_list = code_list, view_chart = False, start = start, end = end, time_lags = 1, dataset_ratio = 0.8, apply_st = True, two_condition = True)


    # machine_learning_recommander.get_tomorrow_trade( code = '009150', start = start, end = end, view_chart = True, time_lags = 1, dataset_ratio = 1, two_condition = False)




@app.route("/ta")
def ta():
    from util.ta_tester import ta_tester
    ta_tester = ta_tester()
    ta_tester.test('008770')

@app.route("/macd")
def macd():
    from util.macd_tester import macd_tester
    start = end - relativedelta(months=12)

    macd_tester = macd_tester()
    # macd_tester.make_best_macd_value_all_kospi(start, end, last_day_sell=False)


    # df = get_df_from_file('028260', (end - relativedelta(months=24)), end)
    # macd_tester.train_macd_value(code='028260', df=df, last_day_sell=True)

    macd_tester.show_profit_total_all_kospi(start, end, view_chart=False, last_day_sell=True)

    # macd_tester.show(code='028260', start=start, end=end, last_day_sell=True)

@app.route("/tomorrow")
def tomorrow():
    from util.tomorrow_recommander import tomorrow_recommander
    tomorrow_recommander = tomorrow_recommander()
    tomorrow_recommander.tomorrow_recommand_stock(end=end, is_update_stock=True, last_month=3, window=10)
    # tomorrow_recommander.recommand_draw('2017-05-10')
    # tomorrow_recommander.recommand_draw()



def init():
    parentPath = os.path.abspath("..")
    if parentPath not in sys.path:
        sys.path.insert(0, parentPath)
    services.register('configurator', Configurator())


    # services.get('configurator').register('input_column', ['Open', 'High','Low', 'Close',  'Volume', 'kospi', 'kospi_volume'])
    # services.get('configurator').register('input_column', ['Close', 'Volume','kospi','kospi_volume'])

    # services.get('configurator').register('input_column',
    #                                       ['Open', 'High', 'Low', 'Close', 'Volume', 'kospi', 'kospi_volume', 'SMA'], )

    # services.get('configurator').register('input_column',
    #                                       ['Open', 'High', 'Low', 'Close', 'Volume', 'kospi', 'kospi_volume',
    #                                        "MACD_macd", "MACD_signal", "MACD_hist", 'foreigner_count'], )

    services.get('configurator').register('input_column',
                                          ['Close', 'Volume', 'kospi', 'kospi_volume',
                                           "MACD_macd", "MACD_signal", "MACD_hist"], )

    # services.get('configurator').register('input_column',
    #                                       ['Close', 'Volume', 'kospi', 'kospi_volume','foreigner_count'], )

    # services.get('configurator').register('input_column',
    #                                       ['Open', 'High', 'Low', 'Close', 'Volume', 'kospi', 'kospi_volume', 'SMA',
    #                                        'BBANDS_upper', 'BBANDS_middle', 'BBANDS_lower', "MOM", "STOCH_slowk",
    #                                        "STOCH_slowd"
    #                                           , "MACD_macd", "MACD_signal", "MACD_hist"], )


    # services.get('configurator').register('input_column', ['Close', 'Volume'])
    # services.get('configurator').register('input_column', ['Close'])


    # services.get('configurator').register('input_column', ['Close', 'Volume'])
    # services.get('configurator').register('input_column',['Close','Volume','Open'])

    """
    'SMA','BBANDS_upper','BBANDS_middle','BBANDS_lower',"MOM","STOCH_slowk","STOCH_slowd"
    ,"MACD_macd","MACD_signal","MACD_hist"
    """

    services.get('configurator').register('output_column', 'Close_Direction')



def get_percent_price(base, p):
    return base + ((base / 100 ) * p)

if __name__ == "__main__":
    init()
    # get_foreigner_info()
    # stationarity()
    tomorrow()
    machine()
    # macd()

    # stationarity_profit()
    # ta()

    # app.debug = True
    # app.run(host='0.0.0.0', port=8088)
