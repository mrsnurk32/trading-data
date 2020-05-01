import pytz
import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import sqlite3 as sql
import os



#Filemanger purpose is to download, store and update Data
class FileManager:

    def __init__(self):
        self.storage_directory = os.getcwd().replace('\\','/')

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
        if 'stock_data' not in arr:
            os.mkdir('{}/stock_data'.format(self.storage_directory))

        if not os.path.exists(
            '{}/stock_data/fin_data.db'.format(self.storage_directory)):
            conn = sql.connect(
                '{}/stock_data/fin_data.db'.format(self.storage_directory))
            #conn.cursor()
            conn.close()

        return True


    def download_stock(self):

        timezone = pytz.timezone('Europe/Moscow')
        utc_from = datetime(2020, 5, 10, tzinfo=timezone)

        rates = mt5.copy_rates_from("YNDX", mt5.TIMEFRAME_H4, utc_from, 10000)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        print(rates_frame)
