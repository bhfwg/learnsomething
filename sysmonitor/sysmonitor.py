#!/usr/bin/env python
from __future__ import generators
__appname__ = 'sysmonitor';
__version__ = '1.0'
__author__ = 'bhfwg'
__license__ = 'LGPL'
import os
import sys
import platform
import getopt
import signal
import time
from datetime import datetime, timedelta
import gettext
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
	ps_get_cpu_percent_tag = False
else:
	ps_get_cput_percent_tag = True

try:
	ps.phymem_usage()
	ps.virtmem_usage()
except Exception:
	ps_mem_usage_tag = False
else:
	ps_mem_usage_tag = True 

try:
	ps.disk_partitions()
	ps.disk_usage('/')
except Exception:
	ps_fs_usage_tag = False
else:
	ps_fs_usage_tag = True

try:
	ps.disk_io_counters()
except Exception:
	ps_disk_io_tag = False
else:
	ps_disk_io_tag = True

try:
	ps_network_io_counters()
except Exception:
	ps_network_io_tag = False
else:
	ps_network_io_tag = True

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

print 'ps_get_cpu_percent_tag=', ps_get_cpu_percent_tag
print 'ps_mem_usage_tag=', ps_mem_usage_tag
print 'ps_fs_usage_tag=', ps_fs_usage_tag
print 'ps_disk_io_tag=',ps_disk_io_tag
print 'ps_network_io_tag=',ps_network_io_tag
print 'jinjia_tag=', jinjia_tag 
print 'csvlib_tag=', csvlib_tag 


def printVersion():
	print _("sysmonitor version : ") + __version__

def printSyntax():
	printVersion()
	print _("usage: sysmonitor [-f file] [-o output] [-t sec] [-h] [-v]")
	print _("\t-d\t\tDisable disk I/O module")
	print _("\t-f file\t\tSet the output folder (HTML) or file (CVS)")
	print _("\t-h\t\tDisplay the syntax and exit")
	print _("\t-m\t\tDisable mount module")
	print _("\t-n\t\tDisable network module")
	print _("\t-o output\t\tDefine additional output (avaiable: HTML or CVS)")
	print _("\t-t sec\t\tSet the refresh time in seconds(default: %d)" % refresh_time) 
	print _("\t-v\t\tDisplay the version and exit")	
	
def init():
	global ps_disk_io_tag, ps_fs_usage_tag, ps_network_io_tag
	global limits, logs, stats, screen
	global htmloutput, csvoutput
	global html_tag, csv_tag
	global refresh_time
	
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
			ps_disk_io_tag = Flase
		elif opt in ("-m", "--mount"):
			ps_fs_usage_tag = False
		elif opt in ("-n", "--netrate"):
			ps_network_io_tag = False
		else:
			printSyntax()
			sys.exit(0)
	if html_tag:
		try:
			output_folder
		except UnboundLocalError:
			print _("Error: HTML export (-o html) need"
				"output folder definition (-f <folder>)")
			sys.exit(2)
	if csv_tag:
		try:
			output_file
		except UnboundLocalError:
			print _("Error: CSV export (-o csv) need"
				"output file definition (-<file>)")
			sys.exit(2)
		
def main():
	print _("-------------------sysmonitor start--------------------")
	init()
'''
	while True:
		stats.update()
		screen.update(stats)
		if html_tag :
			htmloutput.update(stats)
		if csv_tag:
			csvoutput.update(stats)
	print _("-------------------sysmonitor end--------------------")
'''
def end():
	screen.end()
	print _("-------------------sysmonitor end--------------------")

if __name__ == "__main__":
	main()
