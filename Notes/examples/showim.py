#!/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys
from sprite import *

fb = quickinit(dpy=":0.0", w=200, h=200, bpp=32, flags=0)

s = Sprite(fname=sys.argv[1], fb=fb);
fb.clear((128,128,128))
s.blit(flip=1)
sys.stdout.write('Hit return to exit>')
sys.stdin.readline()
