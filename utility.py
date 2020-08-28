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
    def analyze_profit(action_list):
        profit = 0
        pair_list = config.PAIR_LIST.split()
        for i in range(len(pair_list)):
            profit_pair = 0
            ticker_name = pair_list[i]
            for i in range(len(action_list)):
                if action_list[i][1]==ticker_name:
                    if action_list[i][0]=="buy":
                        bought_price = action_list[i][2]
                        name = action_list[i][1]
                        for j in range(i, len(action_list)):
                            if action_list[j][0]=="sell":
                                profit_pair += (action_list[j][2] - bought_price)/bought_price
                                i = j
                                break
            print(ticker_name + " " + str(profit_pair))
            profit += profit_pair
        print("total profit = " + str(profit))

