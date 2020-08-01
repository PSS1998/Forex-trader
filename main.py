

import finnhub_api
import datahandler
import config



finnhub_client = finnhub_api.Client(api_key=config.API)
DataHandler = datahandler.DataHandler()




tickers = DataHandler.refresh_tickers()
print(tickers)
