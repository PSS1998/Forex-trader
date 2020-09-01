import sys
# sys.path.insert(0,'..')
sys.path.append('..')

import pandas as pd

import indicators
import Istrategy

class simple_strategy(Istrategy.Istrategy):

	def indicator(self, ticker):
		df = {}
		df['ema'] = indicators.wma(ticker['close'], window=30)
		bb = indicators.bollinger_bands(ticker['close'])
		df['bb_low'] = bb['lower']
		df['bb_mid'] = bb['mid']
		df['close'] = ticker['close']
		df['volume'] = ticker['volume']
		df['date'] = ticker['date']
		df = pd.DataFrame(df)
		df = df.reset_index(drop=True)

		return df

	def buy_trend(self, ticker):
		buy = ((ticker['close'].iloc[-1]<ticker['ema'].iloc[-1]) and ((ticker['close'].iloc[-1])<(0.999*ticker['bb_low'].iloc[-1])))

		return buy

	def sell_trend(self, ticker):
		sell = (ticker['close'].iloc[-1] > ticker['bb_mid'].iloc[-1])

		return sell