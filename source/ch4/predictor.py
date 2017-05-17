# -*- coding: utf-8 -*-
from __future__ import division

import os, sys, datetime
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import pprint
import statsmodels.tsa.stattools as ts
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.lda import LDA
from sklearn.metrics import confusion_matrix
from sklearn.qda import QDA
from sklearn.svm import LinearSVC, SVC

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *


def make_dataset(df, time_lags=5):
    # print(df)
    df_lag = pd.DataFrame(index=df.index)
    df_lag["Close"] = df["Close"]
    df_lag["Volume"] = df["Volume"]

    df_lag["Close_Lag%s" % str(time_lags)] = df["Close"].shift(time_lags)
    df_lag["Close_Lag%s_Change" % str(time_lags)] = df_lag["Close_Lag%s" % str(time_lags)].pct_change() * 100.0

    df_lag["Volume_Lag%s" % str(time_lags)] = df["Volume"].shift(time_lags)
    df_lag["Volume_Lag%s_Change" % str(time_lags)] = df_lag["Volume_Lag%s" % str(time_lags)].pct_change() * 100.0

    # df_lag["Close_Direction"] = np.sign(df_lag["Close_Lag%s_Change" % str(time_lags)])
    df_lag["%s_Change" % ('Close')] = df_lag["Close"].pct_change() * 100.0
    df_lag["%s_Direction" % ('Close')] = np.sign(df_lag["%s_Change" % ('Close')])
    # print(df_lag["Close_Direction"])
    df_lag["Volume_Direction"] = np.sign(df_lag["Volume_Lag%s_Change" % str(time_lags)])

    return df_lag.dropna(how='any')


def split_dataset(df, input_column_array, output_column, spllit_ratio):
    # print(df)

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


def get_date_by_percent(start_date, end_date, percent):
    days = (end_date - start_date).days
    target_days = np.trunc(days * percent)
    target_date = start_date + datetime.timedelta(days=target_days)
    # print days, target_days,target_date
    return target_date


def do_logistic_regression(x_train, y_train):
    classifier = LogisticRegression()
    classifier.fit(x_train, y_train)
    return classifier


def do_random_forest(x_train, y_train):
    classifier = RandomForestClassifier()
    classifier.fit(x_train, y_train)
    return classifier


def do_svm(x_train, y_train):
    classifier = SVC()
    classifier.fit(x_train, y_train)
    return classifier


def test_predictor(classifier, x_test, y_test):
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


if __name__ == "__main__":

    code_list = []
    end = datetime.datetime.today()
    start = end - relativedelta(months=6)
    data = load_yaml('kospi100')
    time_lags = 1
    for code, value in data.iterItems():
        try:
            df_company = get_df_from_file(code, start, end)
            df_dataset = make_dataset(df_company, time_lags)
            X_train, X_test, Y_train, Y_test = split_dataset(df_dataset,
                                                             ["Close_Lag%s" % (time_lags), "Volume_Lag%s" % (time_lags)],
                                                             "Close_Direction", 0.75)
            # print(df_dataset['Close'])
            # print(X_train)
            # print(Y_train)
            lr_classifier = do_logistic_regression(X_train, Y_train)
            lr_hit_ratio, lr_score = test_predictor(lr_classifier, X_test, Y_test)

            rf_classifier = do_random_forest(X_train, Y_train)
            rf_hit_ratio, rf_score = test_predictor(rf_classifier, X_test, Y_test)

            svm_classifier = do_svm(X_train, Y_train)
            svm_hit_ratio, svm_score = test_predictor(svm_classifier, X_test, Y_test)

            print("%s : Hit Ratio - Logistic Regreesion=%0.2f, RandomForest=%0.2f, SVM=%0.2f" % (code, lr_hit_ratio, rf_hit_ratio, svm_hit_ratio))
        except Exception as ex:
            print('except [%s] %s' % code, ex)
