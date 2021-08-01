from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import re

from pathlib import Path

import backtrader as bt


# Create a Stratey
import numpy as np
from backtrader.feeds import GenericCSVData


class SafeStrategy(bt.Strategy):

    params = (
        ('buy_after_decrease_percents', 30.0),
        ('sell_after_profit_percents', 40.0),
        ('re_buy_percents', 20.0),
        ('buy_size', 0.02),
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.last_maximum = {}
        self.re_ticker = re.compile(r"/([A-Z]+)\.csv")
        for d in self.datas:
            ticker = self.re_ticker.findall(d.params.dataname)[0]
            self.last_maximum[ticker] = 0.0

    def __get_pl_pct(self, position):
        pos_price = position.price
        cur_price = position.adjbase
        if not cur_price or not pos_price:
            return 0
        return (cur_price - pos_price) / pos_price

    def __get_size(self, price):
        part_of_cash = self.broker.cash * self.p.buy_size
        return round(part_of_cash / price)

    def stop(self):
        self.log('buy_after_decrease_percents %2d\tEnding Value %.2f' %
                 (self.p.sell_after_profit_percents, self.broker.getvalue()))

    def next(self):
        for d in self.datas:
            price = d.close[0]
            datetime = d.datetime.datetime()
            ticker = self.re_ticker.findall(d.params.dataname)[0]
            # print(f"{ticker} - {datetime}")
            self.last_maximum[ticker] = price if price > self.last_maximum[ticker] else self.last_maximum[ticker]
            last_maximum = self.last_maximum[ticker]
            position = self.getposition(d)
            pl_pct = self.__get_pl_pct(position)
            if (last_maximum - price) / price * 100 > self.p.buy_after_decrease_percents and not position:
                self.buy(data=d, size=self.__get_size(price))
                if 'AAL' == ticker:
                    print(f'buy: {position.size=}\t{price=}\t{position.price=}\t{pl_pct=}\t{self.last_maximum=}')
            elif position and pl_pct < -self.p.re_buy_percents / 100.0:
                size = self.__get_size(price)
                self.buy(data=d, size=size)
                if 'AAL' in ticker:
                    print(f'buy: {position.size=}\t{price=}\t{position.price=}\t{pl_pct=}\t{self.last_maximum=}')
            elif position and pl_pct > self.p.sell_after_profit_percents / 100.0:
                self.sell(data=d, size=position.size)
                if 'AAL' == ticker:
                    print(f'buy: {position.size=}\t{price=}\t{position.price=}\t{pl_pct=}\t{self.last_maximum=}')


def get_data(ticker):
    datapath = os.path.join(f'stock_market_data/sp500/csv/{ticker}.csv', )
    if not Path(datapath).exists():
        datapath = os.path.join(f'stock_market_data/nasdaq/csv/{ticker}.csv', )
        if not Path(datapath).exists():
            datapath = os.path.join(f'stock_market_data/nyse/csv/{ticker}.csv', )
    # Create a Data Feed
    # Date,Low,Open,Volume,High,Close,Adjusted Close
    return GenericCSVData(
        dtformat='%d-%m-%Y',
        low=1,
        open=2,
        volume=3,
        high=4,
        close=5,
        openinterest=-1,
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2000, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2016, 1, 1),
        # Do not pass values after this date
        reverse=False)


def run_once():
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    #cerebro.addstrategy(SafeStrategy) # best {'buy_after_decrease_percents': 10, 'sell_after_profit_percents': 90, 're_buy_percents': 5, 'buy_size': 0.02}
    cerebro.optstrategy(SafeStrategy,
                                 buy_after_decrease_percents=range(10, 100, 10),
                                 sell_after_profit_percents=range(10, 100, 10),
                                 re_buy_percents=range(5, 40, 5),
                                 buy_size=tuple(np.linspace(0.1, 1, 10)),
                                 )
    # Add the Data Feed to Cerebro
    cerebro.adddata(get_data('AAPL'))
    cerebro.adddata(get_data('ADBE'))
    cerebro.adddata(get_data('ATVI'))
    cerebro.adddata(get_data('AMZN'))
    cerebro.adddata(get_data('AXP'))
    cerebro.adddata(get_data('ALK'))
    cerebro.adddata(get_data('ATO'))
    cerebro.adddata(get_data('COP'))
    cerebro.adddata(get_data('MRO'))

    cerebro.addanalyzer(bt.analyzers.Returns)

    # Set our desired cash start
    start_cash = 10000.0
    cerebro.broker.setcash(start_cash)
    # Set the commission - 0.5% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.005)

    # Run over everything
    results = cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    strats = [x[0] for x in results]  # flatten the result
    strats.sort(key=lambda x: x.analyzers.returns._value_end)
    profitest = strats[-10:]
    for strat in profitest:
        ret = strat.analyzers.returns
        rets = ret.get_analysis()
        final_cash = ret._value_end
        print(f'{final_cash=}\trtot: {rets["rtot"]=}\travg:{rets["ravg"]}\trnorm100: {rets["rnorm100"]}\t{strat.p.__dict__}')

    return cerebro


if __name__ == '__main__':
    cerebro = run_once()
    # cerebro.plot()