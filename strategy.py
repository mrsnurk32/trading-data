"""
The purpose of file is to develop stratagies.

The data from analyzer.py will be used to find most profitable spots.
"""
import pandas as pd
from analyzer import frame
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
from file_manager import FileManager as fm
import os
from trader import Trader
fm.initialize()

trader = Trader()
trader.balance = 10000

flag = True
desired_return = 1.03
risk = 0.98
buy_itteration = 0
buy_price = None

balance_hist = list()


def buy(row,desired_return):

    date = row.time
    ticker = 'YNDX'
    price = row.close * 1.001
    amount = trader.balance // price
    if amount == 0:
        return False
    
    trader.buy(date,price, amount, ticker)
    
    return price

def sell(row,price):
    date = row.time
    ticker = 'YNDX'
    amount = trader.remaining_assets('YNDX')
    trader.sell(date,price,amount , ticker)
    
    flag = True
    buy_price = None
    
    val = trader.balance
    balance_hist.append(val)
    
    return flag,buy_price
    

for index, row in frame.iterrows():
    
    if row['2h_ret'] > 1.03 and flag == True:
        
        flag = False       
        buy_price = buy(row,desired_return)
        if buy_price is False: 
            print('Wiped out')
            break
        continue
    
    if flag == False:
        buy_itteration += 1
        #risk justified
        low_ret = row.low / buy_price
        if low_ret < risk:
            
            price = buy_price * risk
            flag, buy_price = sell(row,price)
            buy_itteration = 0
            continue
            

            
        #return justified
        high_ret = row.high / buy_price
        
        if high_ret > desired_return:
            
            price = buy_price * desired_return
            flag, buy_price = sell(row,price)
            buy_itteration = 0
            continue
        
        
  
        #duration justified
        if buy_itteration == 20:
            price = row.close
            flag, buy_price = sell(row,price)
            buy_itteration = 0
            continue

        
        
        

balance = pd.DataFrame({'Hist':balance_hist})
balance.plot()
trader.balance_sheet.tail()