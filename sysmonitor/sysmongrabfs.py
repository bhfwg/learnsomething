import psutil as ps
class sysmongrabfs:
	''' get fs state'''

	def __init__(self):
		self.ignore_fsname = ('', 'none', 'gvfs_fuse-daemon', 'fusectl','cgroup')
		self.ignore_fstype = ('binfmt_misc', 'devpts', 'iso9660', 'none', 'proc', 'sysfs', 'usbfs','rootfs','autpfs','devtmpfs')
	
	def __update__(self):
		self.fs_list = []
		fs_state = ps.disk_partitions(True)
		for fs in xrange(len(fs_stat)):
			fs_current = {}
			fs_current['device_name'] = fs_state[fs].device
			if fs_current['device_name'] in self.ignore_fsname:
				continue
			fs_current['fs_type'] = fs_state[fs].fstype
			if fs_current['fs_type'] in self.ignore_fstype:
				continue
			fs_current['mnt_point'] = fs_state[fs].mountpoint
			try:
				fs_usage = ps.disk_usage(fs_current['mnt_point'])
			except Exception:
				continue
			fs_current['size'] = fs_usage.total
			fs_current['used'] = fs_usage.used
			fs_currrnt['avail'] = fs_usage.free

			self.fs_list.append(fs_current)
	
	def get(self):
		self.__update__()
		return self.fs_list

if __name__ == '__main__':
	pass
