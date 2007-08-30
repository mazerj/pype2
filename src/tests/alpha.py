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
from psycho import *

fb = PsychoFrameBuffer(None, 256, 256, 32, dga=None, gamma=1.0,
                       flags=DOUBLEBUF|HWSURFACE)

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
