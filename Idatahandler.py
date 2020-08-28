from abc import ABC, abstractmethod

import json
import datetime
import os.path

import pandas as pd

import finnhub_api
import constants
import config
import api
import utility



class Idata_handler(ABC):
	def __init__(self):
		self.API = api.API()
		self.utility = utility.utility()

	def ohlcv_load_from_dict(self, ticker):
		ticker = pd.DataFrame(ticker)
		if(ticker.columns[4] == 's'):
			ticker.drop(ticker.columns[4], axis=1, inplace=True)
			ticker.columns = ['close', 'high', 'low', 'open', 'date', 'volume']
		else:
			ticker.columns = ['close', 'high', 'low', 'open', 'date', 'volume']
		ticker.sort_values('date', inplace=True)
		return ticker

	def ohlcv_save(self, ticker, ticker_name):
		pass

	def ohlcv_load(self, ticker_name):
		pass

	def refresh_tickers(self, timeframe="D"):
		pass

	def update_live_tickers(self, tickers, timeframe="D"):
		pass

	def fetch_backtest_tickers(self, start_date, end_date):
		pass









