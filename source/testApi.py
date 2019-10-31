# -*- coding: utf-8 -*-
from __future__ import division
import os, sys

import pythoncom
import win32com.client as winAPI
import datetime

from time import sleep

STAND_BY = 0
RECEIVED = 1

import win32com.client
import pythoncom
import sys


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

class XAQueryEventHandlerT1102:
    query_state = 0

    def OnReceiveData(self, code):
        XAQueryEventHandlerT1102.query_state = 1

SERVER_PORT = 20001
SHOW_CERTIFICATE_ERROR_DIALOG = False
REPEATED_DATA_QUERY = 1
TRANSACTION_REQUEST_EXCESS = -21
TODAY = datetime.datetime.now().strftime('%Y%m%d')

class Trade():

    def __init__(self):
        print('init')
        id = "phjwithy"
        password = "phj1629"
        certificate_password = "s20036402!"
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

    def get_status_all(self):
        print('get_status_all')
        # ----------------------------------------------------------------------------
        # t1102
        # ----------------------------------------------------------------------------
        self.instXAQueryT1102 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT1102)
        path = "C:\\eBEST\\xingAPI\\Res\\t1102.res"
        self.instXAQueryT1102.ResFileName = path

        today_list = ['000660', '005935', '005380', '207940', '207940']
        while True:
            for code in today_list:
                self.get_status_code(code)
                sleep(10)

    def get_status_code(self, code):

        self.instXAQueryT1102.SetFieldData("t1102InBlock", "shcode", 0, code)
        self.instXAQueryT1102.Request(0)

        while XAQueryEventHandlerT1102.query_state == 0:
            pythoncom.PumpWaitingMessages()
        XAQueryEventHandlerT1102.query_state = 0

        name = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "hname", 0)
        price = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "price", 0)
        diff = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "diff", 0)
        volume = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "volume", 0)  # 누적 거래량
        vol = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "vol", 0)  # 회전율

        fwdvl = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "fwdvl", 0)  # 외국계 매도 함계 수량
        ftradmdcha = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "ftradmdcha", 0)  # 외국계 매도 직전 대비
        ftradmddiff = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "ftradmddiff", 0)  # 외국계 매도 비율

        fwsvl = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "fwsvl", 0)  # 외국계 매수 합계 수향
        ftradmscha = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "ftradmscha", 0)  # 외국계 매수 직전 대비
        ftradmsdiff = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "ftradmsdiff", 0)  # 외국계 매수 비율

        dvol1 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "dvol1", 0)  # 총매도 수량 1
        svol1 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "svol1", 0)  # 총매수 수량 1
        dcha1 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "dcha1", 0)  # 매도 증감 1
        scha1 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "scha1", 0)  # 매수 증감 1
        ddiff1 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "ddiff1", 0)  # 매도 비율 1
        sdiff1 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "sdiff1", 0)  # 매수 비율 1

        dvol2 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "dvol2", 0)  # 총매도 수량 2
        svol2 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "svol2", 0)  # 총매수 수량 2
        dcha2 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "dcha2", 0)  # 매도 증감 2
        scha2 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "scha2", 0)  # 매수 증감 2
        ddiff2 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "ddiff2", 0)  # 매도 비율 2
        sdiff2 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "sdiff2", 0)  # 매수 비율 2

        dvol3 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "dvol3", 0)  # 총매도 수량 3
        svol3 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "svol3", 0)  # 총매수 수량 3
        dcha3 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "dcha3", 0)  # 매도 증감 3
        scha3 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "scha3", 0)  # 매수 증감 3
        ddiff3 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "ddiff3", 0)  # 매도 비율 3
        sdiff3 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "sdiff3", 0)  # 매수 비율 3

        dvol4 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "dvol4", 0)  # 총매도 수량 4
        svol4 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "svol4", 0)  # 총매수 수량 4
        dcha4 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "dcha4", 0)  # 매도 증감 4
        scha4 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "scha4", 0)  # 매수 증감 4
        ddiff4 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "ddiff4", 0)  # 매도 비율 4
        sdiff4 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "sdiff4", 0)  # 매수 비율 4

        dvol5 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "dvol5", 0)  # 총매도 수량 5
        svol5 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "svol5", 0)  # 총매수 수량 5
        dcha5 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "dcha5", 0)  # 매도 증감 5
        scha5 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "scha5", 0)  # 매수 증감 5
        ddiff5 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "ddiff5", 0)  # 매도 비율 5
        sdiff5 = self.instXAQueryT1102.GetFieldData("t1102OutBlock", "sdiff5", 0)  # 매수 비율 5

        sys.stdout = open('20191101.txt', 'a')
        print('%s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s ' % (datetime.datetime.now(), name, code, price, diff, volume, vol, dvol1, svol1, dcha1, scha1, ddiff1, sdiff1))

if __name__ == "__main__":
    Trade = Trade()
    Trade.get_status_all()