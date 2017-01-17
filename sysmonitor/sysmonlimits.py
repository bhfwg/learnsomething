class sysmonlimits:
	'''manage the limit OK, CAREFUL, WARNING, CRITICAL for each states'''

	__limits_list = {'STD':[50,70,90], 'LOAD':[0.7,1.0,5.0]}
	#__limits_list = {'STD':[10,20,30], 'LOAD':[0.5,1.0,1.5]}
	
	def __init__(self,careful=50, warning=70, critical=90):
		self.__limits_list['STD'] = [careful,warning,critical]
	#def __init__(self,careful=10, warning=20, critical=30):
		#self.__limits_list['STD'] = [careful,warning,critical]
	
	def getSTDCareful(self):
		return self.__limits_list['STD'][0]
	
	
	def getSTDWarning(self):
		return self.__limits_list['STD'][1]

	
	def getSTDCritical(self):
		return self.__limits_list['STD'][2]
	

	def getLOADCareful(self,core=1):
		return self.__limits_list['LOAD'][0] * core
	
	
	def getLOADWarning(self,core=1):
		return self.__limits_list['LOAD'][1] * core

	
	def getLOADCritical(self,core=1):
		return self.__limits_list['LOAD'][2] * core

if __name__ == '__main__':
	pass
