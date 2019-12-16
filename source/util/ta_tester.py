# -*- coding: utf-8 -*-
from __future__ import division

import os, sys
import matplotlib.pyplot as plt
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC, SVC
from sklearn.model_selection import cross_validate
#https://github.com/mrjbq7/ta-lib
#https://mrjbq7.github.io/ta-lib/doc_index.html
#https://booja.blogspot.com/2017/12/python-ta-lib.html

#http://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
#https://pip.pypa.io/en/latest/user_guide/#installing-from-wheels
import talib
from talib import MA_Type


parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *
from util.services import *


class ta_tester():
    def __init__(self):
        print('ta_tester')
        self.code = None
        self.fastperiod = 12
        self.slowperiod = 26
        self.signalperiod = 9
        self.profit = 0

    def set_code(self, code):
        self.code = code

    def test(self, code='004990'):
        end = datetime.datetime.today()
        start = end - relativedelta(months=24)
        df = get_df_from_file(code, start, end)

        df = self.add_sma(df)
        df = self.add_bbands(df)
        df = self.add_mom(df)
        # df = self.add_stoch(df)
        df = self.add_macd(df)
        df = self.add_pattern(df)


        # print(df)

        fig, axs = plt.subplots(6)
        ax = axs[0]
        ax.plot(df["Close"])

        ax.plot(df['SMA'])
        ax.grid(True)

        ax2 = ax.twinx()
        ax2.plot(get_foreigner_info(code, start, end), 'r')


        ax = axs[1]
        ax.plot(df["Close"])
        ax.plot(df['BBANDS_upper'])
        ax.plot(df['BBANDS_middle'])
        ax.plot(df['BBANDS_lower'])
        ax.grid(True)

        ax = axs[2]
        ax.plot(df["MOM"], 'r')
        ax.grid(True)

        # ax = axs[3]
        # ax.plot(df["STOCH_slowk"])
        # ax.plot(df["STOCH_slowd"])
        # ax.grid(True)

        ax = axs[3]
        ax.plot(df["MACD_macd"])
        ax.plot(df["MACD_signal"])
        ax.plot(df["MACD_hist"])
        ax.grid(True)

        ax = axs[4]
        ax.plot(df["Volume"])
        ax.grid(True)

        ax = axs[5]
        ax.plot(df['SMA'])
        ax.grid(True)


        plt.show()

    def get_pattern(self, src, result_add, result_minus, new, pattern_index):
        # for i in range(len(new)):
        #     if new[i] > 0:
        #         if 0 == src[i]:
        #             src[i] = pattern_index
        #             result_add[i] = 1
        #         else:
        #             src[i] = '%s : %s ' %(src[i], pattern_index)
        #             result_add[i] = result_add[i] + 1
        #             print('[%s] src[%s] add[%s]' % (i, src[i], pattern_index))
        #     elif new[i] < 0:
        #         if 0 == src[i]:
        #             src[i] = -pattern_index
        #             result_minus[i] = -1
        #         else:
        #             src[i] = '%s : %s ' %(src[i], -pattern_index)
        #             result_minus[i] = result_minus[i] - 1
        #             print('[%s] src[%s] add[%s]' % (i, src[i], -pattern_index))
        return src

    def add_machine(self, df, src, ta_name, index, ret_parrern):
        # if index > 0:
        #     return


        if src[len(src)-1] == 100:
            # print('%s[%s]' %(ta_name, src[len(src)-1]))
            ret_parrern.append('%s[%s]' %(ta_name, src[len(src)-1]))


        # result = []
        # result_plus = []
        # result_minus = []
        # for i in range(len(df)):
        #     result.append(0)
        #     result_plus.append(0)
        #     result_minus.append(0)
        # result = self.get_pattern(result, src, result_plus, result_minus, index)
        # df[ta_name] = result


        # if ta_name in services.get('configurator').get('input_column'):
        #     return
        # services.get('configurator').get('input_column').append(ta_name)

    def add_pattern(self, df):
        ret_parrern = []
        result = []
        result_add = []
        result_minus = []
        output = talib.CDL2CROWS(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDL2CROWS', 63, ret_parrern)
        for i in range(len(output)):
            result.append(0)
            result_add.append(0)
            result_minus.append(0)
        result = self.get_pattern(result, result_add, result_minus, output, 1)

        # output = talib.CDL3BLACKCROWS(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        # self.add_machine(df, output, 'CDL3BLACKCROWS', 2, ret_parrern)
        # result = self.get_pattern(result, result_add, result_minus, output, 2)
        output = talib.CDL3INSIDE(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDL3INSIDE', 3, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 3)
        # output = talib.CDL3LINESTRIKE(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        # self.add_machine(df, output, 'CDL3LINESTRIKE', 4, ret_parrern)
        # result = self.get_pattern(result, result_add, result_minus, output, 4)
        output = talib.CDL3OUTSIDE(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDL3OUTSIDE', 5, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 5)
        output = talib.CDL3STARSINSOUTH(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDL3STARSINSOUTH', 6, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 6)
        output = talib.CDL3WHITESOLDIERS(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDL3WHITESOLDIERS', 7, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 7)
        output = talib.CDLABANDONEDBABY(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLABANDONEDBABY', 8, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 8)
        output = talib.CDLADVANCEBLOCK(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLADVANCEBLOCK', 9, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 9)
        output = talib.CDLBELTHOLD(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLBELTHOLD', 10, ret_parrern)
        result = self.get_pattern(result,result_add, result_minus,  output, 10)
        output = talib.CDLBREAKAWAY(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLBREAKAWAY', 11, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 11)
        output = talib.CDLCLOSINGMARUBOZU(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLCLOSINGMARUBOZU', 12, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 12)
        output = talib.CDLCONCEALBABYSWALL(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLCONCEALBABYSWALL', 13, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 13)
        output = talib.CDLCOUNTERATTACK(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLCOUNTERATTACK', 14, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 14)
        output = talib.CDLDARKCLOUDCOVER(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLDARKCLOUDCOVER', 15, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 15)
        output = talib.CDLDOJISTAR(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLDOJISTAR',17, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 17)
        output = talib.CDLDRAGONFLYDOJI(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLDRAGONFLYDOJI',18, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 18)
        output = talib.CDLENGULFING(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLENGULFING',19, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 19)
        output = talib.CDLEVENINGDOJISTAR(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLEVENINGDOJISTAR',20, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 20)
        output = talib.CDLEVENINGSTAR(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLEVENINGSTAR',21, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 21)
        #     output = talib.CDLGAPSIDESIDEWHITE(df['시가'].values, df['고가'].values, 7XXZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ29io
        # output = talib.CDLGRAVESTONEDOJI(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLGRAVESTONEDOJI',23, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 23)
        output = talib.CDLHAMMER(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLHAMMER',24, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 24)
        output = talib.CDLHANGINGMAN(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLHANGINGMAN',25, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 25)
        output = talib.CDLHARAMI(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLHARAMI',26, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 26)
        output = talib.CDLHARAMICROSS(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLHARAMICROSS',27, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 27)
        output = talib.CDLHIGHWAVE(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLHIGHWAVE',28, ret_parrern)
        result = self.get_pattern(result,result_add, result_minus,  output, 28)
        output = talib.CDLHIKKAKE(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLHIKKAKE',29, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 29)
        output = talib.CDLHIKKAKEMOD(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLHIKKAKEMOD',30, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 30)
        output = talib.CDLHOMINGPIGEON(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLHOMINGPIGEON',31, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 31)
        output = talib.CDLIDENTICAL3CROWS(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLIDENTICAL3CROWS',32, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 32)
        output = talib.CDLINNECK(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLINNECK',33, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 33)
        output = talib.CDLINVERTEDHAMMER(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLINVERTEDHAMMER',34, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 34)
        output = talib.CDLKICKING(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLKICKING',35, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 35)
        output = talib.CDLKICKINGBYLENGTH(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLKICKINGBYLENGTH',36, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 36)
        output = talib.CDLLADDERBOTTOM(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLLADDERBOTTOM',37, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 37)
        output = talib.CDLLONGLEGGEDDOJI(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLLONGLEGGEDDOJI',38, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 38)
        output = talib.CDLLONGLINE(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLLONGLINE',39, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 39)
        output = talib.CDLMARUBOZU(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLMARUBOZU',40, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 40)
        output = talib.CDLMATCHINGLOW(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLMATCHINGLOW',41, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 41)
        output = talib.CDLMATHOLD(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLMATHOLD',42, ret_parrern)
        result = self.get_pattern(result,result_add, result_minus,  output, 42)
        # output = talib.CDLMATCHINGLOW(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        # self.add_machine(df, output, 'CDLMATCHINGLOW',43, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 43)
        output = talib.CDLMORNINGDOJISTAR(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLMORNINGDOJISTAR',44, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 44)
        output = talib.CDLMORNINGSTAR(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLMORNINGSTAR',45, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 45)
        output = talib.CDLONNECK(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLONNECK',46, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 46)
        output = talib.CDLPIERCING(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLPIERCING',47, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 47)
        output = talib.CDLRICKSHAWMAN(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLRICKSHAWMAN',48, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 48)
        output = talib.CDLRISEFALL3METHODS(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLRISEFALL3METHODS',49, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 49)
        output = talib.CDLSEPARATINGLINES(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLSEPARATINGLINES',50, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 50)
        output = talib.CDLSHOOTINGSTAR(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLSHOOTINGSTAR',51, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 51)
        output = talib.CDLSHORTLINE(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLSHORTLINE',52, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 52)
        output = talib.CDLSPINNINGTOP(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLSPINNINGTOP',53, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 53)
        output = talib.CDLSTALLEDPATTERN(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLSTALLEDPATTERN',54, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 54)
        output = talib.CDLSTICKSANDWICH(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLSTICKSANDWICH',55, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 55)
        output = talib.CDLTAKURI(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLTAKURI',56, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 56)
        output = talib.CDLTASUKIGAP(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLTASUKIGAP',57, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 57)
        output = talib.CDLTHRUSTING(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLTHRUSTING',58, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 58)
        output = talib.CDLTRISTAR(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLTRISTAR',59, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 59)
        output = talib.CDLUNIQUE3RIVER(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLUNIQUE3RIVER',60, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 60)
        output = talib.CDLUPSIDEGAP2CROWS(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLUPSIDEGAP2CROWS',61, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 61)
        output = talib.CDLXSIDEGAP3METHODS(df['시가'].values, df['고가'].values, df['저가'].values, df['종가'].values)
        self.add_machine(df, output, 'CDLXSIDEGAP3METHODS',62, ret_parrern)
        result = self.get_pattern(result, result_add, result_minus, output, 62)

        df['PATTERN'] = result
        df['PLUS_PATTERN'] = result_add
        df['MINUS_PATTERN'] = result_minus

        # if 'PLUS_PATTERN' in services.get('configurator').get('input_column'):
        #     print('')
        # else:
        #     services.get('configurator').get('input_column').append('PLUS_PATTERN')
        # if 'MINUS_PATTERN' in services.get('configurator').get('input_column'):
        #     print('')
        # else:
        #     services.get('configurator').get('input_column').append('MINUS_PATTERN')

        # for i in range(len(result)):
        #     print('[%s]: [%s][%s][%s][%s]  plus[%s] minus[%s] %s' % (i, df.iloc[i].name, df['고가'].values[i],  df['종가'].values[i],  df['저가'].values[i], result_add[i], result_minus[i], result[i]))

        # i = len(result) -1
        # print('[%s]: [%s][%s][%s][%s]  plus[%s] minus[%s] %s' % (i, df.iloc[i].name, df['고가'].values[i], df['종가'].values[i], df['저가'].values[i], result_add[i], result_minus[i],result[i]))
        return ret_parrern

    def add_sma(self, df):
        output = talib.SMA(df['Close'].values, timeperiod=25)
        df['SMA'] = output
        return df

    def add_bbands(self, df):
        upper, middle, lower = talib.BBANDS(df['Close'].values, 20, 2, 2)
        df['BBANDS_upper'] = upper
        df['BBANDS_middle'] = middle
        df['BBANDS_lower'] = lower
        return df

    def add_mom(self, df):
        output = talib.MOM(df['Close'].values)
        df['MOM'] = output
        return df

    def add_stoch(self, df):
        slowk, slowd = talib.STOCH(df['High'].values,
                                   df['Low'].values,
                                   df['Open'].values,
                                   fastk_period=5,
                                   slowk_period=3,
                                   slowk_matype=0,
                                   slowd_period=3,
                                   slowd_matype=0)
        df['STOCH_slowk'] = slowk
        df['STOCH_slowd'] = slowd
        return df

    def add_macd(self, df):

        success, profit, fastperiod, slowperiod, signalperiod = get_best_macd_value(self.code)
        if success != True:
            self.fastperiod = 12
            self.slowperiod = 26
            self.signalperiod = 9
        self.profit = profit


        macd, signal, hist = talib.MACD(df['Close'].values,
                                        self.fastperiod,
                                        self.slowperiod,
                                        self.signalperiod)
        df['MACD_macd'] = macd
        df['MACD_signal'] = signal
        df['MACD_hist'] = hist
        return df

    def add_macd_foreigner_count(self, df):

        success, profit, fastperiod, slowperiod, signalperiod = get_best_macd_value(self.code)
        if success != True:
            self.fastperiod = 12
            self.slowperiod = 26
            self.signalperiod = 9
        self.profit = profit

        macd, signal, hist = talib.MACD(df['foreigner_count'].values,
                                        self.fastperiod,
                                        self.slowperiod,
                                        self.signalperiod)
        df['MACD_foreigner_count_macd'] = macd
        df['MACD_foreigner_count_signal'] = signal
        df['MACD_foreigner_count_hist'] = hist
        return df

    def get_best_value(self, code):
        load_yaml()

