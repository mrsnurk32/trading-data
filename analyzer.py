import pandas as pd
import numpy as np
import sqlite3 as sql
import time


#This class will be incharge of gatharing analytical data for strategy class

# 1. Provides current statistics for trading desicion

# 2. Provides moving data like MA (under development)

# 3. Provides data from financial report (under development)
class Metrics:

    def __init__(self):
        pass


    @staticmethod
    def quick_frame(conn,ticker,rows = 510):
        querry = 'SELECT * FROM {} ORDER BY rowid DESC LIMIT {}'.format(ticker,rows)
        frame = pd.read_sql_query(querry, conn).sort_index(ascending = False)
        frame.reset_index(drop = True, inplace = True)
        return frame


    @staticmethod
    def get_frame(ticker,simple = True):

        conn = Metrics.connect_to_db()
        df = Metrics.get_stock_df(ticker,conn,simple = False)

        if simple is False:
            df = Metrics.returns(df)
            df = Metrics.ret_in_n_hour(df)

            period_sequence = [8,100]

            for period in period_sequence:
                df = Metrics.return_over_period(df,period)

        return df



    #This part transforms data from sql to pandas dataframe
    @staticmethod
    def connect_to_db():

        db_file_path = 'stock_data/fin_data.db'.format()

        sqlite3_conn = None

        try:
            sqlite3_conn = sql.connect(db_file_path)
            return sqlite3_conn
        except Error as err:
            print(err)

            if sqlite3_conn is not None:
                sqlite3_conn.close()

    @staticmethod
    def get_stock_df(ticker,conn,simple = True):
            #Returns pandas df
            querry = "SELECT * from {}".format(ticker)
            df = pd.read_sql_query(querry, conn)

            if simple:
                del df['spread']
                del df['tick_volume']
                del df['real_volume']

            return df

    @staticmethod
    def resample(frame):

        frame.time = pd.to_datetime(frame.time)
        frame.set_index('time',inplace = True)
        df = frame.resample('D').agg({'open':'first',
                             'high':'max',
                             'low':'min',
                             'close':'last'}).dropna().reset_index()

        return df


    #The following part retrieves data from future and past periods
    @staticmethod
    def returns(df,increment = True):
        df['Returns'] = df.close.pct_change()
        if increment:df.Returns = df.Returns + 1
        return df

    @staticmethod
    def ret_in_n_hour(df, period=4):

        arr = df.close.values
        result = [v1 / v2 for v1,v2 in zip(arr[period:],arr)]
        for i in range(period):result.insert(-1,None)
        df['ret_in_{}h'.format(period)] = result

        return df

    @staticmethod
    def return_over_period(df, period=2):

        arr = df.close.values

        result = [v2 / v1 for v1,v2 in zip(arr,arr[period:])]

        for i in range(period):result.insert(0,None)
        df['h{}_ret'.format(period)] = result

        return df


    #Moving metrics
    #Moving average section

    @staticmethod
    def get_moving_average(df, period):

        df['MA{}'.format(ma)] = df.close.rolling(ma).mean()
        return df

    #Standard deviation section
    @staticmethod
    def standard_deviation(df,period):

        if 'Returns' not in df.columns:df = self.returns(df)
        df['STD{}'.format(std)] = temp.Return.rolling(std).std()

        return df


    #stochastic oscillator
    @staticmethod
    def stochastic(df):
        df['Min'] = df.low.rolling(14).min()
        df['close-min'] = df.close - df.Min
        df['H-L'] = df.high.rolling(14).max() - df.low.rolling(14).min()
        df['K'] = df['close-min'] / df['H-L'] * 100
        df['SlowK'] = (df['close-min'].rolling(3).sum() / df['H-L'].rolling(3).sum()) * 100
        return df

    #MACD
    @staticmethod
    def macd(frame):
        frame['EMA12'] = frame.close.ewm(span=12).mean()
        frame['EMA26'] = frame.close.ewm(span=26).mean()
        frame['Difference'] = frame.EMA12 - frame.EMA26
        frame['Signal'] = frame.Difference.ewm(span=9).mean() #9 period ema
        frame['Histogram'] = frame.Difference - frame.Signal
        return frame


    #Asset with high level of liquidity and long history
    @staticmethod
    def approved_tickers():
    c = sql.connect(
        '{}/stock_data/fin_data.db'.format(os.getcwd().replace('\\','/'))).cursor()

    table_lst = c.execute(
        "SELECT name FROM sqlite_master WHERE type='table';")

    table_lst = [i[0] for i in table_lst.fetchall() if i[0] != 'stock_info']

    approved = list()

    for ticker in table_lst:
        frame = mtr.get_frame(ticker,simple = False)
        if len(frame) < 10000:continue
        approved.append(ticker)

    confirmed = list()

    for ticker in approved:
        frame = mtr.quick_frame(mtr.connect_to_db(),ticker)
        if frame.real_volume.mean() > 10000:
            confirmed.append(ticker)

    pd.DataFrame({'tickers':confirmed}).to_csv('approved_tickers.csv',index = False)
