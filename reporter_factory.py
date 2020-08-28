import reporter_terminal

class reporter_factory():
	def get_reporter(self):
		return reporter_terminal.reporter_terminal()