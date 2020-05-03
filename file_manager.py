import os
import importlib
import MetaTrader5 as mt5
import pytz
from datetime import datetime
import pandas as pd
import sqlite3 as sql
from sqlite3 import Error

#Filemanger purpose is maintain all files directories
#FileManager will also download, store and update Data


class FileManager:

    def __init__(self):
        self.storage_directory = os.getcwd().replace('\\','/')
        self.timezone = pytz.timezone("Etc/UTC")


    def default_path(self):
        print(os.getcwd())
        self.storage_directory = os.getcwd().replace('\\','/')


    def custom_path(self):
        self.storage_directory = input('Enter path')


    def files_inplace(self):
        #This method tracks if files exist in directory mentioned in self.storage_directory
        #If everything is fine returns True
        arr = os.listdir(self.storage_directory)
        #print(arr)

        stock_db_dir = '{}/stock_data'.format(self.storage_directory)

        if 'stock_data' not in arr:
            os.mkdir(stock_db_dir)

        if not os.path.exists(
            '{}/fin_data.db'.format(stock_db_dir)):
            conn = sql.connect(
                '{}/fin_data.db'.format(stock_db_dir))
            #conn.cursor()
            conn.close()

        return True


    def connect_to_db(self):
        db_file_path = '{}/stock_data/fin_data.db'.format(
            self.storage_directory)

        sqlite3_conn = None

        try:
            sqlite3_conn = sql.connect(db_file_path)
            return sqlite3_conn
        except Error as err:
            print(err)

            if sqlite3_conn is not None:
                sqlite3_conn.close()


    def stock_info_table(self):
        #Creates table to store stock update info
        conn = self.connect_to_db()

        c = conn.cursor()

        c.execute("""
                  CREATE TABLE IF NOT EXISTS stock_info (
                    Ticker text PRIMARY KEY,
                    Currency text,
                    Frame integer,
                    Market text,
                    UpdateDate text,
                    UpdateHour text
                  )
                  """)
        conn.commit()
        conn.close()


    def updateStamp(self,ticker):

        conn = self.connect_to_db()
        c = conn.cursor()

        c.execute("""INSERT INTO stock_info (
                  Ticker,Currency,Frame,Market,UpdateDate,UpDateHour)
                  VALUES({},{},{},{},{},{});
                  """.format(
                      ticker,
                      currency,
                      frame,
                      market,
                      UpdateDate,
                      UpdateHour))


    def download_stock(self,ticker):

        currency = 'Rub'
        frame = '1H'
        market = 'ФР МБ'

        """
        TimeFrame = [
            TIMEFRAME_M1,
         -> TIMEFRAME_H1,
            TIMEFRAME_D1,
            TIMEFRAME_W1,
            TIMEFRAME_MON1
        ]
        """


        #Download scenario
        conn = self.connect_to_db()

        timezone = pytz.timezone("Etc/UTC")

        ymd = datetime.today().strftime('%Y-%m-%d')
        ymd = [int(i) for i in ymd.split('-')]
        y,m,d = ymd[0],ymd[1],ymd[2]
        utc_from = datetime(y, m, d, tzinfo=timezone)

        rates = mt5.copy_rates_from(ticker, mt5.TIMEFRAME_H1, utc_from, 50000)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        if len(rates_frame) < 1:
            return "Check frame data ticker:{}".format(ticker)

        UpdateDate = datetime.today().strftime('%Y.%m.%d')
        UpdateHour = datetime.now().hour

        rates_frame.to_sql(name=ticker,con = conn,index=False)
        c = conn.cursor()
        c.execute("""INSERT INTO stock_info (
                  Ticker,Currency,Frame,Market,UpdateDate,UpDateHour)
                  VALUES(?,?,?,?,?,?);
                  """,(ticker, currency, frame,
                      market, UpdateDate, UpdateHour))
        conn.commit()
        conn.close()
