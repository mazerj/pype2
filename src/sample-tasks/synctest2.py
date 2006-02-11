# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys, types
from pype import *
from Tkinter import *
from events import *
import math
from mplot import *
from Numeric import *

def Run(app):
	s = Sprite(x=0, y=0, fb=app.fb, width=100, height=100, on=1)
	s.fill((1,100,1))
	
	app.fb.clear((1,255,1))
	app.fb.sync(0)
	app.fb.flip()
	warn("warn", "sync off", wait=1)

	
	app.fb.clear((1,1,255))
	app.fb.sync(1)
	app.fb.flip()
	warn("warn", "sync on", wait=1)

	s.blit()
	app.fb.flip()
	warn("warn", "sprite up", wait=1)

	app.fb.flip()
	warn("warn", "flipped", wait=1)


def main(app):
	app.startfn = Run

def cleanup(app):
	pass

if not __name__ == '__main__':
	print "Loaded %s" % __name__
else:
	print "nothing to do (%s)." % __name__
