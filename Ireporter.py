from abc import ABC, abstractmethod

class Ireporter(ABC):

    @abstractmethod
    def notify_buy(self, currency_name):
        pass
    
    @abstractmethod
    def notify_sell(self, currency_name):
        pass