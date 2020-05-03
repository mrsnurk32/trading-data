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

conn = sql.connect(
    '{}/stock_data/fin_data.db'.format(fm.storage_directory))

c = conn.cursor()

for asset in table_lst:
    print(asset)
    querry = c.execute(
        'SELECT * FROM GAZP ORDER BY time DESC LIMIT 1;').fetchall()[0][0]

    date = querry.split()[0].split('-')

    timezone = pytz.timezone("Etc/UTC")

    y,m,d = int(date[0]),int(date[1]),int(date[2])
    start_hour = int(querry.split()[1].split(':')[0]) + 1
    utc_from = datetime(y, m, d, hour = start_hour, tzinfo=timezone)

    ymd = datetime.today().strftime('%Y-%m-%d')
    ymd = [int(i) for i in ymd.split('-')]
    y,m,d = ymd[0],ymd[1],ymd[2]
    utc_to = datetime(y, m, d, hour = 23, tzinfo=timezone)

    rates = mt5.copy_rates_range(asset, mt5.TIMEFRAME_H1, utc_from, utc_to)
    rates_frame = pd.DataFrame(rates)
    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')

    rates_frame.to_sql(name=asset, con=conn, if_exists='append', index=False)
    print(rates_frame)


    print(utc_from)
    print(utc_to)








#fm.download_stock("YNDX")
