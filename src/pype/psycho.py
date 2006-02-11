# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""Psychophysics toolbox

Useful functions for running psychophysics using pypenv. This
module is experimental and I haven't really tested any of
the functions extensively.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**
"""

import sys
from Numeric import *
from types import *

from pype import *
from pypeerrors import *
from dacq import *
from pypeversion import *
from pypedebug import *
from pype_aux import *
from beep import *
from sprite import *
from config import *
from dacq import *
from pygame.constants import *

##################################################################

class PsychoFrameBuffer(FrameBuffer):
	def __init__(self, display, width, height, depth,
				 dga=1, gamma=None, flags=FULLSCREEN|DOUBLEBUF|HWSURFACE):
		FrameBuffer.__init__(self, display, width, height, depth, flags,
							 dga=dga, sync=0)
		if gamma:
			if self.set_gamma(gamma):
				print "pype: gamma set to %f" % gamma
			else:
				print "pype: hardware does not supported gamma correction"
		# start dacq in testmode to get timers
		dacq_start(1, 1, "", "", "", "")
		
	def close(self):
		dacq_stop()

if __name__ == '__main__':
	from spritetools import *
	
	#fb = PsychoFrameBuffer(":0.0", 1024, 768, 24, 1)
	fb = PsychoFrameBuffer(":0.0", 256, 256, 24, 0)
	fps = fb.calcfps()
	print fps, "fps"


	if 0:
		slist = []
		for i in range(0, 180):
			slist.append(Sprite(100, 100, 0, 0, 0, fb=fb, on=1))
			Make_2D_Sine(5.0, 10*float(i), 0.0, 1.0, 1.0, 1.0, slist[-1].im)
			gaussianEnvelope(slist[-1], 20.0)
			sys.stdout.write(".")
			sys.stdout.flush()
		sys.stdout.write("\n")
		
		t = Timer()
		nframes = 0
		for s in slist:
			# must clear first, else the alpha values in the mask
			# lead to accumulation errors..
			fb.clear((128,128,128))
			s.blit()
			fb.flip()
			nframes = nframes + 1
		print nframes / (t.ms() / 1000.0), "fps"

	if 1:
		s = Sprite(100, 100, 0, 0, 0, fb=fb, on=1)
		t = Timer()
		nframes = 0
		for i in range(0, 180):
			Make_2D_Sine(5.0, 10*float(i), 0.0, 1.0, 1.0, 1.0, s.im)
			gaussianEnvelope(s, 20.0)
			
			# must clear first, else the alpha values in the mask
			# lead to accumulation errors..
			fb.clear((128,128,128))
			s.blit()
			fb.flip()
			nframes = nframes + 1
		print nframes / (t.ms() / 1000.0), "fps"



	# note: this gets key from the keyboard on the graphics display, not
	#       necessarily the keyboard you're typing at..
	fb.clear((1,1,1))
	fb.string(0,0,"done",(255,255,255));
	fb.flip()
	fb.getkey(wait=1)
		
	fb.close()
