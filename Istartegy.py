import time

import config
import AI

class Istrategy():
	def __init__(self):
		self.DataHandler = datahandler.DataHandler()

	def run(self):
		tickers = DataHandler.refresh_tickers()
		if config.STATE == "trade":
			while True:
				time.sleep(5)
				tickers = DataHandler.update_live_tickers(tickers)
				self.on_ticker(tickers)
		if config.STATE == "train":
			AI.train(tickers)

	def on_ticker(self, tickers):
		pass