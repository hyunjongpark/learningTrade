# -*- coding: utf-8 -*-
from __future__ import division
import os, sys
import sqlite3
# import pymysql


from data_model import *


class DataHandler():
    def __init__(self):
        # self.conn = pymysql.connect('221.147.129.137', 'james', 'mhrinc01', 'stock', port=63306, charset='utf8');
        # self.conn = pymysql.connect('localhost', 'root', 'mhrinc01', 'race', port=63306, charset='utf8');

        self.conn = sqlite3.connect('test.db');
        # cursor = self.conn.cursor()
        self.createTable()

    # cursor.execute("pragma journal_mode = MEMORY;")
    # cursor.execute("pragma journal_mode = WAL;")

    def createTable(self):
        sql = "Create Table if not exists codes(id INTEGER PRIMARY KEY AUTOINCREMENT, last_update varchar(8), code varchar(200), full_code varchar(200), market_type integer, company varchar(200))"
        self.conn.execute(sql)

        sql = "Create Table if not exists prices(id INTEGER PRIMARY KEY AUTOINCREMENT, last_update varchar(8), price_date datetime default current_timestamp, code varchar(200), price_open integer, price_close integer, price_high integer, price_low integer, price_adj_close integer, price_volume integer)"
        self.conn.execute(sql)
        self.conn.commit();

    def beginTrans(self):
        pass
        # self.conn.autocommit(False)

    def endTrans(self):
        try:
            self.conn.commit()
            # self.conn.autocommit(True)
        except:
            print("Fatal Error in commit !!!")
            self.conn.rollback()

    def openSql(self, sql):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)

            return cursor
        # gCursor.commit()
        except:
            print ("Unexpected error in ExecSQL:", sys.args[0])
            raise

    def execSql(self, sql, db_commit=True):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            if db_commit:
                self.conn.commit()
            # cursor.close()
            return cursor

        except Exception as error:
            print(">>> Unexpected error in ExecSQL: ", error)
            print("--- %s ---" % (sql))
            # raise


            # print "dbhandler.py : cwd=%s" % (os.getcwd())
            # data_handler = MyDataHandler()
