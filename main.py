
from forex_bot import forex_bot

if __name__ == "__main__":
    
    print("Starting Forex Trader")
    
    start_date = "2020/08/01"
    end_date = "2020/08/30"

    bot = forex_bot()
    bot.start(start_date, end_date)
