# -*- coding: utf-8 -*-
from __future__ import division
import os, sys
import sqlite3
# from pymysql import *

from data_handler import *
from data_model import *
from services import *

from stock_common import *


class DataWriter():
    def __init__(self):
        self.dbhandler = services.get('dbhandler')

    def updateCodeToDB(self, codes):
        for key, a_item in codes.iterItems():
            sql = self.generateCodeItemSQL(a_item)

            self.dbhandler.execSql(sql)

    # def generateCodeItemSQL(self, code_item):
    #     sql = "insert into codes set "
    #     sql += "last_update=" + getQuote(getToday())
    #     sql += ",code=" + getQuote(code_item.code)
    #     sql += ",full_code=" + getQuote(code_item.full_code)
    #     sql += ",company=" + getQuote(code_item.company)
    #     sql += ",market_type=" + str(convertMarketType(code_item.market_type))
    #     sql += " ON DUPLICATE KEY UPDATE "
    #     sql += "last_update=" + getQuote(getToday())
    #     sql += ",code=" + getQuote(code_item.code)
    #     sql += ",full_code=" + getQuote(code_item.full_code)
    #     sql += ",company=" + getQuote(code_item.company)
    #     sql += ",market_type=" + str(convertMarketType(code_item.market_type))

    def generateCodeItemSQL(self, code_item):
        sql = "insert into codes(last_update, code, full_code, company, market_type) "
        sql += "values("
        sql += getQuote(getToday())
        sql += "," + getQuote(code_item.code)
        sql += "," + getQuote(code_item.full_code)
        sql += "," + getQuote(code_item.company)
        sql += "," + str(convertMarketType(code_item.market_type))
        sql += ")"
        print(sql)
        return sql

    def updatePriceToDB(self, code, df):
        for row_index in range(df.shape[0]):
            sql = self.generatePriceItemSQL(code, df, row_index)
            self.dbhandler.execSql(sql)

    # def generatePriceItemSQL(self, code, df, row_index):
    #     sql = "insert into prices set "
    #     sql += "last_update='%s'" % (getToday())
    #     sql += ",code='%s'" % (code)
    #     sql += ",price_date='%s'" % (pd.to_datetime(df.loc[row_index, 'Date']).isoformat())
    #     sql += ",price_open=%s" % (df.loc[row_index, 'Open'])
    #     sql += ",price_high=%s" % (df.loc[row_index, 'High'])
    #     sql += ",price_low=%s" % (df.loc[row_index, 'Low'])
    #     sql += ",price_close=%s" % (df.loc[row_index, 'Close'])
    #     sql += ",price_adj_close=%s" % (df.loc[row_index, 'Adj Close'])
    #     sql += ",volume=%s" % (df.loc[row_index, 'Volume'])
    #
    #     sql += " ON DUPLICATE KEY UPDATE "
    #
    #     sql += "last_update='%s'" % (getToday())
    #     sql += ",code='%s'" % (code)
    #     sql += ",price_date='%s'" % (pd.to_datetime(df.loc[row_index, 'Date']).isoformat())
    #     sql += ",price_open=%s" % (df.loc[row_index, 'Open'])
    #     sql += ",price_high=%s" % (df.loc[row_index, 'High'])
    #     sql += ",price_low=%s" % (df.loc[row_index, 'Low'])
    #     sql += ",price_close=%s" % (df.loc[row_index, 'Close'])
    #     sql += ",price_adj_close=%s" % (df.loc[row_index, 'Adj Close'])
    #     sql += ",volume=%s" % (df.loc[row_index, 'Volume'])

    def generatePriceItemSQL(self, code, df, row_index):
        sql = "insert into prices(last_update, price_date, code, price_open, price_close, price_high, price_low, price_adj_close, price_volume) "
        sql += "values(" + "'%s'" % (getToday())
        sql += "," + "%s" % pd.to_datetime(df.loc[row_index, 'Date']).strftime('%Y%m%d')
        sql += "," + "'%s'" % (code)
        sql += "," + "%s" % (df.loc[row_index, 'Open'])
        sql += "," + "%s" % (df.loc[row_index, 'Close'])
        sql += "," + "%s" % (df.loc[row_index, 'High'])
        sql += "," + "%s" % (df.loc[row_index, 'Low'])
        sql += "," + "%s" % (df.loc[row_index, 'Adj Close'])
        sql += "," + "%s" % (df.loc[row_index, 'Volume'])
        sql += ")"
        print(sql)
        return sql