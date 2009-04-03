# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys, types
from pype import *
from Tkinter import *
from events import *
import math
from Numeric import *
from iplot import *

from dacq import *

def Run(app):
	app.fb.clear((128,128,128))
	app.fb.sync(0)
	app.fb.flip()

	app.fb.clear((128,128,128))
	app.fb.sync(0)
	app.fb.flip()

	app.eyetrace(1)
	app.record_start()

	s = 1
	
	app.idlefn(500)
	
	for i in range(10):
		if s:
			app.fb.sync(1)
		else:
			app.fb.sync(0)
		app.fb.flip()
		app.encode('flip %d' % s)
		s = not s
		app.idlefn(500)
		
	app.idlefn(500)
	
	app.eyetrace(0)
	app.record_done()

	(t, p, s) = app.record_write(None, None, None)
	

	subplot(2,1,1)
	plot(t, p)
	ylabel('photo')
	subplot(2,1,2)
	plot(t, s)
	ylabel('spikes')
	

def main(app):
	app.startfn = Run

def cleanup(app):
	pass

if not __name__ == '__main__':
	print "Loaded %s" % __name__
else:
	print "nothing to do (%s)." % __name__


