#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-


import sys

from Numeric import *
from sprite import *
from pygame.constants import *
from spritetools import *

def g2rgb(a):
    return transpose(array([a, a, a]), axes=[1,2,0])

def pixelize(a, rgb=None, norm=1):
    if norm:
        amin = min(ravel(a))
        amax = max(ravel(a))
        a = (255.0 * ((a - amin) / (amax - amin))).astype(UnsignedInt8)
    else:
        a = a.astype(UnsignedInt8)
    if rgb is None:
        return a
    else:
        return g2rgb(a)

def show(s):
    s.blit(flip=1);
    sys.stdin.readline()


N = 128

fb = quickinit(dpy=":0.0", w=256, h=256, bpp=32, fullscreen=0, opengl=1)

s = Sprite(width=N, height=N, x=0, y=0, depth=0, \
           fb=fb, on=1, image=None, dx=0, dy=0,
           fname=None, name="test")

# compute r (0-1.0)
r1 = (((s.ax/(s.w/2))**2) + ((s.ay/(s.h/2))**2))**0.5
r = g2rgb(r1)
# compute theta (-180:180)
theta1 = 180*arctan2(s.yy, s.xx)/pi
theta = g2rgb(theta1)

xs = s.xx*ones(shape(s.yy))
ys = s.yy*ones(shape(s.xx))

fb.clear((128,128,128))
s.array[:] = pixelize(xs, rgb=1)
show(s)

s.array[:] = pixelize(ys, rgb=1)
show(s)

s.array[:] = pixelize(theta1, rgb=1)
show(s)

s.array[:] = pixelize(r1, rgb=1)
show(s)


fb.close()
