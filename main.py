import os
import importlib
import MetaTrader5 as mt5
from file_manager import FileManager


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

#dm.download_stock()
