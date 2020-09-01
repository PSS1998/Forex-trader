import json
import datetime
import os.path

import pandas as pd

import finnhub_api
import constants
import config
import utility

import Idatahandler



class data_handler_json(Idatahandler.Idata_handler):

	def ohlcv_load(self, ticker_name):
		return self._ohlcv_load_from_json(ticker_name)

	def ohlcv_save(self, ticker, ticker_name):
		return self._ohlcv_save_to_json(ticker, ticker_name)

	def _ohlcv_save_to_json(self, ticker, ticker_name):
		state = config.STATE
		timeframe = config.TIMEFRAME
		ticker.sort_index(inplace=True)
		ticker = ticker.to_dict('list')
		if state=="backtest":
			with open(constants.BACKTEST_DATA+ticker_name+":"+timeframe+'.json', 'w', encoding='utf-8') as f:
				json.dump(ticker, f, ensure_ascii=False, indent=4)
		elif state=="trade":
			with open(constants.DATA+ticker_name+":"+timeframe+'.json', 'w', encoding='utf-8') as f:
				json.dump(ticker, f, ensure_ascii=False, indent=4)

	def _ohlcv_load_from_json(self, ticker_name):
		state = config.STATE
		timeframe = config.TIMEFRAME
		if state=="backtest":
			with open(constants.BACKTEST_DATA+ticker_name+":"+timeframe+'.json') as f:
				ticker = json.load(f)
		elif state=="trade":
			with open(constants.DATA+ticker_name+":"+timeframe+'.json') as f:
				ticker = json.load(f)
		ticker = self.ohlcv_load_from_dict(ticker)
		return ticker

	def _refresh_ticker(self, ticker_name):
		timeframe = config.TIMEFRAME
		if os.path.isfile(constants.DATA+ticker_name+":"+timeframe+'.json'):
			ticker = self._ohlcv_load_from_json(ticker_name)
			timestamp = ticker['date'].iloc[-1]
			ticker_new = self.fetch_ticker(ticker_name, from_date=timestamp, to_date=0)
			ticker = ticker.append(ticker_new)
		else:
			ticker = self.fetch_ticker(ticker_name, from_date=0, to_date=0)
		ticker = ticker.drop_duplicates(subset='date')
		self._ohlcv_save_to_json(ticker, ticker_name)
		return ticker

	def refresh_tickers(self):
		tickers = {}
		pair_list = config.PAIR_LIST
		pair_list = pair_list.split()
		for i in range(len(pair_list)):
			ticker = self._refresh_ticker(pair_list[i])
			tickers[pair_list[i]] = ticker.copy()
		return tickers

	def update_live_tickers(self, tickers):
		pair_list = config.PAIR_LIST
		pair_list = pair_list.split()
		for i in range(len(pair_list)):
			ticker_name = pair_list[i]
			timestamp = tickers[ticker_name]['date'].iloc[-1]
			ticker = self.fetch_ticker(ticker_name, from_date=timestamp, to_date=0)
			tickers[ticker_name].append(ticker)
			tickers[ticker_name] = tickers[ticker_name].drop_duplicates(subset='date')
			self._ohlcv_save_to_json(tickers[ticker_name], ticker_name)
		return tickers

	def _get_ticker_end_date_continuous(self, ticker, start_timestamp):
		dates = ticker['date'].tolist()
		timestamp_jump = self.utility.timeframe_to_timestamp()
		index = dates.index(start_timestamp)
		last_date = dates[index]
		for i in range(index, len(dates)):
			if(dates[i] > last_date+timestamp_jump):
				timestamp_jump = i-1
				break
			last_date = dates[i]
		return dates[timestamp_jump]

	def _get_ticker_start_dates(self, ticker):
		dates = ticker['date'].tolist()
		timestamp_jump = self.utility.timeframe_to_timestamp()
		date_jump = []
		date_jump.append(dates[0])
		last_date = dates[0]
		for date in dates:
			if(date > last_date+timestamp_jump):
				date_jump.append(date)
			last_date = date
		return date_jump


	def _ticker_between_time(self, ticker, start_date, end_date):
		mask = (ticker['date'] >= start_date) & (ticker['date'] <= end_date)
		df = ticker.loc[mask]
		return df

	def fetch_backtest_tickers(self, start_date, end_date):
		timeframe = config.TIMEFRAME
		timestamp_jump = self.utility.timeframe_to_timestamp()
		pair_list = config.PAIR_LIST.split()
		tickers = {}
		for i in range(len(pair_list)):
			ticker_name = pair_list[i]
			if os.path.isfile(constants.BACKTEST_DATA+ticker_name+":"+timeframe+'.json'):
				ticker = self._ohlcv_load_from_json(ticker_name)
				start_dates = self._get_ticker_start_dates(ticker)
				if len(start_dates)>1:
					start_date_available_index = next(x for x, val in enumerate(start_dates) if val > (start_date+timestamp_jump-1))-1
				else:
					if start_dates[0] > (start_date+timestamp_jump-1):
						start_date_available_index = 0
					else:
						start_date_available_index = -1
				if start_date_available_index!=-1:
					end_date_available = self._get_ticker_end_date_continuous(ticker, start_dates[start_date_available_index])
				else:
					end_date_available = start_date-10
				# UNCOMMENT‌ NEXT LINE TO NOT DOWNLOAD DATA
				# end_date_available = end_date+10
				if end_date_available < start_date:
					ticker = self.fetch_ticker(ticker_name, from_date=start_date, to_date=end_date)
				elif end_date_available < end_date:
					ticker = self._ticker_between_time(ticker, start_date, end_date_available)
					ticker_new = self.fetch_ticker(ticker_name, from_date=end_date_available, to_date=end_date)
					ticker = ticker.append(ticker_new)
				elif end_date_available > end_date:
					ticker = self._ticker_between_time(ticker, start_date, end_date)
			else:
				ticker = self.fetch_ticker(ticker_name, start_date, end_date)
			ticker = ticker.drop_duplicates(subset='date')
			tickers[ticker_name] = ticker
			self._ohlcv_save_to_json(ticker, ticker_name)
		return tickers




