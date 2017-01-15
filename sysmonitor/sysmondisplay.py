import curses
from sysmonstats import sysmonstats
from sysmontimer import sysmontimer
from sysmonlimits import sysmonlimits
from sysmonlogs import sysmonlogs
import myglobal
import traceback
import sys
class sysmondisplay:
	def __init__(self, refresh_time =1):
		#global ps_network_io_tag
		#global ps_disk_io_tag
		#global ps_fs_usage_tag
                #global ps_cpu_percent_tag

		self.network_tag = myglobal.get_ps_network_io_tag()
		self.diskio_tag = myglobal.get_ps_disk_io_tag()
		self.fs_tag = myglobal.get_ps_fs_usage_tag()
                self.cpu_tag = myglobal.get_ps_cpu_percent_tag()
                self.limits = sysmonlimits()
                self.logs = sysmonlogs()

		self.term_w = 80
		self.term_h = 24
		self.system_x = 0
		self.system_y = 0
		self.cpu_x = 0
		self.cpu_y = 2
		self.load_x = 19
		self.load_y = 2
		self.mem_x = 39
		self.mem_y = 2
		self.network_x = 0
		self.network_y = 7
		self.diskio_x = 0
		self.diskio_y = -1
		self.fs_x = 0
		self.fs_y = -1
		self.process_x = 29
		self.process_y = 7
		self.log_x = 0
		self.log_y = -1
		self.help_x = 0
		self.help_y = 0
		self.now_x = 79
		self.now_y = 3
		self.caption_x =0
		self.caption_y = 3

		self.screen = curses.initscr()
		if not self.screen:
			print _('Error: can not init the curses lib\n')
		curses.start_color()
		if hasattr(curses,'use_default_colors'):
			try:
				curses.use_default_colors()
			except Exception:
				pass
		if hasattr(curses,'noecho'):
			try:
				curses.noecho()
			except Exception:
				pass
		if hasattr(curses,'cbreak'):
			try:
				curses.cbreak()
			except Exception:
				pass
		if hasattr(curses,'curs_set'):
			try:
			    #curses.curs_set(0)
                            pass
			except Exception:
				pass
		
		self.hascolors = False
		if curses.has_colors() and curses.COLOR_PAIRS >8:
			self.hascolors = True
			curses.init_pair(1,curses.COLOR_WHITE, -1)
			curses.init_pair(2,curses.COLOR_WHITE, curses.COLOR_RED) 
			curses.init_pair(3,curses.COLOR_WHITE, curses.COLOR_GREEN) 
			curses.init_pair(4,curses.COLOR_WHITE, curses.COLOR_BLUE)
			curses.init_pair(5,curses.COLOR_WHITE, curses.COLOR_MAGENTA)
			curses.init_pair(6,curses.COLOR_RED, -1)
			curses.init_pair(7,curses.COLOR_GREEN, -1)
			curses.init_pair(8,curses.COLOR_BLUE, -1)
			curses.init_pair(9,curses.COLOR_MAGENTA, -1)
		else:
			self.hascolors = Faslse

		self.title_color = curses.A_BOLD | curses.A_UNDERLINE
		self.help_color = curses.A_BOLD

		if self.hascolors:
			self.no_color = curses.color_pair(1)
			self.default_color = curses.color_pair(3) | curses.A_BOLD
			self.ifCAREFUL_color =  curses.color_pair(4) | curses.A_BOLD
 			self.ifWARNING_color = curses.color_pair(5) | curses.A_BOLD
			self.ifCRITICAL_color =  curses.color_pair(2) | curses.A_BOLD
			self.default_color2 =  curses.color_pair(7) | curses.A_BOLD
			self.ifCAREFUL_color2 =  curses.color_pair(8) | curses.A_BOLD
 			self.ifWARNING_color2 = curses.color_pair(9) | curses.A_BOLD
			self.ifCRITICAL_color2 =  curses.color_pair(6) | curses.A_BOLD
		else:
			self.no_color = curses.A_NORMAL
			self.default_color = curses.A_NORMAL
			self.ifCAREFUL_color =   curses.A_UNDERLINE
 			self.ifWARNING_color =  curses.A_BOLD
			self.ifCRITICAL_color =  curses.A_REVERSE
			self.default_color2 =   curses.A_NORMAL
			self.ifCAREFUL_color2 =  curses.A_UNDERLINE
 			self.ifWARNING_color2 =  curses.A_BOLD
			self.ifCRITICAL_color2 =   curses.A_REVERSE
			
		self.__colors_list = {
			'DEFAULT':self.no_color,
			'OK':self.default_color,
			'CAREFUL':self.ifCAREFUL_color,
			'WARNING':self.ifWARNING_color,
			'CRITICAL':self.ifCRITICAL_color
			}
		self.__colors_list2 = {
			'DEFAULT':self.no_color,
			'OK':self.default_color2,
			'CAREFUL':self.ifCAREFUL_color2,
			'WARNING':self.ifWARNING_color2,
			'CRITICAL':self.ifCRITICAL_color2
			}
		
		self.log_tag = True
		self.help_tag = False

		self.term_window = self.screen.subwin(0,0)
		self.__refresh_time = refresh_time
		self.term_window.keypad(1)
		self.term_window.nodelay(1)
		self.pressedkey = -1
                self.isrunning = 1

	def setProcessSortedBy(self,sorted):
		self.__process_sortedautoflag = False
		self.__process_sortedby = sorted

	def getProcessSortedBy(self):
		return self.__process_sortedby

	def __autoUnit(self, val):
		symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
		prefix = {'Y': 1208925819614629174706176L,
		'Z': 1180591620717411303424L,
		'E': 1152921504606846976L,
		'P': 1125899906842624L,
		'T': 1099511627776L,
		'G': 1073741824, 
		'M': 1048576, 
		'K': 1024				
		}
		for key in reversed(symbols):
			if val > prefix[key]:
				value = float(val)/ prefix[key]
				if key == 'M' or key == 'K':
					return '{0:.0f}{1}'.format(value,key)
				else:
					return '{0:.1f}{1}'.format(value,key)
		return '{!s}'.format(val)

	def __getAlert(self,current=0,max=100):
		try:
			(current*100)/max
		except ZeroDivisionError:
			return 'DEFAULT'

		variable = (current *100)/max
		if variable > self.limits.getSTDCritical():
			return 'CRITICAL'
		elif variable > self.limits.getSTDWarning():
			return 'WARNING'
		elif variable >self.limits.getSTDCareful():
			return 'CAREFUL'
		return 'OK'

	def __getColor(self,current=0,max=100):
		return self.__colors_list[self.__getAlert(current,max)]
	
	def __getColor2(self,current=0,max=100):
		return self.__colors_list2[self.__getAlert(current,max)]

	def __getCpuAlert(self, current=0, max=100):
		return self.__getAlert(current, max)

	def __getCpuColor(self, current=0, max=100):
		return self.__getColor(current, max)

	def __getLoadAlert(self, current=0, core=1):
		if current > self.limits.getLOADCritical(core):
			return 'CRITICAL'
		elif current > self.limits.getLOADWarning(core):
			return 'WARNING'
		elif current > self.limits.getLOADCareful(core):
			return 'CAREFUL'
		return 'OK'

	def __getLoadColor(self, current=0, core=1):
		return self.__colors_list[self.__getLoadAlert(current, core)]

	def __getMemAlert(self, current=0, max=100):
		return self.__getAlert(current, max)

	def __getMemColor(self, current=0, max=100):
		return self.__getColor(current, max)

	def __getNetColor(self, current=0, max=100):
		return self.__getColor2(current, max)

	def __getFsColor(self, current=0, max=100):
		return self.__getColor2(current, max)

	def __getProcessColor(self, current=0, max=100):
		return self.__getColor2(current, max)

	def __catchKey(self):
		self.pressedkey = self.term_window.getch()
		if (self.pressedkey == 27 or self.pressedkey == 113):
                        self.isrunning = 0
			self.end() #ESC or q
		elif self.pressedkey== 97:
			self.setProcessSortedBy('auto') #a sort process auto
		elif self.pressedkey == 99 and myglobal.get_ps_cpu_percent_tag():
			self.setProcessSortedBy('cpu_percent') #c sort process by cpu_percent
		elif self.pressedkey == 100 and myglobal.get_ps_disk_io_tag(): 
			self.diskio_tag = not self.diskio_tag  #d show/hide diskio stat
		elif self.pressedkey == 102 and myglobal.get_ps_fs_usage_tag():
			self.fs_tag = not self.fs_tag #f show/hide fs usage
		elif self.pressedkey == 104:
			self.help_tag = not self.help_tag #h show/hide help
		elif self.pressedkey == 108:
			self.log_tag = not self.log_tag #l show/hide log message
		elif self.pressedkey == 109:
			self.setProcessSortedBy('mem_percent') #m sort process by Mem usage
		elif self.pressedkey == 110 and myglobal.get_ps_network_io_tag():
			self.network_tag = not self.network_tag #n show/hide network state
		elif self.pressedkey == 112:
			self.setProcessSortedB('proc_name')#p sort process by name

		return self.pressedkey

	def end(self):
		curses.echo()
		curses.nocbreak()
		#curses.curs_set(1)
		curses.endwin()

	def display(self,stats):
            try:
	        self.displaySystem(stats.getHost())
		self.displayCpu(stats.getCpu())
		self.displayLoad(stats.getLoad(), stats.getCore())
	        self.displayMem(stats.getMem(), stats.getMemSwap())
                network_count = self.displayNetwork(stats.getNetwork())
		diskio_count = self.displayDiskIO(stats.getDiskIo(), self.network_y + network_count)
		fs_count = self.displayFs(stats.getFs(), self.network_y+ network_count + diskio_count)
		#log_count = self.displayLog(self.network_y + network_count + diskio_count + fs_count)
		#self.displayProcess(stats.getProcessCount(), stats.getProcessList(screen.getProcessSortedBlog_count), log_count)
		self.displayCaption()
		self.displayNow(stats.getNow())
		self.displayHelp()
            except Exception as e:
                traceback.print_exc()

	def erase(self):
		self.term_window.erase()

	def flush(self, stats):
		self.erase()
		self.display(stats)

	def update(self,stats):
		self.flush(stats)
		countdown = sysmontimer(self.__refresh_time)
		while (not countdown.finished()):
			if self.__catchKey() > -1 :
				self.flush(stats)
			curses.napms(100)

	def displaySystem(self, host):
		if not host :
			return 0
		screen_x = self.screen.getmaxyx()[1]
		screen_y = self.screen.getmaxyx()[0]
		if (screen_y > self.system_y and screen_x > self.system_x + 79):
			if host['os_name'] == "linux":
				system_msg = ("{0} {1} with {2} {3} on {4}").format(host['linux_distro'], host['platform'], host['os_name'], host['os_version'],host['hostname'])
			else:
				system_msg = ("{0} {1} {2} on {3}").format(host['os_name'], host['os_version'],host['platform'], host['hostname'])
			self.term_window.addnstr(self.system_y, self.system_x +int(screen_x / 2) - len(system_msg) / 2, system_msg, 80, curses.A_UNDERLINE)

	def displayCpu(self, cpu):
		screen_x = self.screen.getmaxyx()[1]
                screen_y = self.screen.getmaxyx()[0]
                if(screen_y > self.cpu_y + 5 and screen_x > self.cpu_x + 18):
                    self.term_window.addnstr(self.cpu_y, self.cpu_x, "CPU", 8, self.title_color if  self.hascolors else curses.A_UNDERLINE)
                
                    if not cpu:
                        self.term_window.addnstr(self.cpu_y+1, self.cpu_x, ("compute data ..."),15)
                        return 0

                    self.term_window.addnstr(self.cpu_y, self.cpu_x+10,  "%.1f%%" % (100 - cpu['idle']) , 8)
                    self.term_window.addnstr(self.cpu_y+1, self.cpu_x, ("User:") , 8)
                    self.term_window.addnstr(self.cpu_y+2, self.cpu_x, ("Kernel:") , 8)
                    self.term_window.addnstr(self.cpu_y+3, self.cpu_x, ("Nice:") , 8)
                
                    alert = self.__getCpuAlert(cpu['user']) 
                    self.logs.add(alert,"CPU user", cpu['user'])
                    self.term_window.addnstr(self.cpu_y+1, self.cpu_x+10, "%.1f" % cpu['user'], 8, self.__colors_list[alert])
                
                    alert = self.__getCpuAlert(cpu['kernel'])
                    self.logs.add(alert,"CPU kernel", cpu['kernel'])
                    self.term_window.addnstr(self.cpu_y+2, self.cpu_x+10, "%.1f" % cpu['kernel'], 8, self.__colors_list[alert])

                    alert = self.__getCpuAlert(cpu['nice'])
                    self.logs.add(alert,"CPU nice", cpu['nice'])
                    self.term_window.addnstr(self.cpu_y+3, self.cpu_x+10, "%.1f" % cpu['nice'], 8, self.__colors_list[alert])
                    
	def displayLoad(self, load, core):
                if not load:
                    return 0
		screen_x = self.screen.getmaxyx()[1]
                screen_y = self.screen.getmaxyx()[0]
                if(screen_y > self.cpu_y + 5 and screen_x > self.cpu_x + 18):
                    self.term_window.addnstr(self.load_y, self.load_x, "Load", 8, self.title_color if  self.hascolors else curses.A_UNDERLINE)
                
                    self.term_window.addnstr(self.load_y, self.load_x+10,  str(core)+("-Core"), 8)
                    self.term_window.addnstr(self.load_y+1, self.load_x, ("1 min:") , 8)
                    self.term_window.addnstr(self.load_y+2, self.load_x, ("5 min:") , 8)
                    self.term_window.addnstr(self.load_y+3, self.load_x, ("15 min:") , 8)
                
                    self.term_window.addnstr(self.load_y+1, self.load_x+10, "%.2f" % load['min1'], 8)
                
                    alert = self.__getLoadAlert(load['min5'],core)
                    self.logs.add(alert,"LOAD 5-min", load['min5'])
                    self.term_window.addnstr(self.load_y+2, self.load_x+10, "%.2f" % load['min5'], 8,self.__colors_list[alert])

                    alert = self.__getLoadAlert(load['min15'],core)
                    self.logs.add(alert,"LOAD 15-min", load['min15'])
                    self.term_window.addnstr(self.load_y+3, self.load_x+10, "%.2f" % load['min15'], 8,self.__colors_list[alert])

	
	def displayMem(self, mem, memswap):
                if not mem or not memswap:
                    return 0
		screen_x = self.screen.getmaxyx()[1]
                screen_y = self.screen.getmaxyx()[0]
                if(screen_y > self.cpu_y + 5 and screen_x > self.cpu_x + 38):
                    self.term_window.addnstr(self.mem_y, self.mem_x, "Mem", 8, self.title_color if  self.hascolors else curses.A_UNDERLINE)
                
                    self.term_window.addnstr(self.mem_y+1, self.mem_x,  ("Total:"), 8)
                    self.term_window.addnstr(self.mem_y+2, self.mem_x, ("Used:") , 8)
                    self.term_window.addnstr(self.mem_y+3, self.mem_x, ("Free:") , 8)
                
                
                    self.term_window.addnstr(self.mem_y, self.mem_x+9, "{:.1%}".format(mem['percent']/100), 8)
                    self.term_window.addnstr(self.mem_y+1, self.mem_x+9, self.__autoUnit(mem['total']), 8)
                    self.term_window.addnstr(self.mem_y+2, self.mem_x+9, self.__autoUnit(mem['used']), 8)
                    self.term_window.addnstr(self.mem_y+3, self.mem_x+9, self.__autoUnit(mem['free']), 8)

                    real_used_phymem = mem['used'] - mem['cache']
                    if real_used_phymem < 0:
                        real_used_phymem = mem['used']
                    real_free_phymem = mem['free'] + mem['cache']
                    alert = self.__getMemAlert(real_used_phymem, mem['total'])
                    self.logs.add(alert,"MEM real",real_used_phymem)
                    self.term_window.addnstr(self.mem_y+2, self.mem_x+15, "({0})".format(self.__autoUnit(real_used_phymem)), 8,self.__colors_list[alert])
                    self.term_window.addnstr(self.mem_y+3, self.mem_x+15, "({0})".format(self.__autoUnit(real_free_phymem)), 8)
                
                    self.term_window.addnstr(self.mem_y, self.mem_x+25, "Swap", 8, self.title_color if self.hascolors else curses.A_UNDERLINE)
                    self.term_window.addnstr(self.mem_y+1, self.mem_x+25, ('Total:'), 8)
                    self.term_window.addnstr(self.mem_y+2, self.mem_x+25, ('Userd:'), 8)
                    self.term_window.addnstr(self.mem_y+3, self.mem_x+25, ('Free:'), 8)

                    self.term_window.addnstr(self.mem_y, self.mem_x+34, "{:.1%}".format(memswap['percent']/100), 8)
                    alert = self.__getMemAlert(memswap['used'], memswap['total'])
                    self.logs.add(alert,"MEM swap", memswap['used'])
                    self.term_window.addnstr(self.mem_y+1, self.mem_x+34, self.__autoUnit(memswap['total']), 8)
                    self.term_window.addnstr(self.mem_y+2, self.mem_x+34, self.__autoUnit(memswap['used']), 8,self.__colors_list[alert])
                    self.term_window.addnstr(self.mem_y+3, self.mem_x+34, self.__autoUnit(memswap['free']), 8)

	def displayNetwork(self, network):
                if not self.network_tag: 
                    return 0
		screen_x = self.screen.getmaxyx()[1]
                screen_y = self.screen.getmaxyx()[0]
                if(screen_y > (self.network_y + 3) and screen_x > (self.network_x + 28)):
                    self.term_window.addnstr(self.network_y, self.network_x, "Network", 8, self.title_color if  self.hascolors else curses.A_UNDERLINE)
                    self.term_window.addnstr(self.network_y, self.network_x+10,  ("Rx/ps"), 8)
                    self.term_window.addnstr(self.network_y, self.network_x+19, ("Tx/ps") , 8)
                    if not network:
                        self.term_window.addnstr(self.network_y+1, self.network_x, ("compute data") , 15)
                        return 3
                    
                    ret =2
                    net_num = min(screen_y - self.network_y-3, len(network))
                    for ii in xrange(0,net_num):
                        elapsed_time = max(1, self.__refresh_time)
                        self.term_window.addnstr(self.network_y+1+ii, self.network_x, network[ii]['interface_name']+':', 8)
                        self.term_window.addnstr(self.network_y+1+ii, self.network_x+10, self.__autoUnit(network[ii]['rx'] / elapsed_time * 8)+'b', 8)
                        self.term_window.addnstr(self.network_y+1+ii, self.network_x+19, self.__autoUnit(network[ii]['tx'] / elapsed_time * 8)+'b', 8)
                        ret = ret + 1
                    return ret
                return 0

	def displayDiskIO(self, diskio, offset_y=0):
                if not self.diskio_tag: 
                    return 0
		screen_x = self.screen.getmaxyx()[1]
                screen_y = self.screen.getmaxyx()[0]
                self.diskio_y = offset_y
                if(screen_y > (self.diskio_y + 3) and screen_x > (self.diskio_x + 28)):
                    self.term_window.addnstr(self.diskio_y, self.diskio_x, "Disk I/O", 8, self.title_color if  self.hascolors else curses.A_UNDERLINE)
                    self.term_window.addnstr(self.diskio_y, self.diskio_x+10,  ("In/ps"), 8)
                    self.term_window.addnstr(self.diskio_y, self.diskio_x+19, ("Out/ps") , 8)
                    if not diskio:
                        self.term_window.addnstr(self.diskio_y+1, self.diskio_x, ("compute data") , 15)
                        return 3
                    
                    disk = 0
                    disk_num = min(screen_y - self.diskio_y-3, len(diskio))
                    for disk in xrange(0,disk_num):
                        elapsed_time = max(1, self.__refresh_time)
                        self.term_window.addnstr(self.diskio_y+1+disk, self.diskio_x, diskio[disk]['disk_name']+':', len(diskio[disk]['disk_name'])+1)
                        self.term_window.addnstr(self.diskio_y+1+disk, self.diskio_x+10, self.__autoUnit(diskio[disk]['write_bytes'] / elapsed_time )+'B', 8)
                        self.term_window.addnstr(self.diskio_y+1+disk, self.diskio_x+19, self.__autoUnit(diskio[disk]['read_bytes'] / elapsed_time )+'B', 8)
                    return disk+3
                return 0

	def displayFs(self, fs, offset_y=0):
                if not fs or not self.fs_tag: 
                    return 0
		screen_x = self.screen.getmaxyx()[1]
                screen_y = self.screen.getmaxyx()[0]
                self.fs_y = offset_y
                if(screen_y > (self.fs_y + 3) and screen_x > (self.fs_x + 28)):
                    self.term_window.addnstr(self.fs_y, self.fs_x, "Mount", 8, self.title_color if  self.hascolors else curses.A_UNDERLINE)
                    self.term_window.addnstr(self.fs_y, self.fs_x+10,  ("Total"), 8)
                    self.term_window.addnstr(self.fs_y, self.fs_x+19, ("Used") , 8)
                    
                    mounted = 0
                    fs_num = min(screen_y - self.fs_y-3, len(fs))
                    for mounted in xrange(0,fs_num):
                        self.term_window.addnstr(self.fs_y+1+mounted, self.fs_x, fs[mounted]['mnt_point'], len(fs[mounted]['mnt_point']))
                        self.term_window.addnstr(self.fs_y+1+mounted, self.fs_x+10, self.__autoUnit(fs[mounted]['size']), 8)
                        self.term_window.addnstr(self.fs_y+1+mounted, self.fs_x+19, self.__autoUnit(fs[mounted]['used']), 8,self.__getFsColor(fs[mounted]['used'], fs[mounted]['size']))
                    return mounted+3
                return 0

	def displayLog(self, offset_y=0):
		pass


	def displayProcess(self, processcount, processlist, log_count=0):
		pass

	def displayCaption(self):
		screen_x = self.screen.getmaxyx()[1]
                screen_y = self.screen.getmaxyx()[0]
                msg = ("Press 'h' for help")
                if(screen_y > self.caption_y  and screen_x > self.caption_x+32 ):
                    self.term_window.addnstr(max(self.caption_y, screen_y-1), self.caption_x,  msg, self.default_color)
	
	def displayHelp(self):
		pass

	def displayNow(self, now):
                if not now :
                    return 0

		screen_x = self.screen.getmaxyx()[1]
                screen_y = self.screen.getmaxyx()[0]
                if(screen_y > self.now_y  and screen_x > self.now_x ):
                    now_msg = now.strftime("%Y-%m-%d %H:%M:%S")
                    self.term_window.addnstr(max(self.now_y, screen_y-1), max(self.now_x, screen_x-1)-len(now_msg),  now_msg, len(now_msg))
                

if __name__ == "__main__":
    myglobal.set_ps_network_io_tag(True)
    myglobal.set_ps_disk_io_tag(True)
    myglobal.set_ps_fs_usage_tag(True)
    myglobal.set_ps_mem_usage_tag(True)
    myglobal.set_ps_cpu_percent_tag(True)
    status = sysmonstats()
    refreshtime = 2
    i=0
    screen = sysmondisplay(refreshtime)
    while True:
        status.update()
        screen.update(status)
        if screen.isrunning == 0:
            sys.exit(0)
