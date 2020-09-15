from abc import ABC, abstractmethod

import time
from pathlib import Path
import importlib

import config
import constants
import datahandler_factory
import reporter_factory
import utility
import trade

class Istrategy(ABC):
	def __init__(self):
		self.data_handler = datahandler_factory.data_handler_factory().get_data_handler()
		self.reporter = reporter_factory.reporter_factory().get_reporter()
		self.utility = utility.utility()
		self.trades = {}
		pair_list = config.PAIR_LIST.split()
		for pair in pair_list:
			self.trades[pair] = trade.trade(pair)

	def run(self, start_date=None, end_date=None):
		state = config.STATE
		timeframe = config.TIMEFRAME
		if(state == "trade"):
			tickers = self.data_handler.refresh_tickers()
			while True:
				self.reporter.notify_time()
				try:
					tickers = self.data_handler.update_live_tickers(tickers)
					self.on_ticker(tickers)
				except:
					print("There was a problem with the data")
				# tickers = self.data_handler.update_live_tickers(tickers)
				# self.on_ticker(tickers)
				time.sleep(self.utility.timeframe_to_timestamp())
		elif(state == "backtest"):
			start_date = self.utility.parse_date(start_date)
			end_date = self.utility.parse_date(end_date)
			start_date = start_date-self.utility.timeframe_to_timestamp()*30
			tickers = self.data_handler.fetch_backtest_tickers(start_date, end_date)
			self.backtest(tickers)

	def on_ticker(self, tickers):
		for ticker_name, ticker in tickers.items():
			df = self.indicator(ticker)
			if self.buy_trend(df):
				self.reporter.notify_buy(ticker_name)
			if self.sell_trend(df):
				self.reporter.notify_sell(ticker_name)
			if self.general_sell_strategy(ticker_name, df):
				self.reporter.notify_sell(ticker_name)
			

	def backtest(self, tickers):
		money_change = []
		time_change = []
		for ticker_name, ticker in tickers.items():
			df = self.indicator(ticker)
			index = min(30, (len(df.index)-1))
			lenght = (len(df.index)-1)
			while True:
				if index > lenght:
					break
				if self.buy_trend(df.head(index)):
					if self.trades[ticker_name].open==0:
						self.trades[ticker_name].open = df['close'].iloc[index]
						self.trades[ticker_name].num += 1
				if self.sell_trend(df.head(index)):
					if self.trades[ticker_name].open!=0:
						self.trades[ticker_name].close = df['close'].iloc[index]
						profit = (self.trades[ticker_name].close/self.trades[ticker_name].open)-1
						self.trades[ticker_name].profit += profit
						self.trades[ticker_name].open = 0
						self.trades[ticker_name].close = 0
						total_money = profit
						money_change.append(total_money)
						time_change.append(df['date'].iloc[index])
				if self.general_sell_strategy(ticker_name, df.head(index)):
					if self.trades[ticker_name].open!=0:
						self.trades[ticker_name].close = df['close'].iloc[index]
						profit = (self.trades[ticker_name].close/self.trades[ticker_name].open)-1
						self.trades[ticker_name].profit += profit
						self.trades[ticker_name].open = 0
						self.trades[ticker_name].close = 0
						total_money = profit
						money_change.append(total_money)
						time_change.append(df['date'].iloc[index])
				index += 1
			if self.trades[ticker_name].open!=0:
				if self.trades[ticker_name].close==0:
					self.trades[ticker_name].close = df['close'].iloc[-1]
					profit = (self.trades[ticker_name].close/self.trades[ticker_name].open)-1
					self.trades[ticker_name].profit += profit
					self.trades[ticker_name].open = 0
					self.trades[ticker_name].close = 0
					total_money = profit
					money_change.append(total_money)
					time_change.append(df['date'].iloc[-1])
		self.utility.analyze_profit(self.trades, (money_change,time_change))

	def general_sell_strategy(self, ticker_name, ticker):
		if(self.trades[ticker_name].open != 0):
			# Stoploss
			if((ticker['close'].iloc[-1]/self.trades[ticker_name].open)-1) < -0.02:
				return True
			# Take Profit
			# if((ticker['close'].iloc[-1]/self.trades[ticker_name].open)-1) > 0.02:
			# 	return True
		return False

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
