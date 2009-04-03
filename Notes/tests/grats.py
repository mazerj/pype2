#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys

from Numeric import *
from sprite import *
from pygame.constants import *
from spritetools import *

def show(s):
    s.blit(flip=1)

N = 128

fb = quickinit(dpy=":0.0", w=256, h=256, bpp=32, fullscreen=0, opengl=1)

s = Sprite(width=N, height=N, x=0, y=0, depth=0, \
           fb=fb, on=1, image=None, dx=0, dy=0,
           fname=None, name="test")

while 1:
    for phi in arange(0, 360, 20):
        fb.clear()
        singrat(s, 3, phi, 45.0)
        alphaGaussian2(s, 20, 30, 45)
        #hypergrat(s, 3, 0, phi)
        #polargrat(s, 1, 10*phi/360, 0, 1)
        show(s)

fb.close()
