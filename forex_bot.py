import config
import Istrategy

class forex_bot():

    def start(self, start_date=None, end_date=None):
        strategy_factory = Istrategy.strategy_factory()
        strategy = strategy_factory.get_strategy()
        strategy.run(start_date, end_date)
