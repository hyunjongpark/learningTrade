# -*- coding: utf-8 -*-
from __future__ import division

import os, sys, datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import statsmodels.tsa.stattools as ts
from scipy.stats import randint as sp_randint
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.lda import LDA
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.qda import QDA
from sklearn.svm import LinearSVC, SVC
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV

from data_model import *
from data_handler import *
from data_reader import *
from data_writer import *
from services import *
from common import *


# Asbtact Class
class Predictor:
    def __init__(self, name):
        self.name = name
        self.classifier = None

    def train(self, x_train, y_train):
        # print(x_train)
        # print(y_train)
        self.classifier.fit(x_train, y_train)
        return self.classifier.score(x_train, y_train)

    def predict(self, x_test, with_probability=True):
        pred = self.classifier.predict(x_test)
        pred_proba = self.classifier.predict_proba(x_test)
        return pred, pred_proba

    def score(self, x_test, y_test):
        return self.classifier.score(x_test, y_test)

    def confusionMatrix(self, y_true, y_pred):
        print(confusion_matrix(y_true, y_pred))

    def classificationReport(self, y_true, y_pred, target_names):
        print(classification_report(y_true, y_pred, target_names=target_names))

    def drawROC(self, y_true, y_pred):
        false_positive_rate, true_positive_rate, thresholds = roc_curve(y_true, y_pred)
        roc_auc = auc(false_positive_rate, true_positive_rate)

        plt.title('Receiver Operating Characteristic')
        plt.plot(false_positive_rate, true_positive_rate, 'b', label='AUC = %0.2f' % roc_auc)
        plt.legend(loc='lower right')
        plt.plot([0, 1], [0, 1], 'r--')
        plt.xlim([-0.1, 1.2])
        plt.ylim([-0.1, 1.2])
        plt.ylabel('Sensitivity')
        plt.xlabel('Specificity')
        plt.show()

    def doGridSearch(self, x_train, y_train, param_grid):
        grid_search = GridSearchCV(self.classifier, param_grid=param_grid)
        grid_search.fit(x_train, y_train)

        for params, mean_score, scores in grid_search.grid_scores_:
            print("%0.3f (+/-%0.03f) for %r" % (mean_score, scores.std() * 2, params))

    def doRandomSearch(self, x_train, y_train, param_dist, iter_count):
        random_search = RandomizedSearchCV(self.classifier, param_distributions=param_dist, n_iter=iter_count)
        random_search.fit(x_train, y_train)

        for params, mean_score, scores in random_search.grid_scores_:
            print("%0.3f (+/-%0.03f) for %r" % (mean_score, scores.std() * 2, params))


class PredictorLR(Predictor):
    def __init__(self, name):
        Predictor.__init__(self, name)
        self.classifier = LogisticRegression()


class PredictorRF(Predictor):
    def __init__(self, name):
        Predictor.__init__(self, name)
        self.classifier = RandomForestClassifier()


class PredictorSVM(Predictor):
    def __init__(self, name):
        Predictor.__init__(self, name)
        self.classifier = SVC(probability=True)


class Predictors:
    def __init__(self):
        self.dbreader = services.get('dbreader')
        self.config = services.get('configurator')
        self.items = {}

    def createPredictor(self, name):
        if name == 'logistic':
            predictor = PredictorLR('logistic')
        elif name == 'rf':
            predictor = PredictorRF('rf')
        elif name == 'svm':
            predictor = PredictorSVM('svm')
        return predictor

    def find(self, code):
        # if self.items.has_key(code):
        if code in self.items:
            return self.items[code]
        return None

    def add(self, code, name, predictor):
        if self.find(code) is None:
            self.items[code] = {}

        self.items[code][name] = predictor

    def get(self, code, name):
        return self.items[code][name]

    def makeDataSet(self, code, start_date, end_date):
        df = services.get('dbreader').loadDataFrame(code, start_date, end_date)
        return df

    # def make_dataset(self, df, time_lags=5):
    #     print(df)
    #     df_lag = pd.DataFrame(index=df.index)
    #     df_lag["Close"] = df["Close"]
    #     df_lag["Volume"] = df["Volume"]
    #
    #     df_lag["Close_Lag%s" % str(time_lags)] = df["Close"].shift(time_lags)
    #     df_lag["Close_Lag%s_Change" % str(time_lags)] = df_lag["Close_Lag%s" % str(time_lags)].pct_change() * 100.0
    #
    #     df_lag["Volume_Lag%s" % str(time_lags)] = df["Volume"].shift(time_lags)
    #     df_lag["Volume_Lag%s_Change" % str(time_lags)] = df_lag["Volume_Lag%s" % str(time_lags)].pct_change() * 100.0
    #
    #     df_lag["Close_Direction"] = np.sign(df_lag["Close_Lag%s_Change" % str(time_lags)])
    #     df_lag["Volume_Direction"] = np.sign(df_lag["Volume_Lag%s_Change" % str(time_lags)])
    #
    #     return df_lag.dropna(how='any')

    def makeLaggedDataset(self, code, start_date, end_date, input_column, output_column, time_lags=5):
        df = self.makeDataSet(code, start_date, end_date)
        # print(df)

        df = df.set_index(df["price_date"])
        df_lag = df.set_index(df["price_date"])
        # print(df_lag.index)

        df.index = pd.to_datetime(df.index, format='%Y%m%d')
        df_lag.index = pd.to_datetime(df_lag.index, format='%Y%m%d')

        # print(df1)
        # df_lag = pd.DataFrame(index=df['price_date'])
        # print(df_lag)




        # df_lag[input_column] = df[input_column]
        # df_lag["volume"] = df["price_volume"]

        for input in input_column:
            # df_lag["%s_Lag%s" % (input,time_lags)] = df[input].shift(time_lags)
            # df_lag["%s_Lag%s_Change" % (input,time_lags)] = df_lag["%s_Lag%s" % (input,time_lags)].pct_change()*100.0
            #
            # df_lag[output_column] = np.where(df_lag["%s_Lag%s_Change" % (input,time_lags)]>0,1,0)
            df_lag[input] = df[input]

            df_lag["%s_Lag%s" % (input, time_lags)] = df[input].shift(time_lags)
            df_lag["%s_Lag%s_Change" % (input, time_lags)] = df_lag["%s_Lag%s" % (input, time_lags)].pct_change() * 100.0

            # df_lag["%s_Direction" %(input)] = np.where(df_lag["%s_Lag%s_Change" % (input, time_lags)] > 0, 1, 0)

            df_lag["%s_Direction" % (input)] = np.sign(df_lag["%s_Lag%s_Change" % (input, time_lags)])
            # df_lag["close_Direction"] = np.sign(df_lag["Close_Lag%s_Change" % str(time_lags)])



            # df_lag["%s_Direction" % (input)] = np.sign(df_lag["%s_Lag%s_Change" % (input, time_lags)])

        # df_lag["Close"] = df["price_close"]

        # df_lag["Close_Lag%s" % str(time_lags)] = df["price_close"].shift(time_lags)
        # df_lag["Close_Lag%s_Change" % str(time_lags)] = df_lag["Close_Lag%s" % str(time_lags)].pct_change() * 100.0
        #
        # df_lag["close_Direction"] = np.sign(df_lag["Close_Lag%s_Change" % str(time_lags)])



        # df_lag["%s_Lag%s" % (input_column, time_lags)] = df[input_column].shift(time_lags)
        # df_lag["%s_Lag%s_Change" % (input_column, time_lags)] = df_lag["%s_Lag%s" % (
        # input_column, time_lags)].pct_change() * 100.0
        #
        # df_lag["volume_Lag%s" % (time_lags)] = df["price_volume"].shift(time_lags)
        # df_lag["volume_Lag%s_Change" % (time_lags)] = df_lag["volume_Lag%s" % (time_lags)].pct_change() * 100.0
        #




        # print(df_lag)

        # df_lag["price_close"] = df_lag["price_close"]
        # df_lag["price_volume"] = df_lag["price_volume"]
        #
        # df_lag["Close_Lag%s" % str(time_lags)] = df["price_close"].shift(time_lags)
        # df_lag["Close_Lag%s_Change" % str(time_lags)] = df_lag["Close_Lag%s" % str(time_lags)].pct_change() * 100.0
        #
        # df_lag["Volume_Lag%s" % str(time_lags)] = df["price_volume"].shift(time_lags)
        # df_lag["Volume_Lag%s_Change" % str(time_lags)] = df_lag["Volume_Lag%s" % str(time_lags)].pct_change() * 100.0
        #
        # df_lag["Close_Direction"] = np.sign(df_lag["Close_Lag%s_Change" % str(time_lags)])
        # df_lag["Volume_Direction"] = np.sign(df_lag["Volume_Lag%s_Change" % str(time_lags)])

        # print(df_lag["volume"])
        # print(df_lag["Close_Direction"])
        # print(df_lag["volume_indicator"])



        return df_lag.dropna(how='any')

    # def split_dataset(df, input_column_array, output_column, spllit_ratio):
    #     split_date = getDateByPerent(df.index[0], df.index[df.shape[0] - 1], spllit_ratio)
    #
    #     input_data = df[input_column_array]
    #     output_data = df[output_column]
    #
    #     # Create training and test sets
    #     X_train = input_data[input_data.index < split_date]
    #     X_test = input_data[input_data.index >= split_date]
    #     Y_train = output_data[output_data.index < split_date]
    #     Y_test = output_data[output_data.index >= split_date]
    #
    #     return X_train, X_test, Y_train, Y_test

    # def splitDataset(self, df, date_column, input_column_array, output_column, split_ratio):
    #     first_date, last_date = df.loc[0, date_column], df.loc[df.shape[0] - 1, date_column]
    #     split_date = getDateByPerent(first_date, last_date, split_ratio)
    #
    #     print("splitDataset : date=%s" % (split_date))
    #
    #     input_data = df[input_column_array]
    #     # print(input_data)
    #     output_data = df[output_column]
    #     # print(output_data)
    #
    #     # print(input_data.index)
    #
    #     # split_date = convertDateToString(split_date)
    #
    #
    #     # print(df[date_column])
    #     # # Create training and test sets
    #     # X_train = input_data[df[date_column] < split_date]
    #     # X_test = input_data[df[date_column] >= split_date]
    #     # Y_train = output_data[df[date_column] < split_date]
    #     # Y_test = output_data[df[date_column] >= split_date]
    #     #
    #     # return X_train,X_test,Y_train,Y_test
    #
    #     X_train = input_data[input_data.index < split_date]
    #     X_test = input_data[input_data.index >= split_date]
    #     Y_train = output_data[output_data.index < split_date]
    #     Y_test = output_data[output_data.index >= split_date]
    #
    #     return X_train, X_test, Y_train, Y_test

    def split_dataset(self, df, input_column_array, output_column, spllit_ratio):
        # print(df)
        split_date = getDateByPerent(df.index[0], df.index[df.shape[0] - 1], spllit_ratio)
        # split_date = convertDateToString(split_date)

        input_data = df[input_column_array]
        # print(input_data)
        output_data = df[output_column]

        # print(input_data.index)
        # print(split_date)
        # print(type(input_data.index))
        # print(type(split_date))
        #Create training and test sets
        X_train = input_data[input_data.index < split_date]
        X_test = input_data[input_data.index >= split_date]
        Y_train = output_data[output_data.index < split_date]
        Y_test = output_data[output_data.index >= split_date]


        # print(X_train)
        # print(Y_train)
        # print(X_train, Y_train)
        # print(X_test, Y_test)

        return X_train, X_test, Y_train, Y_test

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

    def test_predictor(self, classifier, x_test, y_test):
        pred = classifier.predict(x_test)

        hit_count = 0
        total_count = len(y_test)
        for index in range(total_count):
            if (pred[index]) == (y_test[index]):
                hit_count = hit_count + 1

        hit_ratio = hit_count / total_count
        score = classifier.score(x_test, y_test)
        # print ("hit_count=%s, total=%s, hit_ratio = %s" % (hit_count,total_count,hit_ratio))
        # print("%s\n" % confusion_matrix(pred, y_test))
        return hit_ratio, score

    def make_dataset(self, df, time_lags=5):
        # print(df)
        df_lag = pd.DataFrame(index=df.index)
        # print(df_lag)
        df_lag["Close"] = df["Close"]
        df_lag["Volume"] = df["Volume"]

        df_lag["Close_Lag%s" % str(time_lags)] = df["Close"].shift(time_lags)
        df_lag["Close_Lag%s_Change" % str(time_lags)] = df_lag["Close_Lag%s" % str(time_lags)].pct_change() * 100.0

        df_lag["Volume_Lag%s" % str(time_lags)] = df["Volume"].shift(time_lags)
        df_lag["Volume_Lag%s_Change" % str(time_lags)] = df_lag["Volume_Lag%s" % str(time_lags)].pct_change() * 100.0

        df_lag["Close_Direction"] = np.sign(df_lag["Close_Lag%s_Change" % str(time_lags)])
        df_lag["Volume_Direction"] = np.sign(df_lag["Volume_Lag%s_Change" % str(time_lags)])

        return df_lag.dropna(how='any')

    def split_dataset(self, df, input_column_array, output_column, spllit_ratio):
        # print(df)

        def get_date_by_percent(start_date, end_date, percent):
            days = (end_date - start_date).days
            target_days = np.trunc(days * percent)
            target_date = start_date + datetime.timedelta(days=target_days)
            # print days, target_days,target_date
            return target_date

        split_date = get_date_by_percent(df.index[0], df.index[df.shape[0] - 1], spllit_ratio)

        input_data = df[input_column_array]
        output_data = df[output_column]

        # print(input_data.index )
        # print(split_date)
        # Create training and test sets
        X_train = input_data[input_data.index < split_date]
        X_test = input_data[input_data.index >= split_date]
        Y_train = output_data[output_data.index < split_date]
        Y_test = output_data[output_data.index >= split_date]

        # print(X_train)
        # print(Y_train)

        return X_train, X_test, Y_train, Y_test

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

    def trainAllFromFile(self, time_lags=5, split_ratio=0.75):

        test_result = {'code': [], 'company': [], 'logistic': [], 'rf': [], 'svm': []}

        dataList = get_data_list()
        print(dataList)
        avg_hit_ratio = 0
        index = 0;
        for company in dataList:
            print('    %s/%s' % (index, len(dataList)))
            index = index + 1

            for time_lags in range(1, 6):
                print("- Time Lags=%s" % (time_lags))

                try:
                    df_company = load_stock_data('%s' % (company))
                    df_dataset = self.make_dataset(df_company, time_lags)
                    X_train, X_test, Y_train, Y_test = self.split_dataset(df_dataset, ["Close_Lag%s" % (time_lags),"Volume_Lag%s" % (time_lags)],"Close_Direction", 0.75)

                    lr_classifier = self.do_logistic_regression(X_train, Y_train)
                    lr_hit_ratio, lr_score = test_predictor(lr_classifier, X_test, Y_test)

                    rf_classifier = self.do_random_forest(X_train, Y_train)
                    rf_hit_ratio, rf_score = test_predictor(rf_classifier, X_test, Y_test)

                    svm_classifier = self.do_svm(X_train, Y_train)
                    svm_hit_ratio, svm_score = test_predictor(svm_classifier, X_test, Y_test)

                    df_company_splat = str(df_company).split('_')
                    test_result['code'].append(df_company_splat[0])
                    test_result['company'].append(company)
                    # test_result['time_lags'].append(time_lags)
                    test_result['logistic'].append(lr_score)
                    test_result['rf'].append(rf_score)
                    test_result['svm'].append(svm_score)

                    print("%s - %s : Hit Ratio - Logistic Regreesion=%0.2f, RandomForest=%0.2f, SVM=%0.2f" % (
                    len(X_train), company, lr_hit_ratio, rf_hit_ratio, svm_hit_ratio))
                except:
                    print('except %s' % company)
            # if index >= 3:
            #     break

        df_result = pd.DataFrame(test_result)

        return df_result


    def trainAll(self, time_lags=5, split_ratio=0.75):
        rows_code = self.dbreader.loadCodes(self.config.get('data_limit'))

        test_result = {'code': [], 'company': [], 'logistic': [], 'rf': [], 'svm': []}

        index = 1
        for a_row_code in rows_code:
            code = a_row_code[0]
            company = a_row_code[1]

            print("... %s of %s : Training Machine Learning on %s %s" % (index, len(rows_code), code, company))

            df_dataset = self.makeLaggedDataset(code, self.config.get('start_date'), self.config.get('end_date'),
                                                self.config.get('input_column'), self.config.get('output_column'),
                                                time_lags=time_lags)

            # if str(df_dataset.index[len(df_dataset) - 1]) == str(self.config.get('end_date')) is False:
            #     continue
            # else:
            #     print(convertDateToString(df_dataset.index[0]))
            #     print(self.config.get('start_date'))
            #     print(convertDateToString(df_dataset.index[len(df_dataset)-1]))
            #     print(self.config.get('end_date'))
            #     print(df_dataset)
            #     continue;

            # days = (convertStringToDate(self.config.get('end_date')) - convertStringToDate(self.config.get('start_date'))).days
            # print(days)
            # print(len(df_dataset))
            # print(df_dataset.shape)
            #
            # print(convertDateToString(df_dataset.index[0]))
            # print(convertDateToString(df_dataset.index[len(df_dataset) - 1]))


            if df_dataset.shape[0] > 100:

                test_result['code'].append(code)
                test_result['company'].append(company)

                # print (len(df_dataset))

                # X_train,X_test,Y_train,Y_test = self.splitDataset(df_dataset,'price_date',
                #                                                   [self.config.get('input_column')],
                #                                                   self.config.get('output_column'),split_ratio)

                # X_train, X_test, Y_train, Y_test = self.split_dataset(df_dataset,
                #                                                       ["Close_Lag%s" % (time_lags),
                #                                                        "Volume_Lag%s" % (time_lags)],
                #                                                       "Close_Direction", 0.75)

                X_train, X_test, Y_train, Y_test = self.split_dataset(df_dataset,
                                                                      self.config.get('input_column'),
                                                                      self.config.get('output_column'), split_ratio)




                # print (X_test, Y_test)

                # lr_classifier = self.do_logistic_regression(X_train, Y_train)
                # lr_hit_ratio, lr_score = self.test_predictor(lr_classifier, X_test, Y_test)
                #
                # rf_classifier = self.do_random_forest(X_train, Y_train)
                # rf_hit_ratio, rf_score = self.test_predictor(rf_classifier, X_test, Y_test)
                #
                # svm_classifier = self.do_svm(X_train, Y_train)
                # svm_hit_ratio, svm_score = self.test_predictor(svm_classifier, X_test, Y_test)
                #
                # print("%s - %s : Hit Ratio - Logistic Regreesion=%0.2f, RandomForest=%0.2f, SVM=%0.2f" % (len(X_train), company, lr_hit_ratio, rf_hit_ratio, svm_hit_ratio))


                for a_clasifier in ['logistic', 'rf', 'svm']:
                    predictor = self.createPredictor(a_clasifier)
                    self.add(code, a_clasifier, predictor)

                    predictor.train(X_train, Y_train)
                    score = predictor.score(X_test, Y_test)

                    test_result[a_clasifier].append(score)

                    print("%s    predictor=%s, score=%s" % (code, a_clasifier, score))
            else:
                self.dbreader.deleteCode(code)

                # print (test_result)

            index += 1

        df_result = pd.DataFrame(test_result)

        return df_result

    def dump(self):
        for a_code in self.items.keys():
            for a_predictor in self.items[a_code].keys():
                print("... code=%s , predictor=%s" % (a_code, a_predictor))


def test_predictor(classifier, x_test, y_test):
    pred = classifier.predict(x_test)

    hit_count = 0
    total_count = len(y_test)
    for index in range(total_count):
        if (pred[index]) == (y_test[index]):
            hit_count = hit_count + 1

    hit_ratio = hit_count / total_count
    score = classifier.score(x_test, y_test)
    # print "hit_count=%s, total=%s, hit_ratio = %s" % (hit_count,total_count,hit_ratio)

    return hit_ratio, score
    # Output the hit-rate and the confusion matrix for each model

    # print("%s\n" % confusion_matrix(pred, y_test))


if __name__ == "__main__":
    # Calculate and output the CADF test on the residuals

    avg_hit_ratio = 0
    for time_lags in range(1, 6):
        print("- Time Lags=%s" % (time_lags))

        for company in ['samsung', 'hanmi']:
            df_company = load_stock_data('%s.data' % (company))

            df_dataset = make_dataset(df_company, time_lags)
            X_train, X_test, Y_train, Y_test = split_dataset(df_dataset, ["Close_Lag%s" % (time_lags),
                                                                          "Volume_Lag%s" % (time_lags)],
                                                             "Close_Direction", 0.75)
            # print X_test

            lr_classifier = do_logistic_regression(X_train, Y_train)
            lr_hit_ratio, lr_score = test_predictor(lr_classifier, X_test, Y_test)

            rf_classifier = do_random_forest(X_train, Y_train)
            rf_hit_ratio, rf_score = test_predictor(rf_classifier, X_test, Y_test)

            svm_classifier = do_svm(X_train, Y_train)
            svm_hit_ratio, svm_score = test_predictor(rf_classifier, X_test, Y_test)

            print("%s : Hit Ratio - Logistic Regreesion=%0.2f, RandomForest=%0.2f, SVM=%0.2f" % (
            company, lr_hit_ratio, rf_hit_ratio, svm_hit_ratio))
