#!/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

#
# run this by typing:
#   sh% pypenv ./playmov.py
# or something similar..
#

import sys

print len(sys.argv)

from sprite import *

fb = quickinit(dpy=":0.0", w=512, h=512, bpp=32, flags=0)
print 'init'


if len(sys.argv) > 1:
    m = MpegMovie(sys.argv[1], fb=fb)
else:
    m = MpegMovie('./yaryar.m1v', fb=fb)

i = 0
while 1:
    if m.showframe(i) is None:
        break
    i = i + 1
