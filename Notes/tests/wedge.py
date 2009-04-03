#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Wedge generator for kate
"""

import sys

from Numeric import *
from sprite import *
from pygame.constants import *
from spritetools import *

N = 128

fb = quickinit(dpy=":0.0", w=256, h=256, bpp=32, fullscreen=0, opengl=1)

s = Sprite(width=N, height=N, x=0, y=0, depth=0, \
           fb=fb, on=1, image=None, dx=0, dy=0,
           fname=None, name="test")
s.noise(0.5)

# compute r (0-1.0)
r1 = (((s.ax/(s.w/2))**2) + ((s.ay/(s.h/2))**2))**0.5
r = transpose(array([r1, r1, r1]), axes=[1,2,0])
# compute theta (-180:180)
theta1 = -180*arctan2(s.ay, s.ax)/pi
theta = transpose(array([theta1, theta1, theta1]), axes=[1,2,0])

for phi in arange(-180-45, 180+45+45, 10):
    s.array[:] = 255
    for c in range(0,3):
        s.array[:,:,c] = where(greater(r1,0.25) & less(r1,0.75) &
                               greater(theta1, phi-45) & less(theta1, phi+45),
                               s.array[:,:,c], 0*s.array[:,:,c])
    if 0:
        s.array[:] = where(greater(r,0.25) & less(r,0.75) &
                           greater(theta, phi-45) & less(theta, phi+45),
                           s.array[:], 0*s.array[:])

    s.blit()
    fb.flip()
    
    
sys.stdin.readline()

fb.close()
