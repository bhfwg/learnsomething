from datetime import datetime
import time
class sysmonlogs:
	'''
	logs is a list of list:
	[["begin", "end", "WARNING|CRITICAL", "CPU|LOAD|MEM", MAX, AVG, MIN, SUM, COUNT],...]
	'''
	
	def __init__(self):
		self.logs_max  =10
		self.logs_list = []
	
	def get(self):
		return self.logs_list
	
	def len(self):
		return self.logs_list.__len__()
	
	def __itemexist__(self,item_type):
		for i in xrange(self.len()):
			if (self.logs_list[i][1] < 0 and self.logs_list[i][3] == item_type):
				return i
		return -1
	
	def add(self,item_state,item_type,item_value):
		'''
		item_state = "OK|CAREFUL|WARNING|CRITICAL"
		item_type = "CPU|LOAD|MEM"
		item_value = value
		Item is defined by: 
		["begin", "end", "WARNING|CRITICAL", "CPU|LOAD|MEM",MAX, AVG, MIN, SUM, COUNT]
		If item is a 'new one': add it, else update it
		'''
		item_index = self.__itemexist__(item_type)
		if item_index < 0:
			if (item_state == 'WARNING' or item_state == 'CRITICAL'):
				item = []
				item.append(time.mktime(datetime.now().timtuple()))
				item.append(-1)
				item.append(item_state)
				item.append(item_type)
				item.append(item_value)
				item.append(item_value)
				item.append(item_value)
				item.append(item_value)
				item.append(1)
				self.logs_list.insert(0,item)
				if self.len() > self.logs_max :
					self.logs_list.pop()
		else:
			if (item_state == 'OK' or item_state == 'CAREFUL'):
				self.logs_list[item_index][1] = time.mktime(datetime.now().timetuple())
			else:
				if item_state == 'CRITICAL':
					self.logs_list[item_index][2] = item_state
				if item_value > self.logs_list[item_index][4]:
					self.logs_list[item_index][4] = item_value
				elif item_value < self.logs_list[item_index][6]:
					self.logs_list[item_index][6] = item_value

				self.logs_list[item_index][7] += item_value
				self.logs_list[item_index][8] += 1
				self.logs_list[item_index][5] = (
					self.logs_list[item_index][7]/self.logs_list[item_index][8])


		return self.len()

if __name__ == '__main__':
	pass
