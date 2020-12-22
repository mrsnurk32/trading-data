from data_retriever import DataManager


#return correlation table
class Correlation_table:

    def __init__(self):
        self.data_manager = DataManager()

    @staticmethod
    def combined_frame(tickers = None):

        if tickers is None:
            tickers = self.data_manager.ticker_list[:10]


        with concurrent.futures.ThreadPoolExecutor() as executor:
            
            counter = 0
            
            frame = self.data_manager.get_frame(tickers[0],time_frame = '1h',column_list = ['time','close'], rows = 5000)
            frame[tickers[0]] = frame.close.pct_change()

            while counter < 9:
                counter += 1
                data = self.data_manager.get_frame(tickers[counter],time_frame = '1h',column_list = ['time','close'], rows = 5000)
                frame[tickers[counter]] = data.close.pct_change()
        
            del frame['close']



