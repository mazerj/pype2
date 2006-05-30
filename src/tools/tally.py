#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Generate a summary tally of trial result codes in the specified
datafile.
"""

import sys

from pype import *
from pypedata import *

def dump(fname):
	pf = PypeFile(fname)

	N = {}
	ncorr = 0
	nerr = 0
	n = 0
	while 1:
		d = pf.nth(n)
		if d is None: break
		dance()
		
		try:
			N[d.result] = N[d.result] + 1
		except KeyError:
			N[d.result] = 1
		n = n + 1

		if d.result[0] == 'C':
			ncorr = ncorr + 1
		elif not d.result[0] in 'AU':
			nerr = nerr + 1
			
	dance(None)

	for k in N.keys():
		print "%d\t%.1f%%\t%s" % (N[k], 100.0*N[k]/n, k)

	print "n=%d" % (n,)
	print "%%corr=%.1f%%" % (100.0 * ncorr / (ncorr + nerr),)
		
dump(sys.argv[1])
