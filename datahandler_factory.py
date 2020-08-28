import datahandler_json

class data_handler_factory():
	def get_data_handler(self):
		return datahandler_json.data_handler_json()