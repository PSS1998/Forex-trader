import time
import datetime

import config

class utility():

    # input date fromat is like 2010/12/01 
    @staticmethod
    def parse_date(date):        
        return int(time.mktime(datetime.datetime.strptime(date, "%Y/%m/%d").timetuple()))

    @staticmethod
    def timeframe_to_timestamp():
        timestamp = 0
        timeframe = config.TIMEFRAME
        if timeframe=="1":
            timestamp = 1*60
        elif timeframe=="5":
            timestamp = 5*60
        elif timeframe=="10":
            timestamp = 10*60
        elif timeframe=="30":
            timestamp = 30*60
        elif timeframe=="H":
            timestamp = 60*60
        elif timeframe=="D":
            timestamp = 60*24*60
        return timestamp

    @staticmethod
    def analyze_profit(trades):
        total_profit = 0
        for trade_name, trade in trades.items():
            if trade.num!=0:
                total_profit += trade.profit
                print(trade_name + " " + "number of trades: " + str(trade.num) + ", profit: " + str(trade.profit))
        print("total profit = " + str(total_profit))

