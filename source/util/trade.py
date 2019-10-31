# -*- coding: utf-8 -*-
from __future__ import division

import os, sys

import win32com.client as w32
import pythoncom


class trade():
    login_state = 0

    def __init__(self):
        print('stock_updater')

    def OnLogin(self, code, msg):
        if code == "0000":
            print("login successed")
            XASessionEventHandler.login_state = 1
        else:
            print("login failed")

        id = ""
        passwd = ""
        cert_passwd = ""

        instXASession = w32.DispatchWithEvents("XA_Session.XASession", XASessionEventHandler)
        instXASession.ConnectServer("hts.ebestsec.co.kr", 20001)
        instXASession.Login(id, passwd, cert_passwd, 0, 0)

        while XASessionEventHandler.login_state == 0:
            pythoncom.PumpWaitingMessages()

        # getting acount list
        num_account = instXASession.GetAccountListCount()
        for i in range(num_account):
            account = instXASession.GetAccountList(i)
            print(account)