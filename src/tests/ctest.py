#!/bin/env pypenv
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
keyboard()

fb.close()
