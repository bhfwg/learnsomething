import csv
import sys
import time
class sysmoncsv:
	'''record the log data'''
	def __init__(self, csvfile='./log.csv', refresh_time=1):
		self.__refresh_time = refresh_time
		try:
			self.__csvfile_fd = open("%s" % csvfile, 'wb')
			self.__csvfile = csv.writer(self.__csvfile_fd)
		except IOError, error:
			print _('can not create the output csv file', error[1])
			sys.exit(0)
        def exit(self):
            try:
                self._csvfile_fd.close()
            except Exception:
                pass

	def update(self,stats):
		if stats.getCpu():
			cpu = stats.getCpu()
			self.__csvfile.writerow(['cpu',cpu['user'],cpu['kernel'],cpu['nice']])
		if stats.getLoad():
			load = stats.getLoad()
			self.__csvfile.writerow(['load',load['min1'],load['min5'],load['min15']])
		if (stats.getMem() and stats.getMemSwap()):
			mem = stats.getMem()
			self.__csvfile.writerow(['mem',mem['total'],mem['used'],mem['free']])
			memswap = stats.getMemSwap()
			self.__csvfile.writerow(['swap',mem['total'],mem['used'],mem['free']])
		self.__csvfile_fd.flush()

if __name__ == '__main__':
    import myglobal
    myglobal.set_ps_network_io_tag(True)
    myglobal.set_ps_disk_io_tag(True)
    myglobal.set_ps_fs_usage_tag(True)
    myglobal.set_ps_mem_usage_tag(True)
    myglobal.set_ps_cpu_percent_tag(True)
    mycsv = sysmoncsv()
    from sysmonstats import sysmonstats
    stats = sysmonstats()
    while(True):
        stats.update()
        time.sleep(5)
        mycsv.update(stats)
