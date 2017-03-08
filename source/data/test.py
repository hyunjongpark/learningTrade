import requests
from bs4 import BeautifulSoup
import datetime
import pandas_datareader.data as web


class StockCodeItem:
    def __init__(self, market_type, code, full_code, company):
        self.market_type = market_type
        self.code = code
        self.full_code = full_code
        self.company = company


class StockCode:
    def __init__(self):
        self.items = {}

    def count(self):
        return len(self.items)

    def clear(self):
        self.items.clear()

    def add(self, market_type, code, full_code, company):
        a_item = StockCodeItem(market_type, code, full_code, company)
        self.items[code] = a_item

    def remove(self, stock_code):
        del self.items[stock_code]

    def find(self, stock_code):
        return self.items[stock_code]

    def iterItems(self):
        return self.items.iteritems()

    def dump(self):
        index = 0
        for key, value in self.items.iteritems():
            print("%s : %s - Code=%s, Full Code=%s, Company=%s" % (
                index, value.market_type, key, value.full_code, value.company))
            index += 1


def download_stock_data(file_name, company_code, year1, month1, date1, year2, month2, date2):
    start = datetime.datetime(year1, month1, date1)
    end = datetime.datetime(year2, month2, date2)

    df = web.DataReader("%s.KS" % (company_code), "yahoo", start, end)

    df.to_pickle(file_name)

    return df


def downloadCode(market_type):
    url = 'http://datamall.koscom.co.kr/servlet/infoService/SearchIssue'
    html = requests.post(url, data={'flag': 'SEARCH', 'marketDisabled': 'null', 'marketBit': market_type})
    return html.content


def parseCodeHTML(html, market_type):
    soup = BeautifulSoup(html, "lxml")
    # soup = BeautifulSoup.BeautifulSoup(html)
    options = soup.findAll('option')

    codes = StockCode()
    # print(codes)

    for a_option in options:
        # print a_tr
        if len(a_option) == 0:
            continue

        code = a_option.text[1:7]
        company = a_option.text[8:]
        if company == '':
            continue;

        if "폐지" in str(company):
            continue

        full_code = a_option.get('value')

        print(code + ' - ' + company)
        try:
            download_stock_data('%s.data' % company, str(code), 2010, 1, 1, 2017, 3, 1)
        except:
            print('except')

            # codes.add(market_type, code, full_code, company)

    return codes


def updateAllCodes():
    for market_type in ['kospiVal', 'kosdaqVal']:
        html = downloadCode(market_type)
        codes = parseCodeHTML(html, market_type)
        # print(codes)
        # self.dbwriter.updateCodeToDB(codes)


updateAllCodes()
