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
#v. alpha 1.2.2
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


    def connect_to_db(self,db = 'hour'):

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


    def time_frame(self,time_frame):
        time_frames = {
            'd1':mt5.TIMEFRAME_D1,
            '1h':mt5.TIMEFRAME_H1,
            'min5':mt5.TIMEFRAME_M5
        }

        frames = {
            'd1':'d1',
            '1h':'1h',
            'min5':'min5'
        }
        return frames[time_frame], time_frames[time_frame]


    def download_stock(
        self,ticker,rows,time_frame,for_trading = True):


        frame,mt_t_frame = self.time_frame(time_frame)

        #Download scenario
        conn = self.connect_to_db()

        timezone = pytz.timezone("Etc/UTC")

        #ymd = datetime.today().strftime('%Y-%m-%d')
        ymd = datetime.today()

        if self.work_day and not for_trading:

           delta = dt.timedelta(days = 1)
           ymd = (ymd - delta).strftime('%Y-%m-%d')
           print(ymd)
        else:
            ymd = ymd.strftime('%Y-%m-%d')

        ymd = [int(i) for i in ymd.split('-')]
        y,m,d = ymd[0],ymd[1],ymd[2]


        utc_from = datetime(y, m, d, tzinfo=timezone)

        if for_trading and time_frame == '1h':
            h = datetime.today().hour - 1
            utc_from = datetime(y, m, d,h, tzinfo=timezone)

        rates = mt5.copy_rates_from(ticker, mt_t_frame, utc_from, rows)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')

        if len(rates_frame) < 1:
            return "Check frame data ticker:{}".format(ticker)
        ticker = ticker + '_' + frame
        if not for_trading:
            rates_frame.to_sql(name=ticker,con = conn,index=False)
        else:
            return rates_frame


    def update_stock(self, ticker,time_frame = None):


        frame,mt_t_frame = self.time_frame(time_frame)
        print(frame,mt_t_frame)

        c = self.connect_to_db()
        ticker_ = ticker + '_' + time_frame
        querry = c.execute(
             'SELECT * FROM {} ORDER BY time DESC LIMIT 1;'.format(ticker_)
             ).fetchall()[0][0]

        timezone = pytz.timezone("Etc/UTC")

        if time_frame == '1h':

            utc_from = (
                datetime.strptime(querry,'%Y-%m-%d %H:%M:%S') + dt.timedelta(hours = 1)
                ).replace(tzinfo=timezone)


        if time_frame == 'min5':
            utc_from = (
                datetime.strptime(querry,'%Y-%m-%d %H:%M:%S') + dt.timedelta(minutes = 5)
                ).replace(tzinfo=timezone)


        # utc_to = (
        #     datetime.today()
        #     ).replace(tzinfo=timezone)
        d = datetime.today().strftime('%Y-%m-%d').split('-')
        d = [int(i) for i in d]
        utc_to = datetime(d[0],d[1],d[2],8,tzinfo=timezone)

        print('Updating from {} to {} ({})'.format(utc_from, utc_to, time_frame))
        #today_ = dt.datetime.today().strftime('%Y-%m-%d')


        rates = mt5.copy_rates_range(ticker, mt_t_frame, utc_from, utc_to)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        ticker = ticker + '_' + time_frame
        rates_frame.to_sql(
            name=ticker, con=self.connect_to_db(),
            if_exists='append', index=False)

        self.connect_to_db().commit()
        self.connect_to_db().close()

        return "Updated"


    def update(self,time_frame):
        c = self.connect_to_db().cursor()

        table_lst = c.execute(
            "SELECT name FROM sqlite_master WHERE type='table';")
        table_lst = [i[0] for i in table_lst.fetchall() if i[0] != 'stock_info']

        table_lst = [i.split('_')[0] for i in table_lst if '1h' in i]

        hour = datetime.now().hour

        for asset in table_lst:
            self.update_stock(asset,time_frame)
            print("Updating {}, hour:{}".format(asset,hour))

    def check_data(self):
        pass


    def update_init(self, time_frame = '1h'):

        hour = datetime.now().hour

        self.update(time_frame)


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


    fm.update_init(time_frame = '1h')
