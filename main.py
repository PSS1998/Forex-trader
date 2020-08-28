
from forex_bot import forex_bot


if __name__ == "__main__":

    start_date = "2020/01/15"
    end_date = "2020/08/20"

    bot = forex_bot()
    bot.start(start_date, end_date)
