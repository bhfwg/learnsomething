import curses
from sysmonstats import sysmonstats
from sysmontimer import sysmontimer
from sysmonlimits import sysmonlimits
from sysmonlogs import sysmonlogs
import myglobal
import traceback
from datetime import datetime 
from datetime import timedelta 
import sys
class sysmondisplay:
        __process_sortedby = 'auto'
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

                self.network_count = 0
                self.diskio_count = 0
                self.fs_count = 0

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

	def setProcesssortedBy(self,sorted):
		self.__process_sortedautoflag = False
		self.__process_sortedby = sorted

	def getProcesssortedBy(self):
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
			self.setProcesssortedBy('auto') #a sort process auto
		elif self.pressedkey == 99 and myglobal.get_ps_cpu_percent_tag():
			self.setProcesssortedBy('cpu_percent') #c sort process by cpu_percent
		elif self.pressedkey == 100 and myglobal.get_ps_disk_io_tag(): 
			self.diskio_tag = not self.diskio_tag  #d show/hide diskio stat
		elif self.pressedkey == 102 and myglobal.get_ps_fs_usage_tag():
			self.fs_tag = not self.fs_tag #f show/hide fs usage
		elif self.pressedkey == 104:
			self.help_tag = not self.help_tag #h show/hide help
		elif self.pressedkey == 108:
			self.log_tag = not self.log_tag #l show/hide log message
		elif self.pressedkey == 109:
			self.setProcesssortedBy('mem_percent') #m sort process by Mem usage
		elif self.pressedkey == 110 and myglobal.get_ps_network_io_tag():
			self.network_tag = not self.network_tag #n show/hide network state
		elif self.pressedkey == 112:
			self.setProcesssortedBy('proc_name')#p sort process by name

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
                self.network_count = self.displayNetwork(stats.getNetwork())
		self.diskio_count = self.displayDiskIO(stats.getDiskIo(), self.network_y + self.network_count)
		self.fs_count = self.displayFs(stats.getFs(), self.network_y+ self.network_count + self.diskio_count)
		log_count = self.displayLog(self.network_y + self.network_count + self.diskio_count + self.fs_count)
		self.displayProcess(stats.getProcessCount(), stats.getProcessList(self.getProcesssortedBy()), log_count)
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
                    self.logs.add(alert,"CPU user", cpu['user'])#"CPU user"
                    self.term_window.addnstr(self.cpu_y+1, self.cpu_x+10, "%.1f" % cpu['user'], 8, self.__colors_list[alert])
                
                    alert = self.__getCpuAlert(cpu['kernel'])
                    self.logs.add(alert,"CPU kernel", cpu['kernel'])#"CPU kernel"
                    self.term_window.addnstr(self.cpu_y+2, self.cpu_x+10, "%.1f" % cpu['kernel'], 8, self.__colors_list[alert])

                    alert = self.__getCpuAlert(cpu['nice'])
                    self.logs.add(alert,"CPU nice", cpu['nice'])#"CPU nice"
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
                    self.logs.add(alert,"LOAD 5-min", load['min5'])#"LOAD 5-min"
                    self.term_window.addnstr(self.load_y+2, self.load_x+10, "%.2f" % load['min5'], 8,self.__colors_list[alert])

                    alert = self.__getLoadAlert(load['min15'],core)
                    self.logs.add(alert,"LOAD 15-min", load['min15'])#"LOAD 15-min"
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
                    self.logs.add(alert,"MEM real",real_used_phymem)#MEM real
                    self.term_window.addnstr(self.mem_y+2, self.mem_x+15, "({0})".format(self.__autoUnit(real_used_phymem)), 8,self.__colors_list[alert])
                    self.term_window.addnstr(self.mem_y+3, self.mem_x+15, "({0})".format(self.__autoUnit(real_free_phymem)), 8)
                
                    self.term_window.addnstr(self.mem_y, self.mem_x+25, "Swap", 8, self.title_color if self.hascolors else curses.A_UNDERLINE)
                    self.term_window.addnstr(self.mem_y+1, self.mem_x+25, ('Total:'), 8)
                    self.term_window.addnstr(self.mem_y+2, self.mem_x+25, ('Userd:'), 8)
                    self.term_window.addnstr(self.mem_y+3, self.mem_x+25, ('Free:'), 8)

                    self.term_window.addnstr(self.mem_y, self.mem_x+34, "{:.1%}".format(memswap['percent']/100), 8)
                    alert = self.__getMemAlert(memswap['used'], memswap['total'])
                    self.logs.add(alert,"MEM swap", memswap['used'])#MEM swap
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
                        if disk > 10:
                            break
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
                        if mounted >10:
                            break
                    return mounted+3
                return 0

	def displayLog(self, offset_y=0):
                if self.logs.len()==0 or not self.log_tag: 
                    #self.term_window.addnstr(0, 0,"logs:"+str(self.logs.len()), 8)
                    return 0
                else:
                    #self.term_window.addnstr(1, 0,"logs:"+str(self.logs.len()), 8)
                    pass
                    
		screen_x = self.screen.getmaxyx()[1]
                screen_y = self.screen.getmaxyx()[0]
                self.log_y = offset_y
                if(screen_y > (self.log_y + 3) and screen_x > (self.log_x + 79)):
                    self.log_y = max(offset_y, screen_y-3-min(offset_y -3, screen_y-self.log_y, self.logs.len()))
                    logtodisplay = min(screen_y-self.log_y-3, self.logs.len())
                    logmsg = ("WARNING|CRITICAL| logs for CPU|LOAD|MEM ")
                    if(logtodisplay > 1):
                        logmsg +=("lasts " + str(logtodisplay) + " entries")
                    else:
                        logmsg +=("one entry")
                    self.term_window.addnstr(self.log_y, self.log_x, logmsg, 79, self.title_color if  self.hascolors else curses.A_UNDERLINE)
                    ii =0
                    log = self.logs.get()
                    for ii in xrange(0,logtodisplay):
                        logmsg = "  " + str(datetime.fromtimestamp(log[ii][0]))
                        if (log[ii][1] > 0):
                            logmark = ' '
                            logmark += (' > ')+ str(datetime.fromtimestamp(log[ii][1]))
                        else:
                            logmark='~'
                            logmark += (' > ')+ "%19s" %"___________________"

                        if log[ii][3][:3] =="MEM":
                            logmsg += " {0} ({1}/{2}/{3})".format(log[ii][3], self.__autoUnit(log[ii][6]), self.__autoUnit(log[ii][5]), self.__autoUnit(log[ii][4]))
                        else:
                            logmsg += " {0} ({1:.1f}/{2:.1f}/{3:.1f})".format(log[ii][3], log[ii][6], log[ii][5], log[ii][4])
                        self.term_window.addnstr(self.log_y+1+ii, self.log_x, logmsg, 79)
                        self.term_window.addnstr(self.log_y+1+ii, self.log_x, logmark, 1, self.__colors_list[log[ii][2]])
                    return ii +3
                return 0


	def displayProcess(self, processcount, processlist, log_count=0):
		if not processcount: 
                    return 0
		screen_x = self.screen.getmaxyx()[1]
                screen_y = self.screen.getmaxyx()[0]
                if ( not self.network_tag and not self.diskio_tag and not self.fs_tag):
                    process_x = 0
                else:
                    process_x = self.process_x                

                if(screen_y > (self.process_y + 3) and screen_x > (self.process_x + 48)):
                    self.term_window.addnstr(self.process_y, process_x, "Processes", 9, self.title_color if  self.hascolors else curses.A_UNDERLINE)
                    other = (processcount['total'] - processcount['running'] - processcount['sleeping'])
                    self.term_window.addnstr(self.process_y, process_x+10,  "{0}, {1} {2}, {3} {4}, {5} {6}".format(str(processcount['total']), str(processcount['running']), 'running', str(processcount['sleeping']), 'sleeping', str(other), 'other'), 42)
                tag_pid = False
                tag_uid = False
                tag_nice = False
                tag_status = False
                tag_proc_time = False
                if screen_x > process_x + 55:
                    tag_pid =True
                if screen_x > process_x + 64:
                    tag_uid =True
                if screen_x > process_x + 70:
                    tag_nice =True
                if screen_x > process_x + 74:
                    tag_status =True
                if screen_x > process_x + 77:
                    tag_proc_time =True

                if (screen_y > self.process_y+8 and screen_x > process_x+49):
                    self.term_window.addnstr(self.process_y+2, process_x, ("VIRT") , 5)
                    self.term_window.addnstr(self.process_y+2, process_x+7, ("RES") , 5)
                    self.term_window.addnstr(self.process_y+2, process_x+14, ("CPU%"),5 , curses.A_UNDERLINE if self.getProcesssortedBy() == 'cpu_percent' else 0)
                    self.term_window.addnstr(self.process_y+2, process_x+21, ("MEM%"),5 , curses.A_UNDERLINE if self.getProcesssortedBy() == 'mem_percent' else 0)
                    process_name_x =28
                    if  tag_pid:
                        self.term_window.addnstr(self.process_y+2, process_x + process_name_x, ("PID"), 6)
                        process_name_x += 7
                    if  tag_uid:
                        self.term_window.addnstr(self.process_y+2, process_x + process_name_x, ("USER"), 8)
                        process_name_x += 10
                    if  tag_nice:
                        self.term_window.addnstr(self.process_y+2, process_x + process_name_x, ("NI"), 3)
                        process_name_x += 4
                    if  tag_status:
                        self.term_window.addnstr(self.process_y+2, process_x + process_name_x, ("S"), 1)
                        process_name_x += 3
                    if  tag_proc_time:
                        self.term_window.addnstr(self.process_y+2, process_x + process_name_x, ("TIME+"), 8)
                        process_name_x += 10
                    
                    self.term_window.addnstr(self.process_y+2, process_x+process_name_x, ("NAME"), 12, curses.A_UNDERLINE if self.getProcesssortedBy() == 'proc_name' else 0)

                    if not processlist:
                        self.term_window.addnstr(self.process_y+3, self.process_x, ("Compute data..."), 15)
                        return 6

                    proc_num = min(screen_y - self.term_h+self.process_y-log_count+5, len(processlist))

                    for processes in xrange(0, proc_num):
                        process_size = processlist[processes]['proc_size']
                        self.term_window.addnstr(self.process_y+3+processes, process_x, self.__autoUnit(process_size),5)
                        process_resident = processlist[processes]['proc_resident']
                        self.term_window.addnstr(self.process_y+3+processes, process_x+7, self.__autoUnit(process_resident),5)

                        cpu_percent = processlist[processes]['cpu_percent']
                        if myglobal.get_ps_cpu_percent_tag():
                            self.term_window.addnstr(self.process_y+3+processes, process_x+14, "{:.1f}".format(cpu_percent),5,self.__getProcessColor(cpu_percent))
                        else:
                            self.term_window.addnstr(self.process_y+3+processes, process_x, "N/A", 8)
                    
                        mem_percent = processlist[processes]['mem_percent']
                        self.term_window.addnstr(self.process_y+3+processes, process_x+21, "{:.1f}".format(mem_percent),5,self.__getProcessColor(mem_percent))
                        
                        if tag_pid:
                            pid = processlist[processes]['pid']
                            self.term_window.addnstr(self.process_y+3+processes, process_x+28, str(pid),6)

                        if tag_uid:
                            uid = processlist[processes]['uid']
                            self.term_window.addnstr(self.process_y+3+processes, process_x+35, str(uid),8)

                        if tag_nice:
                            nice = processlist[processes]['nice']
                            self.term_window.addnstr(self.process_y+3+processes, process_x+45, str(nice),3)

                        if tag_status:
                            status = processlist[processes]['status']
                            self.term_window.addnstr(self.process_y+3+processes, process_x+49, str(nice),1)

                        if tag_proc_time:
                            process_time = processlist[processes]['proc_time']
                            dtime = timedelta(seconds=sum(process_time))
                            dtime = '{0}:{1}.{2}'.format(str(dtime.seconds//60 %60).zfill(2), str(dtime.seconds%60).zfill(2), str(dtime.microseconds)[:2])
                            self.term_window.addnstr(self.process_y+3+processes, process_x+52, dtime, 8)

                        max_process_name = screen_x - process_x - process_name_x
                        process_name = processlist[processes]['proc_name']
                        process_cmdline = processlist[processes]['proc_cmdline']
                        if (len(process_cmdline) > max_process_name or len(process_cmdline)==0):
                            command = process_name
                        else:
                            command = process_cmdline
                        self.term_window.addnstr(self.process_y+3+processes, process_x + process_name_x, str(command), max_process_name)


	def displayCaption(self):
		screen_x = self.screen.getmaxyx()[1]
                screen_y = self.screen.getmaxyx()[0]
                msg = ("Press 'h' for help")
                if(screen_y > self.caption_y  and screen_x > self.caption_x+32 ):
                    self.term_window.addnstr(max(self.caption_y, screen_y-1), self.caption_x,  msg, self.default_color)
	
	def displayHelp(self):
                if not self.help_tag: 
                    return 0
		screen_x = self.screen.getmaxyx()[1]
                screen_y = self.screen.getmaxyx()[0]
                if(screen_y > (self.help_y + 23) and screen_x > (self.help_x + 79)):
                    self.erase()
                    ver ="glances version:"+myglobal.glance_version+"   psutil version:"+myglobal.ps_version
                    self.term_window.addnstr(self.help_y, self.help_x, ver, 79, self.title_color if  self.hascolors else 0)
                    self.term_window.addnstr(self.help_y+2, self.help_x, "Captions: ", 79)
                    self.term_window.addnstr(self.help_y+2, self.help_x+10, "   OK   ", 8,self.default_color)
                    self.term_window.addnstr(self.help_y+2, self.help_x+18, "CAREFUL ", 8,self.ifCAREFUL_color)
                    self.term_window.addnstr(self.help_y+2, self.help_x+26, "WARNING ", 8,self.ifWARNING_color)
                    self.term_window.addnstr(self.help_y+2, self.help_x+34, "CRITICAL", 8,self.ifCRITICAL_color)

                    width=5
                    self.term_window.addnstr(self.help_y+4, self.help_x, "{0:^{width}} {1}".format("Key","Function",width=width),  79, self.title_color if  self.hascolors else 0)
                    self.term_window.addnstr(self.help_y+5, self.help_x, "{0:^{width}} {1}".format("a","sort processes automatically","(need psutil 0.2.0+)",width=width),  79, self.ifCRITICAL_color2 if myglobal.get_ps_cpu_percent_tag() else 0)
                    #self.term_window.addnstr(self.help_y+6, self.help_x, "{0:^{width}} {1}".format("c","sort processes by CPU%","(need psutil 0.2.0+)",width=width),  79, self.ifCRITICAL_color2 if myglobal.get_ps_cpu_percent_tag() else 0)
                    self.term_window.addnstr(self.help_y+6, self.help_x, "{0:^{width}} {1}".format("c","sort processes by CPU%","(need psutil 0.2.0+)",width=width),  79)
                    self.term_window.addnstr(self.help_y+7, self.help_x, "{0:^{width}} {1}".format("m","sort processes by MEM%",width=width),  79)
                    self.term_window.addnstr(self.help_y+8, self.help_x, "{0:^{width}} {1}".format("p","sort processes by name",width=width),  79)
                    self.term_window.addnstr(self.help_y+9, self.help_x, "{0:^{width}} {1}".format("d","show/hide disk I/O stats","(need psutil 0.2.0+)",width=width),  79, self.ifCRITICAL_color2 if myglobal.get_ps_disk_io_tag() else 0)
                    self.term_window.addnstr(self.help_y+10, self.help_x, "{0:^{width}} {1}".format("f","show/hide file system stats","(need psutil 0.2.0+)",width=width),  79, self.ifCRITICAL_color2 if myglobal.get_ps_fs_usage_tag() else 0)
                    self.term_window.addnstr(self.help_y+11, self.help_x, "{0:^{width}} {1}".format("n","show/hide network stats","(need psutil 0.2.0+)",width=width),  79, self.ifCRITICAL_color2 if myglobal.get_ps_network_io_tag() else 0)
                    self.term_window.addnstr(self.help_y+12, self.help_x, "{0:^{width}} {1}".format("l","show/hide log messages",width=width),  79, self.ifCRITICAL_color2 if self.log_tag else 0)
                    self.term_window.addnstr(self.help_y+13, self.help_x, "{0:^{width}} {1}".format("h","show/hide this help message",width=width),  79, self.ifCRITICAL_color2 if self.help_tag else 0)
                    self.term_window.addnstr(self.help_y+14, self.help_x, "{0:^{width}} {1}".format("q","Quit (Esc and Ctrl-C also work)",width=width),  79)



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
