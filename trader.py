#Trader class accounts trading activity
# - Balance sheet report
# - Buy request
# - Sell request
# - Portfolio evaluation
# - Efficiency evaluation

class Trader:

    TRADING_DATA = pd.DataFrame(
        columns = ['time','ticker',
                   'buy_price','buy_amount',
                   'sell_price','sell_amount'])

    def __init__(self, risk, return_,):
        self._balance = 0
        self._assets = 0
        self._risk = risk
        self._return = return_
        self._max_duration = 4
        self.flag = True

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self,value):
        self._balance += value
        return self._balance


    def buy(self,time,price,amount,ticker):
        #if not self.flag:return 'Bot is active'

        #Check if enough money to buy asset
        if self.balance - price * amount < 0:return 'Not enough credits'

        #Purchase data
        self.balance = -(amount * price)
        data = dict(
            time = time,
            ticker = ticker,
            buy_price = price,
            buy_amount = amount,
            sell_price = np.nan,
            sell_amount = np.nan
        )

        self.TRADING_DATA = self.TRADING_DATA.append(data,ignore_index=True)
        self.flag = False
        return self.TRADING_DATA

    def sell(self,time,price,amount,ticker):

        if self.remaining_assets(ticker) - amount < 0:
            return 'Don`t have enough assets'

        self.balance = (amount * price)
        data = dict(
            time = time,
            ticker = ticker,
            buy_price = np.nan,
            buy_amount = np.nan,
            sell_price = price,
            sell_amount = amount
        )

        self.TRADING_DATA = self.TRADING_DATA.append(data,ignore_index=True)
        self.flag = True
        return self.TRADING_DATA


    def remaining_assets(self,ticker,asset_value=False):
        data = self.TRADING_DATA
        data = data[data.ticker == ticker]

        report = data.buy_amount.sum() - data.sell_amount.sum()
        report = report if asset_value == None else (
            report * fm.get_last_price(ticker))

        return report

    @property
    def total(self):

        assets = 0
        tickers = list(self.TRADING_DATA.ticker.unique())
        for asset in tickers:
            assets += self.remaining_assets(asset,True)

        return assets + self.balance
