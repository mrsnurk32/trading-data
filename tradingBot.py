from analyzer import Metrics as mtr
import MetaTrader5 as mt5
from file_manager import FileManager as fm

#Strategies
from strategies import MACD_Daily as MD
from strategies import MACD_Hourly as MH


import pandas as pd
import numpy as np
import sqlite3 as sql

import datetime as dt
from datetime import datetime
import pytz
import time

import os


class Bot:

    def __init__(self,d_strategy,h_strategy,m_strategy):

        self.d_strategy = d_strategy
        self.h_strategy = h_strategy
        self.m_strategy = m_strategy

        self.active = None



    def open_positions_exist(self):

        positions=mt5.positions_get()
        if len(positions) > 0:
            self.active = False
            return False
        else:
            self.active = True
            return True



    def is_active(self):
        return self.open_positions_exist()



    def buy(self,ticker,strategy):

        stop_loss = strategy.stop_loss
        take_profit = strategy.take_profit

        account_info = mt5.account_info()
        balance = account_info.margin_free - 1000

        symbol_info = mt5.symbol_info(ticker)
        price = mt5.symbol_info(ticker).ask
        volume = balance // price

        point=mt5.symbol_info(ticker).point

        #stop loss
        x = (price - price * stop_loss)
        y = round((x - price)/-point,0)
        stop = (price - point*y)
        stop = round(stop,2)
        #take profit
        x = (price + price * take_profit)
        y = round((x - price)/point,0)
        take = (price + point*y)

        request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": ticker,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY,
                "price": price,
                "sl":stop,
                "tp":take,
                "deviation": 5,
                "magic": 234001,
                "comment": "python script open",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }

        result = mt5.order_check(request)
        print(result)
        #if result._asdict()['comment'] == 'Done':
            #result = mt5.order_send(request)
            #print(result.retcode)

        return result


bot = Bot(
    d_strategy = MD(),
    h_strategy = None,
    m_strategy = None
    )


if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()


#Update files

fm = fm()
# if datetime.today().hour == 8:
#
#     fm.update_init(time_frame = '1h')
#     fm.update_init(time_frame = 'min5')


#Update stats - saturday


#timer before trading session starts


hour = 10


time_until = dt.timedelta(hours = 10) -dt.timedelta(
    hours = datetime.today().hour,
    minutes = datetime.today().minute,
    seconds = datetime.today().second
)

time_until = time_until.total_seconds()

print(time_until)

#time.sleep(time_until)

trading_hours = [i for i in range(0,24)]

#Daily strategy
lst = bot.d_strategy.get_ticker_list()

for ticker in lst:

    print('Ticker:',ticker)
    if bot.is_active():
        df = fm.download_stock(ticker = ticker,rows = 40,time_frame = 'd1',for_trading = True)
        df = bot.d_strategy.get_strategy_frame(df)
        print(df.iloc[-2:])
        if df.Confirmed.iloc[-1]:
            bot.buy(ticker,bot.d_strategy)

quit()

#loop -> m & h strategy
while True:


    if datetime.today().hour not in trading_hours:
        print('Trading session is over')
        quit()


    h = datetime.today().hour
    m = datetime.today().minute
    s = datetime.today().second

    print(m)
    if m == 0 and h < 5:
        lst = bot.h_strategy.get_ticker_list()
        hour += 1
        print('next hour:',hour)
        print(datetime.today())


        #take action on h basis
        for ticker in lst:
            print('Ticker:',ticker)
            if bot.is_active():
                df = fm.download_stock(
                    ticker = ticker,rows = 40,time_frame = '1h',
                    for_trading = True)
                df = bot.h_strategy.get_strategy_frame(df)
                print(df)
                if df.Confirmed.iloc[-1]:
                    bot.Buy(ticker,bot.h_strategy)

    #take action on 5m basis



    m = str(datetime.today().minute)[-1]
    s = datetime.today().second

    if int(m) >= 5:
        time_left = dt.timedelta(
            minutes = 10) - dt.timedelta(minutes = int(m),seconds = s)

    if int(m) < 5:
        time_left = dt.timedelta(
            minutes = 5) - dt.timedelta(minutes = int(m),seconds = s)


    print(datetime.today())
    time_left = time_left.total_seconds()
    print(time_left)
    time.sleep(time_left)
