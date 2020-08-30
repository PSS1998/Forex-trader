import sys
# sys.path.insert(0,'..')
sys.path.append('..')

import pandas as pd
import pickle

import indicators
import Istrategy
import constants

class test_ai_strategy(Istrategy.Istrategy):

	def indicator(self, ticker):
        f = open(constants.AI_MODEL+self.__class__.__name__+'.pickle', 'rb')
        self.model = pickle.load(f)
		df = {}
		df['sma'] = indicators.sma(ticker['close'], window=10)
		df['close'] = ticker['close']
		df = pd.DataFrame(df)
		df = df.reset_index(drop=True)

		return df

	def buy_trend(self, ticker):
        buy = self.model.predict(ticker)

		return buy

	def sell_trend(self, ticker):
        sell = self.model.predict(ticker)

		return sell