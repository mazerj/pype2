#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys

from Numeric import *
from sprite import *
from pygame.constants import *
from spritetools import *

fb = quickinit(":0.0", 256, 256, 32, flags=DOUBLEBUF|HWSURFACE)

s = Sprite(100,100, fb=fb)
s.fill((0,0,70))
s.line(0,0,50,50, (255,128,128))
s.blit(flip=1)
s.save_ppm('foo.ppm');
s.save_alpha_pgm('foo.pgm');

fb.close()
