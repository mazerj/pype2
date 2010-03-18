# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**Loader for PLEXON generated sorted spike datafiles (*.plx)**

As a standalone module (pypenv pyplex), converts .plx files
into .plx.ts files that can be used directly by pypedata.py.

Authors

- Jack L. Gallant (gallant@berkeley.edu)

- James A. Mazer (james.mmazer@yale.edu)

Original Notes (jack & jamie)::

  Functions
  -------------------
  LoadPlexonFile(filename, save=None)
  LoadTimestampFile(filename, search=1)
  FindTimestampFile(pypefile, search=os.environ['PLXPATH'])
    - NOTE: pypefile should be the name of the PYPE datafile, not
      the plexon file or the timestamp file.  The '.plx.ts' extension
  	is automatically added.
    - PLXPATH should be colon-delimited search path (like PYTHONPATH)
      that indicates were to look for *.plx files (autmatically adds
  	current directory at the head!!)
  
  Classes
  -------------------
  Plexondata
    - Holds all the header and timestamp information contained in
      a plexon datafile.
    - Can be saved and loaded using the python builtin cPickle fns.

**Revision History**

Feb 17, 2002	JLG PYPLEX.PY		v. 3

- Python routines to read plexon data files
 
- All routines converted from plexon-supplied Matlab files plx_info.m, plx_ts.m

Sun Sep 22 17:58:00 2002 mazer ::

- Extensive revision (almost rewrote from scratch).

Fri Jan 15 09:53:24 2010 mazer

- migrated from Numeric to numpy

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

import sys
import struct
import cPickle

from pype import *

# GLOBALS
# Definitions for start and stop event channels on Mazer rig.
# This is not actually specific to the Mazer-rig, but for any
# Plexon file that's collected in external-trigger mode.

def readbytes(fd, count, datatype):
	"""
	Read count integers from binary .plx file.
	Read either Int16 (2 bytes) or Int32 (4 bytes):
	If count is 1, returns a single integer, otherwise, if count > 1
	returns a list of integers.
	"""
	if datatype == 'int16':
		fmt = '%dh' % count
	elif datatype == 'int32':
		fmt = '%di' % count
	siz = struct.calcsize(fmt)

	numstr = fd.read(siz)
	if len(numstr) == 0:
		raise EOFError

	buf = struct.unpack(fmt, numstr)
	if count == 1:
		buf = buf[0]

	return buf

class Header:
	"""
	The Header class stores the basic Plexon header information.
	You should never have to access this directly.
	"""
	def __init__(self, fp):
		buf = readbytes(fp, 64, 'int32')

		# get version information from header
		self.vers = buf[1]		# version file made with
		self.freq = buf[34]		# sampling frequencychanne
		self.ndsp = buf[35]		# number DSP channels
		self.nevents = buf[36]	# number external events
		self.nslow = buf[37]	# number slow channels
		self.npw = buf[38]		# number points in wave
		self.npr = buf[39]		# number points before thresh

		# read to appropriate place in file
		# constant part
		readbytes(fp, 5*130, 'int32') # tscounts header
		readbytes(fp, 5*130, 'int32') # wfcounts header
		readbytes(fp, 512, 'int32')   # evcounts header

		# variable part -- skip??  what's in here?
		fp.seek(((1020*self.ndsp) +
					  (296*self.nevents) + (296*self.nslow)), 1)

class PlexonRecord:
	def __init__(self, fp, waveforms=None):
		import numpy as _N
		
		self.typecode = readbytes(fp, 1, 'int16')
		self.upperbyte = readbytes(fp, 1, 'int16')
		self.timestamp = readbytes(fp, 1, 'int32')
		self.channel = readbytes(fp, 1, 'int16') # channel OR event code!!
		self.unit = readbytes(fp, 1, 'int16')
		self.nwf = readbytes(fp, 1, 'int16')

		# if a waveform is present, read it
		nwords = readbytes(fp, 1, 'int16')
		self.waveform = None
		if nwords > 0:					# read waveform, if any
			w = readbytes(fp, nwords, 'int16')
			if waveforms:
				self.waveform = _N.array(w)

class Plexondata:
	STARTCHANNEL = 258
	STOPCHANNEL = 259
	TIMESTAMP_CODE = 1
	EVENT_CODE = 4

	def __init__(self, filename):
		self.load_plx(filename)

	def __repr__(self):
		return """\
<Plexondata object
  source:  %s
  version: %d
  freq:    %d Hz
  ndsp:    %d
  nevents: %d
  nslow:   %d
  npw:     %d
  npr      %d
  ntrials  %d
  neurons  %s
>""" % (self.filename, self.header.vers, self.header.freq,
		self.header.ndsp, self.header.nevents, self.header.nslow,
		self.header.npw, self.header.npr,
		len(self.trialdata.keys()), self.neurons)

	def print_spikes(self, fp=sys.stdout):
		for n in range(1, max(self.trialdata.keys())):
			for chn in self.neurons:
				print '#%d, <%s>' % (n, chn)
				print self.trialdata[n][chn]

	def load_plx(self, filename):
		self.filename = filename
		fp = open(self.filename, 'r')
		self.header = Header(fp)
		self.trialdata = {}
		self.channellist = {}

		trialno = -1
		while 1:
			try:
				r = PlexonRecord(fp, waveforms=None)
			except EOFError:
				break

			if r.typecode == Plexondata.EVENT_CODE:
				if r.channel == Plexondata.STARTCHANNEL:
					t0 = r.timestamp
					trialno = trialno + 1
					self.trialdata[trialno] = {}
					sys.stderr.write('.')
					sys.stderr.flush()
			else:
				chn = 'sig%02d%c' % (r.channel, ord('a')+r.unit)
				# compute timestamp in integral ms
				ts = int(0.5 + 1000.0 *
						 float(r.timestamp - t0) / float(self.header.freq))
				try:
					self.trialdata[trialno][chn].append(ts)
				except KeyError:
					self.trialdata[trialno][chn] = [ts]
				self.channellist[chn] = 1
		self.neurons = self.channellist.keys()
		sys.stderr.write('\n')
		sys.stderr.flush()

	def save(self, filename):
		file = open(filename, 'w')
		cPickle.dump(self, file)
		file.close()

def LoadPlexonFile(filename, save=None):
	try:
		p = Plexondata(filename)
		if save:
			p.save(save)
		return p
	except IOError:
		return None

def LoadTimestampFile(filename, search=1):
	if search:
		filename = FindTimestampFile(filename)
		if filename is None:
			return None
	try:
		file = open(filename, 'r')
		p = cPickle.load(file)
		file.close()
		return p
	except IOError:
		return None

def FindTimestampFile(pypefile, search=None):
	import os, string, posixpath

	f = '%s.plx.ts' % pypefile
	if posixpath.exists(f):
		return f

	if search is None and os.environ.has_key('PLXPATH'):
		searchpath = os.environ['PLXPATH']
	else:
		searchpath = ''

	searchpath = '.:' + searchpath

	for d in string.split(searchpath, ':'):
		if len(d) > 0:
			f = '%s/%s.plx.ts' % (d, pypefile)
			if posixpath.exists(f):
				return f
	return None

if __name__ == '__main__':
	import os
	from stat import *

	if len(sys.argv) < 2:
		sys.stderr.write('usage: pyplex plexonfile timestampfile\n')
		sys.stderr.write('usage: pyplex timestampfile (to browse)\n')
		sys.exit(1)

	if len(sys.argv) == 2:
		infile = sys.argv[1]
		p = LoadTimestampFile(infile)
		if p is None:
			sys.stderr.write("Can't find/read %s\n" % infile)
		else:
			print p
			print "Loaded into variable 'p'"
			keyboard()
	else:
		infile = sys.argv[1]
		outfile = sys.argv[2]

		intime = os.stat(infile)[ST_MTIME]
		try:
			outtime = os.stat(outfile)[ST_MTIME]
		except OSError:
			outtime = None

		if outtime and outtime > intime:
			sys.stderr.write('%s newer than %s, no need to update.\n' % \
							 (infile, outfile))
		else:
			p = LoadPlexonFile(infile, save=outfile)
