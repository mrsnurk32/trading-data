import os
import importlib
import MetaTrader5 as mt5
from file_manager import FileManager
import pytz
from datetime import datetime
import pandas as pd
import sqlite3 as sql


fm = FileManager()
#Check if files are inplace or creates dataset if not
fm.files_inplace()

module_list = ['MetaTrader5','pandas','numpy']
missing_modules = list()

for module in module_list:
    item = importlib.util.find_spec(module)
    if item is None:os.system(
        'cmd /c"pip install {}"'.format(module))

#initialize connection to MetaTrader5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()

print('Ready for work')



#Download scenario
conn = sql.connect(
    '{}/stock_data/fin_data.db'.format(fm.storage_directory))

timezone = pytz.timezone('Europe/Moscow')
utc_from = datetime(2020, 5, 10, tzinfo=timezone)

rates = mt5.copy_rates_from("YNDX", mt5.TIMEFRAME_H1, utc_from, 50000)
rates_frame = pd.DataFrame(rates)
rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
print(rates_frame)
rates_frame.to_sql(name="YNDX",con = conn,index=False)
conn.close()
#dm.download_stock()
