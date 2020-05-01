import os



#Filemanger purpose is maintain all files directories
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
