ps_cpu_percent_tag = False
ps_mem_usage_tag = False
ps_fs_usage_tag = False
ps_disk_io_tag = False
ps_network_io_tag = False
def get_ps_cpu_percent_tag():
    return ps_cpu_percent_tag
def set_ps_cpu_percent_tag(v):
    global ps_cpu_percent_tag
    ps_cpu_percent_tag = v    

def get_ps_mem_usage_tag():
    return ps_mem_usage_tag
def set_ps_mem_usage_tag(v):
    global ps_mem_usage_tag
    ps_mem_usage_tag = v    

def get_ps_fs_usage_tag():
    return ps_fs_usage_tag
def set_ps_fs_usage_tag(v):
    global ps_fs_usage_tag
    ps_fs_usage_tag = v

def get_ps_disk_io_tag():
    return ps_disk_io_tag
def set_ps_disk_io_tag(v):
    global ps_disk_io_tag
    ps_disk_io_tag = v

def get_ps_network_io_tag():
    return ps_network_io_tag
def set_ps_network_io_tag(v):
    global ps_network_io_tag
    ps_network_io_tag = v