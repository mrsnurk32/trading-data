import pandas as pd
import numpy as np
import sqlite3 as sql
import matplotlib.pyplot as plt



class Analyzer:

    def __init__(self):
        self._capital = capital
        self._compound_return = None


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


    def get_stock_df(self,ticker,conn,simple = True):
            #Returns pandas df
            querry = "SELECT * from {}".format(ticker)
            df = pd.read_sql_query(querry, conn)

            if simple:
                del df['spread']
                del df['tick_volume']
                del df['real_volume']

            return df


    def get_stock_statistics(self,df):

        #Function returns dict with parameters for trading decision
        ma10 = np.mean(df.close.tail(10))
        ma100 = np.mean(df.close.tail(100))

        std8 = np.std(df.close.tail(8))
        std13 = np.std(df.close.tail(13))
        std21 = np.std(df.close.tail(21))

        return {
            'MA10':ma10,
            'MA100':ma100,
            'DiffMA':(ma10/ma100)-1,
            'std8':std8,
            'std13':std13,
            'std21':std21
        }


    def ret_in_n_hour(self,df):
        #Creates df with future returns
        df = df[['time','close']].copy()
        df['Returns'] = df.close.pct_change()

        df.Returns = df.Returns + 1

        temp = pd.DataFrame()

        for i in range(1,5):
            col = 'ret_in_{}h'.format(i)
            if i == 1:
                df[col]=df.Returns.iloc[i:].reset_index(drop=True)
            else:
                prev = 'ret_in_{}h'.format(i-1)
                df[col] = df[prev] * df.Returns.iloc[i:].reset_index(drop=True)

        return df


    def return_over_period(self,df, period=20):
        df['Returns'] = df.close.pct_change()
        #the function returns cumulative income over (n) amount of past periods
        period = period
        per_name = 'h'
        df = df[['time','close','Returns']].copy()
        df.Returns = df.Returns + 1
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

    @staticmethod
    def get_moving_average(df,**kwargs):

        col = 'close'

        for k,v in kwargs.items():
            column_name = '{}{}'.format(k,v)
            df[column_name] = df.close.rolling(v).mean()

        return df

a = Analyzer()
