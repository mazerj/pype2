#!/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

#
# run this by typing:
#   sh% pypenv ./grating.py
# or something similar..
#

from Numeric import *
from sprite import *

fb = quickinit(dpy=":0.0", w=200, h=200, bpp=32, flags=0)

frequency = 5
phase_deg = 0
ori_deg = 0

s = Sprite(100, 100, fb=fb)
s.alpha_gradient(1, 20)


cosgrat(s, frequency, phase_deg, ori_deg)

fb.clear((128,128,128))
s.blit()
fb.line((0, 100), (0, -100), (255,1,1))
fb.flip()

keyboard()
