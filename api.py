import config
import finnhub_api

class API():
    def __init__(self):
        self.finnhub_client = finnhub_api.Client(api_key=config.API)

    def get_candles(self, ticker_name, timeframe, from_time, to_time):
        print("getting candles for " + ticker_name)
        return self.finnhub_client.forex_candles(ticker_name, timeframe, from_time, to_time)