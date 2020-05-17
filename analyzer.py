import pandas as pd
import numpy as np
import sqlite3 as sql
import matplotlib.pyplot as plt
import time


#This class will be incharge of gatharing analytical data for strategy class

# 1. Provides current statistics for trading desicion

# 2. Provides moving data like MA (under development)

# 3. Provides data from financial report (under development)
class Metrics:

    def __init__(self):
        pass


    @staticmethod
    def get_frame(ticker):

        conn = Metrics.connect_to_db()
        df = Metrics.get_stock_df(ticker,conn)

        df = var.returns(df)
        df = var.ret_in_n_hour(df)

        return df



    #This part transforms data from sql to pandas dataframe
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


    def get_stock_df(self, ticker,conn,simple = True):
            #Returns pandas df
            querry = "SELECT * from {}".format(ticker)
            df = pd.read_sql_query(querry, conn)

            if simple:
                del df['spread']
                del df['tick_volume']
                del df['real_volume']

            return df

    #The following part retrieves data from future and past periods
    def returns(self,df,increment = True):
        df['Returns'] = df.close.pct_change()
        if increment:df.Returns = df.Returns + 1
        return df


    def ret_in_n_hour(self, df, period=4):
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


    def return_over_period(self, df, period=2):
        if 'Returns' not in df.columns:df = self.returns(df)
        #the function returns income over (n) amount of past periods
        period = period
        per_name = 'h'

        vals = list(df.Returns.values)

        vals = [i for i in vals if str(i) != 'nan']

        result_lst = list()

        #list one line shorter than df

        for i in range(len(vals)+1):

            if i < period:continue
            lst = vals[i-period:i]
            prev_val = None
            for j in lst:
                if prev_val == None:
                    prev_val = j
                    continue
                else:
                    prev_val = j * prev_val

            result_lst.append(prev_val)

        for i in range(period):result_lst.insert(0,None)

        col = '{}{}_ret'.format(period,per_name)
        df[col] = result_lst
        return df


    #Moving metrics
    #Moving average section


    def get_moving_average(self, df, period):

        df['MA{}'.format(ma)] = df.close.rolling(ma).mean()
        return df

    #Standard deviation section

    def standard_deviation(self,df,period):

        if 'Returns' not in df.columns:df = self.returns(df)
        df['STD{}'.format(std)] = temp.Return.rolling(std).std()

        return df

    #Current metrics

    def current_stats(self):
        pass


if __name__ == '__main__':
    pass
else:
    pass
    #default combination of analytic data
#     frame = Analyzer.create_class(20000)
