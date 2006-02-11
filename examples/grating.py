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

frequency = 3
phase_deg = 0
ori_deg = 45

s = Sprite(100, 100, fb=fb)
s.alpha_gradient(1, 50)



while 1:
    fb.clear((128,128,128))
    
    r = (((s.xx / s.w)**2) + ((s.yy / s.h)**2))**0.5
    t = arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0
    x, y = (r * cos(t), r * sin(t))
    i = 127.0 * sin((2.0 * pi * frequency * x) - (pi * phase_deg / 180.0))
    s.array[:] = transpose((array((i,i,i))+128).astype(UnsignedInt8),
                           axes=[1,2,0])
    s.blit()
    fb.flip()
    
    phase_deg = (phase_deg + 10) % 360
    ori_deg = (ori_deg + 2) % 360

