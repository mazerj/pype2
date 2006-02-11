# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys, types
from pype import *
from Tkinter import *
from events import *
import math

def Run(app):
	app.eyetrace(1)
	try:
		while 1:
			c = app.fb.getkey()
			if c != 0:
				print c
			s1 = 'ESCAPE TO END\n'
			s2 = 'eye.x = %d\neye.y = %d\n' % app.eyepos()
			app.udpy_note(s1+s2)
			app.fb.clear((50,50,50))
			app.fb.string(0, 0, s2, (255,255,255));
			app.fb.flip()

			app.idlefn(ms=10)
	except UserAbort:
		pass
	app.eyetrace(0)

def main(app):
	app.startfn = Run

def cleanup(app):
	pass

if not __name__ == '__main__':
	print "Loaded %s" % __name__
else:
	print "nothing to do (%s)." % __name__
