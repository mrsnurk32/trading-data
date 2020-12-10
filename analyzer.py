import pandas as pd
import numpy as np
import sqlite3 as sql
import time
import matplotlib.pyplot as plt
import os


class CustomError(Exception):
    pass

class MetricsDB:
    #The class will try to establish connection with DB

    def connect_to_db(self):

        db_file_path = 'stock_data/fin_data.db'.format()

        sqlite3_conn = None

        try:

            sqlite3_conn = sql.connect(db_file_path)
            return sqlite3_conn
        
        except Error as err:

            print(err)
            if sqlite3_conn is not None:
                sqlite3_conn.close()

    def stock_list(self):
       raise NotImplemented


class TickerList(MetricsDB):
    #Returns stock list as list

    def __init__(self):

        self._ticker_list = self.connect_to_db()


    @property
    def ticker_list(self):

        c = self._ticker_list.cursor()

        table_lst = c.execute(
            "SELECT name FROM sqlite_master WHERE type='table';")

        table_lst = [i[0] for i in table_lst.fetchall() if i[0] != 'stock_info']
        table_lst = [i.split('_')[0] for i in table_lst if '1h' in i]
        #Must return list of tickers that are located in DB
        return table_lst

    
    def approved_tickers(self):
        raise NotImplemented

    
class GetFrame(TickerList):
    #Gets ticker data from DB by creating querries

    ACCEPTED_TIME_FRAMES = ('1h', '1D')

    COLUMN_LIST = (
        'time','open', 'high', 'low',
        'close', 'tick_volume', 'spread',
        'real_volume'
    )

    #lisf of columns to be deleted if column list == default
    DEFAULT_COLUMN_LIST = (
        'tick_volume', 'spread', 'real_volume'
    )

    MANDATORY_COLUMNS = (
        'time', 'close'
    )

    def __init__(self):
        super().__init__()
        self.conn = self.connect_to_db()


    def ticker_is_valid(self, ticker, time_frame):

        if ticker not in self.ticker_list:
            raise Exception('Ticker is not in the list')

        if time_frame not in self.ACCEPTED_TIME_FRAMES:
            raise Exception(f'Time frame for "{ticker} is not supported"')

        return True


    def validate_column(self, col, col_lst):

        if col not in col_lst:
            raise Exception(f"Column {col} not found in data set \n {self.COLUMN_LIST} - list of acceptable columns")

    
    def get_frame(self, ticker, rows=None, time_frame='1h', column_list = '*'):

        if self.ticker_is_valid(ticker, time_frame):

            if type(column_list) is list:

                #Checks if every column is valid for querry
                [self.validate_column(col = col,col_lst = self.COLUMN_LIST) for col in column_list]
                
                #Checks if required columns are present in the list
                [self.validate_column(col = col, col_lst = column_list) for col in self.MANDATORY_COLUMNS]
                column_list = ', '.join(column_list)
          
            ticker = ticker + '_' + time_frame
            querry = f'SELECT {column_list} FROM {ticker} ORDER BY rowid DESC'

            if rows is not None:
                querry += f' LIMIT {rows}'

            frame = pd.read_sql_query(querry, self.conn).sort_index(ascending = False)
            frame.reset_index(drop = True, inplace = True)

            return frame



        


class Metrics(GetFrame):

    def __init__(self):
        super().__init__()





# class Metrics:

#     def __init__(self):
#         pass




#     @staticmethod
#     def quick_frame(conn,ticker,time_frame = '1h'):
#         ticker = ticker + '_' + time_frame
#         rows = 510
#         querry = 'SELECT * FROM {} ORDER BY rowid DESC LIMIT {}'.format(ticker,rows)
#         frame = pd.read_sql_query(querry, conn).sort_index(ascending = False)
#         frame.reset_index(drop = True, inplace = True)
#         return frame

#     @staticmethod
#     def get_frame(ticker,simple,time_frame):



#         conn = Metrics.connect_to_db()
#         df = Metrics.get_stock_df(ticker,conn,simple,time_frame)
#         df.time = pd.to_datetime(df.time)
#         if simple is False:
#             df = Metrics.returns(df)
#             df = Metrics.ret_in_n_hour(df)

#             period_sequence = [8,100]

#             for period in period_sequence:
#                 df = Metrics.return_over_period(df,period)

#         return df


#     #This part transforms data from sql to pandas dataframe
#     @staticmethod


#     @staticmethod
#     def get_stock_df(ticker,conn,simple,time_frame = '1h'):


#         ticker = ticker + '_' + time_frame

#         #Returns pandas df
#         querry = "SELECT * from {}".format(ticker)
#         df = pd.read_sql_query(querry, conn)

#         if simple:
#             del df['spread']
#             del df['tick_volume']
#             del df['real_volume']

#         return df

#     @staticmethod
#     def resample(frame):


#         frame.time = pd.to_datetime(frame.time)
#         frame.set_index('time',inplace = True)
#         df = frame.resample('D').agg({'open':'first',
#                              'high':'max',
#                              'low':'min',
#                              'close':'last'}).dropna().reset_index()

#         return df


#     #The following part retrieves data from future and past periods
#     @staticmethod
#     def returns(df,increment = True):


#         df['Returns'] = df.close.pct_change()
#         if increment:df.Returns = df.Returns + 1
#         return df

#     @staticmethod
#     def ret_in_n_hour(df, period=4):


#         arr = df.close.values
#         result = [v1 / v2 for v1,v2 in zip(arr[period:],arr)]
#         for i in range(period):result.insert(-1,None)
#         df['ret_in_{}h'.format(period)] = result

#         return df

#     @staticmethod
#     def return_over_period(df, period=2):


#         arr = df.close.values

#         result = [v2 / v1 for v1,v2 in zip(arr,arr[period:])]

#         for i in range(period):result.insert(0,None)
#         df['h{}_ret'.format(period)] = result

#         return df


#     #Moving metrics
#     #Moving average section

#     @staticmethod
#     def get_moving_average(df, period):


#         df['MA{}'.format(ma)] = df.close.rolling(ma).mean()
#         return df

#     #Standard deviation section
#     @staticmethod
#     def standard_deviation(df,period):


#         if 'Returns' not in df.columns:df = self.returns(df)
#         df['STD{}'.format(std)] = temp.Return.rolling(std).std()

#         return df


#     #stochastic oscillator
#     @staticmethod
#     def stochastic(df):


#         df['Min'] = df.low.rolling(14).min()
#         df['close-min'] = df.close - df.Min
#         df['H-L'] = df.high.rolling(14).max() - df.low.rolling(14).min()
#         df['K'] = df['close-min'] / df['H-L'] * 100
#         df['SlowK'] = (df['close-min'].rolling(3).sum() / df['H-L'].rolling(3).sum()) * 100
#         return df

#     #MACD
#     @staticmethod
#     def macd(frame):


#         frame['EMA12'] = frame.close.ewm(span=12).mean()
#         frame['EMA26'] = frame.close.ewm(span=26).mean()
#         frame['Difference'] = frame.EMA12 - frame.EMA26
#         frame['Signal'] = frame.Difference.ewm(span=9).mean() #9 period ema
#         frame['Histogram'] = frame.Difference - frame.Signal
#         return frame


#     @staticmethod
#     def slope(frame):

#         frame['slope_25'] = (frame.close - frame.close.shift(25)) / 25
#         frame['slope_12'] = (frame.close - frame.close.shift(12)) / 12

#         return frame


#     #Asset with high level of liquidity and long history
#     @staticmethod
#     def approved_tickers():


#         c = sql.connect(
#             '{}/stock_data/fin_data.db'.format(os.getcwd().replace('\\','/'))).cursor()

#         table_lst = c.execute(
#             "SELECT name FROM sqlite_master WHERE type='table';")

#         table_lst = [i[0] for i in table_lst.fetchall() if i[0] != 'stock_info']

#         approved = list()

#         for ticker in table_lst:
#             frame = mtr.get_frame(ticker,simple = False)
#             if len(frame) < 10000:continue
#             approved.append(ticker)

#         confirmed = list()

#         for ticker in approved:
#             frame = mtr.quick_frame(mtr.connect_to_db(),ticker)
#             if frame.real_volume.mean() > 10000:
#                 confirmed.append(ticker)

#         pd.DataFrame({'tickers':confirmed}).to_csv('approved_tickers.csv',index = False)




# class BackTester(Metrics):
    
#     def __init__(self, take_profit, stop_loss):
        
#         Metrics.__init__(self)
#         #stop loss and take profit are expressed with integers ex. 1 = 1%
#         self.take_profit = take_profit
#         self.stop_loss = stop_loss
        

#     def test_strategy(self, frame):
#         #frame should be passed with Criteria column.

#         initial_price = frame.close.iloc[0]
#         frame['ret'] = frame.close.pct_change()
        
#         #row_before checks if previus row is False or True
#         row_before = lambda row: frame.Criteria.iloc[row.Index-1]

#         #Checks if previous stop loss is lesser
#         validate_sl = lambda row, sl: row.close - (self.stop_loss/row.close*100) if row.close - (self.stop_loss/row.close*100) >= sl else sl
#         sl = None
        
#         data = list()
        
        
#         for row in frame.itertuples():

#             if row.Criteria and not row_before(row):
#                 sl = row.close - (self.stop_loss/row.close*100)
#                 data.append(sl)
            
            
#             if row.Criteria and row_before(row):
#                 sl = validate_sl(row,sl)
#                 data.append(sl)
                
            
#             if not row.Criteria:
#                 data.append(np.nan)
                
                
#         frame['stop_loss'] = data
#         frame['holding_asset'] = np.where((frame.Criteria) & (frame.close > frame.stop_loss),True,False)        
#         frame['Strategy_returns'] = initial_price * (1 + (frame['holding_asset'].shift(1) * frame['ret'] )).cumprod()      
                        
#         return frame
        

#     @staticmethod
#     def evaluate_strategy(frame):
#     #required columns [close, ret]
    
#         def get_data(df, year = None):
            
#             if year is not None:
#                 df = df[df.time.dt.year == year].copy()
                
#             return dict(
#                 strategy_net_income = df.Strategy_returns.iloc[-1] / df.Strategy_returns.iloc[0] -1,
#                 sharpe_ratio = (df.ret.mean() / df.ret.std())*np.sqrt(len(df)),
#                 max_drop_down = (df.Strategy_returns.min() / df.Strategy_returns.iloc[0]) - 1,
#                 asset_net_income = df.close.iloc[-1] / df.close.iloc[0] - 1,
#                 asset_peak = df.close.max() / df.close.iloc[0] -1,
#                 asset_min = df.close.min() / df.close.iloc[0] -1
#             )
       
#         frame = frame.iloc[1:]
#         total_result = get_data(df = frame)
        
#         year_list = frame.time.dt.year.unique()


#         compare_list = list(map(lambda year:get_data(df = frame, year = year),year_list))
        
#         return pd.DataFrame(compare_list , index = year_list)
            
        
#     @staticmethod
#     def visualize(frame):
        
#         plt.rcParams["figure.figsize"] = [20, 10]
#         return frame[['close', 'Strategy_returns']].plot(grid=True, kind='line', title="Strategy vs Buy & Hold", logy=True)
        

