# -*- coding: utf-8 -*-
from __future__ import division
from flask import Flask, render_template, request, Response, send_file
from util.services import *
from util.tomorrow_recommander import tomorrow_recommander

from common import *
import datetime
from dateutil.relativedelta import relativedelta

from source.common import load_yaml, get_df_from_file

import pythoncom
import win32com.client as winAPI


parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from util.back_tester import back_tester

from util.machineLearning_tester import machine_learning_tester
from util.stock_updater import stock_updater
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

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
    stock_list = ['000030']
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


@app.route("/close_eaual_high")
def close_eaual_high():
    past_time = 36

    endDate = datetime.datetime.today()
    startDate = endDate - relativedelta(months=past_time)

    company_data = load_yaml(services.get('configurator').get('stock_list'))
    # data_backup = load__data_backup_yaml(services.get('configurator').get('stock_list'))

    company_index = 0

    code_list = []

    success_count = 0
    fail_count = 0

    for company_code, value in company_data:
        company_index += 1
        df = get_df_from_file(company_code, startDate, endDate)

        if df is None:
            continue

        if len(df) < 4:
            continue

        if company_index == 2:
            print('START %s ~ %s' % (df.iloc[3].name, df.iloc[len(df) - 1].name))

        for index in range(3, len(df) - 1):
            pre2_data = df.iloc[index - 2]
            pre1_data = df.iloc[index - 1]
            today_data = df.iloc[index]
            next_data = df.iloc[index + 1]

            close = today_data['Close']
            next_high = next_data['High']
            next_low = next_data['Low']

            if pre2_data['Close'] > pre1_data['Close']:
                continue

            if pre1_data['Close'] > today_data['Close']:
                continue

            if pre2_data['Volume'] > pre1_data['Volume']:
                continue

            if pre1_data['Close'] >= today_data['Open']:
                continue

            if pre1_data['Volume'] > today_data['Volume']:
                continue

            today_percentage = (close - today_data['Open']) / (today_data['Open'] / 100)
            if today_percentage < 5:
                continue

            close_volume = (today_data['Close'] * today_data['Volume']) / 100000000
            if close_volume <= 100:  # 억
                continue

            if today_data['Close'] != today_data['High']:
                continue

            next_high_percentage = (next_high - close) / (close / 100)

            next_low_percentage = (next_low - close) / (close / 100)


            if close >= next_high or next_high_percentage < 0.8:
                # print("failed")
                # print(pre2_data)
                # print(pre1_data)
                # print(today_data)
                # print(next_data)
                # print(next_data)
                fail_count = fail_count + 1
                print('+++++++++++++++++')
                print('today_percentage: %s' % (today_percentage))
                print('close_volume: %s' % (close_volume))
                print('next_high_percentage: %s' % (next_high_percentage))
                print('+++++++++++++++++')
                continue
            else:
                success_count = success_count + 1
                print('code: %s, [%s][%s] [%s][%s] profit[%s] lowProfit[%s]' % (company_code, today_data.name, close, next_data.name, next_high, next_high_percentage, next_low_percentage))

    print('date: %s ~ %s, success: %s, fail: %s' % (startDate, endDate, success_count, fail_count))

        # if index > 50:
        #     break

        # pre_1_data = df.iloc[len(df) - 2]
        # today_data = df.iloc[len(df) - 1]
        #

        # if (today_data['Close'] * today_data['Volume']) / 1000000 <= 2000: #20억
        #     continue
        # # if today_data['institution_trading'] <= 0:
        # #     continue
        # if today_data['foreigner_count'] == 0:
        #     continue
        # # if today_data['foreigner_count'] < pre_1_data['foreigner_count']:
        # #     continue
        # # if today_data['Volume'] < pre_1_data['Volume']:
        # #     continue
        # if today_data['Close'] > 100000:
        #     continue

        # code_list.append(company_code)

    # print(len(code_list))
    # print(code_list)


@app.route("/machine")
def machine():
    end = datetime.datetime.today()
    start = end - relativedelta(months=12)

    code_list = []

    data = load_yaml(services.get('configurator').get('stock_list'))
    index = 0;

    for company_code, value in data:
        index += 1
        df = get_df_from_file(company_code, end - relativedelta(months=5), end)
        if df is None or len(df) < 100:
            continue



        pre_1_data = df.iloc[len(df) - 2]
        today_data = df.iloc[len(df) - 1]

        print('%s/%s, %s %s [%s]' % (index, len(data), company_code, len(df), (today_data['Close'] * today_data['Volume']) / 100000000))
        if (today_data['Close'] * today_data['Volume']) / 100000000 <= 1:  # 1억
            continue
        # if today_data['institution_trading'] <= 0:
        #     continue
        # if today_data['foreigner_count'] == 0:
        #     continue
        # if today_data['foreigner_count'] < pre_1_data['foreigner_count']:
        #     continue
        # if today_data['Volume'] < pre_1_data['Volume']:
        #     continue

        # print(Series.rolling(df['Close'], center=False, window=5).mean()[-1:])
        # print(Series.rolling(df['Close'], center=False, window=10).mean()[-1:])
        # print(Series.rolling(df['Close'], center=False, window=20).mean()[-1:])

        if Series.rolling(df['Close'], center=False, window=5).mean()[-1:].values < Series.rolling(df['Close'], center=False, window=10).mean()[-1:].values:
            continue
        if Series.rolling(df['Close'], center=False, window=5).mean()[-1:].values < Series.rolling(df['Close'], center=False, window=20).mean()[-1:].values:
            continue

        code_list.append(company_code)

    print(len(code_list))
    print(code_list)

    machine_learning_recommander = machine_learning_tester()
    code_list = machine_learning_recommander.show_machine_learning(stock_list=code_list, view_chart=False, start=start, end=end, time_lags=1, dataset_ratio=0.8, apply_st=True, two_condition=True)
    print('Machine [%s]' %(code_list))

    save_stocks = machine_learning_recommander.tomorrow_machine_learning(stock_list=code_list, view_chart=False, start=start, end=end, two_condition=False, save_file=True)
    code_list = save_stocks['BUY_list']
    print(code_list)


@app.route("/ta")
def ta():
    from util.ta_tester import ta_tester
    ta_tester = ta_tester()
    ta_tester.test('005930')


@app.route("/macd")
def macd():
    from util.macd_tester import macd_tester
    code='000660'
    start = end - relativedelta(months=24)
    end_minus = end - relativedelta(months=12)

    macd_tester = macd_tester()
    print('MACD make_best_macd_value_all_kospi')
    # macd_tester.make_best_macd_value_all_kospi(start=start, end=end_minus, last_day_sell=False)

    df = get_df_from_file(code=code, start=start, end=end_minus)
    print('MACD train_macd_value')
    # macd_tester.train_macd_value(code=code, df=df, last_day_sell=True)

    print('MACD show_profit_total_all_kospi')
    # macd_tester.show_profit_total_all_kospi(start, end, view_chart=False, last_day_sell=True)
    macd_tester.show(code=code, start=end_minus, end=end, last_day_sell=True)


@app.route("/tomorrow")
def tomorrow():
    from util.tomorrow_recommander import tomorrow_recommander
    tomorrow_recommander = tomorrow_recommander()
    tomorrow_recommander.tomorrow_recommand_stock(end=end, is_update_stock=True, last_month=3, window=10)
    tomorrow_recommander.recommand_draw('2017-05-10')
    tomorrow_recommander.recommand_draw()

def init():
    parentPath = os.path.abspath("..")
    if parentPath not in sys.path:
        sys.path.insert(0, parentPath)
    services.register('configurator', Configurator())

    # services.get('configurator').register('input_column',
    #                                       ['Close', 'Volume',
    #                                        "MACD_macd", "MACD_signal", "MACD_hist",
    #                                        'foreigner_count', 'MACD_foreigner_count_macd',
    #                                        'MACD_foreigner_count_signal', 'MACD_foreigner_count_hist',
    #                                        'institution_trading'], )


    services.get('configurator').register('input_column', ['Close', 'Volume'])
    services.get('configurator').register('output_column', 'Close_Direction')
    services.get('configurator').register('stock_list', 'kospi')


def get_percent_price(base, p):
    return base + ((base / 100) * p)


if __name__ == "__main__":
    init()

    # stock_updater = stock_updater()
    # stock_updater.update_kospi(end_index=10)


    # close_eaual_high()
    machine()
    # macd()
    # ta()

    # tomorrow()



    # app.debug = True
    # app.run(host='0.0.0.0', port=8088)
