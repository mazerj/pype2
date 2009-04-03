#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-


import sys

from Numeric import *
from sprite import *
from pygame.constants import *
from spritetools import *

N = 128

fb = quickinit(dpy=":0.0", w=256, h=256, bpp=32, fullscreen=0, opengl=1)

s1 = Sprite(width=N, height=N, x=0, y=0, depth=0, \
            fb=fb, on=1, image=None, dx=0, dy=0,
            fname=None, name="s1")

s2 = Sprite(width=N, height=N, x=0, y=0, depth=0, \
            fb=fb, on=1, image=None, dx=0, dy=0,
            fname=None, name="s2")

s1.alpha[:]=128
s2.alpha[:]=128

s1.rmove(dy=N/4)
s2.rmove(dy=-N/4)

for phi in arange(0, 10*360, 10):
    fb.clear()
    singrat(s1, 2, phi, 0, 1, 0, 0)
    singrat(s2, 2, 360-phi, 0, 0, 1, 0)
    s1.blit()
    s2.blit()
    fb.flip()

sys.stdin.readline()

fb.close()
