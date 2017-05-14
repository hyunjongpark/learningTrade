# -*- coding: utf-8 -*-
from __future__ import division
from dateutil.relativedelta import relativedelta
from util.stationarity_tester import stationarity_tester
import os, sys
parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *
import datetime

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)


class back_tester():
    def __init__(self):
        print('back_tester')
        self.stationarity_tester = stationarity_tester()
        self.end = datetime.datetime.today()
        # self.end = datetime.datetime.strptime('20170101', '%Y%m%d')

    def run(self):
        for index in [3, 6 , 12, 24 ]:
            start = self.end - relativedelta(months=index)
            self.stationarity_tester.show_stationarity(None, False, start, self.end, 10)

    def run_series(self):
        end = datetime.datetime.today()
        # end = datetime.datetime.strptime('20160513', '%Y%m%d')
        start = end - relativedelta(months=6)
        self.stationarity_tester.show_stationarity(None, False, start, end, 10)
        print('%s ~ %s' %(start, end))

        for i in range(3):
            end = start
            start = end - relativedelta(months=6)
            print('%s ~ %s' % (start, end))
            self.stationarity_tester.show_stationarity(None, False, start, end, 10)


