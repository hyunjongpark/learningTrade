# -*- coding: utf-8 -*-
from __future__ import division

import os, sys
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC, SVC
from sklearn.model_selection import cross_validate

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *
from util.services import *
from util.ta_tester import ta_tester
from util.stationarity_tester import stationarity_tester

np.seterr(divide='ignore', invalid='ignore')


class machine_learning_tester():
    def __init__(self):
        print('machine_learning_tester')
        self.ta_tester = ta_tester()
        self.stationarity_tester = stationarity_tester()

    def show_machine_learning(self, stock_list=None, view_chart=False, start='20160101', end='20170101', time_lags=5, dataset_ratio=0.8, apply_st=False, two_condition=False):
        row_index = 0
        code_list = []
        if stock_list == None:
            stock_list = load_yaml(services.get('configurator').get('stock_list'))
            for company_code, value in stock_list.iterItems():
                code_list.append(company_code)
        else:
            code_list = stock_list
        lr_totla = 0
        rf_totla = 0
        svm_totla = 0
        vote_totla = 0
        ret_stocks = []
        for code in code_list:
            print('%s/%s code:%s ==================================' % (row_index, len(code_list), code))
            if apply_st == True:
                success, title, df_rank = self.stationarity_tester.get_stationarity_value(code=code, start=start,end=end, view_chart=False, window=10)
                if success == False:
                    print('Skip success: %s' % (success))
                    continue
                if self.filter_condition(df_rank) == False:
                    print('Skip filter_condition')
                    continue

            isSuccess, profit_result = self.trading_machine_learning(code, start, end, view_chart, time_lags, dataset_ratio, two_condition)
            if isSuccess == False:
                continue
            lr_totla += profit_result['logistic'].values
            rf_totla += profit_result['rf'].values
            svm_totla += profit_result['svm'].values
            vote_totla += profit_result['vote'].values
            ret_stocks.append(code)
            row_index += 1
        print("Total Hit Ratio - Logistic Regreesion=%0.2f, RandomForest=%0.2f, SVM=%0.2f, vote=%0.2f [%s ~ %s]" % (lr_totla / row_index, rf_totla / row_index, svm_totla / row_index, vote_totla / row_index, start, end))
        return ret_stocks

    def tomorrow_machine_learning(self, stock_list=None, view_chart=True, start='20160101', end='20170101', two_condition=False, save_file=False):
        row_index = 0
        code_list = []
        if stock_list == None:
            stock_list = load_yaml(services.get('configurator').get('stock_list'))
            for company_code, value in stock_list.iterItems():
                code_list.append(company_code)
        else:
            code_list = stock_list

        save_stocks = {'date': str(end), 'SELL_list': [], 'BUY_list': []}

        for code in code_list:
            print('[tomorrow_machine_learning] %s/%s code:%s ==================================' % (row_index, len(code_list), code))

            isSuccess, result = self.get_tomorrow_trade(code=code, start=start, end=end, view_chart=view_chart, time_lags=1, dataset_ratio=1, two_condition=two_condition)
            if isSuccess == False:
                continue

            print('Code: %s, tomorrow:%s' % (code, result))

            if result == 1:
                save_stocks['BUY_list'].append(code)
            if result == -1:
                save_stocks['SELL_list'].append(code)

            row_index += 1

        print('=========================================')
        print(save_stocks)

        return_array = []

        for code in save_stocks['BUY_list']:

            # tomorrow = get_trade_next_day(save_stocks['date'])
            df = get_df_from_file(code, start, end)
            # print(df)

            pre_1_data = df.iloc[len(df) - 2]
            today_data = df.iloc[len(df) - 1]

            pass_institution_trading = True
            pass_foreigner_count = True
            pass_Volume = True
            pass_is_mean_state = True

            # if today_data['foreigner_count'] <= pre_1_data['foreigner_count']:
            #     pass_foreigner_count = False
            #     # continue
            if today_data['Volume'] < pre_1_data['Volume']:
                pass_Volume = False
                # continue
            if is_mean_state(code) != 1:
                pass_is_mean_state = False
                # continue
            # if today_data['institution_trading'] <= 0:
            #     pass_institution_trading = False
            # continue  nhy6tygh                                                              v

            print('StockList.add("%s"); //pass_institution_trading:%s, foreigner_count:%s, Volume:%s, is_mean_state:%s' % (code, pass_institution_trading, pass_foreigner_count, pass_Volume, pass_is_mean_state))
            return_array.append(code)

        save_stocks['BUY_list'] = return_array
        return save_stocks

    def test_tomorrow_match_count_of_specific_date(self, stock_list, date):
        # end = datetime.datetime.today()
        # start = end - relativedelta(months=6)
        # end = datetime.datetime.strptime('20170529', '%Y%m%d')

        end = datetime.datetime.strptime(date, '%Y-%m-%d')
        start = end - relativedelta(months=6)

        result = self.tomorrow_machine_learning(stock_list=stock_list, view_chart=False, start=start, end=end,
                                                two_condition=False, save_file=True)

        match_count = 0
        index = 0

        # buy_list = ['028260', '004700', '008060', '009240', '009290', '007690', '005440', '004170', '078930', '007340', '003490', '000880', '012630', '104700', '000660', '034120', '020150', '007070', '009420', '003520', '000240', '020000', '064960', '008930', '000070', '005300', '139480', '036580', '000150', '000100', '012450', '185750', '066570', '036570', '025860', '016360', '003200', '005610', '006280', '000640', '051910', '001680', '027410', '021240', '005180', '012750', '029530', '006400', '071050', '018880', '005090', '000810', '007570', '019680', '010780', '003550', '000120']

        for code in result['BUY_list']:
            # for code in result['SELL_list']:

            # print('code: %s, date: %s, next: %s '%(code, result['date'], get_trade_next_day(result['date'])))
            # print('code: %s' % (code))

            tomorrow = get_trade_next_day(result['date'])
            # tomorrow = get_trade_next_day('20170501')
            df = get_df_from_file(code, start, tomorrow)

            pre_1_data = df.iloc[len(df) - 3]
            today_data = df.iloc[len(df) - 2]
            tomorrow_data = df.iloc[len(df) - 1]

            # if today_data['institution_trading'] <= 0:
            #     continue
            # if today_data['foreigner_count'] == 0:
            #     continue

            print('%s %s - %s' % (code, today_data['Close'], tomorrow_data['Close']))
            index += 1
            if today_data['Close'] < tomorrow_data['Close']:
                match_count += 1

            #
            # if today_data['Close'] < tomorrow_data['Open']:
            #     if today_data['Close'] > tomorrow_data['Low']:
            #         # print(df)
            #         if get_percent_price(today_data['Close'], -0.1) > tomorrow_data['Low']:
            #             buy_price = get_percent_price(today_data['Close'], -0.1)
            #             index += 1
            #             if today_data['Close'] <= tomorrow_data['Close']:
            #                 match_count += 1
            #             elif buy_price < tomorrow_data['Close']:
            #                 match_count += 1
            #             # elif today_data['Close'] < tomorrow_data['High'] and today_data['Close'] > tomorrow_data['Low']:
            #             #     match_count += 1
            #             else:
            #                 print(df)
            #                 print('+++buy_price: %s ' % (buy_price))
            #                 print('+++Open: %s ' % (get_percent(today_data['Close'], tomorrow_data['Open'])))
            #                 print('+++High: %s ' % (get_percent(today_data['Close'], tomorrow_data['High'])))
            #                 print('+++Low: %s ' % (get_percent(today_data['Close'], tomorrow_data['Low'])))
            #                 print('+++CLOSE: %s ' % (get_percent(today_data['Close'], tomorrow_data['Close'])))

        print('+++++%s/%s' % (match_count, index))

        return str('%s, %s/%s' % (end, match_count, index))

    def filter_condition(self, df_rank):
        if df_rank['rank_adf'].values < 1 and df_rank['rank_hurst'].values < 1 and df_rank['rank_halflife'].values < 1:
            return False
        # if df_rank['score'].values < 6:
        #     return False
        else:
            return True

    def get_df_for_train(self, code, start, end):
        df = get_df_from_file(code, start, end)
        for input in services.get('configurator').get('input_column'):
            if input == 'SMA':
                df = self.ta_tester.add_sma(df)
            if input == 'BBANDS_middle':
                df = self.ta_tester.add_bbands(df)

            if input == 'MOM':
                df = self.ta_tester.add_mom(df)

            if input == 'STOCH_slowk':
                df = self.ta_tester.add_stoch(df)

            if input == 'MACD_macd':
                self.ta_tester.set_code(code)
                df = self.ta_tester.add_macd(df)

            if input == 'MACD_foreigner_count_macd':
                df = self.ta_tester.add_macd_foreigner_count(df)

            if input == 'kospi':
                kospi_df = get_df_from_file('kospi.data', start, end)
                df['kospi'] = kospi_df['Close']
                df['kospi_volume'] = kospi_df['Volume']
        return df

    def get_tomorrow_trade(self, code='009150', start='20160101', end='20170101', view_chart=True, time_lags=1, dataset_ratio=0.8, two_condition=False):
        print('%s %s ~ %s' % (code, start, end))
        test_result = {'code': [], 'logistic': [], 'rf': [], 'svm': [], 'vote': [], 'logistic_tomorrow_predic': [],'rf_tomorrow_predic': [], 'svm_tomorrow_predic': [], 'vote_tomorrow_predic': []}
        try:
            df = self.get_df_for_train(code, start, end)
            trining_split_date = getDateByPercent(df.index[0], df.index[df.shape[0] - 1], 1)
            test_split_date = getDateByPercent(df.index[0], df.index[df.shape[0] - 1], 0.5)

            X_train, Y_train, X_test, Y_test = self.get_train_df(df, time_lags, trining_split_date, two_condition)
            lr_classifier = self.do_logistic_regression(X_train, Y_train)
            X_test, Y_test = self.get_test_df(df, time_lags, test_split_date, two_condition)
            lr_hit_ratio, lr_score, lr_hit_index, lr_fail_index, lr_tomorrow_predic = self.test_predictor(lr_classifier,X_test,Y_test)
            # print('---------- %s' % lr_tomorrow_predic)

            X_train, Y_train, X_test, Y_test = self.get_train_df(df, time_lags, trining_split_date, two_condition)
            rf_classifier = self.do_random_forest(X_train, Y_train)
            X_test, Y_test = self.get_test_df(df, time_lags, test_split_date, two_condition)
            rf_hit_ratio, rf_score, rf_hit_index, rf_fail_index, rf_tomorrow_predic = self.test_predictor(rf_classifier,X_test,Y_test)
            # print('---------- %s' % rf_tomorrow_predic)

            X_train, Y_train, X_test, Y_test = self.get_train_df(df, time_lags, trining_split_date, two_condition)
            svm_classifier = self.do_svm(X_train, Y_train)
            X_test, Y_test = self.get_test_df(df, time_lags, test_split_date, two_condition)
            svm_hit_ratio, svm_score, svm_hit_index, svm_fail_index, svm_tomorrow_predic = self.test_predictor(svm_classifier, X_test, Y_test)
            # print('---------- %s' % svm_tomorrow_predic)

            X_test, Y_test = self.get_test_df(df, time_lags, test_split_date, two_condition)
            vaild_count, vote_hit_ratio, vote_score, vote_hit_index, vote_fail_index, vote_tomorrow_predic = self.test_vote_predictor(
                lr_classifier, rf_classifier, svm_classifier, X_test, Y_test)

            # print('---------- %s' % vote_tomorrow_predic)

            test_result['code'].append(code)
            test_result['logistic'].append(lr_score)
            test_result['rf'].append(rf_score)
            test_result['svm'].append(svm_score)
            test_result['vote'].append(vote_score)
            test_result['logistic_tomorrow_predic'].append(lr_tomorrow_predic)
            test_result['rf_tomorrow_predic'].append(rf_tomorrow_predic)
            test_result['svm_tomorrow_predic'].append(svm_tomorrow_predic)
            test_result['vote_tomorrow_predic'].append(vote_tomorrow_predic)

            print("%s : Hit Ratio - Logistic Regreesion=%0.2f, RandomForest=%0.2f, SVM=%0.2f, vote=%0.2f, [%s ~ %s]" % (
                code, lr_hit_ratio, rf_hit_ratio, svm_hit_ratio, vote_hit_ratio, X_test.iloc[0].name,
                X_test.iloc[len(X_test) - 1].name))
        except Exception as ex:
            print('except [%s] %s' % (code, ex))
            return False, None

        if view_chart == True:
            self.drawHitRatio(code, df, lr_hit_index, lr_fail_index, rf_hit_index, rf_fail_index, svm_hit_index,
                              svm_fail_index, vote_hit_index, vote_fail_index, time_lags)
            # self.drawHitRatioTest(code, df, lr_classifier, rf_classifier, svm_classifier)

        # print(df_result)
        return True, vote_tomorrow_predic

    def trading_machine_learning(self, code='009150', start='20160101', end='20170101', view_chart=True, time_lags=1,
                                 dataset_ratio=0.8, two_condition=False):
        if view_chart == True:
            print(' trading_machine_learning: %s %s ~ %s' % (code, start, end))
        test_result = {'code': [], 'logistic': [], 'rf': [], 'svm': [], 'vote': [], 'logistic_tomorrow_predic': [], 'rf_tomorrow_predic': [], 'svm_tomorrow_predic': [], 'vote_tomorrow_predic': []}
        try:
            df = self.get_df_for_train(code, start, end)

            split_date = getDateByPercent(df.index[0], df.index[df.shape[0] - 1], dataset_ratio)

            X_train, Y_train, X_test, Y_test = self.get_train_df(df, time_lags, split_date, two_condition)
            lr_classifier = self.do_logistic_regression(X_train, Y_train)
            score = lr_classifier.score(X_test, Y_test)
            lr_hit_ratio, lr_score, lr_hit_index, lr_fail_index, lr_tomorrow_predic = self.test_predictor(lr_classifier, X_test, Y_test)
            if view_chart == True:
                print(' do_logistic_regression: score[%s]  lr_tomorrow_predic[%s]' % (score, lr_tomorrow_predic))

            X_train, Y_train, X_test, Y_test = self.get_train_df(df, time_lags, split_date, two_condition)
            rf_classifier = self.do_random_forest(X_train, Y_train)
            score = rf_classifier.score(X_test, Y_test)
            rf_hit_ratio, rf_score, rf_hit_index, rf_fail_index, rf_tomorrow_predic = self.test_predictor(rf_classifier, X_test, Y_test)
            if view_chart == True:
                print(' do_random_forest: score[%s]  lr_tomorrow_predic[%s]' % (score, lr_tomorrow_predic))

            X_train, Y_train, X_test, Y_test = self.get_train_df(df, time_lags, split_date, two_condition)
            svm_classifier = self.do_svm(X_train, Y_train)
            score = svm_classifier.score(X_test, Y_test)
            svm_hit_ratio, svm_score, svm_hit_index, svm_fail_index, svm_tomorrow_predic = self.test_predictor(svm_classifier, X_test, Y_test)
            if view_chart == True:
                print(' do_svm: score[%s]  lr_tomorrow_predic[%s]' % (score, lr_tomorrow_predic))

            vaild_count, vote_hit_ratio, vote_score, vote_hit_index, vote_fail_index, vote_tomorrow_predic = self.test_vote_predictor(lr_classifier, rf_classifier, svm_classifier, X_test, Y_test)
            # if vote_score < 0.5:
            #     print('vote.score < 0.5')
            #     return False, None

            test_result['code'].append(code)
            test_result['logistic'].append(lr_score)
            test_result['rf'].append(rf_score)
            test_result['svm'].append(svm_score)
            test_result['vote'].append(vote_score)
            test_result['logistic_tomorrow_predic'].append(lr_tomorrow_predic)
            test_result['rf_tomorrow_predic'].append(rf_tomorrow_predic)
            test_result['svm_tomorrow_predic'].append(svm_tomorrow_predic)
            test_result['vote_tomorrow_predic'].append(vote_tomorrow_predic)


            print(" trading_machine_learning %s : Hit Ratio - Logistic Regreesion=%0.2f, RandomForest=%0.2f, SVM=%0.2f, vote=%0.2f, [%s ~ %s]" % ( code, lr_hit_ratio, rf_hit_ratio, svm_hit_ratio, vote_hit_ratio, start, X_test.iloc[len(X_test) - 1].name))
        except Exception as ex:
            print('except [%s] %s' % (code, ex))
            return False, None

        if view_chart == True:
            self.drawHitRatio(code, df, lr_hit_index, lr_fail_index, rf_hit_index, rf_fail_index, svm_hit_index, svm_fail_index, vote_hit_index, vote_fail_index, time_lags)
            # self.drawHitRatioTest(code, df, lr_classifier, rf_classifier, svm_classifier)

        # print(df_result)
        return True, pd.DataFrame(test_result)

    def get_train_df(self, df, time_lags, split_date, two_condition=False):
        df_dataset = self.make_dataset(df, time_lags, two_condition)
        df_dataset = df_dataset.dropna(how='any')
        X_train, X_test, Y_train, Y_test = self.split_dataset(df_dataset,
                                                              services.get('configurator').get('input_column'),
                                                              "Close_Lag%s_Direction" % (time_lags), split_date)
        return X_train, Y_train, X_test, Y_test

    def get_test_df(self, df, time_lags, dataset_ratio=0.8, two_condition=False):
        df_dataset = self.make_dataset(df, time_lags, two_condition)
        X_train, X_test, Y_train, Y_test = self.split_dataset(df_dataset,
                                                              services.get('configurator').get('input_column'),
                                                              "Close_Lag%s_Direction" % (time_lags), dataset_ratio)
        for i in range(0, time_lags):
            a = i + 1
            index = len(Y_test) - a
            Y_test[index] = 0.0

        return X_test, Y_test

    def drawHitRatioTest(self, code, df, lr_classifier, rf_classifier, svm_classifier):
        df_dataset = self.make_dataset(df, 0)
        input_column_name = []
        for input in services.get('configurator').get('input_column'):
            input_column_name.append("%s_Lag%s" % (input, 0))

        input_data = df_dataset[input_column_name]
        output_data = df_dataset[services.get('configurator').get('output_column')]

        lr_hit_ratio, lr_score, lr_hit_index, lr_fail_index, lr_tomorrow_predic = self.test_predictor(lr_classifier,
                                                                                                      input_data,
                                                                                                      output_data)
        rf_hit_ratio, rf_score, rf_hit_index, rf_fail_index, rf_classifiertomorrow_predic = self.test_predictor(
            rf_classifier, input_data, output_data)
        svm_hit_ratio, svm_score, svm_hit_index, svm_fail_index, svm_tomorrow_predic = self.test_predictor(
            svm_classifier, input_data, output_data)

        self.drawHitRatio(code, df_dataset, lr_hit_index, lr_fail_index, rf_hit_index, rf_fail_index, svm_hit_index,
                          svm_fail_index, 0)

    def close_from_date(self, df, date_array):
        close = []
        for index, v in enumerate(df.index, start=0):
            for row, d in enumerate(date_array.index, start=0):
                if v == d:
                    close.append(df.iloc[index]['Close'])

        return close

    def drawHitRatio(self, code, df, lr_hit_index, lr_fail_index, rf_hit_index, rf_fail_index, svm_hit_index,
                     svm_fail_index, vote_hit_index, vote_fail_index, time_lags):
        fig, axs = plt.subplots(4)
        ax = axs[0]
        ax.plot(df["Close"])
        ax.plot(lr_fail_index.index, self.close_from_date(df, lr_fail_index), 'ro')
        ax.plot(lr_hit_index.index, self.close_from_date(df, lr_hit_index), 'bo')
        ax.set_title('%s logistic_regression' % (code))
        ax.grid(True)

        ax = axs[1]
        ax.plot(df["Close"])
        ax.plot(rf_fail_index.index, self.close_from_date(df, rf_fail_index), 'ro')
        ax.plot(rf_hit_index.index, self.close_from_date(df, rf_hit_index), 'bo')
        ax.set_title('random_forest')
        ax.grid(True)

        ax = axs[2]
        ax.plot(df["Close"])
        ax.plot(svm_fail_index.index, self.close_from_date(df, svm_fail_index), 'ro')
        ax.plot(svm_hit_index.index, self.close_from_date(df, svm_hit_index), 'bo')
        ax.set_title('svm')
        ax.grid(True)

        ax = axs[3]
        ax.plot(df["Close"])
        ax.plot(vote_fail_index.index, self.close_from_date(df, vote_fail_index), 'ro')
        ax.plot(vote_hit_index.index, self.close_from_date(df, vote_hit_index), 'bo')
        ax.set_title('vote')
        ax.grid(True)

        plt.show()

    def make_dataset(self, df, time_lags=5, two_condition=False):
        df_lag = pd.DataFrame(index=df.index)
        shift = time_lags * -1
        df_lag['Close'] = df['Close']
        df_lag["Close_Lag%s" % (time_lags)] = df['Close'].shift(shift)
        df_lag["Close_Lag%s_Change" % (time_lags)] = df_lag["Close_Lag%s" % (time_lags)].pct_change() * 100.0
        df_lag["Close_Lag%s_Direction" % (time_lags)] = np.sign(df_lag["Close_Lag%s_Change" % (time_lags)])

        if two_condition == True:
            df_lag["Close_Lag%s_Direction" % (time_lags)] = np.where(df_lag["Close_Lag%s_Direction" % (time_lags)] == 0,
                                                                     1, df_lag["Close_Lag%s_Direction" % (time_lags)])

        df_lag["Close_Change"] = df_lag["Close"].pct_change() * 100.0
        df_lag["Close_Direction"] = np.sign(df_lag["Close_Change"])
        df_lag["Volume"] = df["Volume"]
        for input in services.get('configurator').get('input_column'):
            df_lag["%s" % (input)] = df[input]

        return df_lag

    def split_dataset(self, df, input_column_array, output_column, split_date):
        input_data = df[input_column_array]
        output_data = df[output_column]
        X_train = input_data[input_data.index <= split_date]
        Y_train = output_data[output_data.index <= split_date]

        X_test = input_data[input_data.index > split_date]
        Y_test = output_data[output_data.index > split_date]

        return X_train, X_test, Y_train, Y_test

    def test_predictor(self, classifier, x_test, y_test):
        pred = classifier.predict(x_test)

        hit_count = 0
        total_count = len(y_test)
        hit_index_array = []
        fail_index_array = []
        for index in range(total_count):
            if (pred[index]) == (y_test[index]):
                hit_count = hit_count + 1
                hit_index_array.append(x_test.iloc[index])
            else:
                fail_index_array.append(x_test.iloc[index])

        hit_ratio = hit_count / total_count
        score = classifier.score(x_test, y_test)
        # print("hit_count=%s, total=%s, hit_ratio = %s , accuracy_score: %s[%s ~ %s]" % (hit_count, total_count, hit_ratio, score, x_test.iloc[0].name, x_test.iloc[len(x_test) - 1].name))
        return hit_ratio, score, pd.DataFrame(hit_index_array), pd.DataFrame(fail_index_array), pred[len(pred) - 1]

    def test_vote_predictor(self, lr_classifier, rf_classifier, svm_classifier, x_test, y_test):
        lr_pred = lr_classifier.predict(x_test)
        rf_pred = rf_classifier.predict(x_test)
        svm_pred = svm_classifier.predict(x_test)

        hit_count = 0
        total_count = len(y_test)
        hit_index_array = []
        fail_index_array = []
        trade = 0
        vaild_count = 0
        for index in range(total_count):

            trade = 0
            vote_buy_count = 0
            vote_sell_count = 0
            vote_maintenance_count = 0

            if lr_pred[index] == -1:
                vote_sell_count += 1
            elif lr_pred[index] == 1:
                vote_buy_count += 1
            else:
                vote_maintenance_count += 1

            if rf_pred[index] == -1:
                vote_sell_count += 1
            elif rf_pred[index] == 1:
                vote_buy_count += 1
            else:
                vote_maintenance_count += 1

            if svm_pred[index] == -1:
                vote_sell_count += 1
            elif svm_pred[index] == 1:
                vote_buy_count += 1
            else:
                vote_maintenance_count += 1

            if vote_buy_count == 3:
                trade = 1
            elif vote_sell_count == 3:
                trade = -1

            if vote_buy_count == 3 or vote_sell_count == 3:
                vaild_count += 1
                if (trade) == (y_test[index]):
                    hit_count = hit_count + 1
                    hit_index_array.append(x_test.iloc[index])
                else:
                    fail_index_array.append(x_test.iloc[index])

        if hit_count != 0 and 0 != vaild_count:
            hit_ratio = hit_count / vaild_count
        print("====  all_vote_predictor hit_count=%s, total=%s, hit_ratio = %s [%s ~ %s]" % ( hit_count, vaild_count, hit_ratio, x_test.iloc[0].name, x_test.iloc[len(x_test) - 1].name))
        return vaild_count, hit_ratio, hit_ratio, pd.DataFrame(hit_index_array), pd.DataFrame(fail_index_array), trade

    def do_logistic_regression(self, x_train, y_train):
        classifier = LogisticRegression(solver='lbfgs')
        classifier.fit(x_train, y_train)
        return classifier

    def do_random_forest(self, x_train, y_train):
        classifier = RandomForestClassifier(n_estimators=100)
        classifier.fit(x_train, y_train)
        return classifier

    def do_svm(self, x_train, y_train):
        classifier = SVC(gamma='scale')
        classifier.fit(x_train, y_train)
        return classifier
