import sys
# sys.path.insert(0,'..')
sys.path.append('..')

import pandas as pd
import pickle

import indicators
import Istrategy
import constants

import test_ai_model

class test_ai_strategy(Istrategy.Istrategy):

	def indicator(self, ticker):
		df  = test_ai_model.indicators_dataframe(ticker)

		return df

	def buy_trend(self, ticker):
		buy = test_ai_model.predict_buy(ticker)

		return buy

	def sell_trend(self, ticker):
		sell = test_ai_model.predict_sell(ticker)

		return sell