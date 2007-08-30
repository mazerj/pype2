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

fb = quickinit(":0.0", 512, 512, 32, flags=DOUBLEBUF|HWSURFACE)
keyboard()

fb.close()
