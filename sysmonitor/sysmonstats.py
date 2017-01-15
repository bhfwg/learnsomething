from datetime import datetime
import os
import platform
from sysmongrabfs import sysmongrabfs
from sysmonlimits import sysmonlimits
import psutil as ps
import myglobal
import time
import pprint
class sysmonstats:
	'''this class store, update and give stats
	'''
	def __init__(self):
		try:
			self.sysmongrabfs = sysmongrabfs()
                        self.limits = sysmonlimits()
		except Exception:
			self.sysmongrabfs = {}
		self.process_list_refresh = True
	
	def __update__(self):
		self.host ={}
		self.host['os_name'] = platform.system().lower()
		self.host['hostname'] = platform.node().lower()
		self.host['platform'] = platform.architecture()[0]
		is_archlinux = os.path.exists(os.path.join('/','etc','arch-release'))
		
		try:
			if self.host['os_name'] == 'linux':
				if is_archlinux:
					self.host['linux_distro'] = 'Arch Linux'
				else:
					linux_distro = platform.linux_distribution()
					self.host['linux_distro'] = (' '.join(linux_distro[:2])).lower()
				self.host['os_version'] = platform.release().lower()
			elif self.host['os_name'] == 'FreeBSD':
				self.host['os_version'] = platform.release().lower()
			elif self.host['os_name'] == 'Darwin':
				self.host['os_version'] = (platform.mac_ver()[0]).lower()
			elif self.host['os_version'] == ' Windows':
				os_version = platform.win32_ver()
				self.host['os_version'] = (' '.join(os_version[::2])).lower()
			else:
				self.host['os_version'] = ''
		except Exception:
			self.host['os_version'] = ''

		#cpu
		percent = 0
		try:
			self.cputime_old
		except Exception:
			self.cputime_old = ps.cpu_times()
			self.cputime_total_old = (self.cputime_old.user + self.cputime_old.system +self.cputime_old.idle)
			#some os is available	
			try:
				self.cputime_total_old += self.cputime_old.nice
			except Exception:
				pass
			try:
				self.cputime_total_old += self.cputime_old.iowait
			except Exception:
				pass
			try:
				self.cputime_total_old += self.cputime_old.irq
			except Exception:
				pass
			try:
				self.cputime_total_old += self.cputime_old.softirq
			except Exception:
				pass
			self.cpu = {}
		else:
			try:
				self.cputime_new = ps.cpu_times()
				self.cputime_total_new = (self.cputime_new.user + self.cputime_new.system +self.cputime_new.idle)		
				#some os is available
				try:
					self.cputime_total_new += self.cputime_new.nice
				except Exception:
					pass
				try:
					self.cputime_total_new += self.cputime_new.iowait
				except Exception:
					pass
				try:
					self.cputime_total_new += self.cputime_new.irq
				except Exception:
					pass
				try:
					self.cputime_total_new += self.cputime_new.softirq
				except Exception:
					pass
			
				percent = 100/(self.cputime_total_new - self.cputime_total_old)
				self.cpu = {'kernel':(self.cputime_new.system - self.cputime_old.system) * percent, 'user':(self.cputime_new.user - self.cputime_old.user) * percent, 'idle':(self.cputime_new.idle - self.cputime_old.idle)*percent, 'nice':(self.cputime_new.nice-self.cputime_old.nice)*percent}
				self.cputime_old = self.cputime_new
				self.cputime_total_old = self.cputime_total_new
			except Exception, e:
				self.cpu ={}	
                                #print(e)

		#Load
		try:
			getload = os.getloadavg()
			self.load={'min1':getload[0],'min5':getload[1],'min15':getload[2]}
		except Exception, e:
			self.load={}
                        #print(e)

		#Mem only for linux
                try:
                    mem = ps.virtual_memory()
                    self.mem={'cache':mem.cached, 'total':mem.total, 'used':mem.used, 'free':mem.free, 'percent':mem.percent}
                except Exception, e:
                    self.mem={}
                    #print(e)

                try:
                    swapmem = ps.swap_memory()
                    self.memswap={'total':swapmem.total, 'used':swapmem.used, 'free':swapmem.free, 'percent':swapmem.percent}
                except Exception, e:
                    self.memswap = {}
                    #print(e)

		#Net
		if myglobal.get_ps_network_io_tag():
			self.network = []
			try:
				self.network_old
			except Exception, e:
				if myglobal.get_ps_network_io_tag():
					self.network_old = ps.net_io_counters(True)
			else:
				try:
                                    self.network_new = ps.net_io_counters(True)
				except Exception, e:
                                    #print(e)
				    pass
				else:
				    for net in self.network_new:
					try:
					    netstat={}
					    netstat['interface_name'] = net
					    netstat['rx']=(self.network_new[net].bytes_recv - self.network_old[net].bytes_recv)
					    netstat['tx']=(self.network_new[net].bytes_sent - self.network_old[net].bytes_sent)
					except Exception, e:
                                            #print(e)
					    continue
					else:
					    self.network.append(netstat)
				    self.network_old = self.network_new

		#disk io
		if myglobal.get_ps_disk_io_tag():
			self.diskio=[]
			try:
				self.diskio_old
			except Exception:
                            if myglobal.get_ps_disk_io_tag():
			        self.diskio_old = ps.disk_io_counters(True)
			else:
			    try:
				self.diskio_new =  ps.disk_io_counters(True) 
			    except Exceptioni, e:
                                #print(e)
				pass
			    else:
				for disk in self.diskio_new:
				    try:
					diskstat = {}
					diskstat['disk_name'] = disk
					diskstat['read_bytes'] = (self.diskio_new[disk].read_bytes - self.diskio_old[disk].read_bytes)
				        diskstat['write_bytes'] = (self.diskio_new[disk].write_bytes - self.diskio_old[disk].write_bytes)
				    except Exception, e:
                                        #print(e)
					continue
				    else:
					self.diskio.append(diskstat)
				self.diskio_old = self.diskio_new

		#file system
                if myglobal.get_ps_fs_usage_tag():
			try:
				self.fs=self.sysmongrabfs.get()
			except Exception:
				self.fs = {}

		#process
		if self.process_list_refresh:
                    self.process_first_grab = False
		    try:
		        self.process_all
		    except Exception:
			self.process_all = [proc for proc in ps.process_iter()]
			self.process_first_grab = True
		    
                    self.process = []
		    self.processcount = {'total':0, 'running':0, 'sleeping':0}
		    process_new =  [proc.pid for proc in self.process_all]
		    for proc in ps.process_iter():
                        if proc.pid not in process_new:
			    self.process_all.append(proc)
		    for proc in self.process_all[:]:
			try:
			    if not proc.is_running():
				try:
				    self.process_all.remove(proc)
				except Exception,e:
                                    #print(e)
				    pass
			except Exception:
			    try:
				self.process_all.remove(proc)
			    except Exception, e:
                                #print(e)
				pass
			else:
			    try:
			        self.processcount[str(proc.status())]+=1
			    except Exception, e:
                                #print(e)
				pass
			    except KeyError, e:
                                #print(e)
				self.processcount[str(proc.status())]=1
			    finally:
				self.processcount['total']+=1
			    
                            try:
				procstate = {}
				procstate['proc_size'] = proc.memory_info().vms
				procstate['proc_resident'] = proc.memory_info().rss
				if myglobal.get_ps_cpu_percent_tag():
				    procstate['cpu_percent'] =  proc.cpu_percent(interval=0)
			        procstate['mem_percent'] = proc.memory_percent()
			        procstate['pid']=proc.pid
				procstate['uid'] = proc.username()
			        procstate['nice'] = proc.nice()
                                procstate['status'] = str(proc.status())[:1].upper()
				procstate['proc_time'] = proc.cpu_times()
				procstate['proc_cmdline']=' '.join(proc.cmdline())
				self.process.append(procstate)
			    except Exception,e:
                                #print(e)
				pass

		    if self.process_first_grab:
			self.process = []

		self.process_list_refresh = not self.process_list_refresh

		# get datetime
		self.now = datetime.now()
		self.core_number = ps.cpu_count()


	def update(self):
		self.__update__()

	def getHost(self):
		return self.host

        def getSystem(self):
		return self.host

	def getCpu(self):
		return self.cpu

	def getCore(self):
		return self.core_number

	def getLoad(self):
		return self.load

	def getMem(self):
		return self.mem

	def getMemSwap(self):
		return self.memswap

	def getNetwork(self):
		if myglobal.get_ps_network_io_tag():
			return sorted(self.network,key=lambda network: network['interface_name'])
		else:
			return 0

	def getDiskIo(self):
		if myglobal.get_ps_disk_io_tag():
			return sorted(self.diskio,key=lambda diskio:diskio['disk_name'])
		else:
			return 0

	def getFs(self):
		if myglobal.get_ps_fs_usage_tag():
			return sorted(self.fs, key=lambda fs: fs['mnt_point'])
		else:
			return 0

	def getProcessCount(self):
		return self.processcount

	def getProcessList(self, sortedby='auto'):
		sortedReverse=True
		if sortedby == 'auto':
			if myglobal.get_ps_cpu_percent_tag():
				sortedby = 'cpu_percent'
			else:
				sortedby = 'mem_percent'
			real_used_phymem = self.mem['used'] - self.mem['cache']
			try:
				memtotal = (real_used_phymem * 100)/self.mem['total']
			except Exception:
				pass
			else:
				if memtotal > self.limits.getSTDWarning():
					sortedby = 'mem_percent'
		elif sortedby=='proc_name':
			sortedReverse = False

		return sorted(self.process, key = lambda process: process[sortedby], reverse = sortedReverse)

	def getNow(self):
		return self.now

if __name__ == "__main__":
    myglobal.set_ps_network_io_tag(True)
    myglobal.set_ps_disk_io_tag(True)
    myglobal.set_ps_fs_usage_tag(True)
    myglobal.set_ps_mem_usage_tag(True)
    myglobal.set_ps_cpu_percent_tag(True)
    stats = sysmonstats()
    i = 0
    while(True):
        stats.update()

        pprint.pprint(stats.getNow())
        print("Host:")
        pprint.pprint(stats.getHost())
        print("Cpu:")
        pprint.pprint(stats.getCpu())
        print("Core:")
        pprint.pprint(stats.getCore())
        print("Load:")
        pprint.pprint(stats.getLoad())
        print("Mem:")
        pprint.pprint(stats.getMem())
        print("Swap:")
        pprint.pprint(stats.getMemSwap())
        print("Network:")
        pprint.pprint(stats.getNetwork())
        print("DiskIo:")
        pprint.pprint(stats.getDiskIo())
        print("Fs:")
        pprint.pprint(stats.getFs())
        print("ProcessCount:")
        pprint.pprint(stats.getProcessCount())
        print("processList:")
        pl = stats.getProcessList()
        j = 0
        for p in pl:
            if  j<10:
                pprint.pprint(p)
                j=j+1
            else:
                break
        print("%d................................................" %(i))
        print
        print
        i=i+1
        time.sleep(5)
