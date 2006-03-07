#!/bin/env pypenv
# -*- Mode: Python; tab-width:4 py-indent-offset:4 -*-

"""
Tue Mar  7 13:16:19 2006 mazer

 - Example pypefile filter function. This code reads a pype datafile
   on stdin, potentially filters the data stream and then writes the
   filtered result to stdout.

 - You could use this to correct errors or bugs in a datafile etc

 - WARNING: USE WITH CAUTION AND BACKUP BEFORE APPLYING ANY FILTERS.
            YOU *COULD* EASILY DESTROY YOUR DATA!!!
			
"""

import sys
from pype import *

while 1:
	label, obj = labeled_load(sys.stdin)
	if label is None:
		break
	if label == 'encode':
		(result, rt, P, taskinfo) = obj[1]
		#...
		# change P[] or anything else in obj[1] here
		#...
		obj[1] = (result, rt, P, taskinfo)

		encodes = obj[2]
		new = []
		for (t, ev) in encodes:
			#...
			# filter encodes here -- modify t and ev as required
			#...
			new.append((t, ev))
		obj[2] = new
	labeled_dump(label, obj, sys.stdout, bin=1)
