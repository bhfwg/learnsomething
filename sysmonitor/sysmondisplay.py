import curses
from sysmonstats import sysmonstats
from sysmontimer import sysmontimer
class sysmondisplay:
	def __init__(self, refresh_time =1):
		#global ps_network_io_tag
		#global ps_disk_io_tag
		#global ps_fs_usage_tag
                #global ps_cpu_percent_tag

		self.network_tag = ps_network_io_tag
		self.diskio_tag = ps_disk_io_tag
		self.fs_tag = ps_fs_usage_tag
                self.cpu_tag = ps_cpu_percent_tag

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
				curses.curs_set(0)
			except Exception:
				pass
		
		self.hascolors = False
		if curses.has_colors() and curses.COLOR_PAIRS >8:
			self.hascolors = True
			curse.init_pair(1,curses.COLOR_WHITE, -1)
			curse.init_pair(2,curses.COLOR_WHITE, curses.COLOR_RED) 
			curse.init_pair(3,curses.COLOR_WHITE, curses.COLOR_GREEN) 
			curse.init_pair(4,curses.COLOR_WHITE, curses.COLOR_BLUE)
			curse.init_pair(5,curses.COLOR_WHITE, curses.COLOR_MAGENTA)
			curse.init_pair(6,curses.COLOR_RED, -1)
			curse.init_pair(7,curses.COLOR_GREEN, -1)
			curse.init_pair(8,curses.COLOR_BLUE, -1)
			curse.init_pair(9,curses.COLOR_MAGENTA, -1)

		else:
			self.hascolors = Faslse
		self.title_color = curses.A_BOLD | curses.A_UNDERLINE
		self.help_color = curses.A_BOLD
		if self.hasscolors:
			self.no_color = curses.color_pair(1)
			self.default_color = curses.color_pair(3) | curses.A_BOLD
			self.ifCAREFUL_color =  curses.color_pair(4) | curses.A_BOLD
 			self.ifWARNING_color = curses.color_pair(5) | curses.A_BOLD
			slef.ifCRITICAL_color =  curses.color_pair(2) | curses.A_BOLD
			self.default_color2 =  curses.color_pair(7) | curses.A_BOLD
			self.ifCAREFUL_color2 =  curses.color_pair(8) | curses.A_BOLD
 			self.ifWARNING_color2 = curses.color_pair(9) | curses.A_BOLD
			slef.ifCRITICAL_color2 =  curses.color_pair(6) | curses.A_BOLD
		else:
			self.no_color = curses.A_NORMAL
			self.default_color = curses.A_NORMAL
			self.ifCAREFUL_color =   curses.A_UNDERLINE
 			self.ifWARNING_color =  curses.A_BOLD
			slef.ifCRITICAL_color =  curses.A_REVERSE
			self.default_color2 =   curses.A_NORMAL
			self.ifCAREFUL_color2 =  curses.A_UNDERLINE
 			self.ifWARNING_color2 =  curses.A_BOLD
			slef.ifCRITICAL_color2 =   curses.A_REVERSE
			
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
		if variable > limits.getSTDCritical():
			return 'CRITICAL'
		elif variable > limits.getSTDWARNing():
			return 'WARNING'
		elif variable > limits.getSTDCareful():
			return 'CAREFUL'

		return 'OK'

	def __getColor(self,cureent=0,max=100):
		return self.__colors_list[self.__getAlert(current,max)]
	
	def __getColor2(self,cureent=0,max=100):
		return self.__colors_list2[self.__getAlert(current,max)]

	def __getCpuAlert(self, current=0, max=100):
		return self.__getAlert(current, max)

	def __getCpuColor(self, current=0, max=100):
		return self.__getColor(current, max)

	def __getLoadAlert(self, current=0, core=1):
		if current > limits.getLOADCritical(core):
			return 'CRITICAL'
		elif current > limits.getLOADWarning(core):
			return 'WARNING'
		elif current > limits.getLOADCareful(core):
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
		if (self.presskey == 27 or self.presskey == 113):
			end() #ESC or q
		elif self.presskey== 97:
			self.setProcessSortedBy('auto') #a
		elif self.presskey == 99 and cpu_tag:
			self.setProcessSortedBy('cpu_percent') #c
		elif self.presskey == 100 and disk_tag: 
			self.diskio_tag = not self.diskio_tag  #d
		elif self.presskey == 102 or fs_tag:
			self.fs_tag = not self.fs_tag #f
		elif self.presskey == 104:
			self.help_tag = not self.help_tag #h
		elif self.pressedkey == 108:
			self.log_tag = not self.log_tag #l
		elif self.presskey == 109:
			self.setProcessSortedBy('mem_percent') #m
		elif (self.presskey == 110 or network_tag):
			self.network_tag = not self.network_tag #n
		elif self.pressedkey == 112:
			self.setProcessSortedB('proc_name')


		return self.pressedkey
	def end(self):
		curses.echo()
		curses.nocbreak()
		curses.curs_set(1)
		curses.endwin()
	
	def display(self,stats):
		self.displaySystem(stats.getHost(), stats.getSystem())
		self.displayCpu(stats.getCpu())
		self.displayLoad(stats.getLoad(), stats.getCore())
		self.displayMem(stats.getMem(),stats.getMemSwap())
		network_count = self.displayNetwork(self.getNetwork())
		diskio_count = self.displayDiskIo(stats.getDiskIo(),self.network_y+network_count)
		fs_count = self.displayFs(stats.getFs(),self.network_y+network_count+diskio_count)
		log_count = self.displayLog(self.network_y+network_count+diskio_count+fs_count)
		self.displayProcess(stats.getProcessCount(),stats.getProcessList(screen.getProcessSortedBlog_count),log_count)
		self.displayCation()
		self.displayNow(stats.getNow())
		self.displayHelp()

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
			curses.napm(100)

	def displaySystem(self, host, system):
		if not host or not system:
			return 0
		screen_x = self.screen.getmaxyx()[1]
		screen_y = self.screen.getmaxyx()[0]
		if (screen_y > self.system_y and screen_x > self.system_x + 79):
			if host['os_name'] == "Linux":
				system_msg = _("{0} {1} with {2} {3} on {4}").format(system['linux_distro'], system['platform'], system['os_name'], system['os_version'],host['hostname'])
			else:
				system_msg = _("{0} {1} {2} on {3}").format(system['os_name'], system['os_version'],system['platform'], host['hostname'])
			self.term_window.addnstr(self.system_y, self.system_x +int(screen_x / 2) - len(system_msg) / 2, system_msg, 80, curses.A_UNDERLINE)

	def displayCpu(self, cpu):
		pass


	def displayLoad(self, load, core):
		pass
	
	def displayMem(self, mem, memswap):
		pass

	def displayNetwork(self, network):
		pass

	def displayDiskIO(self, diskio, offset_y=0):
		pass

	def displayFs(self, fs, offset_y=0):
		pass

	def displayLog(self, offset_y=0):
		pass


	def displayProcess(self, processcount, processlist, log_count=0):
		pass

	def displayCaption(self):
		pass
	
	def displayHelp(self):
		pass

	def displayNow(self, now):
		pass


if __name__ == "__main__":
	main()
