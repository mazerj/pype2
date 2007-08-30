#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys
from pype import *
from events import *
from pypedata import *
from Numeric import *
from iplot import *


def extract(fname):
	clist = {}
	pf = PypeFile(fname)
	recno = 0
	while 1:
		d = pf.nth(recno)
		if d is None:
			break
		recno = recno + 1
		d.compute()

		if d.plex_ids is not None:
			for id in d.plex_ids:
				clist[id] = 1
		dance('.')
	dance(None)
	ids = clist.keys()
	ids.sort()
	for id in ids:
		print fname, id

if __name__ == '__main__':
	for f in sys.argv[1:]:
		extract(f)
