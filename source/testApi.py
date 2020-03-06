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
from source.common import get_buy_count, get_percent, get_percent_price

from source.util.StockManager import stockManager
from source.util.StockManagerETF import StockManagerETF

SERVER_PORT = 20001
SHOW_CERTIFICATE_ERROR_DIALOG = False
REPEATED_DATA_QUERY = 1
TRANSACTION_REQUEST_EXCESS = -21
TODAY = datetime.datetime.now().strftime('%Y%m%d')
today_time = datetime.date.today()

# from util.StockManager import *
# from util.StockManagerETF import *

STAND_BY = 0
RECEIVED = 1

id = "phjwithy"
password = "phj1629"
tradePW = "1629"
certificate_password = "s20036402!"
money = 50000
REAL_TRADE = True


class TodayTradeStock:
    def __init__(self, code, count, is_plus_sell):
        self.code = code
        self.buy_count = count
        self.already_plus_sell = is_plus_sell
        self.trade_number = 0


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
        if int(messageCode) != 0:
            print("OnReceiveMessage : ", systemError, messageCode, message)


class Trade:
    today_trade_stocks = dict()

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

        self.계좌 = []
        계좌수 = self.instXASession.GetAccountListCount()

        for i in range(계좌수):
            self.계좌.append(self.instXASession.GetAccountList(i))

        print(self.계좌)

        df0, df = self.t0424(계좌번호=self.계좌[0], 비밀번호=password, 단가구분='1', 체결구분='0', 단일가구분='0', 제비용포함여부='1', CTS_종목번호='')
        print(df0)
        print(df)

        self.buy_stock_list = []

    def handle_buy(self, code, price):
        if not REAL_TRADE:
            return
        매매구분 = 2  # 매수
        trade_count = int(get_buy_count(money, price))
        trade_price = get_percent_price(price, 4)
        df0, df = self.CSPAT00600(계좌번호=self.계좌[0], 입력비밀번호=tradePW, 종목번호=code, 주문수량=trade_count, 매매구분=매매구분,
                                  가격=trade_price, 가격구분="00")
        print(df0)
        print(df)

        self.today_trade_stocks[code] = TodayTradeStock(code, trade_count, False)

    def handle_sell(self, code):
        if not REAL_TRADE:
            return
        매매구분 = 1  # 매도
        trade_count = self.today_trade_stocks.get(code).buy_count
        df0, df = self.CSPAT00600(계좌번호=self.계좌[0], 입력비밀번호=tradePW, 종목번호=code, 주문수량=trade_count, 매매구분=매매구분, 가격=0,
                                  가격구분="03")
        print(df0)
        print(df)

    def handle_sell_percent(self, code, buy_price, percent):
        if not REAL_TRADE:
            return
        매매구분 = 1  # 매도
        trade_count = self.today_trade_stocks.get(code).buy_count
        sell_price = get_percent_price(buy_price, percent)
        df0, df = self.CSPAT00600(계좌번호=self.계좌[0], 입력비밀번호=tradePW, 종목번호=code, 주문수량=trade_count, 매매구분=매매구분,
                                  가격=sell_price, 가격구분="00")
        print(df0)
        print(df)
        back_stock = self.today_trade_stocks.get(code)
        back_stock.already_plus_sell = True
        back_stock.trade_number = int(df['주문번호'][0])

    def handle_trade_condition_profit_by_bank(self):
        df0, df = self.t0424(계좌번호=self.계좌[0], 비밀번호=password, 단가구분='1', 체결구분='0', 단일가구분='0', 제비용포함여부='1', CTS_종목번호='')
        for i in df.index:
            current_profit = int(df['수익율'][i])
            if current_profit == 0 or current_profit == -100:
                continue

            back_stock = self.today_trade_stocks.get(df['종목번호'][i])
            if back_stock.already_plus_sell is False:
                self.handle_sell_percent(df['종목번호'][i], df['평균단가'][i], 1)
            if back_stock.already_plus_sell is True and current_profit < -2:
                self.CSPAT00800(원주문번호=back_stock.trade_number, 계좌번호=self.계좌[0], 입력비밀번호=tradePW, 종목번호=back_stock.code,
                                주문수량=back_stock.buy_count)
                self.handle_sell(df['종목번호'][i])

    def handle_trade_all_end_time(self):
        df0, df = self.t0424(계좌번호=self.계좌[0], 비밀번호=password, 단가구분='1', 체결구분='0', 단일가구분='0', 제비용포함여부='1', CTS_종목번호='')
        for i in df.index:
            self.buy_stock_list.con
            current_profit = int(df['수익율'][i])
            if current_profit == 0 or current_profit == -100:
                continue
            self.handle_sell(df['종목번호'][i])

    def check_realTime_ETF_stock(self):

        today_list = self.t8436(gubun=1)
        resultList = []
        for stock in today_list:
            sleep(0.1)
            df, sortList = self.t1102(stock[0])
            resultList.append(sortList)

        retList = sorted(resultList, key=itemgetter('거래대금'), reverse=True)
        for d in retList:
            print(d)
        filter_list = retList[0:10]

        log_folder = ('log/%s' % TODAY)
        if not os.path.exists(log_folder):
            pathlib.Path(log_folder).mkdir(parents=True, exist_ok=True)

        while True:
            for stock in filter_list:
                code = stock['코드']
                sleep(0.1)
                # code = '122630'
                df, sortList = self.t1102(code)
                stockManager.register(code, df)
                trade, log = stockManager.get_stock_code(code).is_trade(debug=True)

                df.to_csv('log/%s/t1102_%s_%s.csv' % (TODAY, TODAY, code), mode='a', index=False, header=False)

                if trade == 'buy':
                    # self.handle_buy(code, int(df['종가'][0]))
                    print('BUY [%s][%s][%s] profit[%s]' % (
                        code, df['시간'][0], df['종가'][0], stockManager.get_stock_code(code).test_profit()))
                elif trade == 'sell_success':
                    # self.handle_sell(code)
                    print('SELL SUCCESS [%s][%s][%s] profit[%s]' % (
                        code, df['시간'][0], df['종가'][0], stockManager.get_stock_code(code).test_profit()))
                elif trade == 'sell_failed':
                    # self.handle_sell(code)
                    print('SELL FAILED [%s][%s][%s] profit[%s]' % (
                        code, df['시간'][0], df['종가'][0], stockManager.get_stock_code(code).test_profit()))

    def check_realTime_stock(self):
        print('check_realTime_stock')

        today = datetime.date.today()
        getListTime = datetime.datetime(today.year, today.month, today.day, 8, 59, 0)
        startTime = datetime.datetime(today.year, today.month, today.day, 9, 00, 0)
        logEndTime = datetime.datetime(today.year, today.month, today.day, 9, 10, 0)
        endTime = datetime.datetime(today.year, today.month, today.day, 15, 30, 0)
        lastTradeStartTime = datetime.datetime(today.year, today.month, today.day, 15, 25, 0)
        today_list = []

        log_folder = ('log/%s' % TODAY)
        if not os.path.exists(log_folder):
            pathlib.Path(log_folder).mkdir(parents=True, exist_ok=True)

        isRunLastTrade = False
        while True:
            ## 그날에 주식 종목 가져오기
            if len(today_list) == 0 and datetime.datetime.now() > getListTime:
                today_list = self.t1488(field=2)
                print(today_list)

            # if startTime < datetime.datetime.now() < logEndTime:
            #     self.t1488(field=1)
            #     self.t1488(field=2)

            ## 장 시작전까지 홀딩
            if datetime.datetime.now() < startTime:
                print('Before[%s]' % (datetime.datetime.now()))
                self.handle_trade_condition_profit_by_bank()
                sleep(5)
                continue

            ## 3시25분 안 팔린 주식 일괄 매도
            if lastTradeStartTime <= datetime.datetime.now() <= endTime and isRunLastTrade is False:
                self.handle_trade_all_end_time()
                isRunLastTrade = True

            ## 프로그램 종료
            if datetime.datetime.now() > endTime:
                total_profit = 0
                for stock in today_list:
                    code = stock['code']
                    profit = stockManager.get_stock_code(code).test_profit()
                    total_profit += profit;
                    print('Today [%s] profit[%s] total_profit[%s]' % (code, profit, total_profit))
                break

            ## 주식 종목들 매수/매도 체크
            for stock in today_list:
                sleep(1)
                self.handle_trade_condition_profit_by_bank()
                sleep(2)
                code = stock['code']
                df0, df = self.t1302(단축코드=code, 작업구분='2', 시간='1', 건수='1')
                if df is None:
                    print('Skip:[%s]' % code)
                    continue

                df.to_csv('log/%s/t1302_%s_%s.csv' % (TODAY, TODAY, code), mode='a', index=False, header=False)

                stockManager.register(code, df)
                trade, log = stockManager.get_stock_code(code).is_trade(debug=False)
                if trade == 'buy':
                    self.handle_buy(code, int(df['종가'][0]))
                    print('BUY [%s][%s][%s] profit[%s]' % (
                        code, df['시간'][0], df['종가'][0], stockManager.get_stock_code(code).test_profit()))
                elif trade == 'sell_success':
                    self.handle_sell(code)
                    print('SELL SUCCESS [%s][%s][%s] profit[%s]' % (
                        code, df['시간'][0], df['종가'][0], stockManager.get_stock_code(code).test_profit()))
                elif trade == 'sell_failed':
                    self.handle_sell(code)
                    print('SELL FAILED [%s][%s][%s] profit[%s]' % (
                        code, df['시간'][0], df['종가'][0], stockManager.get_stock_code(code).test_profit()))

    def t1488(self, field=1, day=0):
        '''
              주식 종목 가져오기
        '''
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
        df = pd.DataFrame.from_dict(retList)
        df.to_csv("daily_stock_list/%s_%s.txt" % today_time, field, header=True, index=True, mode='a')

        return retList[0:5]

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

    def t0424(self, 계좌번호='', 비밀번호='', 단가구분='1', 체결구분='0', 단일가구분='0', 제비용포함여부='1', CTS_종목번호=''):
        '''
        주식잔고2
        '''
        pathname = os.path.dirname(sys.argv[0])
        resdir = os.path.abspath(pathname)

        query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)

        MYNAME = inspect.currentframe().f_code.co_name
        INBLOCK = "%sInBlock" % MYNAME
        INBLOCK1 = "%sInBlock1" % MYNAME
        OUTBLOCK = "%sOutBlock" % MYNAME
        OUTBLOCK1 = "%sOutBlock1" % MYNAME
        OUTBLOCK2 = "%sOutBlock2" % MYNAME
        RESFILE = "%s\\Res\\%s.res" % (resdir, MYNAME)

        # print(MYNAME, RESFILE)

        query.LoadFromResFile(RESFILE)
        query.SetFieldData(INBLOCK, "accno", 0, 계좌번호)
        query.SetFieldData(INBLOCK, "passwd", 0, 비밀번호)
        query.SetFieldData(INBLOCK, "prcgb", 0, 단가구분)
        query.SetFieldData(INBLOCK, "chegb", 0, 체결구분)
        query.SetFieldData(INBLOCK, "dangb", 0, 단일가구분)
        query.SetFieldData(INBLOCK, "charge", 0, 제비용포함여부)
        query.SetFieldData(INBLOCK, "cts_expcode", 0, CTS_종목번호)
        query.Request(0)

        while XAQueryEvents.상태 == False:
            pythoncom.PumpWaitingMessages()

        result = []
        nCount = query.GetBlockCount(OUTBLOCK)
        for i in range(nCount):
            추정순자산 = int(query.GetFieldData(OUTBLOCK, "sunamt", i).strip())
            실현손익 = int(query.GetFieldData(OUTBLOCK, "dtsunik", i).strip())
            매입금액 = int(query.GetFieldData(OUTBLOCK, "mamt", i).strip())
            추정D2예수금 = int(query.GetFieldData(OUTBLOCK, "sunamt1", i).strip())
            CTS_종목번호 = query.GetFieldData(OUTBLOCK, "cts_expcode", i).strip()
            평가금액 = int(query.GetFieldData(OUTBLOCK, "tappamt", i).strip())
            평가손익 = int(query.GetFieldData(OUTBLOCK, "tdtsunik", i).strip())

            lst = [추정순자산, 실현손익, 매입금액, 추정D2예수금, CTS_종목번호, 평가금액, 평가손익]
            result.append(lst)

        columns = ['추정순자산', '실현손익', '매입금액', '추정D2예수금', 'CTS_종목번호', '평가금액', '평가손익']
        df = DataFrame(data=result, columns=columns)

        result = []
        nCount = query.GetBlockCount(OUTBLOCK1)
        for i in range(nCount):
            종목번호 = query.GetFieldData(OUTBLOCK1, "expcode", i).strip()
            잔고구분 = query.GetFieldData(OUTBLOCK1, "jangb", i).strip()
            잔고수량 = int(query.GetFieldData(OUTBLOCK1, "janqty", i).strip())
            매도가능수량 = int(query.GetFieldData(OUTBLOCK1, "mdposqt", i).strip())
            평균단가 = int(query.GetFieldData(OUTBLOCK1, "pamt", i).strip())
            매입금액 = int(query.GetFieldData(OUTBLOCK1, "mamt", i).strip())
            대출금액 = int(query.GetFieldData(OUTBLOCK1, "sinamt", i).strip())
            만기일자 = query.GetFieldData(OUTBLOCK1, "lastdt", i).strip()
            당일매수금액 = int(query.GetFieldData(OUTBLOCK1, "msat", i).strip())
            당일매수단가 = int(query.GetFieldData(OUTBLOCK1, "mpms", i).strip())
            당일매도금액 = int(query.GetFieldData(OUTBLOCK1, "mdat", i).strip())
            당일매도단가 = int(query.GetFieldData(OUTBLOCK1, "mpmd", i).strip())
            전일매수금액 = int(query.GetFieldData(OUTBLOCK1, "jsat", i).strip())
            전일매수단가 = int(query.GetFieldData(OUTBLOCK1, "jpms", i).strip())
            전일매도금액 = int(query.GetFieldData(OUTBLOCK1, "jdat", i).strip())
            전일매도단가 = int(query.GetFieldData(OUTBLOCK1, "jpmd", i).strip())
            처리순번 = int(query.GetFieldData(OUTBLOCK1, "sysprocseq", i).strip())
            대출일자 = query.GetFieldData(OUTBLOCK1, "loandt", i).strip()
            종목명 = query.GetFieldData(OUTBLOCK1, "hname", i).strip()
            시장구분 = query.GetFieldData(OUTBLOCK1, "marketgb", i).strip()
            종목구분 = query.GetFieldData(OUTBLOCK1, "jonggb", i).strip()
            보유비중 = float(query.GetFieldData(OUTBLOCK1, "janrt", i).strip())
            현재가 = int(query.GetFieldData(OUTBLOCK1, "price", i).strip())
            평가금액 = int(query.GetFieldData(OUTBLOCK1, "appamt", i).strip())
            평가손익 = int(query.GetFieldData(OUTBLOCK1, "dtsunik", i).strip())
            수익율 = float(query.GetFieldData(OUTBLOCK1, "sunikrt", i).strip())
            수수료 = int(query.GetFieldData(OUTBLOCK1, "fee", i).strip())
            제세금 = int(query.GetFieldData(OUTBLOCK1, "tax", i).strip())
            신용이자 = int(query.GetFieldData(OUTBLOCK1, "sininter", i).strip())

            lst = [종목번호, 잔고구분, 잔고수량, 매도가능수량, 평균단가, 매입금액, 대출금액, 만기일자, 당일매수금액,
                   당일매수단가, 당일매도금액, 당일매도단가, 전일매수금액, 전일매수단가, 전일매도금액, 전일매도단가,
                   처리순번, 대출일자, 종목명, 시장구분, 종목구분, 보유비중, 현재가, 평가금액, 평가손익, 수익율, 수수료, 제세금, 신용이자]
            result.append(lst)

        columns = ['종목번호', '잔고구분', '잔고수량', '매도가능수량', '평균단가', '매입금액', '대출금액', '만기일자', '당일매수금액', ' 당일매수단가', '당일매도금액',
                   '당일매도단가', '전일매수금액', '전일매수단가', '전일매도금액', '전일매도단가', ' 처리순번', '대출일자', '종목명', '시장구분', '종목구분', '보유비중',
                   '현재가', '평가금액', '평가손익', '수익율', '수수료', '제세금', '신용이자']
        df1 = DataFrame(data=result, columns=columns)

        XAQueryEvents.상태 = False
        return (df, df1)

    def CSPAT00600(self, 계좌번호, 입력비밀번호, 종목번호, 주문수량, 매매구분, 가격, 가격구분):
        '''
              주식 매도/매수 거래
        '''
        pathname = os.path.dirname(sys.argv[0])
        resdir = os.path.abspath(pathname)

        query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)

        MYNAME = inspect.currentframe().f_code.co_name
        INBLOCK = "%sInBlock" % MYNAME
        INBLOCK1 = "%sInBlock1" % MYNAME
        OUTBLOCK = "%sOutBlock" % MYNAME
        OUTBLOCK1 = "%sOutBlock1" % MYNAME
        OUTBLOCK2 = "%sOutBlock2" % MYNAME
        RESFILE = "%s\\Res\\%s.res" % (resdir, MYNAME)

        print(MYNAME, RESFILE)

        query.LoadFromResFile(RESFILE)
        query.SetFieldData(INBLOCK1, "AcntNo", 0, 계좌번호)
        query.SetFieldData(INBLOCK1, "InptPwd", 0, 입력비밀번호)
        query.SetFieldData(INBLOCK1, "IsuNo", 0, 종목번호)
        query.SetFieldData(INBLOCK1, "OrdQty", 0, 주문수량)
        query.SetFieldData(INBLOCK1, "OrdPrc", 0, 가격)  # 지정가일 경우 가격을, 시장가일 경우 0을 입력
        query.SetFieldData(INBLOCK1, "BnsTpCode", 0, 매매구분)  # 매도 1 매수 2
        query.SetFieldData(INBLOCK1, "OrdprcPtnCode", 0,
                           가격구분)  # 지정가 00, 시장가 03, 조건부지정가 05, 최유리지정가 06, 최우선지정가 07, 장개시전시간외 61, 시간외종가 81, 시간외단일가 82
        query.SetFieldData(INBLOCK1, "MgntrnCode", 0, "000")
        query.SetFieldData(INBLOCK1, "LoanDt", 0, "0")
        query.SetFieldData(INBLOCK1, "OrdCndiTpCode", 0, "0")
        query.Request(0)

        while XAQueryEvents.상태 == False:
            pythoncom.PumpWaitingMessages()

        result = []
        nCount = query.GetBlockCount(OUTBLOCK1)
        for i in range(nCount):
            레코드갯수 = int(query.GetFieldData(OUTBLOCK1, "RecCnt", i).strip())
            계좌번호 = query.GetFieldData(OUTBLOCK1, "AcntNo", i).strip()
            입력비밀번호 = query.GetFieldData(OUTBLOCK1, "InptPwd", i).strip()
            종목번호 = query.GetFieldData(OUTBLOCK1, "IsuNo", i).strip()
            주문수량 = int(query.GetFieldData(OUTBLOCK1, "OrdQty", i).strip())
            주문가 = query.GetFieldData(OUTBLOCK1, "OrdPrc", i).strip()
            매매구분 = query.GetFieldData(OUTBLOCK1, "BnsTpCode", i).strip()
            호가유형코드 = query.GetFieldData(OUTBLOCK1, "OrdprcPtnCode", i).strip()
            프로그램호가유형코드 = query.GetFieldData(OUTBLOCK1, "PrgmOrdprcPtnCode", i).strip()
            공매도가능여부 = query.GetFieldData(OUTBLOCK1, "StslAbleYn", i).strip()
            공매도호가구분 = query.GetFieldData(OUTBLOCK1, "StslOrdprcTpCode", i).strip()
            통신매체코드 = query.GetFieldData(OUTBLOCK1, "CommdaCode", i).strip()
            신용거래코드 = query.GetFieldData(OUTBLOCK1, "MgntrnCode", i).strip()
            대출일 = query.GetFieldData(OUTBLOCK1, "LoanDt", i).strip()
            회원번호 = query.GetFieldData(OUTBLOCK1, "MbrNo", i).strip()
            주문조건구분 = query.GetFieldData(OUTBLOCK1, "OrdCndiTpCode", i).strip()
            전략코드 = query.GetFieldData(OUTBLOCK1, "StrtgCode", i).strip()
            그룹ID = query.GetFieldData(OUTBLOCK1, "GrpId", i).strip()
            주문회차 = int(query.GetFieldData(OUTBLOCK1, "OrdSeqNo", i).strip())
            포트폴리오번호 = int(query.GetFieldData(OUTBLOCK1, "PtflNo", i).strip())
            바스켓번호 = int(query.GetFieldData(OUTBLOCK1, "BskNo", i).strip())
            트렌치번호 = int(query.GetFieldData(OUTBLOCK1, "TrchNo", i).strip())
            아이템번호 = int(query.GetFieldData(OUTBLOCK1, "ItemNo", i).strip())
            운용지시번호 = query.GetFieldData(OUTBLOCK1, "OpDrtnNo", i).strip()
            유동성공급자여부 = query.GetFieldData(OUTBLOCK1, "LpYn", i).strip()
            반대매매구분 = query.GetFieldData(OUTBLOCK1, "CvrgTpCode", i).strip()

            lst = [레코드갯수, 계좌번호, 입력비밀번호, 종목번호, 주문수량, 주문가, 매매구분, 호가유형코드, 프로그램호가유형코드, 공매도가능여부, 공매도호가구분, 통신매체코드, 신용거래코드,
                   대출일, 회원번호, 주문조건구분, 전략코드, 그룹ID, 주문회차, 포트폴리오번호, 바스켓번호, 트렌치번호, 아이템번호, 운용지시번호, 유동성공급자여부, 반대매매구분]
            result.append(lst)

        columns = ['레코드갯수', '계좌번호', '입력비밀번호', '종목번호', '주문수량', '주문가', '매매구분', '호가유형코드', '프로그램호가유형코드', '공매도가능여부',
                   '공매도호가구분', '통신매체코드', '신용거래코드', '대출일', '회원번호', '주문조건구분', '전략코드', '그룹ID', '주문회차', '포트폴리오번호', '바스켓번호',
                   '트렌치번호', '아이템번호', '운용지시번호', '유동성공급자여부', '반대매매구분']
        df = DataFrame(data=result, columns=columns)

        result = []
        nCount = query.GetBlockCount(OUTBLOCK2)
        for i in range(nCount):
            레코드갯수 = int(query.GetFieldData(OUTBLOCK2, "RecCnt", i).strip())
            주문번호 = int(query.GetFieldData(OUTBLOCK2, "OrdNo", i).strip())
            주문시각 = query.GetFieldData(OUTBLOCK2, "OrdTime", i).strip()
            주문시장코드 = query.GetFieldData(OUTBLOCK2, "OrdMktCode", i).strip()
            주문유형코드 = query.GetFieldData(OUTBLOCK2, "OrdPtnCode", i).strip()
            단축종목번호 = query.GetFieldData(OUTBLOCK2, "ShtnIsuNo", i).strip()
            관리사원번호 = query.GetFieldData(OUTBLOCK2, "MgempNo", i).strip()
            주문금액 = int(query.GetFieldData(OUTBLOCK2, "OrdAmt", i).strip())
            예비주문번호 = int(query.GetFieldData(OUTBLOCK2, "SpareOrdNo", i).strip())
            반대매매일련번호 = int(query.GetFieldData(OUTBLOCK2, "CvrgSeqno", i).strip())
            예약주문번호 = int(query.GetFieldData(OUTBLOCK2, "RsvOrdNo", i).strip())
            실물주문수량 = int(query.GetFieldData(OUTBLOCK2, "SpotOrdQty", i).strip())
            재사용주문수량 = int(query.GetFieldData(OUTBLOCK2, "RuseOrdQty", i).strip())
            현금주문금액 = int(query.GetFieldData(OUTBLOCK2, "MnyOrdAmt", i).strip())
            대용주문금액 = int(query.GetFieldData(OUTBLOCK2, "SubstOrdAmt", i).strip())
            재사용주문금액 = int(query.GetFieldData(OUTBLOCK2, "RuseOrdAmt", i).strip())
            계좌명 = query.GetFieldData(OUTBLOCK2, "AcntNm", i).strip()
            종목명 = query.GetFieldData(OUTBLOCK2, "IsuNm", i).strip()

            lst = [레코드갯수, 주문번호, 주문시각, 주문시장코드, 주문유형코드, 단축종목번호, 관리사원번호, 주문금액, 예비주문번호, 반대매매일련번호, 예약주문번호, 실물주문수량, 재사용주문수량,
                   현금주문금액, 대용주문금액, 재사용주문금액, 계좌명, 종목명]
            result.append(lst)

        columns = ['레코드갯수', '주문번호', '주문시각', '주문시장코드', '주문유형코드', '단축종목번호', '관리사원번호', '주문금액', '예비주문번호', '반대매매일련번호',
                   '예약주문번호', '실물주문수량', '재사용주문수량', '현금주문금액', '대용주문금액', '재사용주문금액', '계좌명', '종목명']
        df1 = DataFrame(data=result, columns=columns)

        XAQueryEvents.상태 = False
        return (df, df1)

    def CSPAT00800(self, 원주문번호, 계좌번호, 입력비밀번호, 종목번호, 주문수량):
        pathname = os.path.dirname(sys.argv[0])
        resdir = os.path.abspath(pathname)

        query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)

        MYNAME = inspect.currentframe().f_code.co_name
        INBLOCK = "%sInBlock" % MYNAME
        INBLOCK1 = "%sInBlock1" % MYNAME
        OUTBLOCK = "%sOutBlock" % MYNAME
        OUTBLOCK1 = "%sOutBlock1" % MYNAME
        OUTBLOCK2 = "%sOutBlock2" % MYNAME
        RESFILE = "%s\\Res\\%s.res" % (resdir, MYNAME)

        print(MYNAME, RESFILE)

        query.LoadFromResFile(RESFILE)
        query.SetFieldData(INBLOCK1, "OrgOrdNo", 0, 원주문번호)
        query.SetFieldData(INBLOCK1, "AcntNo", 0, 계좌번호)
        query.SetFieldData(INBLOCK1, "InptPwd", 0, 입력비밀번호)
        query.SetFieldData(INBLOCK1, "IsuNo", 0, 종목번호)
        query.SetFieldData(INBLOCK1, "OrdQty", 0, 주문수량)
        query.Request(0)

        while XAQueryEvents.상태 == False:
            pythoncom.PumpWaitingMessages()

        result = []
        nCount = query.GetBlockCount(OUTBLOCK1)
        for i in range(nCount):
            레코드갯수 = int(query.GetFieldData(OUTBLOCK1, "RecCnt", i).strip())
            원주문번호 = int(query.GetFieldData(OUTBLOCK1, "OrgOrdNo", i).strip())
            계좌번호 = query.GetFieldData(OUTBLOCK1, "AcntNo", i).strip()
            입력비밀번호 = query.GetFieldData(OUTBLOCK1, "InptPwd", i).strip()
            종목번호 = query.GetFieldData(OUTBLOCK1, "IsuNo", i).strip()
            주문수량 = int(query.GetFieldData(OUTBLOCK1, "OrdQty", i).strip())
            통신매체코드 = query.GetFieldData(OUTBLOCK1, "CommdaCode", i).strip()
            그룹ID = query.GetFieldData(OUTBLOCK1, "GrpId", i).strip()
            전략코드 = query.GetFieldData(OUTBLOCK1, "StrtgCode", i).strip()
            주문회차 = int(query.GetFieldData(OUTBLOCK1, "OrdSeqNo", i).strip())
            포트폴리오번호 = int(query.GetFieldData(OUTBLOCK1, "PtflNo", i).strip())
            바스켓번호 = int(query.GetFieldData(OUTBLOCK1, "BskNo", i).strip())
            트렌치번호 = int(query.GetFieldData(OUTBLOCK1, "TrchNo", i).strip())
            아이템번호 = int(query.GetFieldData(OUTBLOCK1, "ItemNo", i).strip())

            lst = [레코드갯수, 원주문번호, 계좌번호, 입력비밀번호, 종목번호, 주문수량, 통신매체코드, 그룹ID, 전략코드, 주문회차, 포트폴리오번호, 바스켓번호, 트렌치번호, 아이템번호]
            result.append(lst)

        columns = ['레코드갯수', '원주문번호', '계좌번호', '입력비밀번호', '종목번호', '주문수량', '통신매체코드', '그룹ID', '전략코드', '주문회차', '포트폴리오번호',
                   '바스켓번호', '트렌치번호', '아이템번호']
        df = DataFrame(data=result, columns=columns)

        result = []
        nCount = query.GetBlockCount(OUTBLOCK2)
        for i in range(nCount):
            레코드갯수 = int(query.GetFieldData(OUTBLOCK2, "RecCnt", i).strip())
            주문번호 = int(query.GetFieldData(OUTBLOCK2, "OrdNo", i).strip())
            모주문번호 = int(query.GetFieldData(OUTBLOCK2, "PrntOrdNo", i).strip())
            주문시각 = query.GetFieldData(OUTBLOCK2, "OrdTime", i).strip()
            주문시장코드 = query.GetFieldData(OUTBLOCK2, "OrdMktCode", i).strip()
            주문유형코드 = query.GetFieldData(OUTBLOCK2, "OrdPtnCode", i).strip()
            단축종목번호 = query.GetFieldData(OUTBLOCK2, "ShtnIsuNo", i).strip()
            프로그램호가유형코드 = query.GetFieldData(OUTBLOCK2, "PrgmOrdprcPtnCode", i).strip()
            공매도호가구분 = query.GetFieldData(OUTBLOCK2, "StslOrdprcTpCode", i).strip()
            공매도가능여부 = query.GetFieldData(OUTBLOCK2, "StslAbleYn", i).strip()
            신용거래코드 = query.GetFieldData(OUTBLOCK2, "MgntrnCode", i).strip()
            대출일 = query.GetFieldData(OUTBLOCK2, "LoanDt", i).strip()
            반대매매주문구분 = query.GetFieldData(OUTBLOCK2, "CvrgOrdTp", i).strip()
            유동성공급자여부 = query.GetFieldData(OUTBLOCK2, "LpYn", i).strip()
            관리사원번호 = query.GetFieldData(OUTBLOCK2, "MgempNo", i).strip()
            매매구분 = query.GetFieldData(OUTBLOCK2, "BnsTpCode", i).strip()
            예비주문번호 = int(query.GetFieldData(OUTBLOCK2, "SpareOrdNo", i).strip())
            반대매매일련번호 = int(query.GetFieldData(OUTBLOCK2, "CvrgSeqno", i).strip())
            예약주문번호 = int(query.GetFieldData(OUTBLOCK2, "RsvOrdNo", i).strip())
            계좌명 = query.GetFieldData(OUTBLOCK2, "AcntNm", i).strip()
            종목명 = query.GetFieldData(OUTBLOCK2, "IsuNm", i).strip()

            lst = [레코드갯수, 주문번호, 모주문번호, 주문시각, 주문시장코드, 주문유형코드, 단축종목번호, 프로그램호가유형코드, 공매도호가구분, 공매도가능여부, 신용거래코드, 대출일,
                   반대매매주문구분, 유동성공급자여부, 관리사원번호, 매매구분, 예비주문번호, 반대매매일련번호, 예약주문번호, 계좌명, 종목명]
            result.append(lst)

        columns = ['레코드갯수', '주문번호', '모주문번호', '주문시각', '주문시장코드', '주문유형코드', '단축종목번호', '프로그램호가유형코드', '공매도호가구분', '공매도가능여부',
                   '신용거래코드', '대출일', '반대매매주문구분', '유동성공급자여부', '관리사원번호', '매매구분', '예비주문번호', '반대매매일련번호', '예약주문번호', '계좌명',
                   '종목명']
        df1 = DataFrame(data=result, columns=columns)

        XAQueryEvents.상태 = False

        return (df, df1)

    # def t1427(self, field=1, day=0, diff=10, list=[]):
    #     inXAQuery = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    #
    #     pathname = os.path.dirname(sys.argv[0])
    #     RESDIR = os.path.abspath(pathname)
    #     MYNAME = inspect.currentframe().f_code.co_name
    #     RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)
    #
    #     inXAQuery.LoadFromResFile(RESFILE)
    #     inXAQuery.SetFieldData('t1427InBlock', 'gubun', 0, field)
    #     inXAQuery.Request(0)
    #
    #     while XAQueryEvents.상태 == False:
    #         sleep(1)
    #         pythoncom.PumpWaitingMessages()
    #     XAQueryEvents.상태 = False
    #
    #     nCount = inXAQuery.GetBlockCount('t1427OutBlock1')
    #     resultList = []
    #     for i in range(nCount):
    #         code = inXAQuery.GetFieldData('t1427OutBlock1', 'shcode', i)
    #         price = int(inXAQuery.GetFieldData('t1427OutBlock1', 'price', i))
    #         volume = int(inXAQuery.GetFieldData('t1427OutBlock1', 'volume', i))  # type: int
    #         jnilvolume = int(inXAQuery.GetFieldData('t1427OutBlock1', 'jnilvolume', i))
    #         low = int(inXAQuery.GetFieldData('t1427OutBlock1', 'low', i))
    #         high = int(inXAQuery.GetFieldData('t1427OutBlock1', 'high', i))
    #         value = int(inXAQuery.GetFieldData('t1427OutBlock1', 'value', i))
    #
    #         stock = {}
    #         stock['code'] = code
    #         stock['price'] = price
    #         stock['volume'] = volume
    #         stock['jnilvolume'] = jnilvolume
    #         stock['priceVolume'] = price * volume
    #         stock['value'] = value
    #         stock['low'] = low
    #         stock['high'] = high
    #         stock['percent'] = get_percent(low, high)
    #         if get_percent(low, high) > diff:
    #             if stock not in list:
    #                 resultList.append(stock)
    #
    #     retList = sorted(resultList, key=itemgetter('value'), reverse=True)
    #
    #     for d in retList:
    #         print(d)
    #     return retList[0:10]

    # def t0425(self, 계좌번호='', 비밀번호='', 종목번호='', 체결구분='0', 매매구분='0', 정렬순서='2', 주문번호=''):
    #     '''
    #     주식 체결/미체결
    #     '''
    #     pathname = os.path.dirname(sys.argv[0])
    #     resdir = os.path.abspath(pathname)
    #
    #     query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    #
    #     MYNAME = inspect.currentframe().f_code.co_name
    #     INBLOCK = "%sInBlock" % MYNAME
    #     INBLOCK1 = "%sInBlock1" % MYNAME
    #     OUTBLOCK = "%sOutBlock" % MYNAME
    #     OUTBLOCK1 = "%sOutBlock1" % MYNAME
    #     OUTBLOCK2 = "%sOutBlock2" % MYNAME
    #     RESFILE = "%s\\Res\\%s.res" % (resdir, MYNAME)
    #
    #     print(MYNAME, RESFILE)
    #
    #     query.LoadFromResFile(RESFILE)
    #     query.SetFieldData(INBLOCK, "accno", 0, 계좌번호)
    #     query.SetFieldData(INBLOCK, "passwd", 0, 비밀번호)
    #     query.SetFieldData(INBLOCK, "expcode", 0, 종목번호)
    #     query.SetFieldData(INBLOCK, "chegb", 0, 체결구분)
    #     query.SetFieldData(INBLOCK, "medosu", 0, 매매구분)
    #     query.SetFieldData(INBLOCK, "sortgb", 0, 정렬순서)
    #     query.SetFieldData(INBLOCK, "cts_ordno", 0, 주문번호)
    #     query.Request(0)
    #
    #     while XAQueryEvents.상태 == False:
    #         pythoncom.PumpWaitingMessages()
    #
    #     result = []
    #     nCount = query.GetBlockCount(OUTBLOCK)
    #     for i in range(nCount):
    #         총주문수량 = int(query.GetFieldData(OUTBLOCK, "tqty", i).strip())
    #         총체결수량 = int(query.GetFieldData(OUTBLOCK, "tcheqty", i).strip())
    #         총미체결수량 = int(query.GetFieldData(OUTBLOCK, "tordrem", i).strip())
    #         추정수수료 = int(query.GetFieldData(OUTBLOCK, "cmss", i).strip())
    #         총주문금액 = int(query.GetFieldData(OUTBLOCK, "tamt", i).strip())
    #         총매도체결금액 = int(query.GetFieldData(OUTBLOCK, "tmdamt", i).strip())
    #         총매수체결금액 = int(query.GetFieldData(OUTBLOCK, "tmsamt", i).strip())
    #         추정제세금 = int(query.GetFieldData(OUTBLOCK, "tax", i).strip())
    #         주문번호 = query.GetFieldData(OUTBLOCK, "cts_ordno", i).strip()
    #
    #         lst = [총주문수량, 총체결수량, 총미체결수량, 추정수수료, 총주문금액, 총매도체결금액, 총매수체결금액, 추정제세금, 주문번호]
    #         result.append(lst)
    #
    #     columns = ['총주문수량', '총체결수량', '총미체결수량', '추정수수료', '총주문금액', '총매도체결금액', '총매수체결금액', '추정제세금', '주문번호']
    #     df = DataFrame(data=result, columns=columns)
    #
    #     result = []
    #     nCount = query.GetBlockCount(OUTBLOCK1)
    #     for i in range(nCount):
    #         주문번호 = int(query.GetFieldData(OUTBLOCK1, "ordno", i).strip())
    #         종목번호 = query.GetFieldData(OUTBLOCK1, "expcode", i).strip()
    #         구분 = query.GetFieldData(OUTBLOCK1, "medosu", i).strip()
    #         주문수량 = int(query.GetFieldData(OUTBLOCK1, "qty", i).strip())
    #         주문가격 = int(query.GetFieldData(OUTBLOCK1, "price", i).strip())
    #         체결수량 = int(query.GetFieldData(OUTBLOCK1, "cheqty", i).strip())
    #         체결가격 = int(query.GetFieldData(OUTBLOCK1, "cheprice", i).strip())
    #         미체결잔량 = int(query.GetFieldData(OUTBLOCK1, "ordrem", i).strip())
    #         확인수량 = int(query.GetFieldData(OUTBLOCK1, "cfmqty", i).strip())
    #         상태 = query.GetFieldData(OUTBLOCK1, "status", i).strip()
    #         원주문번호 = int(query.GetFieldData(OUTBLOCK1, "orgordno", i).strip())
    #         유형 = query.GetFieldData(OUTBLOCK1, "ordgb", i).strip()
    #         주문시간 = query.GetFieldData(OUTBLOCK1, "ordtime", i).strip()
    #         주문매체 = query.GetFieldData(OUTBLOCK1, "ordermtd", i).strip()
    #         처리순번 = int(query.GetFieldData(OUTBLOCK1, "sysprocseq", i).strip())
    #         호가유형 = query.GetFieldData(OUTBLOCK1, "hogagb", i).strip()
    #         현재가 = int(query.GetFieldData(OUTBLOCK1, "price1", i).strip())
    #         주문구분 = query.GetFieldData(OUTBLOCK1, "orggb", i).strip()
    #         신용구분 = query.GetFieldData(OUTBLOCK1, "singb", i).strip()
    #         대출일자 = query.GetFieldData(OUTBLOCK1, "loandt", i).strip()
    #
    #         lst = [주문번호, 종목번호, 구분, 주문수량, 주문가격, 체결수량, 체결가격, 미체결잔량, 확인수량, 상태, 원주문번호, 유형, 주문시간, 주문매체, 처리순번, 호가유형, 현재가,
    #                주문구분, 신용구분, 대출일자]
    #         result.append(lst)
    #
    #     columns = ['주문번호', '종목번호', '구분', '주문수량', '주문가격', '체결수량', '체결가격', '미체결잔량', '확인수량', '상태', '원주문번호', '유형', '주문시간',
    #                '주문매체', '처리순번', '호가유형', '현재가', '주문구분', '신용구분', '대출일자']
    #     df1 = DataFrame(data=result, columns=columns)
    #
    #     XAQueryEvents.상태 = False
    #
    #     return (df, df1)

    def t8436(self, gubun=1):
        print("call t8436")
        inXAQuery = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)

        pathname = os.path.dirname(sys.argv[0])
        RESDIR = os.path.abspath(pathname)
        MYNAME = inspect.currentframe().f_code.co_name
        RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)

        inXAQuery.LoadFromResFile(RESFILE)
        inXAQuery.SetFieldData('t8436InBlock', 'gubun', 0, gubun)
        inXAQuery.Request(0)

        while XAQueryEvents.상태 == False:
            pythoncom.PumpWaitingMessages()
        XAQueryEvents.상태 = False

        nCount = inXAQuery.GetBlockCount('t8436OutBlock')

        resultList = []

        for i in range(nCount):
            코드 = inXAQuery.GetFieldData('t8436OutBlock', 'shcode', i)
            ETF = int(inXAQuery.GetFieldData('t8436OutBlock', 'etfgubun', i))
            상한가 = inXAQuery.GetFieldData('t8436OutBlock', 'uplmtprice', i)
            하한가 = inXAQuery.GetFieldData('t8436OutBlock', 'dnlmtprice', i)
            전일가 = inXAQuery.GetFieldData('t8436OutBlock', 'jnilclose', i)
            주문수량단위 = inXAQuery.GetFieldData('t8436OutBlock', 'memedan', i)
            기준가 = inXAQuery.GetFieldData('t8436OutBlock', 'recprice', i)
            lst = [코드, 전일가, 기준가]
            if ETF is 1:
                resultList.append(lst)
        print(resultList)
        return resultList

    def t1102(self, shcode, code_list=[]):
        inXAQuery = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)

        pathname = os.path.dirname(sys.argv[0])
        RESDIR = os.path.abspath(pathname)
        MYNAME = inspect.currentframe().f_code.co_name
        RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)

        inXAQuery.LoadFromResFile(RESFILE)
        inXAQuery.SetFieldData('t1102InBlock', 'shcode', 0, shcode)
        inXAQuery.Request(0)

        while XAQueryEvents.상태 == False:
            pythoncom.PumpWaitingMessages()
        XAQueryEvents.상태 = False

        nCount = inXAQuery.GetBlockCount('t1102OutBlock')
        resultList = []
        stock = {}
        for i in range(nCount):

            시간 = int(int(datetime.datetime.today().strftime("%H%M%S%f")) / 100000)

            코드 = inXAQuery.GetFieldData('t1102OutBlock', 'shcode', i)
            한글명 = inXAQuery.GetFieldData('t1102OutBlock', 'hname', i)
            현재가 = int(inXAQuery.GetFieldData('t1102OutBlock', 'price', i))
            등락율 = float(inXAQuery.GetFieldData('t1102OutBlock', 'diff', i))
            누적거래량 = int(inXAQuery.GetFieldData('t1102OutBlock', 'volume', i))

            거래량차 = int(inXAQuery.GetFieldData('t1102OutBlock', 'volumediff', i))
            거래대금 = 현재가 * 누적거래량

            # stock['전일거래량'] = int(inXAQuery.GetFieldData('t1102OutBlock', 'jnilvolume', i))
            # stock['고가'] = int(inXAQuery.GetFieldData('t1102OutBlock', 'high', i))
            # stock['저가'] = int(inXAQuery.GetFieldData('t1102OutBlock', 'low', i))
            # stock['소진율'] = inXAQuery.GetFieldData('t1102OutBlock', 'exhratio', i)
            # stock['회전율'] = inXAQuery.GetFieldData('t1102OutBlock', 'vol', i)
            # stock['percent'] = get_percent(stock['저가'], stock['고가'])

            stock['코드'] = 코드
            stock['거래대금'] = 거래대금

            lst = [시간, 한글명, 코드, 현재가, 등락율, 누적거래량, 거래량차, 거래대금]
            resultList.append(lst)

        df = DataFrame(data=resultList, columns=['시간', '한글명', '코드', '현재가', '등락율', '누적거래량', '거래량차', '거래대금'])
        # print(df)
        return df, stock


if __name__ == "__main__":
    debug_mode = False
    Trade = Trade(debug=debug_mode)
    # Trade.check_realTime_stock()
    Trade.check_realTime_ETF_stock()

