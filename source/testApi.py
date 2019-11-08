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

SERVER_PORT = 20001
SHOW_CERTIFICATE_ERROR_DIALOG = False
REPEATED_DATA_QUERY = 1
TRANSACTION_REQUEST_EXCESS = -21
TODAY = datetime.datetime.now().strftime('%Y%m%d')

from util.StockManager import *

STAND_BY = 0
RECEIVED = 1

id = ""
password = ""
certificate_password = "!"


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
    query_state = STAND_BY

    def OnReceiveData(self, code):
        XAQueryEvents.query_state = RECEIVED

    def OnReceiveMessage(self, error, nMessageCode, szMessage):
        print(szMessage)


class XAQueryEvents:
    상태 = False

    def OnReceiveData(self, szTrCode):
        print("OnReceiveData : %s" % szTrCode)
        XAQueryEvents.상태 = True

    def OnReceiveMessage(self, systemError, messageCode, message):
        print("OnReceiveMessage : ", systemError, messageCode, message)


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

    def check_realTime_stoks(self):
        print('check_realTime_stoks')

        today = datetime.date.today()
        today_list = []
        getListTime = datetime.datetime(today.year, today.month, today.day, 8, 58, 0)
        startTime = datetime.datetime(today.year, today.month, today.day, 9, 0, 0)
        endTime = datetime.datetime(today.year, today.month, today.day, 15, 30, 0)

        while True:
            if datetime.datetime.now() < startTime:
                print('Before[%s]' % (datetime.datetime.now()))
                sleep(5)  # 10 -> 1분
                continue

            if len(today_list) != 0 and datetime.datetime.now() < getListTime:
                today_list = self.get_top_trade_volume(field=1)
                print(today_list)

            if datetime.datetime.now() > endTime:
                break

            log_folder = ('log/%s' % (TODAY))
            if not os.path.exists(log_folder):
                pathlib.Path(log_folder).mkdir(parents=True, exist_ok=True)

            for code in today_list:
                sleep(3)
                df0, df = self.t1302(단축코드=code, 작업구분='1', 시간='1', 건수='1')
                if df is None:
                    print('Skip:[%s]' % (code))
                    continue
                stockManager.register(code, df)
                df.to_csv('log/%s/t1302_%s_%s.csv' % (TODAY, TODAY, code), mode='a', index=False, header=False)

    def get_top_trade_volume(self, field=1, day=0):
        sleep(1)
        inXAQuery = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
        inXAQuery.LoadFromResFile("C:\\eBest\\xingAPI\\Res\\t1488.res")
        inXAQuery.SetFieldData('t1488InBlock', 'gubun', 0, field)
        # inXAQuery.SetFieldData('t1488InBlock', 'jnilgubun', 0, day)
        inXAQuery.Request(0)

        while XAQueryEvents.상태 == False:
            pythoncom.PumpWaitingMessages()

        nCount = inXAQuery.GetBlockCount('t1488OutBlock1')
        result = []
        for i in range(nCount):
            code = inXAQuery.GetFieldData('t1488OutBlock1', 'shcode', i)
            result.append(code)

        XAQueryEvents.상태 = False
        return result

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

        result = []
        nCount = query.GetBlockCount(OUTBLOCK)
        if nCount == 0:
            XAQueryEvents.상태 = False
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
                        columns=[시간, 단축코드, 종가, 전일대비구분, 전일대비, 등락율, 체결강도, 매도체결수량, 매수체결수량, 순매수체결량, 매도체결건수, 매수체결건수, 순체결건수,
                                 거래량, 시가, 고가, 저가, 체결량,
                                 매도체결건수시간, 매수체결건수시간, 매도잔량, 매수잔량, 시간별매도체결량, 시간별매수체결량])

        XAQueryEvents.상태 = False

        return (df, df1)

    def file_test2(self):
        TODAY = '20191108'
        log_folder = ('log/%s' % (TODAY))
        if not os.path.exists(log_folder):
            return
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
                # stockManager.get_stock_code(code).is_buy_price()
            # stockManager.get_stock_code(code).is_buy_price()
            stockManager.all_print_stock()


    def file_test(self):
        TODAY = '20191106'
        log_folder = ('log/%s' % (TODAY))
        if not os.path.exists(log_folder):
            return
        files = os.listdir(log_folder)

        for file in files:
            df = pd.read_csv('log/%s/%s' % (TODAY, file),
                             names=['시간', '단축코드', '종가', '전일대비구분', '전일대비', '등락율', '체결강도', '매도체결수량', '매수체결수량', '순매수체결량',
                                    '매도체결건수',
                                    '매수체결건수', '순체결건수', '거래량', '시가', '고가', '저가', '체결량', '매도체결건수시간', '매수체결건수시간', '매도잔량',
                                    '매수잔량', '시간별매도체결량', '시간별매수체결량'])
            volume_list = []
            buy_list = []
            diff_buy_list = []
            code = ''

            test_buy_price_list = []
            test_buy_index_list = []

            is_buy = False
            test_success_sell_price_list = []
            test_success_sell_index_list = []

            test_fail_sell_price_list = []
            test_fail_sell_index_list = []

            buy_limit_list = []
            max_volume = 0

            real_buy_percent = 50

            for i in df.index:
                if 0 == i:
                    volume_list.append(0)
                    buy_list.append(0)
                    diff_buy_list.append(0)
                    buy_limit_list.append(0)
                    code = df['단축코드'][i]
                    continue

                diff_time = int(df['시간'][i]) - int(df['시간'][i - 1])
                diff_volume = int(df['거래량'][i]) - int(df['거래량'][i - 1])
                diff_buy_pre_limit = int(df['매수잔량'][i - 1]) - int(df['매도잔량'][i - 1])
                diff_buy_limit = int(df['매수잔량'][i]) - int(df['매도잔량'][i])
                diff_diff_buy = diff_buy_limit - diff_buy_pre_limit

                volume_list.append(diff_volume)
                buy_list.append(diff_buy_limit)
                diff_buy_list.append(diff_diff_buy)

                if diff_volume > max_volume:
                    max_volume = diff_volume;

                buy_limit_price = (diff_buy_limit * diff_volume) / 100000000
                buy_limit_list.append(buy_limit_price)

                print('[%s] [%s] [%s] [%s] [%s] [%s]' % (df['시간'][i], df['등락율'][i], diff_buy_limit, diff_diff_buy, diff_volume, diff_time))

                if diff_buy_limit > 0 and diff_diff_buy > 0 and diff_volume >= max_volume / 2 and df['등락율'][i] > \
                        df['등락율'][i - 1] and buy_limit_price > 2 and df['등락율'][i] > 0 and diff_buy_list[i] > \
                        diff_buy_list[i - 1]:
                    print('============== Buy')
                    test_buy_index_list.append([i])
                    test_buy_price_list.append(df['등락율'][i])
                    real_buy_percent = float(df['등락율'][i])
                    is_buy = True

                if is_buy is True and float(df['등락율'][i]) > real_buy_percent + 1.0:
                    print('============== Sell')
                    test_success_sell_index_list.append([i])
                    test_success_sell_price_list.append(df['등락율'][i])
                    real_buy_percent = 50
                    is_buy = False

                if is_buy is True and float(df['등락율'][i]) < real_buy_percent - 1.0:
                    print('============== Failed Sell')
                    test_fail_sell_index_list.append([i])
                    test_fail_sell_price_list.append(df['등락율'][i])
                    real_buy_percent = 50
                    is_buy = False

            fig, axs = plt.subplots(5)

            ax = axs[0]
            ax.plot(df['등락율'])
            ax.scatter(test_buy_index_list, test_buy_price_list, c='r')
            ax.scatter(test_success_sell_index_list, test_success_sell_price_list, c='b')
            ax.scatter(test_fail_sell_index_list, test_fail_sell_price_list, c='y')
            ax.grid(True)
            plt.title(code)

            ax = axs[1]
            ax.plot(volume_list)
            ax.grid(True)

            ax = axs[2]
            ax.plot(buy_list)
            ax.grid(True)

            ax = axs[3]
            ax.plot(diff_buy_list)
            ax.grid(True)

            ax = axs[4]
            ax.plot(buy_limit_list)
            ax.grid(True)

            plt.show()


if __name__ == "__main__":
    debug_mode = True
    Trade = Trade(debug=debug_mode)
    if debug_mode:
        # Trade.file_test()
        Trade.file_test2()
    else:
        Trade.check_realTime_stoks()
