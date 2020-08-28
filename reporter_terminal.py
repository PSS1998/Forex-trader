import Ireporter

class reporter_terminal(Ireporter.Ireporter):

	def notify_buy(self, currency_name):
		print("buy "+currency_name)

	def notify_sell(self, currency_name):
		print("sell "+currency_name)