import sys
# sys.path.insert(0,'..')
sys.path.append('..')

import pandas as pd

import indicators
import Istrategy

class test_strategy(Istrategy.Istrategy):

	def indicator(self, ticker):
		df = {}
		df['sma'] = indicators.sma(ticker['close'], window=10)
		df['close'] = ticker['close']
		df = pd.DataFrame(df)
		df = df.reset_index(drop=True)

		return df

	def buy_trend(self, ticker):
		buy = (ticker['sma'].iloc[-1] > ticker['sma'].iloc[-2])

		return buy

	def sell_trend(self, ticker):
		sell = (ticker['sma'].iloc[-1] < ticker['sma'].iloc[-2])

		return sell