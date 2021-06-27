import numpy as np
import pandas as pd
import backtesting
from backtesting import Backtest, Strategy
from backtesting.lib import plot_heatmaps


class SafeStrategy(Strategy):
    buy_after_decrease_percents = 30.0
    sell_after_profit_percents = 40.0
    re_buy_percents = 20.0
    buy_size = 0.05

    def init(self):
        self.last_maximum = 0

    def next(self):
        price = self.data.Close[-1]
        self.last_maximum = price if price > self.last_maximum else self.last_maximum
        if (self.last_maximum - price) / price * 100 > self.buy_after_decrease_percents and not self.position:
            self.buy(size=self.buy_size)
        elif self.position and self.position.pl_pct < -self.re_buy_percents / 100.0:
            self.buy(size=self.buy_size)
        elif self.position and self.position.pl_pct > self.sell_after_profit_percents / 100.0:
            self.position.close()


def _read_file(filename):
    return pd.read_csv(filename, dayfirst=True,
                       index_col=0, parse_dates=True, infer_datetime_format=True)


def calculate():
    sp500 = [
        'stock_market_data/sp500/csv/AAPL.csv',
        'stock_market_data/sp500/csv/A.csv',
        'stock_market_data/sp500/csv/MSI.csv',
        'stock_market_data/sp500/csv/AMZN.csv'
        'stock_market_data/sp500/csv/IBM.csv'
    ]

    df = _read_file(sp500[0])
    df = df['2000-01-01':'2016-01-01']
    bt = Backtest(df, SafeStrategy, commission=.005)

    return bt, bt.optimize(
        buy_after_decrease_percents=range(10, 100, 10),
        sell_after_profit_percents=range(10, 100, 10),
        re_buy_percents=range(5, 40, 5),
        #buy_size=tuple(np.linspace(0.1, 1, 10)),
        maximize='Equity Final [$]',
        max_tries=500,
        random_state=0,
        return_heatmap=True)


if __name__ == '__main__':
    df = _read_file('stock_market_data/sp500/csv/AAPL.csv')
    df = df['2000-01-01':'2016-01-01']
    bt = Backtest(df, SafeStrategy, commission=.005)
    stats = bt.run()
    bt.plot()
    print(stats)