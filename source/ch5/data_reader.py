# -*- coding: utf-8 -*-
from __future__ import division
import os, sys
import sqlite3
# from pymysql import *

from data_handler import *
from data_model import *
from services import *

from stock_common import *
np.seterr(divide='ignore', invalid='ignore')

class DataReader():
    def __init__(self):
        self.dbhandler = services.get('dbhandler')

    def loadDataFrame(self, code, start_date, end_date):
        print("loadDataFrame : %s, %s" % (start_date, end_date))
        converted_start_date = start_date
        converted_end_date = end_date
        sql = "select price_date, price_open, price_close, price_high, price_low, price_adj_close, price_volume  from prices"
        sql += " where code='%s'" % (code)
        sql += " and price_date between '%s' and '%s' " % (converted_start_date, converted_end_date)
        print('sql: %s' %(sql))
        df = pd.read_sql(sql, self.dbhandler.conn)
        print('df %s' %(df))
        return df


    def loadCodes(self, limit=0):
        sql = "select code,company from codes where market_type=1"
        if limit > 0:
            sql += " limit %s" % (limit)

        rows = self.dbhandler.openSql(sql).fetchall()

        return rows

    def deleteCode(self, code):
        sql = "delete from codes where code='%s'" %(code)
        print(sql)
        rows = self.dbhandler.execSql(sql).fetchall()

    def totlaCountCode(self):
        sql = "select count(*) from codes"
        print(sql)
        rows = self.dbhandler.openSql(sql).fetchall()
        print(rows)
