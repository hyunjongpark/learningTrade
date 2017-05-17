# -*- coding: utf-8 -*-
from __future__ import division

import os, sys
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC, SVC
from sklearn import cross_validation

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *
from util.services import *
# from util.ta_tester import ta_tester


class machine_learning_tester():
    def __init__(self):
        print('machine_learning_tester')
        # self.ta_tester = ta_tester()

    def show_machine_learning(self, stock_list=None, view_chart=True, start='20160101', end='20170101', time_lags=5):
        stock_trade = []
        row_index = 0
        code_list = []
        if stock_list == None:
            stock_list = load_yaml('kospi200')
            for company_code, value in stock_list.iterItems():
                code_list.append(company_code)
        else:
            code_list = stock_list

        lr_totla = 0
        rf_totla = 0
        svm_totla = 0

        for code in code_list:
        # for code in ['047040','000120','010130','006800','009830','002790','114090','105560','000720']:

            if code == '042660':
                continue

            print('%s/%s code:%s ==================================' % (row_index, len(code_list), code))
            isSuccess, profit_result = self.trading_machine_learning(code, start, end, view_chart, time_lags)
            if isSuccess == False:
                continue
            lr_totla += profit_result['logistic'].values
            rf_totla += profit_result['rf'].values
            svm_totla += profit_result['svm'].values
            row_index += 1


        print("Total Hit Ratio - Logistic Regreesion=%0.2f, RandomForest=%0.2f, SVM=%0.2f, [%s ~ %s]" % (
        lr_totla / row_index, rf_totla / row_index, svm_totla / row_index, start, end))

        return stock_trade

    def trading_machine_learning(self, code='009150', start='20160101', end='20170101', view_chart=True, time_lags=1):
        print('%s %s ~ %s' % (code, start, end))
        test_result = {'code': [], 'logistic': [], 'rf': [], 'svm': [], 'logistic_tomorrow_predic': [],
                       'rf_tomorrow_predic': [], 'svm_tomorrow_predic': []}
        try:
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
                    df = self.ta_tester.add_macd(df)




            df_dataset = self.make_dataset(df, time_lags)
            # print(df_dataset)

            input_column_name = []
            for input in services.get('configurator').get('input_column'):
                input_column_name.append("%s_Lag%s" % (input,time_lags))

            # X_train, X_test, Y_train, Y_test = self.split_dataset(df_dataset, input_column_name,
            #                                                       "Close_Lag%s_Direction" % (time_lags), 0.75)

            X_train, X_test, Y_train, Y_test = self.split_dataset(df_dataset, services.get('configurator').get('input_column'),
                                                                  "Close_Lag%s_Direction" % (time_lags),
                                                                  0.75)

            # X_train, X_test, Y_train, Y_test = self.split_dataset(df_dataset, input_column_name,
            #                                                       services.get('configurator').get('output_column'),
            #                                                       0.75)

            # print(X_test)
            # print(Y_test)

            lr_classifier = self.do_logistic_regression(X_train, Y_train)
            lr_hit_ratio, lr_score, lr_hit_index, lr_fail_index, lr_tomorrow_predic = self.test_predictor(lr_classifier, X_test, Y_test)

            rf_classifier = self.do_random_forest(X_train, Y_train)
            rf_hit_ratio, rf_score, rf_hit_index, rf_fail_index, rf_tomorrow_predic = self.test_predictor(rf_classifier, X_test, Y_test)

            svm_classifier = self.do_svm(X_train, Y_train)
            svm_hit_ratio, svm_score, svm_hit_index, svm_fail_index, svm_tomorrow_predic = self.test_predictor(svm_classifier, X_test, Y_test)

            if lr_hit_ratio < 0.5:
                if rf_hit_ratio < 0.5:
                    if svm_hit_ratio < 0.5:
                        # print("PASS %s : Hit Ratio - Logistic Regreesion=%0.2f, RandomForest=%0.2f, SVM=%0.2f, [%s ~ %s]" % (code, lr_hit_ratio, rf_hit_ratio, svm_hit_ratio, start, end))
                        return False, None

            test_result['code'].append(code)
            test_result['logistic'].append(lr_score)
            test_result['rf'].append(rf_score)
            test_result['svm'].append(svm_score)
            test_result['logistic_tomorrow_predic'].append(lr_tomorrow_predic)
            test_result['rf_tomorrow_predic'].append(rf_tomorrow_predic)
            test_result['svm_tomorrow_predic'].append(svm_tomorrow_predic)


            print("%s : Hit Ratio - Logistic Regreesion=%0.2f, RandomForest=%0.2f, SVM=%0.2f, [%s ~ %s]" % (
            code, lr_hit_ratio, rf_hit_ratio, svm_hit_ratio, start, end))
        except Exception as ex:
            print('except [%s] %s' % (code, ex))
            return False, None

        if view_chart == True:
            self.drawHitRatio(code, df, lr_hit_index, lr_fail_index, rf_hit_index, rf_fail_index, svm_hit_index, svm_fail_index, time_lags)
            # self.drawHitRatioTest(code, df, lr_classifier, rf_classifier, svm_classifier)

        # print(df_result)
        return True, pd.DataFrame(test_result)

    def drawHitRatioTest(self, code, df, lr_classifier, rf_classifier, svm_classifier):
        df_dataset = self.make_dataset(df, 0)
        input_column_name = []
        for input in services.get('configurator').get('input_column'):
            input_column_name.append("%s_Lag%s" % (input, 0))

        input_data = df_dataset[input_column_name]
        output_data = df_dataset[services.get('configurator').get('output_column')]

        lr_hit_ratio, lr_score, lr_hit_index, lr_fail_index, lr_tomorrow_predic = self.test_predictor(lr_classifier, input_data, output_data)
        rf_hit_ratio, rf_score, rf_hit_index, rf_fail_index, rf_classifiertomorrow_predic = self.test_predictor(rf_classifier, input_data, output_data)
        svm_hit_ratio, svm_score, svm_hit_index, svm_fail_index, svm_tomorrow_predic = self.test_predictor(svm_classifier, input_data, output_data)

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
                     svm_fail_index, time_lags):
        fig, axs = plt.subplots(3)
        ax = axs[0]
        ax.plot(df["Close"])
        ax.plot(lr_fail_index.index, self.close_from_date(df, lr_fail_index), 'ro')
        ax.plot(lr_hit_index.index, self.close_from_date(df, lr_hit_index), 'bo')
        ax.set_title('%s logistic_regression' %(code))
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

        plt.show()

    # def make_dataset(self, df, time_lags=5):
    #     # print(df.describe())
    #     df_lag = pd.DataFrame(index=df.index)
    #
    #     df_lag['Close'] = df['Close']
    #
    #
    #     df_lag["Close_Lag%s" % (time_lags)] = df['Close'].shift(time_lags)
    #     df_lag["Close_Lag%s_Change" % (time_lags)] = df_lag["Close_Lag%s" % (time_lags)].pct_change()*100.0
    #     df_lag["Close_Lag%s_Direction" % (time_lags)] = np.sign(df_lag["Close_Lag%s_Change" % (time_lags)])
    #
    #     df_lag["Close_Change"] = df_lag["Close"].pct_change() * 100.0
    #     df_lag["Close_Direction"] = np.sign(df_lag["Close_Change"])
    #
    #     df_lag["Volume"] = df["Volume"]
    #
    #     for input in services.get('configurator').get('input_column'):
    #         df_lag["%s_Lag%s" % (input,time_lags)] = df[input].shift(time_lags)
    #
    #
    #
    #     # for input in services.get('configurator').get('input_column'):
    #     #     df_lag["%s_Lag%s" % (input,time_lags)] = df[input].shift(time_lags)
    #     #     df_lag["%s_Lag%s_Change" % (input,time_lags)] = df_lag["%s_Lag%s" % (input,time_lags)].pct_change()*100.0
    #     #     df_lag["%s_Lang%s_Direction" % (input,time_lags)] = np.sign(df_lag["%s_Lag%s_Change" % (input, time_lags)])
    #     #
    #     #     df_lag["%s_Change" % (input)] = df_lag["Close"].pct_change() * 100.0
    #     #     df_lag["%s_Direction" % (input)] = np.sign(df_lag["%s_Change" % (input)])
    #
    #     return df_lag.dropna(how='any')


    def make_dataset(self, df, time_lags=5):
        # print(df.describe())
        df_lag = pd.DataFrame(index=df.index)

        df_lag['Close'] = df['Close']

        df_lag["Close_Lag%s" % (time_lags)] = df['Close'].shift(-1)
        df_lag["Close_Lag%s_Change" % (time_lags)] = df_lag["Close_Lag%s" % (time_lags)].pct_change()*100.0
        df_lag["Close_Lag%s_Direction" % (time_lags)] = np.sign(df_lag["Close_Lag%s_Change" % (time_lags)])

        df_lag["Close_Change"] = df_lag["Close"].pct_change() * 100.0
        df_lag["Close_Direction"] = np.sign(df_lag["Close_Change"])

        df_lag["Volume"] = df["Volume"]

        for input in services.get('configurator').get('input_column'):
            # df_lag["%s_Lag%s" % (input,time_lags)] = df[input].shift(time_lags)
            df_lag["%s" % (input)] = df[input].shift(time_lags)



        return df_lag.dropna(how='any')



    def split_dataset(self, df, input_column_array, output_column, spllit_ratio):
        split_date = getDateByPerent(df.index[0], df.index[df.shape[0] - 1], spllit_ratio)

        input_data = df[input_column_array]
        output_data = df[output_column]

        X_train = input_data[input_data.index < split_date]
        Y_train = output_data[output_data.index < split_date]

        X_test = input_data[input_data.index >= split_date]
        Y_test = output_data[output_data.index >= split_date]

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
                # if pred[index] > 0:
                #     print('%s: UP' %(x_test.iloc[index].name))
                # if pred[index] < 0:
                #     print('%s: DOWN' %(x_test.iloc[index].name))
                # if pred[index] == 0:
                #     print('%s: HOLD' %(x_test.iloc[index].name))
            else:
                fail_index_array.append(x_test.iloc[index])


        hit_ratio = hit_count / total_count
        score = classifier.score(x_test, y_test)
        print("hit_count=%s, total=%s, hit_ratio = %s [%s ~ %s]" % (
        hit_count, total_count, hit_ratio, x_test.iloc[0].name, x_test.iloc[len(x_test) - 1].name))

        return hit_ratio, score, pd.DataFrame(hit_index_array), pd.DataFrame(fail_index_array), pred[len(pred)-1]

    def do_logistic_regression(self, x_train, y_train):
        classifier = LogisticRegression()
        classifier.fit(x_train, y_train)
        return classifier

    def do_random_forest(self, x_train, y_train):
        classifier = RandomForestClassifier()
        classifier.fit(x_train, y_train)
        return classifier

    def do_svm(self, x_train, y_train):
        classifier = SVC()
        classifier.fit(x_train, y_train)
        return classifier
