# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

from Tkinter import *
from Pmw import *
from guitools import *

import cPickle
import glob
import tdt

#from pype import *
from pypedebug import *

class Controller:
    def __init__(self, app, tdthost):
        self.tdtconnx = tdt.TDTClient(tdthost)
        self.app = app
        self._server = None
        self._tank = None
        self._block = None

    def save(self):
        # write to next file in pattern tmp-NNN.hoop
        try:
            nmax = 0
            for f in glob.glob('tmp-*.hoop'):
                f = int(f.split('-')[1].split('.')[0])
                nmax = max(nmax, f)
            f = 'tmp-%03d.hoop' % (nmax + 1)
            sortp = self.tdtconnx.tdev_sortparams()
            fp = open(f, 'w')
            fp.write(cPickle.dumps(sortp))
            fp.close()
            self.app.console.writenl('hoops -> %s' % f)
        except:
			# [[effort to remove all unnamed exceptions:
			import pypedebug
			pypedebug.get_traceback(1)
			# effort to remove all unnamed exceptions:]]
            reporterror()
            warn('tdt save', 'Error saving TDT hoops');

    def restore(self):
        try:
            nmax = -1
            for f in glob.glob('tmp-*.hoop'):
                f = int(f.split('-')[1].split('.')[0])
                nmax = max(nmax, f)
            if nmax < 0:
                self.app.console.writenl('nothing to restore from!')
            else:
                f = 'tmp-%03d.hoop' % nmax
                fp = open(f, 'r')
                sortp = cPickle.loads(fp.read())
                self.tdtconnx.tdev_sortparams(sortp)
                fp.close()
                self.app.console.writenl('%s -> hoops' % f)
        except:
			# [[effort to remove all unnamed exceptions:
			import pypedebug
			pypedebug.get_traceback(1)
			# effort to remove all unnamed exceptions:]]
            
            reporterror()
            warn('tdt restore', 'Error restoring TDT hoops');

    def settank(self, dirname, name):
        # this will only work in IDLE or STANDBY mode, so do it 1st!

        td = self.tdtconnx.tdev_invoke
        tt = self.tdtconnx.ttank_invoke

        if not tt('CheckTank', '%s%s' % (dirname, name)):
            tt('AddTank', name, dirname)
            
        if td('SetTankName', '%s%s' % (dirname, name)) == 0:
            # circuit's probably not running, bail now..
            return None

        for x in [tdt.STANDBY, tdt.RECORD, tdt.PREVIEW]:
            td('SetSysMode', x)
            while td('GetSysMode') != x:
                pass
            
        tt('OpenTank', '%s%s' % (dirname, name), 'R')

        return td('GetTankName')

    def newblock(self, record=1):
        (self._server, self._tank, self._block) = \
                       self.tdtconnx.tdev_newblock(record=record)
        return (self._server, self._tank, self._block)
        
	def getblock(self):
        tnum = self.tdtconnx.tdev_tnum()
        return (self._server, self._tank, self._block, tnum)
    
if __name__ == '__main__':
	sys.stderr.write('%s should never be loaded as main.\n' % __file__)
	sys.exit(1)
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
		
