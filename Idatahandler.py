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
import exceptions



class Idata_handler(ABC):
	def __init__(self):
		self.API = api.API()
		self.utility = utility.utility()

	def ohlcv_load_from_dict(self, ticker):
		ticker = pd.DataFrame(ticker)
		if(ticker.columns[4] == 's'):
			ticker.drop(ticker.columns[4], axis=1, inplace=True)
			ticker.columns = ['close', 'high', 'low', 'open', 'date', 'volume']
			# ticker.columns = ['close', 'high', 'low', 'open', 'date']
		else:
			ticker.columns = ['close', 'high', 'low', 'open', 'date', 'volume']
			# ticker.columns = ['close', 'high', 'low', 'open', 'date']
		ticker.sort_values('date', inplace=True)
		return ticker

	def fetch_ticker(self, ticker_name, from_date=0, to_date=0):
		timeframe = config.TIMEFRAME
		if to_date==0:
			to_time = datetime.datetime.now()
			to_time = int(to_time.replace(tzinfo=datetime.timezone.utc).timestamp())
		else:
			to_time = to_date
		if from_date==0:
			from_time = datetime.datetime.now() - datetime.timedelta(30)
			from_time = int(from_time.replace(tzinfo=datetime.timezone.utc).timestamp())
		else:
			from_time = from_date
		ticker = self.API.get_candles(ticker_name, timeframe, from_time, to_time)
		if(ticker['s']=="no_data"):
			raise exceptions.FinnhubRequestException("No Data!")
		ticker = self.ohlcv_load_from_dict(ticker)
		return ticker

	def ohlcv_save(self, ticker, ticker_name):
		pass

	def ohlcv_load(self, ticker_name):
		pass

	def refresh_tickers(self):
		pass

	def update_live_tickers(self, tickers):
		pass

	def fetch_backtest_tickers(self, start_date, end_date):
		pass









