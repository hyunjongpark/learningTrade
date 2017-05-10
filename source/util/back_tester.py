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

    def run(self):
        # for index in [24,15,12,20,8, 6,4,3,2]:
        # for index in [6]:
        # for window in [5,10,15,20]:
        for window in [20]:
            start = self.end - relativedelta(months=6)
            self.stationarity_tester.show_stationarity(False, start, self.end, window)
