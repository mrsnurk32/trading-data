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

for asset in table_lst:
    fm.update_stock(asset)




#fm.download_stock("YNDX")
