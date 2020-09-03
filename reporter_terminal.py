import Ireporter

from time import localtime, strftime

class reporter_terminal(Ireporter.Ireporter):

	def notify_buy(self, currency_name):
		print(str(strftime("%Y-%m-%d %H:%M:%S", localtime())) + ": buy "+currency_name)

	def notify_sell(self, currency_name):
		print(str(strftime("%Y-%m-%d %H:%M:%S", localtime())) + ": sell "+currency_name)