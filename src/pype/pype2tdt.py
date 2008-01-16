# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

from Tkinter import *
from Pmw import *
from guitools import *

import pickle
import glob
from tdt import TDTClient

#from pype import *
from pypedebug import *

class Controller:
    def __init__(self, buttonpane, tdthost):
        self.tdtconnx = TDTClient(tdthost)
        
        button = Checkbutton(buttonpane, text='tdt control',
                             relief=RAISED, pady=4)
        button.pack(expand=0, fill=X, side=TOP)
        
        self.top = DockWindow(checkbutton=button, title='tdt control')

        bb = Frame(self.top)
        bb.pack(fill=X)
        Button(bb, text='clear msg',
               command=lambda s=self: s.text(None)).pack(side=LEFT)
        Button(bb, text='save', command=self.save).pack(side=LEFT)
        Button(bb, text='restore', command=self.restore).pack(side=LEFT)
        Button(bb, text='update', command=self.update).pack(side=LEFT)

		self._info = Label(self.top, text='', anchor=NW, justify=LEFT)
		self._info.pack(expand=1, side=TOP, fill=BOTH)

		self._text = ScrolledText(self.top)
		self._text.pack(expand=1, side=TOP, fill=BOTH)

    def text(self, text):
        w = self._text.component('text')
        w.config(state=NORMAL)
        if text:
            w.insert(END, text)
            w.update()
            w.see(END)
        else:
            w.delete(0.0, END)
        w.config(state=DISABLED)

    def info(self, text):
        self._info.config(text=text)

    def update(self):
        (server, tank, block, tnum) = self.tdtconnx.getblock()
        tank = self.tdtconnx.tank()
        tank = tank.split('\\')[-1]
        
        t = ""
        t = t + "server:  %s\n" % server
        t = t + "  tank:  %s\n" % tank
        t = t + " block:  %s\n" % block
        t = t + " trial:  %d\n" % tnum
        t = t + "  mode:  %s\n" % self.tdtconnx.mode(name=1)
        
        self.info(t)
    
    def save(self):
        # write to next file in pattern tmp-NNN.hoop
        try:
            nmax = 0
            for f in glob.glob('tmp-*.hoop'):
                f = int(f.split('-')[1].split('.')[0])
                nmax = max(nmax, f)
            f = 'tmp-%03d.hoop' % (nmax + 1)
            sortp = self.tdtconnx.sortparams()
            fp = open(f, 'w')
            fp.write(pickle.dumps(sortp))
            fp.close()
            self.text('hoops -> %s\n' % f)
        except:
            reporterror()
            warn('Control.save', 'Error saving TDT hoops');

    def restore(self):
        try:
            nmax = -1
            for f in glob.glob('tmp-*.hoop'):
                f = int(f.split('-')[1].split('.')[0])
                nmax = max(nmax, f)
            if nmax < 0:
                self.text('nothing to restore from!\n')
            else:
                f = 'tmp-%03d.hoop' % nmax
                fp = open(f, 'r')
                sortp = pickle.loads(fp.read())
                self.tdtconnx.sortparams(sortp)
                fp.close()
                self.text('%s -> hoops\n' % f)
        except:
            reporterror()
            warn('Control.restore', 'Error restoring TDT hoops');

    def newblock(self, record=1):
        """just a pass through to underlying tdt instance -- SUBCLASS ME!!"""
        return self.tdtconnx.newblock(record=record)
        
	def getblock(self):
        """just a pass through to underlying tdt instance -- SUBCLASS ME!!"""
        return self.tdtconnx.getblock()
        

if __name__ == '__main__':
    tk = Tk()
    x = Controller(tk, None)
    x.save()
    tk.mainloop()
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass

