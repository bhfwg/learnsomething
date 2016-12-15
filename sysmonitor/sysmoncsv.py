improt csv
import sys
class sysmoncsv:
	def __init__(self, csvfile='./sysmon.csv', refresh_time=1):
		self.__refresh_time = refresh_time
		try:
			self.__csvfile_fd = open("%s" % csvfile, 'wb')
			self.__csvfile = csv.writer(self.__csvfile_fd)
		except IOError, error:
			print _('can not create the output csv file', error[1])
			sys.exit(0)
	def update(self,stats):
		if stats.getcpu():
			cpu = stats.getcpu()
			self.__csvfile.writerow(['cpu',cpu['user'],cpu['kernel'],cpu['nice']])
		if stats.getload():
			load = stats.getLoad()
			self.__csvfile.writerow(['load',load['min1'],load['min5'],load['min15']])
		if (stats.getmem() and stats.getmemswap()):
			mem = stats.getmem()
			self.__csvfile.writerow(['mem',mem['total'],mem['used'],mem['free']])
			memswap = stats.getmemswap()
			self.__csvfile.writerow(['swap',mem['total'],mem['used'],mem['free']])
		self.__csvfile_fd.flush()

