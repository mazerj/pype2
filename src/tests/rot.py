#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
New Numeric/pygame grating codes

Thu Mar  4 17:15:40 2004 mazer:
 these are all now in src/pype/spritetools.py .. partially documented
"""

import sys

from Numeric import *
from sprite import *
from pygame.constants import *
from spritetools import *
from psycho import *

def show(s, wait=None):
    s.blit(flip=1)
    if wait:
        sys.stdout.write('<hit return to continue>')
        sys.stdout.flush()
        sys.stdin.readline()

N = 128
fb = PsychoFrameBuffer(None, 256, 256, 32, dga=None, gamma=1.0,
                       flags=DOUBLEBUF|HWSURFACE)
s = Sprite(width=N, height=N, x=0, y=0, depth=0, \
           fb=fb, on=1, image=None, dx=0, dy=0,
           fname=None, name="test")

s.noise(thresh=None)
show(s, wait=1)

keyboard()

fb.close()
