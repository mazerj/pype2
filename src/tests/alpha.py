#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-


import sys

from Numeric import *
from sprite import *
from pygame.constants import *
from spritetools import *

fb = quickinit(dpy=":0.0", w=256, h=256, bpp=32, fullscreen=0, opengl=1)

N = 128
s = Sprite(width=N, height=N, x=0, y=0, depth=0, \
           fb=fb, on=1, image=None, dx=0, dy=0,
           fname=None)
fb.clear((128,128,128))
singrat(s, 4, 0, 0)
#s.alpha_aperture(64)
s.alpha_gradient(40,64)
s.blit(flip=1)
keyboard()

fb.close()
