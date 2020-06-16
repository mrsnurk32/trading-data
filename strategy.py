import pandas as pd
from analyzer import Metrics as mtr
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
from file_manager import FileManager as fm
import os
from trader import Trader

fm.initialize()

#Designed for back testing
class TradingBot:

    def __init__(self):
        #self.trader = Trader()
        self.back_trader = Trader()
        self.frame_manager = mtr
        self.risk = 0.93
        self.desired_ret = 1.12
        self.strategy = None
        self.BUY = []
        self.SELL = []
        self.frame = None

    def visualize(self):
        f, (ax1,ax2,ax3) = plt.subplots(3,1, sharex=True,figsize=(20,15))

        ax1.set_title('Price chart', fontsize=18)
        ax1.plot(self.frame.index,self.frame.MA200,label = 'MA200')
        ax1.plot(self.frame.index,self.frame.close,label = 'close')
        # ax1.plot(self.frame.index,self.frame.low,label = 'low')
        # ax1.plot(self.frame.index,self.frame.high,label = 'high')
        # ax1.plot(self.frame.index,self.frame.open,label = 'open')
        buy = pd.DataFrame(self.BUY).set_index('index')
        sell = pd.DataFrame(self.SELL).set_index('index')
        ax1.scatter(buy.index,buy.price,color = 'green',label = 'Buy')
        ax1.scatter(sell.index,sell.price,color = 'red',label = 'Sell')
        ax1.legend()
        ax1.grid(color='#a6a6a6', linestyle='-', linewidth=1)

        ax2.set_title('Indicator', fontsize=18)
        ax2.plot(self.frame.index,self.frame.Signal,label = 'Signal')
        ax2.plot(self.frame.index,self.frame.Difference, label = 'Difference')
        ax2.bar(self.frame.index,self.frame.Histogram,color='blue')

        cross = self.frame[self.frame.Cross == True]
        ax2.bar(cross.index,cross.Histogram,color='red')

        confirmed = self.frame[self.frame.Confirmed == True]
        ax2.bar(confirmed.index,confirmed.Histogram,color='yellow')

        buy = self.frame[self.frame.Buy == True]
        ax2.bar(buy.index,buy.Histogram,color='green')

        neg = self.frame[self.frame.Neg_hist == True]
        ax2.bar(neg.index,neg.Histogram,color='grey')

        neg2 = self.frame[self.frame.neg2inrow == True]
        ax2.bar(neg2.index,neg2.Histogram,color='orange')
        ax2.legend()
        balance = pd.DataFrame(self.back_trader.BALANCE)
        balance['index'] = sell.index
        balance = balance.set_index('index')
        ax3.plot(balance.index, balance.balance)

        ax3.legend()
        return plt.show()


    def back_test(self,ticker,test = False):

        if self.strategy is None:
            return 'Add strategy to TradingBot class'


        self.back_trader = Trader()
        self.back_trader.balance = 100000
        frame = self.frame_manager.get_frame(ticker)
        if test:frame = frame.iloc[-1200:].copy()
        #frame = self.frame_manager.resample(frame)
        #frame['time'] =pd.to_datetime(frame.time)
        frame = self.strategy.get_strategy_frame(frame)

        self.frame = frame
        #frame = frame.iloc[-400:].copy()
        flag = True
        buy_itteration = 0
        buy_price = None


        def buy(row,ticker):

            self.strategy.active = False
            date = row.time

            price = row.open * 1.001
            amount = self.back_trader.balance // price
            if amount == 0:
                return False
            self.back_trader.buy(date,price, amount, ticker)
            self.BUY.append(dict(
                index = row.Index,price = price
            ))
            #print('Date',row.time,'Open',row.open, 'Balance',self.back_trader.balance,'Amount',amount,'Price',price,'Buy')
            #print('Buy:',price,amount,date)
            return price


        def sell(row,price,ticker,reason = None):

            self.strategy.active = True
            amount = self.back_trader.ASSETS[ticker]
            date = row.time
            self.back_trader.sell(date,price,amount , ticker, reason)
            #print('Date',row.time,'Open',row.open, 'Balance',self.back_trader.balance,'Amount',amount,'Price',price,'Sell')
            flag = True
            buy_price = None
            self.SELL.append(dict(
                index = row.Index,price = price
            ))

            return flag,buy_price

        buy_iter = False
        sell_iter = False
        #for index, row in frame.iterrows():
        for row in frame.itertuples(index=True):

            if flag is True:
                if self.strategy.condition(row) == 'Buy':
                    buy_iter = True
                    flag = False
                    continue

            if buy_iter:
                buy_iter = False
                buy_price = buy(row,ticker)


                if buy_price is False:
                    #print('Not enough money')
                    flag = True
                    self.strategy.active = True
                    continue



            if flag == False:



                buy_itteration += 1
                if sell_iter:
                    price = row.open
                    flag, buy_price = sell(row,price,ticker,reason = 'strategy')
                    buy_itteration = 0
                    sell_iter = False
                    continue


                #risk justified
                low_ret = row.low / buy_price
                if low_ret < self.risk:

                    price = buy_price * self.risk
                    flag, buy_price = sell(row,price,ticker,reason = 'sl')
                    buy_itteration = 0
                    continue

                #return justified
                high_ret = row.high / buy_price

                if high_ret >= self.desired_ret:

                    price = buy_price * self.desired_ret
                    flag, buy_price = sell(row,price,ticker,reason = 'tp')
                    buy_itteration = 0
                    continue

                #duration justified
                if buy_itteration == 60:
                    price = row.close
                    flag, buy_price = sell(row,price,ticker,reason = 'duration')
                    buy_itteration = 0
                    continue

                #strategy condition justified
                if self.strategy.condition(row) == 'Sell':
                    sell_iter = True
                    continue
