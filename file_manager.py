import os
import importlib
import MetaTrader5 as mt5
import pytz
import datetime as dt
from datetime import datetime
import pandas as pd
import sqlite3 as sql
from sqlite3 import Error
import time

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


    def work_day(self):
        #Return true if its working day, doesn`t account national holidays
        weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
        weekDay = weekDays[datetime.date.today().weekday()]
        today = datetime.date.today().strftime('%Y.%m.%d')
        hour = datetime.datetime.now().hour
        work_time = (9,19)
        if weekDay in weekDays[-2:]:
            return False
        else:
            return True


    def updateStamp(self,ticker):

        conn = self.connect_to_db()
        c = conn.cursor()

        c.execute("""INSERT INTO stock_info (
                  Ticker,Currency,Frame,Market,UpdateDate,UpDateHour)
                  VALUES({},{},{},{},{},{});
                  """.format(ticker,currency,frame,
                             market,UpdateDate,UpdateHour))


    def download_stock(self,ticker):

        currency = 'Rub'
        frame = '1H'
        market = 'ФР МБ'

        #Download scenario
        conn = self.connect_to_db()

        timezone = pytz.timezone("Etc/UTC")

        #ymd = datetime.today().strftime('%Y-%m-%d')
        ymd = datetime.today()

        if self.work_day:
           delta = dt.timedelta(days = 1)
           ymd = (ymd - delta).strftime('%Y-%m-%d')
           print(ymd)
        else:
            ymd.strftime('%Y-%m-%d')

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


    def update_stock(self, ticker):

        c = self.connect_to_db()

        querry = c.execute(
             'SELECT * FROM {} ORDER BY time DESC LIMIT 1;'.format(ticker)
             ).fetchall()[0][0]
        date_ = querry.split()[0]
        date = querry.split()[0].split('-')

        timezone = pytz.timezone("Etc/UTC")

        y,m,d = int(date[0]),int(date[1]),int(date[2])
        start_hour = int(querry.split()[1].split(':')[0]) + 1
        utc_from = datetime(y, m, d, hour = start_hour, tzinfo=timezone)

        ymd = datetime.today().strftime('%Y-%m-%d')
        ymd = [int(i) for i in ymd.split('-')]
        y,m,d = ymd[0],ymd[1],ymd[2]

        hour = datetime.now().hour - 1
        utc_to = datetime(y, m, d, hour = hour, tzinfo=timezone)

        today_ = dt.datetime.today().strftime('%Y-%m-%d')

        if start_hour > hour and date_ == today_:return 'Up to date'

        rates = mt5.copy_rates_range(ticker, mt5.TIMEFRAME_H1, utc_from, utc_to)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        rates_frame.to_sql(
            name=ticker, con=self.connect_to_db(),
            if_exists='append', index=False)

        self.connect_to_db().commit()
        self.connect_to_db().close()

        return "Updated"


    def update(self):

        c = self.connect_to_db().cursor()

        table_lst = c.execute(
            "SELECT name FROM sqlite_master WHERE type='table';")
        table_lst = [i[0] for i in table_lst.fetchall() if i[0] != 'stock_info']
        print(table_lst)

        hour = datetime.now().hour

        for asset in table_lst:
            self.update_stock(asset)
            print("Updating {}, hour:{}".format(asset,hour))


    def update_init(self):


        update_time_lst = [i for i in range(10,20)]

        hour = datetime.now().hour

        if hour in update_time_lst:
            self.update()



        exhange_mins = 120 #Exchange timer is 2 min ahead
        current_time = dt.datetime.now().time().strftime('%H:%M:%S').split(':')

        h,m = int(current_time[0]),int(current_time[1])
        s = int(current_time[2])

        hour = hour + 1

        time_left = dt.timedelta(
            hours = hour) - dt.timedelta(hours = h,minutes = m,seconds = s)
        time_left = time_left.total_seconds() + exhange_mins
        time.sleep(time_left)

    @staticmethod
    def get_last_price(ticker):
        timezone = pytz.timezone("Etc/UTC")
        ymd = datetime.today()

        if FileManager.work_day:
           delta = dt.timedelta(days = 1)
           ymd = (ymd - delta).strftime('%Y-%m-%d')
        else:
            ymd.strftime('%Y-%m-%d')

        ymd = [int(i) for i in ymd.split('-')]
        y,m,d = ymd[0],ymd[1],ymd[2]
        utc_from = datetime(y, m, d, tzinfo=timezone)
        rates = mt5.copy_rates_from(ticker, mt5.TIMEFRAME_H1, utc_from, 1)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        return list(rates_frame.close.values)[0]


    @staticmethod
    def initialize():
        if not mt5.initialize():
            print("initialize() failed, error code =",mt5.last_error())
            quit()



if __name__ == "__main__":


    fm = FileManager()
    #Check if files are inplace or creates dataset if not
    fm.files_inplace()

    module_list = ['MetaTrader5','pandas','numpy']
    missing_modules = list()

    for module in module_list:
        item = importlib.util.find_spec(module)
        if item is None:os.system(
            'cmd /c"pip install {}"'.format(module))


    #Check if stock_info table is inplace

    c = sql.connect(
        '{}/stock_data/fin_data.db'.format(fm.storage_directory)).cursor()

    table_lst = c.execute(
        "SELECT name FROM sqlite_master WHERE type='table';")

    table_lst = [i[0] for i in table_lst.fetchall()]

    if "stock_info" not in table_lst:fm.stock_info_table()
    c.close()


    #initialize connection to MetaTrader5 terminal

    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit()

    print('Ready for work')


    #Update every asset

    while True:
        fm.update_init()
