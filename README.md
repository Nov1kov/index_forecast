# Try predict finance chart or find profitest strategy

## Index
- example.ipynb - copy example about predict temperature
- Predict_INTC_1.ipynb - follow tutorial 1
- Predict_INTC_2.ipynb - second try follow another tutorial

## Environmetn

```commandline
brew install cmake openmpi
install anaconda
conda install swig
```

```
pip install -r requirements.txt
```

Если используете virtual env отдельный, то чтобы зарегистрировать его в jupyter lab

```
python -m ipykernel install --user --name=myenv
```

## data sets

- 9.36 GB - [(for all NASDAQ, S&P500, and NYSE listed companies](https://www.kaggle.com/paultimothymooney/stock-market-data)
- скачать и положить в корень, чтобы папка stock_market_data лежала в корне


# Что тут делал? 

1. Backtrading-1.ipynb - взять стратегию купить и продать, и найти оптимальные значения, когда купить когда продать.
2. Backtrading-2.ipynb - та же самая стратегия, но проверять на рандомных акциях в рандомный промежуток.

## Backtesting trading
Backtesting assesses the viability of a trading strategy by discovering how it would play out using historical data. If backtesting works, traders and analysts may have the confidence to employ it going forward.
- [Backtesting](https://github.com/kernc/backtesting.py) - library with good api, but don't support multi stocks instruments
- [Backtrader](https://github.com/mementum/backtrader) - library for Backtesting
- [other py libraries list](https://github.com/kernc/backtesting.py/blob/master/doc/alternatives.md) for Backtesting

## Reinforcement learning
Reinforcement learning is the training of machine learning models to make a sequence of decisions
- https://towardsdatascience.com/finrl-for-quantitative-finance-tutorial-for-multiple-stock-trading-7b00763b7530
- [FinRL py lib](https://github.com/AI4Finance-LLC/FinRL)
- [some example](https://github.com/AI4Finance-LLC/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020)

## ROADMAP reading
- https://www.youtube.com/watch?v=D9sU1hLT0QY
- [ML with backtesting](https://medium.com/analytics-vidhya/ml-classification-algorithms-to-predict-market-movements-and-backtesting-2382fdaf7a32)
- [A curated list of awesome machine learning strategies & tools in financial market.](https://www.analyticsvidhya.com/blog/2021/01/bear-run-or-bull-run-can-reinforcement-learning-help-in-automated-trading/)
- [Bear run or bull run](https://pythonrepo.com/repo/georgezouq-awesome-ai-in-finance-python-machine-learning)
- [kaggle](https://www.kaggle.com/itoeiji/deep-reinforcement-learning-on-stock-data)
- [Book - ML for Trading - 2nd Edition](https://github.com/stefan-jansen/machine-learning-for-trading)