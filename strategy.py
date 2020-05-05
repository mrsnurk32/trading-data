import pandas as pd
import numpy as np
import sqlite3 as sql
import matplotlib.pyplot as plt


#1st stage connect to db and return latest statistics

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


def get_stock_df(ticker,conn,simple = True):

        querry = "SELECT * from {}".format(ticker)
        df = pd.read_sql_query(querry, conn)

        if simple:
            del df['spread']
            del df['tick_volume']
            del df['real_volume']

        return df


def get_stock_data(ticker, conn):

    pass

conn = connect_to_db()
df = get_stock_df('YNDX',conn)
print(df.head())
