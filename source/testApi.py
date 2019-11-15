# -*- coding: utf-8 -*-
from __future__ import division

import win32com.client as winAPI
import datetime
import win32com.client
import pythoncom
import os, sys, inspect
import pathlib
from time import sleep
from pandas import DataFrame, Series, Panel
import pandas as pd
import numpy as np
from operator import itemgetter

from source.util.StockManager import stockManager

SERVER_PORT = 20001
SHOW_CERTIFICATE_ERROR_DIALOG = False
REPEATED_DATA_QUERY = 1
TRANSACTION_REQUEST_EXCESS = -21
TODAY = datetime.datetime.now().strftime('%Y%m%d')

from util.StockManager import *

STAND_BY = 0
RECEIVED = 1

id = "phjwithy"
password = "phj1629"
certificate_password = "s20036402!"


class XASessionEvents:
    login_state = STAND_BY

    def OnLogin(self, code, msg):
        XASessionEvents.login_state = RECEIVED
        print(msg)
        if code == "0000":
            print("로그인 성공")
            XASessionEvents.login_state = 1
        else:
            print("로그인 실패")

    def OnDisconnect(self, code, msg):
        pass


class XAQueryEvents:
    상태 = False

    def OnReceiveData(self, szTrCode):
        XAQueryEvents.상태 = True

    def OnReceiveMessage(self, systemError, messageCode, message):
        if message != "조회완료":
            print("ERROR - OnReceiveMessage : ", systemError, messageCode, message)


class Trade():
    def __init__(self, debug):
        if debug:
            return
        print('init')

        self.instXASession = winAPI.DispatchWithEvents("XA_Session.XASession", XASessionEvents)
        if self.instXASession.IsConnected() is True:
            self.instXASession.DisconnectServer()

        # demo.ebestsec.co.kr => 모의투자
        # hts.ebestsec.co.kr => 실투자
        self.instXASession.ConnectServer("hts.ebestsec.co.kr", SERVER_PORT)
        self.instXASession.Login(id, password, certificate_password, SERVER_PORT, SHOW_CERTIFICATE_ERROR_DIALOG)

        while XASessionEvents.login_state is STAND_BY:
            pythoncom.PumpWaitingMessages()
        XASessionEvents.login_state = STAND_BY

    def check_realTime_stock(self):
        print('check_realTime_stock')

        today = datetime.date.today()
        getListTime = datetime.datetime(today.year, today.month, today.day, 8, 58, 0)
        startTime = datetime.datetime(today.year, today.month, today.day, 8, 58, 0)
        endTime = datetime.datetime(today.year, today.month, today.day, 15, 30, 0)
        today_list = []
        total_profit = 0
        while True:
            if len(today_list) == 0 and datetime.datetime.now() > getListTime:
                today_list = self.t1488(field=1)
                print(today_list)

            if datetime.datetime.now() < startTime:
                print('Before[%s]' % (datetime.datetime.now()))
                sleep(5)
                continue

            if datetime.datetime.now() > endTime:
                break

            log_folder = ('log/%s' % (TODAY))
            if not os.path.exists(log_folder):
                pathlib.Path(log_folder).mkdir(parents=True, exist_ok=True)

            for stock in today_list:
                sleep(3)
                df0, df = self.t1302(단축코드=stock['code'], 작업구분='1', 시간='1', 건수='1')
                if df is None:
                    print('Skip:[%s]' % (stock['code']))
                    continue

                df.to_csv('log/%s/t1302_%s_%s.csv' % (TODAY, TODAY, stock['code']), mode='a', index=False, header=False)

                stockManager.register(stock['code'], df)
                trade = stockManager.get_stock_code(stock['code']).is_trade(debug=False)
                if trade == 'buy':
                    total_profit += stockManager.get_stock_code(stock['code']).test_profit()
                    print('BUY [%s][%s][%s] profit[%s]' % (stock['code'], df['시간'][0], df['종가'][0], total_profit))
                elif trade == 'sell_success':
                    total_profit += stockManager.get_stock_code(stock['code']).test_profit()
                    print('SELL SUCCESS [%s][%s][%s] profit[%s]' % (stock['code'], df['시간'][0], df['종가'][0], total_profit))
                elif trade == 'sell_failed':
                    total_profit += stockManager.get_stock_code(stock['code']).test_profit()
                    print('SELL FAILED [%s][%s][%s] profit[%s]' % (stock['code'], df['시간'][0], df['종가'][0], total_profit))

    def t1488(self, field=1, day=0):
        sleep(1)
        inXAQuery = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)

        pathname = os.path.dirname(sys.argv[0])
        RESDIR = os.path.abspath(pathname)
        MYNAME = inspect.currentframe().f_code.co_name
        RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)

        inXAQuery.LoadFromResFile(RESFILE)
        inXAQuery.SetFieldData('t1488InBlock', 'gubun', 0, field)
        inXAQuery.Request(0)

        while XAQueryEvents.상태 == False:
            pythoncom.PumpWaitingMessages()
        XAQueryEvents.상태 = False

        nCount = inXAQuery.GetBlockCount('t1488OutBlock1')
        result = []
        resultList = []
        for i in range(nCount):
            code = inXAQuery.GetFieldData('t1488OutBlock1', 'shcode', i)
            price = int(inXAQuery.GetFieldData('t1488OutBlock1', 'price', i))
            volume = int(inXAQuery.GetFieldData('t1488OutBlock1', 'volume', i))
            jnilvolume = int(inXAQuery.GetFieldData('t1488OutBlock1', 'jnilvolume', i))
            stock = {}
            stock['code'] = code
            stock['price'] = price
            stock['volume'] = volume
            stock['jnilvolume'] = jnilvolume
            stock['priceVolume'] = price * volume
            resultList.append(stock)
            print('today list - code[%s] [%s][%s] price[%s] volume[%s] jnilvolume[%s] ' % (
            code, price * volume / 100000000, price * jnilvolume / 100000000, price, volume, jnilvolume))
            result.append(code)

        retList = sorted(resultList, key=itemgetter('priceVolume'), reverse=True)
        for d in retList:
            print(d)

        return retList[0:10]

    def t1302(self, 단축코드='', 작업구분='1', 시간='1', 건수='1'):
        '''
        주식분별주가조회
        '''
        query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
        pathname = os.path.dirname(sys.argv[0])
        RESDIR = os.path.abspath(pathname)

        MYNAME = inspect.currentframe().f_code.co_name
        INBLOCK = "%sInBlock" % MYNAME
        OUTBLOCK = "%sOutBlock" % MYNAME
        OUTBLOCK1 = "%sOutBlock1" % MYNAME
        RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)

        query.LoadFromResFile(RESFILE)
        query.SetFieldData(INBLOCK, "shcode", 0, 단축코드)
        query.SetFieldData(INBLOCK, "gubun", 0, 작업구분)
        query.SetFieldData(INBLOCK, "time", 0, 시간)
        query.SetFieldData(INBLOCK, "cnt", 0, 건수)
        query.Request(0)

        while XAQueryEvents.상태 == False:
            pythoncom.PumpWaitingMessages()

        XAQueryEvents.상태 = False

        result = []
        nCount = query.GetBlockCount(OUTBLOCK)
        if nCount == 0:
            return (None, None)

        for i in range(nCount):
            시간CTS = query.GetFieldData(OUTBLOCK, "cts_time", i).strip()

            lst = [시간CTS]
            result.append(lst)

        df = DataFrame(data=result, columns=['시간CTS'])

        result = []
        nCount = query.GetBlockCount(OUTBLOCK1)

        for i in range(nCount):
            시간 = query.GetFieldData(OUTBLOCK1, "chetime", i).strip()
            종가 = int(query.GetFieldData(OUTBLOCK1, "close", i).strip())
            전일대비구분 = query.GetFieldData(OUTBLOCK1, "sign", i).strip()
            전일대비 = int(query.GetFieldData(OUTBLOCK1, "change", i).strip())
            등락율 = float(query.GetFieldData(OUTBLOCK1, "diff", i).strip())
            체결강도 = float(query.GetFieldData(OUTBLOCK1, "chdegree", i).strip())
            매도체결수량 = int(query.GetFieldData(OUTBLOCK1, "mdvolume", i).strip())
            매수체결수량 = int(query.GetFieldData(OUTBLOCK1, "msvolume", i).strip())
            순매수체결량 = int(query.GetFieldData(OUTBLOCK1, "revolume", i).strip())
            매도체결건수 = int(query.GetFieldData(OUTBLOCK1, "mdchecnt", i).strip())
            매수체결건수 = int(query.GetFieldData(OUTBLOCK1, "mschecnt", i).strip())
            순체결건수 = int(query.GetFieldData(OUTBLOCK1, "rechecnt", i).strip())
            거래량 = int(query.GetFieldData(OUTBLOCK1, "volume", i).strip())
            시가 = int(query.GetFieldData(OUTBLOCK1, "open", i).strip())
            고가 = int(query.GetFieldData(OUTBLOCK1, "high", i).strip())
            저가 = int(query.GetFieldData(OUTBLOCK1, "low", i).strip())
            체결량 = int(query.GetFieldData(OUTBLOCK1, "cvolume", i).strip())
            매도체결건수시간 = int(query.GetFieldData(OUTBLOCK1, "mdchecnttm", i).strip())
            매수체결건수시간 = int(query.GetFieldData(OUTBLOCK1, "mschecnttm", i).strip())
            매도잔량 = int(query.GetFieldData(OUTBLOCK1, "totofferrem", i).strip())
            매수잔량 = int(query.GetFieldData(OUTBLOCK1, "totbidrem", i).strip())
            시간별매도체결량 = int(query.GetFieldData(OUTBLOCK1, "mdvolumetm", i).strip())
            시간별매수체결량 = int(query.GetFieldData(OUTBLOCK1, "msvolumetm", i).strip())

            lst = [시간, 단축코드, 종가, 전일대비구분, 전일대비, 등락율, 체결강도, 매도체결수량, 매수체결수량, 순매수체결량, 매도체결건수, 매수체결건수, 순체결건수, 거래량, 시가, 고가,
                   저가, 체결량,
                   매도체결건수시간, 매수체결건수시간, 매도잔량, 매수잔량, 시간별매도체결량, 시간별매수체결량]
            result.append(lst)

        df1 = DataFrame(data=result,
                        columns=['시간', '단축코드', '종가', '전일대비구분', '전일대비', '등락율', '체결강도', '매도체결수량', '매수체결수량', '순매수체결량',
                                 '매도체결건수', '매수체결건수', '순체결건수',
                                 '거래량', '시가', '고가', '저가', '체결량',
                                 '매도체결건수시간', '매수체결건수시간', '매도잔량', '매수잔량', '시간별매도체결량', '시간별매수체결량'])

        return (df, df1)

    def all_file_test(self):
        total_profit = 0
        folders = os.listdir('log')
        for folder in folders:
            files = os.listdir('log/%s' % (folder))
            for file in files:
                df = pd.read_csv('log/%s/%s' % (folder, file),
                                 names=['시간', '단축코드', '종가', '전일대비구분', '전일대비', '등락율', '체결강도', '매도체결수량', '매수체결수량',
                                        '순매수체결량',
                                        '매도체결건수',
                                        '매수체결건수', '순체결건수', '거래량', '시가', '고가', '저가', '체결량', '매도체결건수시간', '매수체결건수시간',
                                        '매도잔량',
                                        '매수잔량', '시간별매도체결량', '시간별매수체결량'])
                for i in df.index:
                    code = df['단축코드'][i]
                    stockManager.register(code, df.iloc[i])
                    trade = stockManager.get_stock_code(code).is_trade(debug=False)
                    if trade == 'buy':
                        print('BUY [%s][%s][%s]' % (code, df['시간'][i], df['종가'][i]))
                    elif trade == 'sell_success':
                        print('SELL SUCCESS [%s][%s][%s]' % (code, df['시간'][i], df['종가'][i]))
                    elif trade == 'sell_failed':
                        print('SELL FAILED [%s][%s][%s]' % (code, df['시간'][i], df['종가'][i]))

                total_profit += stockManager.get_stock_code(code).test_profit()
                # stockManager.get_stock_code(code).show_graph()
                print('TOTAL - Profit[%s][%s][%s] ' % (folder, file, total_profit))

    def file_test(self):
        TODAY = '20191115'
        log_folder = ('log/%s' % (TODAY))
        if not os.path.exists(log_folder):
            return

        total_profit = 0
        files = os.listdir(log_folder)

        for file in files:
            df = pd.read_csv('log/%s/%s' % (TODAY, file),
                             names=['시간', '단축코드', '종가', '전일대비구분', '전일대비', '등락율', '체결강도', '매도체결수량', '매수체결수량', '순매수체결량',
                                    '매도체결건수',
                                    '매수체결건수', '순체결건수', '거래량', '시가', '고가', '저가', '체결량', '매도체결건수시간', '매수체결건수시간', '매도잔량',
                                    '매수잔량', '시간별매도체결량', '시간별매수체결량'])
            for i in df.index:
                code = df['단축코드'][i]
                stockManager.register(code, df.iloc[i])
                trade = stockManager.get_stock_code(code).is_trade(debug=True)
                if trade == 'buy':
                    print('BUY [%s][%s][%s]' % (code, df['시간'][i], df['종가'][i]))
                elif trade == 'sell_success':
                    print('SELL SUCCESS [%s][%s][%s]' % (code, df['시간'][i], df['종가'][i]))
                elif trade == 'sell_failed':
                    print('SELL FAILED [%s][%s][%s]' % (code, df['시간'][i], df['종가'][i]))

            total_profit += stockManager.get_stock_code(code).test_profit()
            # stockManager.get_stock_code(code).show_graph()
            print('TOTAL - Profit[%s] ' % (total_profit))


if __name__ == "__main__":
    debug_mode = True
    Trade = Trade(debug=debug_mode)
    if debug_mode:
        # Trade.all_file_test()
        Trade.file_test()
    else:
        Trade.check_realTime_stock()
