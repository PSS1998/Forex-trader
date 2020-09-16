import sys
# sys.path.insert(0,'..')
sys.path.append('..')

import pandas as pd
import numpy

import indicators
import Istrategy

# import talib as ta
import talib_indicators as ta

class simple2_strategy(Istrategy.Istrategy):

	def indicator(self, ticker):
		df = {}

		dataframe = ticker

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
		df['highsma'] = pd.DataFrame(numpy.nan_to_num(ta.EMA(dataframe, timeperiod=120)))
		df['fastsma'] = pd.DataFrame(numpy.nan_to_num(indicators.sma(dataframe['close'], window=120)))
		df['slowsma'] = pd.DataFrame(numpy.nan_to_num(indicators.sma(dataframe['close'], window=240)))

		df['trend'] = pd.DataFrame(df['fastsma'] - df['slowsma'])
		df['trend'].columns = ['close']
		temp = df['fastsma'].gt(df['slowsma'])
		temp.columns = ['close']
	
		df['bigup'] = pd.DataFrame(temp & pd.DataFrame(df['trend'].gt(pd.DataFrame(dataframe['close'].reset_index() / 300))))
		df['bigdown'] = pd.DataFrame(~df['bigup'])
	
		df['preparechangetrend'] = pd.DataFrame(df['trend'].gt(df['trend'].shift()))
		df['preparechangetrendconfirm'] = pd.DataFrame(df['preparechangetrend'] & (df['trend'].shift().gt(df['trend'].shift(2))))
		df['continueup'] = pd.DataFrame((df['slowsma'].gt(df['slowsma'].shift())) & (df['slowsma'].shift().gt(df['slowsma'].shift(2))))
		df['delta'] = pd.DataFrame(df['fastsma'] - df['fastsma'].shift())
		df['slowingdown'] = pd.DataFrame(df['delta'].lt(df['delta'].shift()))



		# sd = {}
		df['close'] = ticker['close']
		df['volume'] = pd.DataFrame(ticker['volume'])
		df['date'] = ticker['date']
		for key in df:
			df[key] = df[key].values.tolist()
		df = pd.DataFrame(df)
		df = df.reset_index(drop=True)

		return df

	def buy_trend(self, ticker):
		buy =(	(ticker['slowsma'].iloc[-1][0]>0) and
				((ticker['close'].iloc[-1])<(ticker['highsma'].iloc[-1][0])) and
				((ticker['close'].iloc[-1])<(ticker['lowsma'].iloc[-1][0])) and
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
				(ticker['close'].iloc[-1]>(ticker['lowsma'].iloc[-1][0]) or ticker['close'].iloc[-1]>(ticker['highsma'].iloc[-1][0])) and
				ticker['highsma'].iloc[-1][0]>0 and
				ticker['bigdown'].iloc[-1][0]
			  ) or
			  (
				~ticker['preparechangetrendconfirm'].iloc[-1][0] and
				~ticker['continueup'].iloc[-1][0] and
				(ticker['close'].iloc[-1])>(ticker['highsma'].iloc[-1][0]) and
				(ticker['highsma'].iloc[-1][0])>0 and
				(ticker['emarsi'].iloc[-1][0]>75 or ticker['close'].iloc[-1]>(ticker['slowsma'].iloc[-1][0])) and
				ticker['bigdown'].iloc[-1][0]
			  ) or
			  (
				~ticker['preparechangetrendconfirm'].iloc[-1][0] and
				ticker['close'].iloc[-1]>(ticker['highsma'].iloc[-1][0]) and
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
				ticker['close'].iloc[-1]>(ticker['lowsma'].iloc[-1][0]) and
				ticker['slowsma'].iloc[-1][0]>0
			  )
			)

		return sell