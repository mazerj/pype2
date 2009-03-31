#!/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

#
# run this by typing:
#   sh% pypenv ./sprites.py
# or something similar..
#

from sprite import *
from movie2 import Movie

fb = quickinit(dpy=":0.0", w=200, h=200, bpp=32, flags=0)


m = Movie('./wnoise/', 'index', fb)
speed=1
for n in range(m.len(speed)):
    s = m.frame(n, nrepeats=speed)
    s.on()
    s.alpha_gradient(20, 30, x=0, y=0)
    fb.clear((128,128,128))
    s.blit()
    fb.flip()
    
sys.stdout.write('>>'); sys.stdin.readline()


