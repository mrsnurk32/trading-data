import pandas as pd
from analyzer import Metrics as m
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
from file_manager import FileManager as fm
import os
from trader import Trader

#visualization libraries
import plotly.graph_objects as go
from plotly.offline import init_notebook_mode, iplot
from plotly import tools
from plotly.subplots import make_subplots

fm.initialize()

class Standard_strategy:

    def __init__(self,MaIndex,StdIndex,h8_ret):
        self.MaIndex = MaIndex # Index < 1.1
        self.StdIndex = StdIndex # Index < 1
        self.h8_ret = h8_ret # Index > 0

    def get_strategy_frame(self,frame):
        frame['STD50'] = frame.close.rolling(50).std()
        frame['STD100'] = frame.close.rolling(100).std()
        frame['MA50'] = frame.close.rolling(50).mean()
        frame['MA500'] = frame.close.rolling(500).mean()

        frame['IndexMA'] = frame.MA50 / frame.MA500
        frame['IndexSTD'] = frame.STD50 / frame.STD100

        return frame

    def condition(self,row):
        if row.MA50/row.MA500 < 1.1:
            if row.STD50 / row.STD100 < self.StdIndex:
                if row.MA50 > row.MA500:
                    if row.h8_ret != np.nan:
                        if row.h8_ret > 0:
                            return True
        else:
            return False



class TradingBot:

    def __init__(self):
        #self.trader = Trader()
        self.back_trader = Trader()
        self.frame_manager = m
        self.risk = 0.97
        self.desired_ret = 1.02
        self.strategy = Standard_strategy(MaIndex = 1.1,StdIndex = 1,h8_ret = 0)

    def back_test(self,ticker):

        self.back_trader = Trader()
        self.back_trader.balance = 10000
        frame = self.frame_manager.get_frame(ticker)
        frame['time'] =pd.to_datetime(frame.time)

        frame = self.strategy.get_strategy_frame(frame)

        # frame = frame.iloc[-1200:].copy()

        flag = True
        buy_itteration = 0
        buy_price = None

        balance = {}

        def balance_frame(balance):
            return pd.DataFrame(
                list(balance.items()),columns = ['time','income'])


        def buy(row,ticker):

            date = row.time

            price = row.close * 1.001
            amount = self.back_trader.balance // price
            if amount == 0:
                return False

            self.back_trader.buy(date,price, amount, ticker)
            #print('Buy:',price,amount,date)
            return price


        def sell(row,price,ticker):
            date = row.time

            amount = self.back_trader.remaining_assets(ticker)

            self.back_trader.sell(date,price,amount , ticker)

            flag = True
            buy_price = None

            val = self.back_trader.balance

            balance[date] = val
            return flag,buy_price


        #for index, row in frame.iterrows():
        for row in frame.itertuples(index=False):

            #if row.STD50 / row.STD100 < 1 and row.MA50 > row.MA500 and row['8h_ret'] > 0 and row.MA50/row.MA500 < 1.1 and flag == True:
            if flag is True:
                if self.strategy.condition(row):

                    flag = False
                    buy_price = buy(row,ticker)
                    if buy_price is False:
                        print('Wiped out')
                        break
                    continue

            if flag == False:
                buy_itteration += 1
                #risk justified
                low_ret = row.low / buy_price
                if low_ret < self.risk:

                    price = buy_price * self.risk
                    flag, buy_price = sell(row,price,ticker)
                    buy_itteration = 0
                    continue

                #return justified
                high_ret = row.high / buy_price

                if high_ret > self.desired_ret:

                    price = buy_price * self.desired_ret
                    flag, buy_price = sell(row,price,ticker)
                    buy_itteration = 0
                    continue

                #duration justified
                if buy_itteration == 100:
                    price = row.close
                    flag, buy_price = sell(row,price,ticker)
                    buy_itteration = 0
                    continue

        return balance_frame(balance)
