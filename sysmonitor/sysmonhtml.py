import jinjia2
class glanceshtml:
    """
    This class manages the HTML output
    """

    def __init__(self, htmlfolder="/usr/share", refresh_time=1):
        # Global information to display

        # Init refresh time
        self.__refresh_time = refresh_time

        # Set the templates path
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(htmlfolder + '/html'),
            extensions=['jinja2.ext.loopcontrols'])

        # Open the template
        self.template = environment.get_template('default.html')

        # Define the colors list (hash table) for logged stats
        self.__colors_list = {
            #         CAREFUL WARNING CRITICAL
            'DEFAULT': "bgcdefault fgdefault",
            'OK': "bgcok fgok",
            'CAREFUL': "bgccareful fgcareful",
            'WARNING': "bgcwarning fgcwarning",
            'CRITICAL': "bgcritical fgcritical"
        }

    def __getAlert(self, current=0, max=100):
        # If current < CAREFUL of max then alert = OK
        # If current > CAREFUL of max then alert = CAREFUL
        # If current > WARNING of max then alert = WARNING
        # If current > CRITICAL of max then alert = CRITICAL
        try:
            (current * 100) / max
        except ZeroDivisionError:
            return 'DEFAULT'

        variable = (current * 100) / max

        if variable > limits.getSTDCritical():
            return 'CRITICAL'
        elif variable > limits.getSTDWarning():
            return 'WARNING'
        elif variable > limits.getSTDCareful():
            return 'CAREFUL'

        return 'OK'

    def __getColor(self, current=0, max=100):
        """
        Return colors for logged stats
        """
        return self.__colors_list[self.__getAlert(current, max)]

    def __getCpuColor(self, cpu, max=100):
        cpu['user_color'] = self.__getColor(cpu['user'], max)
        cpu['kernel_color'] = self.__getColor(cpu['kernel'], max)
        cpu['nice_color'] = self.__getColor(cpu['nice'], max)
        return cpu

    def __getLoadAlert(self, current=0, core=1):
        # If current < CAREFUL*core of max then alert = OK
        # If current > CAREFUL*core of max then alert = CAREFUL
        # If current > WARNING*core of max then alert = WARNING
        # If current > CRITICAL*core of max then alert = CRITICAL
        if current > limits.getLOADCritical(core):
            return 'CRITICAL'
        elif current > limits.getLOADWarning(core):
            return 'WARNING'
        elif current > limits.getLOADCareful(core):
            return 'CAREFUL'
        return 'OK'

    def __getLoadColor(self, load, core=1):
        load['min1_color'] = (
            self.__colors_list[self.__getLoadAlert(load['min1'], core)])
        load['min5_color'] = (
            self.__colors_list[self.__getLoadAlert(load['min5'], core)])
        load['min15_color'] = (
            self.__colors_list[self.__getLoadAlert(load['min15'], core)])
        return load

    def __getMemColor(self, mem):
        real_used_phymem = mem['used'] - mem['cache']
        mem['used_color'] = self.__getColor(real_used_phymem, mem['total'])

        return mem

    def __getMemSwapColor(self, memswap):
        memswap['used_color'] = self.__getColor(memswap['used'],
                                                memswap['total'])
        return memswap

    def __getFsColor(self, fs):
        mounted = 0
        for mounted in xrange(0, len(fs)):
            fs[mounted]['used_color'] = self.__getColor(fs[mounted]['used'],
                                                        fs[mounted]['size'])
        return fs

    def update(self, stats):
        if stats.getcpu():
            # Open the output file
            f = open('sysmon.html', 'w')

            # Process color

            # Render it
            # HTML Refresh is set to 1.5 * refresh_time
            # ... to avoid display while page rendering
            data = self.template.render(
                refresh=int(self.__refresh_time * 1.5),
                host=stats.gethost(),
                system=stats.getsystem(),
                cpu=self.__getCpuColor(stats.getcpu()),
                load=self.__getLoadColor(stats.getload(), stats.getcore()),
                core=stats.getcore(),
                mem=self.__getMemColor(stats.getmem()),
                memswap=self.__getMemSwapColor(stats.getmemswap()),
                net=stats.getnetwork(),
                diskio=stats.getdiskio(),
                fs=self.__getFsColor(stats.getfs()),
                proccount=stats.getprocesscount(),
                proclist=stats.getprocesslist())

            # Write data into the file
            f.write(data)

            # Close the file
            f.close()