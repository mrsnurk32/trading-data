import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class BackTester:
    
    def __init__(self, take_profit, stop_loss):
        
        #stop loss and take profit are expressed with integers ex. 1 = 1%
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        

    def test_strategy(self, frame):
        #frame should be passed with Criteria column.

        initial_price = frame.close.iloc[0]
        frame['ret'] = frame.close.pct_change()
        
        #row_before checks if previus row is False or True
        row_before = lambda row: frame.Criteria.iloc[row.Index-1]

        #Checks if previous stop loss is lesser
        validate_sl = lambda row, sl: row.close - (self.stop_loss/row.close*100) if row.close - (self.stop_loss/row.close*100) >= sl else sl
        sl = None
        
        data = list()
        
        
        for row in frame.itertuples():

            if row.Criteria and not row_before(row):
                sl = row.close - (self.stop_loss/row.close*100)
                data.append(sl)
            
            
            if row.Criteria and row_before(row):
                sl = validate_sl(row,sl)
                data.append(sl)
                
            
            if not row.Criteria:
                data.append(np.nan)
                
                
        frame['stop_loss'] = data
        frame['holding_asset'] = np.where((frame.Criteria) & (frame.close > frame.stop_loss),True,False)        
        frame['Strategy_returns'] = initial_price * (1 + (frame['holding_asset'].shift(1) * frame['ret'] )).cumprod()      
                        
        return frame
        

    @staticmethod
    def evaluate_strategy(frame):
    #required columns [close, ret]
    
        def get_data(df, year = None):
            
            if year is not None:
                df = df[df.time.dt.year == year].copy()
                
            return dict(
                strategy_net_income = df.Strategy_returns.iloc[-1] / df.Strategy_returns.iloc[0] -1,
                sharpe_ratio = (df.ret.mean() / df.ret.std())*np.sqrt(len(df)),
                max_drop_down = (df.Strategy_returns.min() / df.Strategy_returns.iloc[0]) - 1,
                asset_net_income = df.close.iloc[-1] / df.close.iloc[0] - 1,
                asset_peak = df.close.max() / df.close.iloc[0] -1,
                asset_min = df.close.min() / df.close.iloc[0] -1
            )
       
        frame = frame.iloc[1:]
        total_result = get_data(df = frame)
        
        year_list = frame.time.dt.year.unique()


        compare_list = list(map(lambda year:get_data(df = frame, year = year),year_list))
        
        return pd.DataFrame(compare_list , index = year_list)
            
        
    @staticmethod
    def visualize(frame):
        
        plt.rcParams["figure.figsize"] = [20, 10]
        return frame[['close', 'Strategy_returns']].plot(grid=True, kind='line', title="Strategy vs Buy & Hold", logy=True)
        

