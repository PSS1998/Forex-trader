import sys
# sys.path.insert(0,'..')
sys.path.append('..')

import pandas as pd
import numpy

import indicators
import Istrategy

# import talib as ta
import talib_indicators as ta

class binhv27_strategy(Istrategy.Istrategy):

	def indicator(self, ticker):
		df = {}

		# df['ema'] = indicators.wma(ticker['close'], window=30)
		# bb = indicators.bollinger_bands(ticker['close'])
		# df['bb_low'] = bb['lower']
		# df['bb_mid'] = bb['mid']


		dataframe = ticker

		# print(dataframe)
		df['rsi'] = pd.DataFrame(numpy.nan_to_num(ta.RSI(dataframe, timeperiod=5)))
		rsiframe = pd.DataFrame(df['rsi'])
		rsiframe.columns = ['close']
		df['emarsi'] = pd.DataFrame(numpy.nan_to_num(ta.EMA(rsiframe, timeperiod=5)))
		df['adx'] = pd.DataFrame(numpy.nan_to_num(ta.ADX(dataframe)))
		df['minusdi'] = pd.DataFrame(numpy.nan_to_num(ta.MINUS_DI(dataframe)))
		minusdiframe = pd.DataFrame(df['minusdi'])
		minusdiframe.columns = ['close']
		df['minusdiema'] = pd.DataFrame(numpy.nan_to_num(ta.EMA(minusdiframe, timeperiod=25)))
		df['plusdi'] = pd.DataFrame(numpy.nan_to_num(ta.PLUS_DI(dataframe)))
		plusdiframe = pd.DataFrame(df['plusdi'])
		plusdiframe.columns = ['close']
		df['plusdiema'] = pd.DataFrame(numpy.nan_to_num(ta.EMA(plusdiframe, timeperiod=5)))
		df['lowsma'] = pd.DataFrame(numpy.nan_to_num(ta.EMA(dataframe, timeperiod=60)))
		# print(type(ta.EMA(dataframe, timeperiod=60)))
		df['highsma'] = pd.DataFrame(numpy.nan_to_num(ta.EMA(dataframe, timeperiod=120)))
		df['fastsma'] = pd.DataFrame(numpy.nan_to_num(indicators.sma(dataframe['close'], window=120)))
		df['slowsma'] = pd.DataFrame(numpy.nan_to_num(indicators.sma(dataframe['close'], window=240)))
		# a = (df['fastsma'] - df['slowsma'])
		# a.columns = ['close']
		# print((df['fastsma'] - df['slowsma']))
		# b = pd.DataFrame(dataframe['close'] / 300)
		# print((dataframe['close'] / 300))
		# c = a.values > b.values
		# print(pd.DataFrame(pd.DataFrame(df['fastsma'] - df['slowsma']) > pd.DataFrame(dataframe['close'] / 300)))
		# print(((df['fastsma'] - df['slowsma']) > (dataframe['close'] / 300)))
		
		# print(type(df['fastsma']))
		# print(df['fastsma']>df['slowsma'])
		df['trend'] = pd.DataFrame(df['fastsma'] - df['slowsma'])
		# print((df['trend']))
		# print(df['trend'].columns)
		df['trend'].columns = ['close']
		# print(df['trend'].columns)
		# print((pd.DataFrame(dataframe['close'] / 300)))
		# print(df['trend'].gt(pd.DataFrame(dataframe['close'] / 300)))
		temp = df['fastsma'].gt(df['slowsma'])
		temp.columns = ['close']
		# a = (df['trend'].gt(pd.DataFrame(dataframe['close'].reset_index() / 300)))
		# print(len(a))
		# print(df['trend'])
		# print(pd.DataFrame(dataframe['close'].reset_index() / 300))
		# print(a)

		df['bigup'] = pd.DataFrame(temp & pd.DataFrame(df['trend'].gt(pd.DataFrame(dataframe['close'].reset_index() / 300))))
		df['bigdown'] = pd.DataFrame(~df['bigup'])
		# df['trend'] = pd.DataFrame(df['trend'])
		# print(pd.DataFrame(dataframe['close'] / 300))
		# print(df['bigup'])
		# print(pd.DataFrame(df['trend'].gt(pd.DataFrame(dataframe['close'] / 300))))
		df['preparechangetrend'] = pd.DataFrame(df['trend'].gt(df['trend'].shift()))
		df['preparechangetrendconfirm'] = pd.DataFrame(df['preparechangetrend'] & (df['trend'].shift().gt(df['trend'].shift(2))))
		df['continueup'] = pd.DataFrame((df['slowsma'].gt(df['slowsma'].shift())) & (df['slowsma'].shift().gt(df['slowsma'].shift(2))))
		df['delta'] = pd.DataFrame(df['fastsma'] - df['fastsma'].shift())
		df['slowingdown'] = pd.DataFrame(df['delta'].lt(df['delta'].shift()))



		# sd = {}
		df['close'] = pd.DataFrame(ticker['close'])
		# print(sd['close'])
		df['volume'] = pd.DataFrame(ticker['volume'])
		df['date'] = pd.DataFrame(ticker['date'])
		# print(sd)
		for key in df:
			# print(key)
			# print(len(df[key]))
			df[key] = df[key].values.tolist()
		# print(type(df['bigdown']))
		df = pd.DataFrame(df)
		# print(df)
		df = df.reset_index(drop=True)

		return df

	def buy_trend(self, ticker):
		# buy = ((ticker['close'].iloc[-1][0]<ticker['ema'].iloc[-1][0]) and ((ticker['close'].iloc[-1][0])<(0.999*ticker['bb_low'].iloc[-1][0])))
		# print(ticker['slowsma'].iloc[-1][0])
		buy =(	(ticker['slowsma'].iloc[-1][0]>0) and
				((ticker['close'].iloc[-1][0])<(ticker['highsma'].iloc[-1][0])) and
				((ticker['close'].iloc[-1][0])<(ticker['lowsma'].iloc[-1][0])) and
				((ticker['minusdi'].iloc[-1][0])>(ticker['minusdiema'].iloc[-1][0])) and
				((ticker['rsi'].iloc[-1][0])>(ticker['rsi'].iloc[-2][0])) and
				(
				  (
					(~(ticker['preparechangetrend'].iloc[-1][0])) and
					(~(ticker['continueup'].iloc[-1][0])) and
					(ticker['adx'].iloc[-1][0]>25) and
					(ticker['bigdown'].iloc[-1][0]) and
					(ticker['emarsi'].iloc[-1][0]<20)
				  ) or
				  (
					(~(ticker['preparechangetrend'].iloc[-1][0])) and
					(ticker['continueup'].iloc[-1][0]) and
					(ticker['adx'].iloc[-1][0]>30) and
					(ticker['bigdown'].iloc[-1][0]) and
					(ticker['emarsi'].iloc[-1][0]<20)
				  ) or
				  (
					(~(ticker['continueup'].iloc[-1][0])) and
					(ticker['adx'].iloc[-1][0]>35) and
					(ticker['bigup'].iloc[-1][0]) and
					(ticker['emarsi'].iloc[-1][0]<20)
				  ) or
				  (
					(ticker['continueup'].iloc[-1][0]) and
					(ticker['adx'].iloc[-1][0]>30) and
					(ticker['bigup'].iloc[-1][0]) and
					(ticker['emarsi'].iloc[-1][0]<25)
				  )
				)
			)


		return buy

	def sell_trend(self, ticker):
		sell = (
			  (
				~ticker['preparechangetrendconfirm'].iloc[-1][0] and
				~ticker['continueup'].iloc[-1][0] and
				(ticker['close'].iloc[-1][0]>(ticker['lowsma'].iloc[-1][0]) or ticker['close'].iloc[-1][0]>(ticker['highsma'].iloc[-1][0])) and
				ticker['highsma'].iloc[-1][0]>0 and
				ticker['bigdown'].iloc[-1][0]
			  ) or
			  (
				~ticker['preparechangetrendconfirm'].iloc[-1][0] and
				~ticker['continueup'].iloc[-1][0] and
				(ticker['close'].iloc[-1][0])>(ticker['highsma'].iloc[-1][0]) and
				(ticker['highsma'].iloc[-1][0])>0 and
				(ticker['emarsi'].iloc[-1][0]>75 or ticker['close'].iloc[-1][0]>(ticker['slowsma'].iloc[-1][0])) and
				ticker['bigdown'].iloc[-1][0]
			  ) or
			  (
				~ticker['preparechangetrendconfirm'].iloc[-1][0] and
				ticker['close'].iloc[-1][0]>(ticker['highsma'].iloc[-1][0]) and
				ticker['highsma'].iloc[-1][0]>0 and
				ticker['adx'].iloc[-1][0]>30 and
				ticker['emarsi'].iloc[-1][0]>80 and
				ticker['bigup'].iloc[-1][0]
			  ) or
			  (
				ticker['preparechangetrendconfirm'].iloc[-1][0] and
				~ticker['continueup'].iloc[-1][0] and
				ticker['slowingdown'].iloc[-1][0] and
				ticker['emarsi'].iloc[-1][0]>75 and
				ticker['slowsma'].iloc[-1][0]>0
			  ) or
			  (
				ticker['preparechangetrendconfirm'].iloc[-1][0] and
				ticker['minusdi'].iloc[-1][0]<(ticker['plusdi'].iloc[-1][0]) and
				ticker['close'].iloc[-1][0]>(ticker['lowsma'].iloc[-1][0]) and
				ticker['slowsma'].iloc[-1][0]>0
			  )
			)

		return sell