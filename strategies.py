import pandas as pd
from analyzer import Metrics as mtr
import datetime as dt
import numpy as np


class MACD_Simple:

    def __init__(self):
        self.strategy_name = 'MACD_SIMPLE'
    
    @staticmethod
    def get_strategy_frame(frame):
        frame = mtr.macd(frame)
        frame['MA_100'] = frame.close.rolling(100).mean()
        frame['Criteria'] = np.where(
            (frame['EMA12'] > frame['EMA26']) & (frame.close > frame['MA_100']), True,False
        )
        return frame




class MACD_Hourly:

    def __init__(self):

        self.magic = 100002
        self.active = True
        self.stop_loss = 0.04
        self.take_profit = 0.08


    def get_strategy_frame(self,frame, resample = False):

        frame = mtr.macd(frame)
        frame['Cross'] = np.where(
            (frame.Histogram > 0) & (frame.Histogram.shift(1) < 0),True,False)

        frame['Confirmed'] = np.where(
            (frame.Cross.shift(1) == True) & (frame.Histogram > frame.Histogram.shift(1)),True,False)

        frame['Buy'] = frame.Confirmed.shift(1)
        frame['Neg_hist'] = np.where(
            frame.Histogram < frame.Histogram.shift(1),True,False)

        frame['neg2inrow'] = np.where(
            (frame.Neg_hist == True) & (frame.Neg_hist.shift(1)==True),True,False)

        frame['Hist_below_0'] = frame.Histogram < 0

        frame['MA200'] = frame.close.rolling(200).mean()
        frame['MA200_crossed'] = np.where(
            (frame.MA200 < frame.close) & (frame.MA200.shift(1) > frame.close.shift(1)),True,False
        )


        frame = frame.iloc[200:].copy()

        frame = mtr.slope(frame)

        return frame


    def get_ticker_list(self):
        df = pd.read_csv('MACD_Hourly.csv')
        return df.ticker.values


    def condition(self,row):

        # if self.active and row.MA200_crossed and row.slope_25 > 0.01 and row.slope_12 > 0.01:
        #     return 'Buy'


        if self.active and row.Confirmed:
            return 'Buy'

        # if not self.active and row.neg2inrow or row.Hist_below_0:
        #     return 'Sell'


class MACD_Daily:

    def __init__(self):

        self.magic = 100001
        self.active = True
        self.stop_loss = 0.04
        self.take_profit = 0.08


    def get_strategy_frame(self,frame, resample = False):

        frame = mtr.resample(frame)

        frame = mtr.macd(frame)
        frame['Cross'] = np.where(
            (frame.Histogram > 0) & (frame.Histogram.shift(1) < 0),True,False)

        frame['Confirmed'] = np.where(
            (frame.Cross.shift(1) == True) & (frame.Histogram > frame.Histogram.shift(1)),True,False)

        frame['Buy'] = frame.Confirmed.shift(1)
        frame['Neg_hist'] = np.where(
            frame.Histogram < frame.Histogram.shift(1),True,False)

        frame['neg2inrow'] = np.where(
            (frame.Neg_hist == True) & (frame.Neg_hist.shift(1)==True),True,False)

        frame['Hist_below_0'] = frame.Histogram < 0

        frame = frame.iloc[26:].copy()

        return frame

    def get_ticker_list(self):
        df = pd.read_csv('MACD_Daily.csv')
        return df.ticker.values


    def condition(self,row):

        if self.active and row.Confirmed:
            return 'Buy'

        # if not self.active and row.neg2inrow or row.Hist_below_0:
        #     return 'Sell'


class Standard_strategy:

    def __init__(self,MA,slicer):
        self.MA = MA
        self.slicer = slicer
        self.magic = 100001


    def get_strategy_frame(self,frame):

        frame = m.stochastic(frame)
        frame['stoc_change'] = frame.SlowK.pct_change()
        frame['stoc_index'] = frame.K / frame.SlowK
        frame['STD50'] = frame.close.rolling(50).std()
        frame['STD100'] = frame.close.rolling(100).std()
        return frame


    def condition(self,row):

        if row.SlowK == 'nan':pass


        if row.SlowK > self.MA and row.SlowK < self.MA + self.slicer:
            if row.STD50 > row.STD100:
                return 'Buy'


