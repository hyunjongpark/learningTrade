import requests
import os, sys
from bs4 import BeautifulSoup
import datetime
import pandas_datareader.data as web


class StockDownload:
    def __init__(self):
        self.updateAllCodes()

    def download_stock_data(self, file_name, company_code, year1, month1, date1, year2, month2, date2):
        start = datetime.datetime(year1, month1, date1)
        end = datetime.datetime(year2, month2, date2)
        df = web.DataReader("%s.KS" % (company_code), "yahoo", start, end)
        df.to_pickle(file_name)
        return df

    def downloadCode(self, market_type):
        url = 'http://datamall.koscom.co.kr/servlet/infoService/SearchIssue'
        html = requests.post(url, data={'flag': 'SEARCH', 'marketDisabled': 'null', 'marketBit': market_type})
        return html.content

    def parseCodeHTML(self, html, market_type):
        soup = BeautifulSoup(html, "lxml")
        options = soup.findAll('option')

        # print(codes)

        for a_option in options:
            # print a_tr
            if len(a_option) == 0:
                continue

            code = a_option.text[1:7]
            company = a_option.text[8:]
            full_code = a_option.get('value')
            if company == '':
                continue;

            if "폐지" in str(company):
                continue

            print(code + ' - ' + company)
            try:
                self.download_stock_data('%s.data' % company, str(code), 2010, 1, 1, 2017, 3, 1)
            except:
                print('except')
                # codes.add(market_type, code, full_code, company)

                # return codes

    def updateAllCodes(self):
        for market_type in ['kospiVal', 'kosdaqVal']:
            html = self.downloadCode(market_type)
            codes = self.parseCodeHTML(html, market_type)
            print(codes)


StockDownload()
