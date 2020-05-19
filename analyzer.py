import pandas as pd
import numpy as np
import sqlite3 as sql
import matplotlib.pyplot as plt
import time
from functools import reduce


#This class will be incharge of gatharing analytical data for strategy class

# 1. Provides current statistics for trading desicion

# 2. Provides moving data like MA (under development)

# 3. Provides data from financial report (under development)
class Metrics:

    def __init__(self):
        pass


    @staticmethod
    def get_frame(ticker,simple = False):

        conn = Metrics.connect_to_db()
        df = Metrics.get_stock_df(ticker,conn)

        if simple is False:
            df = Metrics.returns(df)
            df = Metrics.ret_in_n_hour(df)

            period_sequence = [1,2,3,5,8,13,100]

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

    #The following part retrieves data from future and past periods
    @staticmethod
    def returns(df,increment = True):
        df['Returns'] = df.close.pct_change()
        if increment:df.Returns = df.Returns + 1
        return df

    @staticmethod
    def ret_in_n_hour(df, period=4):
        #Creates df with future returns

        #df['Returns'] = df.close.pct_change()

        if 'Returns' not in df.columns:df = self.returns(df)
        temp = df[['time','close','Returns']].copy()


        period += 1

        for i in range(1,period):
            col = 'ret_in_{}h'.format(i)
            if i == 1:
                temp[col] = temp.Returns.shift(-i)
            else:
                prev = 'ret_in_{}h'.format(i-1)
                temp[col] = temp[prev] * temp.Returns.shift(-i)

        for i in ['time','close','Returns']:
            del temp[i]

        df = pd.concat([df, temp], axis=1)

        return df

    @staticmethod
    def return_over_period(df, period=2):
        if 'Returns' not in df.columns:df = self.returns(df)
        #the function returns income over (n) amount of past periods

        arr = df.Returns.values

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

    #Current metrics

    def current_stats(self):
        pass
