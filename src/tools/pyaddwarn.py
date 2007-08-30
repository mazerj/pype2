#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width:4 py-indent-offset:4 -*-

"""
Sun Apr  4 16:37:56 2004 mazer 

Add a WARN tag to the front of an existing pype datafile. The
message incorporated into the tag will be printed to stderr
everything the file is loaded using the tools in pypedata.py.

Be careful -- this program has the capability to destroy existing
datafiles. It tries to back things up, but I suggest you perform
a manual backup first!

Usage:  pyaddwarn.py infile outfile <warningtext

If infile == outfile, then the modified datafile will be written
to a temp file and moved into place at the end, after moving
the original file to a backup locate ('infile.orig')

The warning message is supplied via stdin so it can be more
than one line, if necessary. Typical usage:
  echo "file is corrupt!" | pypaddwarn.py m0000.mtouch19.000 m0000.mtouch19.000
"""

import os, sys, tempfile, string

from pype import *

if len(sys.argv) < 2:
    sys.stderr.write('usage: pyaddwarn.py infile [outfile] < warningmsg\n')
	sys.stderr.write('       if outfile is not specified, then infile will\n')
	sys.stderr.write('       get overwritten.\n')
	sys.stderr.write('       THIS IS DANGEROUS -- USE WISELY!\n')
    sys.exit(1)

infile = sys.argv[1]
outfile = sys.argv[2]
warning = sys.stdin.read()

try:
    fin = open(infile, 'r');
except IOError:
    sys.stderr.write('can''t open %s for read\n' % infile);
    sys.exit(1)

try:
    tmp = tempfile.mktemp()
    fout = open(tmp, 'w');
except IOError:
    sys.stderr.write('can''t open temporary output file\n');
    sys.exit(1)

labeled_dump(WARN, warning, fout, bin=1)

while 1:
    label, obj = labeled_load(fin)
    if label is None:
        break
    labeled_dump(label, obj, fout, bin=1)
    dance('.')
dance(None)

fin.close()
fout.close()

if infile == outfile:
    os.system('mv %s %s.orig' % (infile, infile))
    sys.stderr.write('backed up original to %s.orig\n' % infile)
os.system('mv %s %s' % (tmp, outfile))
