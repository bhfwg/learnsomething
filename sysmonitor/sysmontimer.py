import time
from datetime  import timedelta
class sysmontimer:
	''' the timer class '''
	def __init__(self,duration):
		self.started(duration)
	def started(self,duration):
		self.target = time.time()+duration
	def finished(self):
		return time.time() > self.target
	
if __name__ == '__main__':
        import time
	mytimer = sysmontimer(10)
        while(not mytimer.finished()):
            print('sleep...')
            time.sleep(1)
        print('wake up...')
