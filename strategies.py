import pandas as pd
import datetime as dt
import numpy as np


class MACD_Simple:
    
    @staticmethod
    def get_strategy_frame(frame):
        
        frame['EMA12'] = frame.close.ewm(span=12).mean()
        frame['EMA26'] = frame.close.ewm(span=26).mean()
        frame['Difference'] = frame.EMA12 - frame.EMA26
        frame['Signal'] = frame.Difference.ewm(span=9).mean() #9 period ema
        frame['Histogram'] = frame.Difference - frame.Signal
        frame['MA_100'] = frame.close.rolling(100).mean()
        frame['Criteria'] = np.where(
            (frame['EMA12'] > frame['EMA26']) & (frame.close > frame['MA_100']), True,False
        )
        return frame




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


