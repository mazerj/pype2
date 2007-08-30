#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width:4 py-indent-offset:4 -*-

import os, sys, tempfile, string

from pype import *

if len(sys.argv) < 4:
    sys.stderr.write('usage: pypenote infile outfile warning-message\n');
    sys.exit(1)

infile = sys.argv[1]
outfile = sys.argv[2]
warning = string.join(sys.argv[3:], ' ')

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

fin.close()
fout.close()

if infile == outfile:
    os.system('mv %s %s.original' % (infile, infile))
os.system('mv %s %s' % (tmp, outfile))
