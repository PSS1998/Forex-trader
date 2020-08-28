from abc import ABC, abstractmethod

import time
from pathlib import Path
import importlib

import config
import constants
import datahandler_factory
import reporter_factory
import utility

class Istrategy(ABC):
	def __init__(self):
		self.data_handler = datahandler_factory.data_handler_factory().get_data_handler()
		self.reporter = reporter_factory.reporter_factory().get_reporter()
		self.utility = utility.utility()

	def run(self, start_date=None, end_date=None):
		state = config.STATE
		if(state == "trade"):
			tickers = self.data_handler.refresh_tickers()
			while True:
				time.sleep(5)
				tickers = self.data_handler.update_live_tickers(tickers)
				self.on_ticker(tickers)
		elif(state == "backtest"):
			start_date = self.utility.parse_date(start_date)
			end_date = self.utility.parse_date(end_date)
			tickers = self.data_handler.fetch_backtest_tickers(start_date, end_date)
			self.backtest(tickers)

	def on_ticker(self, tickers):
		for ticker_name, ticker in tickers.items():
			df = self.indicator(ticker)
			if self.buy_trend(df):
				self.reporter.notify_buy(ticker_name)
			if self.sell_trend(df):
				self.reporter.notify_sell(ticker_name)
			

	def backtest(self, tickers):
		for ticker_name, ticker in tickers.items():
			action_list = []
			df = self.indicator(ticker)
			index = min(30, (len(df.index)-1))
			lenght = (len(df.index)-1)
			while True:
				if index > lenght:
					break
				if self.buy_trend(df.head(index)):
					action = []
					action.append("buy")
					action.append(ticker_name)
					action.append(df['close'].iloc[index])
					action_list.append(action)
				if self.sell_trend(df.head(index)):
					action = []
					action.append("sell")
					action.append(ticker_name)
					action.append(df['close'].iloc[index])
					action_list.append(action)
				index += 1
		self.utility.analyze_profit(action_list)

	@abstractmethod
	def indicator(self, ticker):
		pass

	@abstractmethod
	def buy_trend(self, ticker):
		pass

	@abstractmethod
	def sell_trend(self, ticker):
		pass


class strategy_factory():
	def get_strategy(self):
		strategy_name = config.STRATEGY
		strategy = Path(constants.STRATEGY_PATH + strategy_name + ".py")
		if strategy.is_file():
			strategy_module = importlib.import_module(constants.STRATEGY_PATH[:-1] + "." + strategy_name, package=None)
			strategy = getattr(strategy_module, strategy_name)()
			return strategy
		else:
			print("Strategy Not Found!!!")