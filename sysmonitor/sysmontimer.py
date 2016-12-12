import time
class sysmontimer:
	''' the timer class '''
	def __init__(self,duration):
		self.started(duration)
	def started(sefl,duration):
		self.target = time.time()+duration
	def finished(self):
		return time.time() > self.target
	
