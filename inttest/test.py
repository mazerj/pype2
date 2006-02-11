#!/usr/bin/env python2
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys, os
from signal import *

class TestError(Exception): pass

def handler(signal, frame):
    sys.stderr.write('<handler>')
    return
    raise TestError, "inside handler function"

def testloop():
    try:
        print "sitting in loop..."
        while 1:
            pass
    except TestError:
        print "caught the right exception"
        print sys.exc_info()
    except:
        print "caught some other exception"

signal(SIGUSR2, handler)

print "try: kill -USR2 %d" % os.getpid()
testloop()


