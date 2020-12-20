from data_retriever import DataManager



class StockData(DataManager):

    def __init__(self):
        super().__init__()


    def get_stock_data(self, ticker, time_frame, columns = ['time','open','high','low','close']):

        return self.get_frame(
            ticker,
            time_frame = time_frame,
            column_list = columns
        )


class DependencyTest(StockData):

    def __init__(self):
        super().__init__()

    def dependency_test(frame, col_a, col_b):
        pass


