# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from common import *
# import BeautifulSoup
import pandas_datareader.data as web
from dateutil.relativedelta import relativedelta
from data_model import *
from util.services import *
import re

class stock_updater():
    def __init__(self):
        print('stock_updater')

    def update_kospi_100(self):
        self.update_stock_list(file_name='kospi100', whereCode=61)
        return self.download_stock_datas(stock_list_file_name='kospi100')

    def update_kospi_200(self):
        services.get('configurator').register('stock_list', 'kospi200')
        # self.update_stock_list(file_name=services.get('configurator').get('stock_list'), whereCode=51)
        self.download_kospi_200_stock_list(file_name=services.get('configurator').get('stock_list'))
        return self.download_stock_datas(stock_list_file_name=services.get('configurator').get('stock_list'))

    def update_kospi_big(self):
        services.get('configurator').register('stock_list', 'kospi_big')
        self.update_stock_list(file_name=services.get('configurator').get('stock_list'), whereCode=1)
        return self.download_stock_datas(stock_list_file_name=services.get('configurator').get('stock_list'))

    def update_kospi_ETF(self):
        services.get('configurator').register('stock_list', 'kospi_etf')
        self.update_stock_list_etf(file_name=services.get('configurator').get('stock_list'), whereCode=1)
        return self.download_stock_datas(stock_list_file_name=services.get('configurator').get('stock_list'))


    def download_kospi_200_stock_list(self, file_name):
        code_list = []
        base_url = 'http://finance.naver.com/sise/entryJongmok.nhn?&page='
        for i in range(1,20):
            url = base_url + str(i);
            html = requests.post(url).content
            soup = BeautifulSoup(html, "lxml")
            items = soup.find_all('td', {'class': 'ctg'})
            for item in items:
                txt = item.a.get('href')
                k = re.search('[\d]+', txt)
                if k:
                    code = k.group()
                    name = item.text
                    data = code, name
                    code_list.append(data)
                    print(data)
        write_yaml(file_name, code_list)





    def update_stock_list(self, file_name, whereCode=51):
        for market_type in ['kospiVal']:
            html = self.downloadCode(market_type,whereCode)
            codes = self.parseCodeHTML(html, market_type)
            print('code len %s' %(len(codes.iterItems())))
            delete_file(file_name)
            write_yaml(file_name, codes)
            code_list = [k for k, v in codes.iterItems()]
            print(code_list)
            # write_yaml('kospi_200_code', code_list)
            write_yaml(file_name, code_list)

    def update_stock_list_etf(self, file_name, whereCode=51):
        url = 'http://datamall.koscom.co.kr/servlet/infoService/SearchIssue'
        html = requests.post(url).content
        codes = self.parseCodeHTML_ETF(html)
        print('code len %s' % (len(codes.iterItems())))
        delete_file(file_name)
        write_yaml(file_name, codes)
        code_list = [k for k, v in codes.iterItems()]
        print(code_list)
        write_yaml(file_name, code_list)


    def downloadCode(self, market_type,whereCode):
        url = 'http://datamall.koscom.co.kr/servlet/infoService/SearchIssue'
        html = requests.post(url, data={'flag': 'SEARCH', 'marketDisabled': 'null', 'marketBit': market_type, 'where':'', 'whereCode':whereCode})
        return html.content


    def parseCodeHTML(self, html, market_type):
        soup = BeautifulSoup(html, "lxml")
        options = soup.findAll('option')

        codes = StockCode()

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
            if str(company) == '550003' or str(company) == '251270' or str(company) == '267250' or str(company) == '003380':
                continue

            if 'ARIRANG' in company:
                continue
            if 'ETN' in company:
                continue
            if '스팩' in company:
                continue
            if 'KBSTAR' in company:
                continue
            if 'KINDEX' in company:
                continue
            if 'KODEX' in company:
                continue
            if 'KOSEF' in company:
                continue
            if 'amp' in company:
                continue
            if 'TIGER' in company:
                continue
            if 'WR' in company:
                continue
            if '인버스' in company:
                continue
            if ' ' in company:
                continue
            if 'S자산관리' in company:
                continue
            if '우' in company:
                continue
            if '호' in company:
                continue


            print(a_option)
            codes.add(market_type, code, full_code, company)

        return codes

    def parseCodeHTML_ETF(self, html):
        soup = BeautifulSoup(html, "lxml")
        options = soup.findAll('option')

        codes = StockCode()

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
            if "P" in str(company):
                continue

            if "KODEX" in str(company) or "TIGER" in str(company) or "KBSTAR" in str(company) or "KINDEX" in str(company) or "ARIRANG" in str(company) or "KOSEF" in str(company):
                print(a_option)
                codes.add('kospiVal', code, full_code, company)

        return codes


    def download_stock_datas(self, stock_list_file_name):
        data = load_yaml(stock_list_file_name)
        index = 0
        end = datetime.datetime.today()
        start = end - relativedelta(months=48)
        code_list = []
        for company_code, value in data:
            print("%s/%s : Code=%s, Company=%s" % (index, len(data), company_code, value))
            index += 1
            find_name = '%s_%s.data' % (company_code, value)
            if self.download_stock_data(file_name=find_name, company_code=company_code, start=start, end=end) is not None:
                code_list.append(company_code)


        return code_list

    def download_stock_data(self, file_name, company_code, start, end):
        # company_code='001470'
        df_fe = get_df_from_file(company_code, start, end)
        # print(df_fe)
        if df_fe is None:
            df_fe = get_foreigner_info(company_code, start, end)
        else:
            df_new =get_foreigner_info(company_code, start, end)
            df_new.sort_index(inplace=True)
            # print(df_new)
            df_fe = df_fe.append(df_new, ignore_index=False)
            # print(df_fe)
            df_fe = df_fe.drop_duplicates(subset =['Close','foreigner_count','institution_trading'], take_last=True)
            df_fe.groupby(df_fe.index).first()
        df_fe.sort_index(inplace=True)
        print(df_fe)
        save_stock_data(df_fe, file_name)
        return df_fe

    def download_kospi_data(self):
        end = datetime.datetime.today()
        start = end - relativedelta(months=48)
        try:
            df = web.DataReader("KRX:KOSPI", "google", start, end)
            print(df)
            save_stock_data(df, 'kospi.data')
            # web.DataReader("KRX:KOSPI", "google", start, end).to_csv('kospi.csv')
        except Exception as ex:
            print('except [%s] %s' % ('kospi', ex))
            return None
        return df
