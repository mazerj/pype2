# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys, types
from pype import *
from Tkinter import *
from events import *
import math

def Run(app):
	try:
		while 1:
			s = 'bardown=%d sw1=%d sw2=%d' % \
				 (app.bardown(), app.sw1(), app.sw2())
			app.udpy_note(s)
			app.fb.clear((50,50,50))
			app.fb.string(0, 0, s, (255,255,255));
			app.fb.flip()
			app.idlefn(ms=50)
	except UserAbort:
		pass

def main(app):
	app.startfn = Run

def cleanup(app):
	pass

if not __name__ == '__main__':
	print "Loaded %s" % __name__
else:
	print "nothing to do (%s)." % __name__
