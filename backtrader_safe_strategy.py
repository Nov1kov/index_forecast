from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import itertools
import random
import re
from pathlib import Path

import backtrader as bt
# Create a Stratey
import numpy as np
from backtrader.feeds import GenericCSVData

DATASET_PATH = 'stock_market_data'
FROM_DATE = datetime.datetime(2010, 1, 1)
TO_DATE = datetime.datetime(2021, 12, 1)
COUNT_OF_STOCKS = 8
TRADE_INTERVAL = datetime.timedelta(days=365 * 3)


class SafeStrategy(bt.Strategy):
    params = (
        ('buy_after_decrease_percents', 30.0),
        ('sell_after_profit_percents', 40.0),
        ('re_buy_percents', 20.0),
        ('buy_size', 0.02),
        ('re_buy_size', 1.0),
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
            ticker = d.params.dataname.name.replace('.csv', '')
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
        self.log('params %s\nPortfolio Value %.2f\tCash: %.2f' % (self.p.__dict__, self.broker.getvalue(), self.broker.cash))

    def next(self):
        for d in self.datas:
            price = d.close[0]
            ticker = d.params.dataname.name.replace('.csv', '')
            # print(f"{ticker} - {d.datetime.datetime()}")
            self.last_maximum[ticker] = price if price > self.last_maximum[ticker] else self.last_maximum[ticker]
            last_maximum = self.last_maximum[ticker]
            position = self.getposition(d)
            pl_pct = self.__get_pl_pct(position)
            down_from_max_pct = (last_maximum - price) / price * 100
            if down_from_max_pct > self.p.buy_after_decrease_percents and not position:
                self.buy(data=d, size=self.__get_size(price))
                if 'AAL' == ticker:
                    print(f'buy: {position.size=}\t{price=}\t{position.price=}\t{pl_pct=}\t{self.last_maximum=}')
            elif position and pl_pct < -self.p.re_buy_percents / 100.0:
                size = round(position.size * self.p.re_buy_size)
                self.buy(data=d, size=size)
                if 'AAL' in ticker:
                    print(f'buy: {position.size=}\t{price=}\t{position.price=}\t{pl_pct=}\t{self.last_maximum=}')
            elif position and pl_pct > self.p.sell_after_profit_percents / 100.0 and down_from_max_pct < self.p.buy_after_decrease_percents:
                self.sell(data=d, size=position.size)
                if 'AAL' == ticker:
                    print(f'buy: {position.size=}\t{price=}\t{position.price=}\t{pl_pct=}\t{self.last_maximum=}')


def get_data(ticker_path, from_date: datetime, to_date: datetime):
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
        dataname=ticker_path,
        # Do not pass values before this date
        fromdate=from_date,
        # Do not pass values before this date
        todate=to_date,
        # Do not pass values after this date
        reverse=False)


def run(optimize: bool, data_sets: list = None, **kwargs):
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    start_time = datetime.datetime.now()
    if optimize:
        params = {'buy_after_decrease_percents': range(10, 100, 20),
                  'sell_after_profit_percents': range(10, 200, 20),
                  're_buy_percents': range(5, 100, 15),
                  'buy_size': tuple(np.linspace(0.01, 0.5, 10)),
                  're_buy_size': tuple(np.linspace(0.5, 3, 5)),
                  }
        cerebro.optstrategy(SafeStrategy, **params)
        vals = cerebro.iterize(params.values())
        optvals = itertools.product(*vals)
        count_of_iters = len(list(optvals))
        print('Count of iterations:' + str(count_of_iters))
    else:
        cerebro.addstrategy(SafeStrategy, **kwargs)

    # get random trade interval
    if data_sets is None:
        data_sets = []
        total_days_of_dataset = TO_DATE - FROM_DATE - TRADE_INTERVAL
        random_day = random.randint(0, total_days_of_dataset.days)
        start_date = FROM_DATE + datetime.timedelta(days=random_day)
        to_date = start_date + TRADE_INTERVAL
        print(f"trade from {start_date} to {to_date}")
        all_tickers = [(p.name.replace('.csv', ''), p) for p in Path(DATASET_PATH).rglob("**/*.csv")]
        for i in range(COUNT_OF_STOCKS):
            ticker_index = random.randint(0, len(all_tickers))
            ticker, ticker_path = all_tickers[ticker_index]
            data_sets.append((get_data(ticker_path, start_date, to_date), ticker))
            print('add data set of ' + ticker)
    list(map(lambda d: cerebro.adddata(d[0], d[1]), data_sets))

    cerebro.addanalyzer(bt.analyzers.Returns)

    # Set our desired cash start
    start_cash = 10000.0
    cerebro.broker.setcash(start_cash)
    # Set the commission - 0.5% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.005)

    # Run over everything
    results = cerebro.run()

    if optimize:
        strats = [x[0] for x in results]  # flatten the result
        strats.sort(key=lambda x: x.analyzers.returns._value_end)
        profitest = strats[-20:]
        for strat in profitest:
            ret = strat.analyzers.returns
            rets = ret.get_analysis()
            final_cash = ret._value_end
            print(
                f'{final_cash=}\trtot: {rets["rtot"]=}\travg:{rets["ravg"]}\trnorm100: {rets["rnorm100"]}\t{strat.p.__dict__}')
        strat = profitest[-1]
        with open('result.txt', 'w+') as f:
            report = ','.join([d[1] for d in data_sets]) + '\t'
            report += '\t'.join([str(v) for v in strat.p.__dict__.values()])
            f.write(report + '\n')
        print(f'Analyze duration: {datetime.datetime.now() - start_time}')
        run(False, data_sets=data_sets, **strat.p.__dict__)
    else:
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.plot()


if __name__ == '__main__':
    run(True)

#  AAPL, ADBE, ATVI, AMZN, AXP, ALK, EQIX, COP, MRO, COF, NEM
# 2006 - 2010 years: buy_after_decrease_percents': 70, 'sell_after_profit_percents': 10, 're_buy_percents': 5
# 2010 - 2018 years: buy_after_decrease_percents': 10, 'sell_after_profit_percents': 190, 're_buy_percents': 5
