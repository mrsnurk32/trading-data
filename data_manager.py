import pytz
import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd



#Datamanger purpose is to download, store and update Data
class DataManager:

    def __init__(self):
        pass

    def download_stock(self):

        timezone = pytz.timezone('Europe/Moscow')
        utc_from = datetime(2020, 5, 10, tzinfo=timezone)

        rates = mt5.copy_rates_from("YNDX", mt5.TIMEFRAME_H4, utc_from, 10000)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        print(rates_frame)
