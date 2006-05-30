#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Count number of records in a pypefile as fast as possible.
"""

import sys

from pype import *
from pypedata import *

def count(fname):
	pf = PypeFile(fname)
	n = 0
	while 1:
		d = pf.nth(n)
		if d is None:
			break
		n = n + 1
	pf.close()
	print "n=%d: %s" % (n, f)

for f in sys.argv[3:]:
	count(f)
