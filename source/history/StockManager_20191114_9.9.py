# -*- coding: utf-8 -*-
from __future__ import division
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from common import *

from source.common import get_percent


#
# C:\ProgramData\Anaconda3\envs\py35_32\python.exe C:/Users/phj/git/learningTrade/source/testApi.py
# 0
# TOTAL - Profit[20191106][t1302_20191106_002210.csv][0]
# 0
# TOTAL - Profit[20191106][t1302_20191106_002990.csv][0]
# 0
# TOTAL - Profit[20191106][t1302_20191106_005690.csv][0]
# 0
# TOTAL - Profit[20191106][t1302_20191106_006490.csv][0]
# 0
# TOTAL - Profit[20191106][t1302_20191106_012630.csv][0]
# 0
# TOTAL - Profit[20191106][t1302_20191106_014820.csv][0]
# 0
# TOTAL - Profit[20191106][t1302_20191106_016580.csv][0]
# 0
# TOTAL - Profit[20191106][t1302_20191106_019170.csv][0]
# 0
# TOTAL - Profit[20191106][t1302_20191106_032350.csv][0]
# BUY [33180][90300][9200]
# SELL SUCCESS [33180][90300][9280]
# BUY [33180][91300][9310]
# SELL FAILED [33180][91300][9300]
# BUY [33180][91500][9200]
# SELL SUCCESS [33180][91700][9260]
# BUY [33180][92000][9170]
# SELL SUCCESS [33180][92000][9220]
# BUY [33180][92700][9070]
# SELL FAILED [33180][92900][8940]
# BUY [33180][93600][9090]
# SELL FAILED [33180][93600][9110]
# BUY [33180][101600][8990]
# SELL FAILED [33180][102800][8820]
# BUY [33180][113300][9130]
# SELL FAILED [33180][113600][9130]
# BUY [33180][115600][9090]
# SELL FAILED [33180][121700][9100]
# BUY [33180][122500][9060]
# SELL FAILED [33180][124300][9060]
# BUY [33180][125800][9030]
# SELL SUCCESS [33180][130300][9060]
# BUY [33180][144200][9100]
# SELL FAILED [33180][144300][9120]
# BUY [33180][144800][9090]
# SELL SUCCESS [33180][145200][9120]
# -4.4426304157382885
# TOTAL - Profit[20191106][t1302_20191106_033180.csv][-4.4426304157382885]
# 0
# TOTAL - Profit[20191107][t1302_20191107_002320.csv][-4.4426304157382885]
# 0
# TOTAL - Profit[20191107][t1302_20191107_002780.csv][-4.4426304157382885]
# 0
# TOTAL - Profit[20191107][t1302_20191107_004170.csv][-4.4426304157382885]
# 0
# TOTAL - Profit[20191107][t1302_20191107_007700.csv][-4.4426304157382885]
# 0
# TOTAL - Profit[20191107][t1302_20191107_009580.csv][-4.4426304157382885]
# 0
# TOTAL - Profit[20191107][t1302_20191107_019170.csv][-4.4426304157382885]
# 0
# TOTAL - Profit[20191107][t1302_20191107_020000.csv][-4.4426304157382885]
# BUY [33180][101900][9280]
# SELL FAILED [33180][105500][9270]
# BUY [33180][140700][9260]
# SELL FAILED [33180][141500][9250]
# -5.318380397119088
# TOTAL - Profit[20191107][t1302_20191107_033180.csv][-9.761010812857377]
# 0
# TOTAL - Profit[20191107][t1302_20191107_074610.csv][-9.761010812857377]
# 0
# TOTAL - Profit[20191107][t1302_20191107_229640.csv][-9.761010812857377]
# 0
# TOTAL - Profit[20191107][t1302_20191107_249420.csv][-9.761010812857377]
# 0
# TOTAL - Profit[20191108][t1302_20191108_001210.csv][-9.761010812857377]
# BUY [1360][102000][5640]
# SELL SUCCESS [1360][102200][5670]
# BUY [1360][105100][5640]
# SELL SUCCESS [1360][105200][5670]
# BUY [1360][105800][5620]
# SELL SUCCESS [1360][110200][5640]
# BUY [1360][112400][5550]
# SELL SUCCESS [1360][112800][5610]
# 1.18078275443612
# TOTAL - Profit[20191108][t1302_20191108_001360.csv][-8.580228058421257]
# 0
# TOTAL - Profit[20191108][t1302_20191108_002990.csv][-8.580228058421257]
# 0
# TOTAL - Profit[20191108][t1302_20191108_002995.csv][-8.580228058421257]
# BUY [3280][101100][517]
# SELL SUCCESS [3280][101500][523]
# BUY [3280][102800][507]
# SELL SUCCESS [3280][103100][517]
# BUY [3280][112100][508]
# SELL FAILED [3280][122100][501]
# 0.7649754179391917
# TOTAL - Profit[20191108][t1302_20191108_003280.csv][-7.815252640482066]
# 0
# TOTAL - Profit[20191108][t1302_20191108_003350.csv][-7.815252640482066]
# BUY [6490][93300][4020]
# SELL FAILED [6490][93400][3975]
# BUY [6490][100700][4145]
# SELL SUCCESS [6490][100800][4235]
# BUY [6490][103000][4340]
# SELL FAILED [6490][103200][4340]
# BUY [6490][103700][4270]
# SELL SUCCESS [6490][103900][4320]
# BUY [6490][115200][4495]
# SELL SUCCESS [6490][115300][4520]
# BUY [6490][125400][4410]
# SELL FAILED [6490][125800][4370]
# -0.10800803833804684
# TOTAL - Profit[20191108][t1302_20191108_006490.csv][-7.923260678820112]
# 0
# TOTAL - Profit[20191108][t1302_20191108_010770.csv][-7.923260678820112]
# 0
# TOTAL - Profit[20191108][t1302_20191108_016380.csv][-7.923260678820112]
# BUY [20560][111800][5380]
# SELL SUCCESS [20560][114400][5420]
# 0.4134944237918216
# TOTAL - Profit[20191108][t1302_20191108_020560.csv][-7.509766255028291]
# BUY [25620][111600][5410]
# SELL SUCCESS [25620][113400][5460]
# BUY [25620][115900][5350]
# SELL FAILED [25620][121300][5300]
# -0.6703650215074197
# TOTAL - Profit[20191108][t1302_20191108_025620.csv][-8.180131276535711]
# 0
# TOTAL - Profit[20191108][t1302_20191108_069460.csv][-8.180131276535711]
# 0
# TOTAL - Profit[20191108][t1302_20191108_123690.csv][-8.180131276535711]
# 0
# TOTAL - Profit[20191108][t1302_20191108_214420.csv][-8.180131276535711]
# 0
# TOTAL - Profit[20191108][t1302_20191108_500030.csv][-8.180131276535711]
# 0
# TOTAL - Profit[20191108][t1302_20191108_500035.csv][-8.180131276535711]
# 0
# TOTAL - Profit[20191108][t1302_20191108_500036.csv][-8.180131276535711]
# 0
# TOTAL - Profit[20191108][t1302_20191108_530062.csv][-8.180131276535711]
# 0
# TOTAL - Profit[20191108][t1302_20191108_550045.csv][-8.180131276535711]
# 0
# TOTAL - Profit[20191111][t1302_20191111_001060.csv][-8.180131276535711]
# 0
# TOTAL - Profit[20191111][t1302_20191111_001525.csv][-8.180131276535711]
# 0
# TOTAL - Profit[20191111][t1302_20191111_001527.csv][-8.180131276535711]
# BUY [3560][92300][1870]
# SELL FAILED [3560][92400][1870]
# BUY [3560][125200][2010]
# SELL SUCCESS [3560][125300][2030]
# BUY [3560][125900][2110]
# SELL SUCCESS [3560][130000][2150]
# BUY [3560][131100][2065]
# SELL SUCCESS [3560][131200][2085]
# BUY [3560][140800][2100]
# SELL FAILED [3560][140900][2080]
# BUY [3560][142300][2050]
# SELL FAILED [3560][142600][2020]
# BUY [3560][143100][1980]
# SELL SUCCESS [3560][143700][2000]
# BUY [3560][151500][2000]
# 0.1435878987733119
# TOTAL - Profit[20191111][t1302_20191111_003560.csv][-8.0365433777624]
# 0
# TOTAL - Profit[20191111][t1302_20191111_007280.csv][-8.0365433777624]
# 0
# TOTAL - Profit[20191111][t1302_20191111_020000.csv][-8.0365433777624]
# BUY [24900][90400][1430]
# SELL SUCCESS [24900][90500][1465]
# BUY [24900][91500][1395]
# SELL FAILED [24900][91700][1380]
# BUY [24900][92700][1350]
# SELL SUCCESS [24900][93700][1365]
# BUY [24900][134600][1325]
# SELL FAILED [24900][141000][1310]
# BUY [24900][151900][1290]
# 0.031319269761143964
# TOTAL - Profit[20191111][t1302_20191111_024900.csv][-8.005224108001254]
# BUY [26940][112100][5260]
# SELL SUCCESS [26940][112400][5420]
# 2.711825095057034
# TOTAL - Profit[20191111][t1302_20191111_026940.csv][-5.293399012944221]
# 0
# TOTAL - Profit[20191111][t1302_20191111_037560.csv][-5.293399012944221]
# 0
# TOTAL - Profit[20191111][t1302_20191111_039570.csv][-5.293399012944221]
# 0
# TOTAL - Profit[20191111][t1302_20191111_069460.csv][-5.293399012944221]
# 0
# TOTAL - Profit[20191111][t1302_20191111_072130.csv][-5.293399012944221]
# 0
# TOTAL - Profit[20191111][t1302_20191111_163560.csv][-5.293399012944221]
# 0
# TOTAL - Profit[20191111][t1302_20191111_195920.csv][-5.293399012944221]
# 0
# TOTAL - Profit[20191111][t1302_20191111_253250.csv][-5.293399012944221]
# 0
# TOTAL - Profit[20191111][t1302_20191111_267850.csv][-5.293399012944221]
# 0
# TOTAL - Profit[20191111][t1302_20191111_334700.csv][-5.293399012944221]
# 0
# TOTAL - Profit[20191111][t1302_20191111_500022.csv][-5.293399012944221]
# 0
# TOTAL - Profit[20191111][t1302_20191111_500032.csv][-5.293399012944221]
# 0
# TOTAL - Profit[20191111][t1302_20191111_530038.csv][-5.293399012944221]
# BUY [1360][92200][4905]
# SELL SUCCESS [1360][92500][4960]
# BUY [1360][92800][4905]
# SELL FAILED [1360][93100][4900]
# BUY [1360][95900][4895]
# SELL SUCCESS [1360][100400][4945]
# BUY [1360][101900][4895]
# SELL FAILED [1360][102700][4835]
# BUY [1360][103000][4775]
# SELL SUCCESS [1360][103200][4840]
# BUY [1360][103700][4795]
# SELL FAILED [1360][104700][4735]
# BUY [1360][104800][4750]
# SELL SUCCESS [1360][105000][4780]
# BUY [1360][105700][4735]
# SELL SUCCESS [1360][111200][4790]
# BUY [1360][113400][4760]
# SELL SUCCESS [1360][114000][4825]
# BUY [1360][130100][4775]
# SELL SUCCESS [1360][130800][4810]
# BUY [1360][135900][4770]
# SELL SUCCESS [1360][140500][4805]
# BUY [1360][143300][4685]
# SELL SUCCESS [1360][143700][4765]
# 4.478816041952623
# TOTAL - Profit[20191112][t1302_20191112_001360.csv][-0.8145829709915979]
# 0
# TOTAL - Profit[20191112][t1302_20191112_001527.csv][-0.8145829709915979]
# 0
# TOTAL - Profit[20191112][t1302_20191112_005257.csv][-0.8145829709915979]
# 0
# TOTAL - Profit[20191112][t1302_20191112_006390.csv][-0.8145829709915979]
# 0
# TOTAL - Profit[20191112][t1302_20191112_00781K.csv][-0.8145829709915979]
# 0
# TOTAL - Profit[20191112][t1302_20191112_012450.csv][-0.8145829709915979]
# BUY [20560][92600][5900]
# SELL FAILED [20560][92900][5910]
# BUY [20560][120900][6340]
# SELL SUCCESS [20560][121400][6380]
# BUY [20560][123600][6150]
# SELL SUCCESS [20560][123800][6220]
# BUY [20560][124300][6180]
# SELL SUCCESS [20560][124500][6230]
# BUY [20560][131500][6320]
# SELL SUCCESS [20560][131600][6370]
# BUY [20560][142600][6860]
# SELL SUCCESS [20560][142900][6910]
# BUY [20560][143300][6870]
# SELL FAILED [20560][143800][6890]
# BUY [20560][144500][6770]
# SELL FAILED [20560][144600][6770]
# BUY [20560][150800][6590]
# 2.332296675906478
# TOTAL - Profit[20191112][t1302_20191112_020560.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191112][t1302_20191112_033250.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191112][t1302_20191112_039570.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191112][t1302_20191112_081660.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191112][t1302_20191112_097950.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191112][t1302_20191112_118000.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191112][t1302_20191112_181480.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191112][t1302_20191112_267850.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191112][t1302_20191112_317400.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191112][t1302_20191112_334700.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191112][t1302_20191112_500032.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191112][t1302_20191112_530038.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191113][t1302_20191113_001065.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191113][t1302_20191113_001210.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191113][t1302_20191113_001525.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191113][t1302_20191113_001527.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191113][t1302_20191113_003780.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191113][t1302_20191113_004250.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191113][t1302_20191113_005725.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191113][t1302_20191113_005750.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191113][t1302_20191113_009415.csv][1.51771370491488]
# 0
# TOTAL - Profit[20191113][t1302_20191113_017370.csv][1.51771370491488]
# SELL FAILED [20560][90300][7000]
# BUY [20560][91700][6740]
# SELL SUCCESS [20560][92100][6810]
# BUY [20560][93800][6590]
# SELL FAILED [20560][93900][6530]
# 7.69194973354709
# TOTAL - Profit[20191113][t1302_20191113_020560.csv][9.20966343846197]
# BUY [39570][90400][14350]
# SELL SUCCESS [39570][90500][15200]
# BUY [39570][93300][13600]
# SELL SUCCESS [39570][93500][13700]
# 5.998639065382251
# TOTAL - Profit[20191113][t1302_20191113_039570.csv][15.20830250384422]
# 0
# TOTAL - Profit[20191113][t1302_20191113_051630.csv][15.20830250384422]
# 0
# TOTAL - Profit[20191113][t1302_20191113_077500.csv][15.20830250384422]
# BUY [82740][92000][4785]
# SELL FAILED [82740][92100][4695]
# -2.2108777429467086
# TOTAL - Profit[20191113][t1302_20191113_082740.csv][12.99742476089751]
# 0
# TOTAL - Profit[20191113][t1302_20191113_112610.csv][12.99742476089751]
# 0
# TOTAL - Profit[20191113][t1302_20191113_118000.csv][12.99742476089751]
# 0
# TOTAL - Profit[20191113][t1302_20191113_163560.csv][12.99742476089751]
# 0
# TOTAL - Profit[20191113][t1302_20191113_298690.csv][12.99742476089751]
# 0
# TOTAL - Profit[20191113][t1302_20191113_500041.csv][12.99742476089751]
# BUY [1360][100300][5050]
# SELL SUCCESS [1360][100400][5190]
# BUY [1360][101800][4945]
# SELL FAILED [1360][102100][4895]
# BUY [1360][102200][4885]
# SELL SUCCESS [1360][102300][4950]
# BUY [1360][104000][4920]
# SELL SUCCESS [1360][104100][4955]
# BUY [1360][104400][4910]
# SELL FAILED [1360][104800][4855]
# 5.511793994359989
# TOTAL - Profit[20191114][t1302_20191114_001360.csv][18.5092187552575]
# BUY [2720][101000][5590]
# SELL FAILED [2720][101100][5510]
# BUY [2720][101400][5580]
# SELL SUCCESS [2720][101400][5610]
# BUY [2720][102700][5440]
# SELL SUCCESS [2720][103200][5490]
# BUY [2720][123300][5420]
# SELL SUCCESS [2720][123600][5460]
# BUY [2720][134600][5380]
# SELL FAILED [2720][135100][5260]
# BUY [2720][135200][5230]
# SELL SUCCESS [2720][135400][5280]
# -2.4908279036123817
# TOTAL - Profit[20191114][t1302_20191114_002720.csv][16.01839085164512]
# 0
# TOTAL - Profit[20191114][t1302_20191114_003550.csv][16.01839085164512]
# 0
# TOTAL - Profit[20191114][t1302_20191114_003850.csv][16.01839085164512]
# 0
# TOTAL - Profit[20191114][t1302_20191114_005110.csv][16.01839085164512]
# BUY [19170][103700][7350]
# SELL FAILED [19170][104400][7250]
# -1.6905442176870749
# TOTAL - Profit[20191114][t1302_20191114_019170.csv][14.327846633958044]
# BUY [33180][100200][9240]
# SELL SUCCESS [33180][100300][9360]
# -4.3496790984177895
# TOTAL - Profit[20191114][t1302_20191114_033180.csv][9.978167535540255]
# 0
# TOTAL - Profit[20191114][t1302_20191114_035420.csv][9.978167535540255]
# 0
# TOTAL - Profit[20191114][t1302_20191114_063160.csv][9.978167535540255]
# 0
# TOTAL - Profit[20191114][t1302_20191114_336260.csv][9.978167535540255]
#
# Process finished with exit code 0
#

    def is_trade(self, debug):
        is_trade = ''
        if self.index == 0:
            self.index += 1
            return

        시간차이 = int(self.df['시간'][self.index]) - int(self.df['시간'][self.index - 1])
        거래량차이 = int(self.df['거래량'][self.index]) - int(self.df['거래량'][self.index - 1])
        이전_시간_매수_매도_차이 = int(self.df['매수잔량'][self.index - 1]) - int(self.df['매도잔량'][self.index - 1])
        현재_시간_매수_매도_차이 = int(self.df['매수잔량'][self.index]) - int(self.df['매도잔량'][self.index])
        이전시간_현재시간_매수_매도_차이 = 현재_시간_매수_매도_차이 - 이전_시간_매수_매도_차이

        self.거래량_차이_리스트.append(거래량차이)
        self.현재_시간_매수_매도_차이_리스트.append(현재_시간_매수_매도_차이)
        self.이전시간_현재시간_매수_매도_차이_리스트.append(이전시간_현재시간_매수_매도_차이)

        if 거래량차이 > self.max_volume:
            self.max_volume = 거래량차이;

        남은매수대금 = (현재_시간_매수_매도_차이 * 거래량차이) / 100000000

        if debug is True:
            print('[%s] [%s] 거래량차이[%s] 남은매수대금[%s] 현재_차이[%s] 이전_차이[%s] DIFF_차이[%s] 시간차이[%s]' % (
            self.df['시간'][self.index], self.df['등락율'][self.index], 거래량차이, 남은매수대금, 현재_시간_매수_매도_차이, 이전_시간_매수_매도_차이,
            이전시간_현재시간_매수_매도_차이, 시간차이))

        if self.is_buy is False \
            and 이전시간_현재시간_매수_매도_차이 > 0 \
            and 현재_시간_매수_매도_차이 > 0 \
            and self.df['등락율'][self.index] > self.df['등락율'][self.index - 1] \
            and self.df['등락율'][self.index] > 0 \
            and 남은매수대금 > 10 \
            and int(self.df['등락율'][self.index]) <= 20:
            self.buy_list.append([self.index])
            self.real_buy_percent = float(self.df['등락율'][self.index])
            self.등략율_list.append(self.df['등락율'][self.index])
            self.is_buy = True
            self.preBuyPrice = int(self.df['종가'][self.index])
            if debug is True:
                print('============== Buy')
            if self.index == len(self.df.index) - 1:
                is_trade = 'buy'

        if self.is_buy is True and 남은매수대금 < 0:
            self.real_buy_percent = 50
            self.is_buy = False
            profit = (get_percent(self.preBuyPrice, int(self.df['종가'][self.index])) - 0.33)
            if profit > 0:
                self.test_success_sell_index_list.append(self.index)
                self.test_success_sell_price_list.append(self.df['등락율'][self.index])
                if debug is True:
                    print('============== SUCCESS Sell[%s][%s][%s]' % (self.preBuyPrice, int(self.df['종가'][self.index]), profit))
                if self.index == len(self.df.index) - 1:
                    is_trade = 'sell_success'
            else:
                self.test_fail_sell_index_list.append(self.index)
                self.test_fail_sell_price_list.append(self.df['등락율'][self.index])
                if debug is True:
                    print('============== FAILED Sell[%s][%s][%s]' % (self.preBuyPrice, int(self.df['종가'][self.index]), profit))
                if self.index == len(self.df.index) - 1:
                    is_trade = 'sell_failed'
            self.profit += profit

        if self.is_buy is True and float(self.df['등락율'][self.index]) > self.real_buy_percent + 1.0:

            self.real_buy_percent = 50
            self.is_buy = False
            self.test_success_sell_index_list.append(self.index)
            self.test_success_sell_price_list.append(self.df['등락율'][self.index])
            profit = (get_percent(self.preBuyPrice, int(self.df['종가'][self.index])) - 0.33)
            self.profit += profit
            if debug is True:
                print('============== SUCCESS Sell[%s][%s][%s]' % (self.preBuyPrice, int(self.df['종가'][self.index]), profit))
            if self.index == len(self.df.index)-1:
                is_trade = 'sell_success'

        if self.is_buy is True and float(self.df['등락율'][self.index]) < self.real_buy_percent - 1.0:
            if debug is True:
                print('============== Failed Sell')

            self.real_buy_percent = 50
            self.is_buy = False
            self.test_fail_sell_index_list.append(self.index)
            self.test_fail_sell_price_list.append(self.df['등락율'][self.index])
            profit = (get_percent(self.preBuyPrice, int(self.df['종가'][self.index])) - 0.33)
            self.profit += profit
            if debug is True:
                print('============== FAILED Sell[%s][%s][%s]' % (self.preBuyPrice, int(self.df['종가'][self.index]), profit))
            if self.index == len(self.df.index)-1:
                is_trade = 'sell_failed'

        self.index += 1
        return is_trade

