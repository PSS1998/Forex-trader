import json
import datetime
import os.path

import pandas as pd

import finnhub_api
import constants
import config



class DataHandler():
	def __init__(self):
		self.finnhub_client = finnhub_api.Client(api_key="bsgta37rh5rdc8pmr8dg")

	def ohlcv_load_from_dict(self, ticker):
		ticker = pd.DataFrame(ticker)
		if(ticker.columns[4] == 's'):
			ticker.drop(ticker.columns[4], axis=1, inplace=True)
			ticker.columns = ['close', 'high', 'low', 'open', 'date', 'volume']
		else:
			ticker.columns = ['close', 'high', 'low', 'open', 'date', 'volume']
		ticker.sort_values('date', inplace=True)
		return ticker

	def ohlcv_save_to_json(self, ticker, ticker_name):
		ticker.sort_index(inplace=True)
		ticker = ticker.to_dict('list')
		with open(constants.DATA+ticker_name+'.json', 'w', encoding='utf-8') as f:
			json.dump(ticker, f, ensure_ascii=False, indent=4)

	def ohlcv_load_from_json(self, ticker_name):
		with open(constants.DATA+ticker_name+'.json') as f:
			ticker = json.load(f)
		ticker = self.ohlcv_load_from_dict(ticker)
		return ticker

	def fetch_ticker(self, ticker_name, timeframe="5", from_date=0):
		to_time = datetime.datetime.now()
		from_time = datetime.datetime.now() - datetime.timedelta(30)
		to_time = int(to_time.replace(tzinfo=datetime.timezone.utc).timestamp())
		if from_date==0:
			from_time = int(from_time.replace(tzinfo=datetime.timezone.utc).timestamp())
		else:
			from_time = from_date
		ticker = self.finnhub_client.forex_candles(ticker_name, timeframe, from_time, to_time)
		ticker = self.ohlcv_load_from_dict(ticker)
		return ticker

	def refresh_ticker(self, ticker_name, timeframe="5"):
		if os.path.isfile(constants.DATA+ticker_name+'.json'):
			ticker = self.ohlcv_load_from_json(ticker_name)
			timestamp = ticker['date'].iloc[-1]
			ticker_new = self.fetch_ticker(ticker_name, timeframe, from_date=timestamp)
			ticker = ticker.append(ticker_new)
		else:
			ticker = self.fetch_ticker(ticker_name, timeframe, from_date=0)
		ticker = ticker.drop_duplicates(subset='date')
		self.ohlcv_save_to_json(ticker, ticker_name)
		return ticker

	def refresh_tickers(self, timeframe="5"):
		tickers = {}
		pair_list = config.PAIR_LIST
		pair_list = pair_list.split()
		for i in range(len(pair_list)):
			ticker = self.refresh_ticker(pair_list[i], "D")
			tickers[pair_list[i]] = ticker.copy()
		return tickers


