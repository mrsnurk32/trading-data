import os
import importlib
import MetaTrader5 as mt5
from file_manager import FileManager
import pytz
import sqlite3 as sql
from datetime import datetime
import pandas as pd


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


#Asset update section


table_lst = [i for i in table_lst if i != 'stock_info'] #Creates list of securities

c = sql.connect(
    '{}/stock_data/fin_data.db'.format(fm.storage_directory)).cursor()

# for asset in table_lst:
#     querry = c.execute('SELECT * FROM GAZP ORDER BY time DESC LIMIT 1;').fetchall()[0][0]
#
#     date = querry.split()[0].split('-')
#     y,m,d = int(date[0]),int(date[1]),int(date[2])
#     timezone = pytz.timezone('Europe/Moscow')
#     utc_from = datetime(y, m, d, tzinfo=timezone)
#     print(utc_from)
#     #print(date,time)
timezone = pytz.timezone("Etc/UTC")

#real hour = hour - 2

utc_from = datetime(2020, 1, 10, hour = 11, tzinfo=timezone)
utc_to = datetime(2020, 1, 13,hour=23, tzinfo=timezone)
rates = mt5.copy_rates_range("YNDX", mt5.TIMEFRAME_H1, utc_from, utc_to)
# создадим из полученных данных DataFrame
rates_frame = pd.DataFrame(rates)
# сконвертируем время в виде секунд в формат datetime
rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
print(rates_frame)
#fm.download_stock("GAZP")
