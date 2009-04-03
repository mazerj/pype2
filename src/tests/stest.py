#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys

from pygame.constants import *
from Numeric import *
from sprite import *
from spritetools import *

N = 128
fb = quickinit(dpy=":0.0", w=2*N, h=2*N, bpp=32, fullscreen=0, opengl=1)

s = Sprite(width=N, height=N, x=0, y=0, depth=0, \
           fb=fb, on=1, image=None, dx=0, dy=0,
           fname=None, name="test")

fb.clear()
cosgrat(s, float(sys.argv[1]), 0, float(sys.argv[2]))
s.blit(flip=1)
sys.stdout.write('hit return to exit')
sys.stdin.readline()

fb.close()

