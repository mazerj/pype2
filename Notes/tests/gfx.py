#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Testing code for sprite.py
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

s.fill((0,0,0));
# s.alpha[:]=128

# compute r (0-1.0)
r1 = (((s.ax/(s.w/2))**2) + ((s.ay/(s.h/2))**2))**0.5
r = transpose(array([r1, r1, r1]), axes=[1,2,0])
# compute theta (0-2pi)
theta1 = arctan2(s.ay, s.ax)
theta = transpose(array([theta1, theta1, theta1]), axes=[1,2,0])

if 0:
    for phi in arange(0, 2*pi, 0.1):
        s.array[:] = (127*sin(3*theta[:]-phi)+128).astype(UnsignedInt8)
        s.array[:] = where(less(r, 1.0), s.array, 1+0*s.array)
        s.blit()
        fb.flip()
else:
    F = 5
    for phi in arange(0, 8*2*pi, 0.1):
        fb.clear((128,128,128))
        
        s.alpha[:] = (255 - 255*r1).astype(UnsignedInt8)[:]
        s.alpha[:] = where(less(r1, 1.0), s.alpha[:], 0).astype(UnsignedInt8)
        s.array[:,:,0] = (127*sin(F*theta1[:]-phi)+128).astype(UnsignedInt8)
        s.array[:,:,1] = 0
        s.array[:,:,2] = (127*sin(-F*theta1[:]-phi)+128).astype(UnsignedInt8)
        s.moveto(-30, 0);
        s.blit()
        
        s.array[:,:,1] = (127*sin(-F*theta1[:]-phi)+128).astype(UnsignedInt8)
        s.array[:,:,2] = 0
        s.moveto(30, 0);
        s.blit()
        
        fb.flip()
    
sys.stdin.readline()

fb.close()
