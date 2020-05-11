import pandas as pd
import numpy as np
import sqlite3 as sql
import matplotlib.pyplot as plt
import time


#This class will be incharge of gatharing analytical data for strategy class

# 1. Provides current statistics for trading desicion

# 2. Provides moving data like MA (under development)

# 3. Provides data from financial report (under development)
class Analyzer:

    def __init__(self,capital):
        self._capital = capital
        self._compound_return = None


    @staticmethod
    def create_class(capital):

        var = Analyzer(capital)
        conn = var.connect_to_db()
        df = var.get_stock_df('YNDX',conn)
        alligator_df = var.alligator(df)
        df = var.get_moving_average(alligator_df,50,100)
        df = var.standard_deviation(df,50,100)
        df = var.returns(df)
        df = var.ret_in_n_hour(df)
        df = var.return_over_period(df)

        return df


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


    def get_stock_statistics(self, df):

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


    def get_moving_average(self, df, *args):

        col = 'close'

        for ma in args:
            column_name = 'MA{}'.format(ma)
            df[column_name] = df.close.rolling(ma).mean()

        return df


    def alligator(self, df):
        return self.get_moving_average(df,5,8,13)


    #Standard deviation section

    def standard_deviation(self,df,*args):

        col = 'close'

        temp = pd.DataFrame()
        temp['Return'] = df.close.pct_change()

        for std in args:
            column_name = 'STD{}'.format(std)
            df[column_name] = temp.Return.rolling(std).std()

        return df

    #Current metrics

    def current_stats(self):
        pass


if __name__ == '__main__':
    #default combination of analytic data
    t1 = time.time()
    frame = Analyzer.create_class(20000)
    t2 = time.time()

    result = t1 - t2
    print(frame.head(55))

    print(frame.columns)
else:
    pass
