#!/usr/bin/env python
from __future__ import generators
__appname__ = 'sysmon';
__version__ = '1.0'
__author__ = 'bhfwg'
__license__ = 'LGPL'
import sys
import platform
import getopt
import signal
import time
from datetime import datetime, timedelta
import gettext
#from sysmonlimits import sysmonlimits
#from sysmonlogs import sysmonlogs
from sysmonstats import sysmonstats
from sysmoncsv import sysmoncsv
from sysmondisplay import sysmondisplay
import myglobal

gettext.install(__appname__)
try:
	import curses
	import curses.panel
except ImportError:
	print _('curses module not found')
	sys.exit(1)

try:
	import psutil as ps
except ImportError:
	print _('psutil module not found')
	print _('using pip install psutil')
	sys.exit(1)

try:
	ps.Process(os.getpid()).get_cpu_percent(interval=0)
except Exception:
	myglobal.set_ps_cpu_percent_tag(False)
else:
	myglobal.set_ps_cpu_percent_tag (True)

try:
	ps.phymem_usage()
	ps.virtmem_usage()
except Exception:
	myglobal.set_ps_mem_usage_tag(False)
else:
	myglobal.set_ps_mem_usage_tag(True )

try:
	ps.disk_partitions()
	ps.disk_usage('/')
except Exception:
	myglobal.set_ps_fs_usage_tag(False)
else:
	myglobal.set_ps_fs_usage_tag(True)

try:
	ps.disk_io_counters()
except Exception:
	myglobal.set_ps_disk_io_tag(False)
else:
	myglobal.set_ps_disk_io_tag(True)

try:
	ps.network_io_counters()
except Exception:
	myglobal.set_ps_network_io_tag(False)
else:
	myglobal.set_ps_network_io_tag(True)

try:
	import jinja2
except ImportError:
	jinjia_tag= False
else:
	jinjia_tag = True

try:
	import csv
except ImportError:
	csvlib_tag=False
else:
	csvlib_tag = True

#print
#print 'ps_cpu_percent_tag=', myglobal.get_ps_cpu_percent_tag()
#print 'ps_mem_usage_tag=',myglobal.get_ps_mem_usage_tag()
#print 'ps_fs_usage_tag=', myglobal.get_ps_fs_usage_tag()
#print 'ps_disk_io_tag=',myglobal.get_ps_disk_io_tag()
#print 'ps_network_io_tag=',myglobal.get_ps_network_io_tag()
#print 'jinjia_tag=', jinjia_tag 
#print 'csvlib_tag=', csvlib_tag 
#print

def printVersion():
	print _("sysmon version : ") + __version__

def printSyntax():
	printVersion()
	print _("usage: sysmon [-f file] [-o output] [-t sec] [-h] [-v]")
	print _("\t-d\t\tDisable disk I/O module")
	print _("\t-m\t\tDisable mount module")
	print _("\t-n\t\tDisable network module")
	print _("\t-f file\t\tSet the output folder (HTML) or file (CSV")
	print _("\t-h\t\tDisplay the syntax and exit")
	print _("\t-o output\tDefine additional output (avaiable: HTML or CVS)")
	print _("\t-t sec\t\tSet the refresh time in seconds(default: %d)" % refresh_time) 
	print _("\t-v\t\tDisplay the version and exit")	
	
def init():
	#global limits, logs, stats, screen
	global stats, screen
	global htmloutput, csvoutput
	global html_tag, csv_tag
	global refresh_time
	
        myglobal.set_ps_network_io_tag(True)
        myglobal.set_ps_disk_io_tag(True)
        myglobal.set_ps_fs_usage_tag(True)
        myglobal.set_ps_mem_usage_tag(True)
        myglobal.set_ps_cpu_percent_tag(True)

	html_tag = False
	csv_tag = False
	refresh_time  = 2
	try:
		opts,args = getopt.getopt(sys.argv[1:],"dmnho:f:t:v",["help","output","file","time","version"])
	except getopt.GetoptError, err:
		print str(err)
		printSyntax()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-v", "--version"):
			printVersion()
			sys.exit(0)
		elif opt in ("-h", "--help"):
                        printSyntax()
                        sys.exit(0)
		elif opt in ("-o", "--output"):
			if arg == "html":
				if jinja_tag:
					html_tag=True
				else:
					print _("Error: Need Jinjia2 library to export into HTML")
					print
					print _("Try to install the python-jinjia2 package")
					sys.exit(2)
			elif arg == "csv":
					if csvlib_tag:
						csv_tag = True
                                                print 'csv_tag is true 1'
					else:
						print _("Error: Need CSV library to export to CSV")
						sys.exit(2)
			else:
				print _("Error: Unknown output %s" % arg)
				sys.exit(2)
		elif opt in ("-f", "--file"):
			output_file = arg
			output_folder = arg
		elif opt in ("-t","--time"):
			if int(arg) >= 1:
				refresh_time = int(arg)
			else:
				print _("Error: Refresh time should be a positive integer")
				sys.exit(2)
		elif opt in ("d", "--diskio"):
			myglobal.set_ps_disk_io_tag(False)
		elif opt in ("-m", "--mount"):
			myglobal.set_ps_fs_usage_tag(False)
		elif opt in ("-n", "--netrate"):
			myglobal.set_ps_network_io_tag(False)
		else:
			printSyntax()
			sys.exit(0)
	if html_tag:
		try:
			output_folder
		except UnboundLocalError:
			print _("Error: HTML export (-o html) need output folder definition (-f <folder>)")
			sys.exit(2)
	if csv_tag:
                print 'csv_tag is true 2'
		try:
			output_file
		except UnboundLocalError:
			print _("Error: CSV export (-o csv) need"
				"output file definition (-<file>)")
			sys.exit(2)
	
	signal.signal(signal.SIGINT, signal_handler)
        #limits = sysmonlimits()
	#logs = sysmonlogs()
	stats = sysmonstats()

	if html_tag:
		htmloutput = sysmonhtml(htmlfolder= output_folder, refresh_time = refresh_time)
	if csv_tag:
		csvoutput = sysmoncsv(csvfile = output_file, refresh_time=refresh_time)

	screen = sysmondisplay(refresh_time=refresh_time)

def main():
        #python sysmon.py -f ./test.csv -o csv -t 2
	print _("-------------------sysmon start--------------------")

	init()
	while True:
		stats.update()
		screen.update(stats)
		if html_tag :
			htmloutput.update(stats)
		if csv_tag:
			csvoutput.update(stats)
                        
	print _("-------------------sysmon end--------------------")

def end():
	screen.end()
	print _("-------------------sysmon end--------------------")
	if csv_tag:
		csvoutput.exit()
	sys.exit(0)

def signal_handler(signal, frame):
	end()

if __name__ == "__main__":
	main()
