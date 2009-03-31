#!/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys
from sprite import *

fb = quickinit(dpy=":0.0", w=512, h=512, bpp=32, flags=0)

s = Sprite(width=100, height=100, fb=fb)
#singrat(s, 2.0, 0.0, 180.0, R=1.0, G=1.0, B=1.0)
#polargrat(s, 0.0, 2.0, 0.0, 1, R=1.0, G=1.0, B=1.0)
hypergrat(s, 2.0, 0.0, 0.0, R=1.0, G=1.0, B=1.0)
fb.clear((128,128,128))
s.blit(flip=1)
sys.stdout.write('Hit return to exit>')
sys.stdin.readline()
