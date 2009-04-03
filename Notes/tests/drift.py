#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys

from pygame.constants import *
from Numeric import *
from sprite import *
from spritetools import *

N = 128

fb = quickinit(dpy=":0.0", w=256, h=256, bpp=32, fullscreen=0, opengl=1)

s = Sprite(width=N, height=N, x=0, y=0, depth=0, \
           fb=fb, on=1, image=None, dx=0, dy=0,
           fname=None, name="test")

while 1:
    for phi in arange(0, 360, 20):
        fb.clear()
        singrat(s, 4, phi, 0)
        alphaGaussian2(s, 10, 20, 45)
        s.blit(flip=1)

fb.close()
