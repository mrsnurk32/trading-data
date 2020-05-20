# Trader alpha 1.2.4
#
# Trader class accounts trading activity
# - Balance sheet report
# - Buy request
# - Sell request
# - Portfolio evaluation
# - Efficiency evaluation

import pandas as pd
import numpy as np
from file_manager import FileManager as fm
import os
fm.initialize()

class Trader:

    TRADING_DATA = []

    AMOUNT = None

    def __init__(self, risk=None, return_=None):
        self._balance = 0
        self._assets = 0
        self._risk = risk
        self._return = return_
        self._max_duration = 4

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self,value):
        self._balance += value
        return self._balance

    @property
    def balance_sheet(self):
        return pd.DataFrame(self.TRADING_DATA)


    def buy(self,time,price,amount,ticker):

        if self.balance - price * amount < 0:return 'Not enough credits'

        #Purchase data
        self.balance = (-amount * price)
        data = dict(
            time = time, ticker = ticker, buy_price = price,
            buy_amount = amount, sell_price = np.nan, sell_amount = np.nan
        )

        self.TRADING_DATA.append(data)
        self.AMOUNT = amount


    def sell(self,time,price,amount,ticker):

        if self.AMOUNT - amount < 0:return 'Not enough assets'


        self.balance = (amount * price)
        data = dict(
            time = time, ticker = ticker, buy_price = np.nan,
            buy_amount = np.nan, sell_price = price, sell_amount = amount
        )

        self.TRADING_DATA.append(data)



    def remaining_assets(self,ticker,asset_value=False):
        data = pd.DataFrame(self.TRADING_DATA)


        #data = pd.DataFrame(data,columns = self.COLUMNS)

        data = data[data.ticker == ticker]

        report = data.buy_amount.sum() - data.sell_amount.sum()
        report = report if asset_value == False else (
            report * fm.get_last_price(ticker))

        return report

    @property
    def total(self):
        data = pd.DataFrame(self.TRADING_DATA)
        assets = 0
        tickers = list(data.ticker.unique())
        for asset in tickers:
            assets += self.remaining_assets(asset,True)

        return assets + self.balance

    def get_last_price(self,ticker):
        return fm.get_last_price(ticker)


    @property
    def net_income(self):
        data = self.TRADING_DATA
        purchases = (data.buy_price * data.buy_amount).sum()
        sales = (data.sell_price * data.sell_amount).sum()
        report = self.total - (self.total + (purchases-sales))

        return report
