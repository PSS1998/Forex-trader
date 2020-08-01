

import indicators
import reporter

class strategy(Istrategy):
	def __init__(self):
		pass

	def run(self):
		pass

	def on_ticker(self, tickers):
		for ticker_name, ticker in tickers.items():
			df = indicators.sma(ticker)
			if df.iloc[-1] > df.iloc[-2]:
				reporter.report_buy(ticker_name)