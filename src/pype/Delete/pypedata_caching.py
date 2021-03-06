# -*- Mode: Python; tab-width:4 py-indent-offset:4 -*-
# $Id$

"""Classes for reading pype data files.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Tue Jan 25 15:23:19 2000 mazer

- Originally *pview.py*. This is a multithreaded browser for pype datafiles
It includes a few useful and interesting tricks.

 1. Object class for encapsulating trial records

 2. Object class for encapsulating entire pype data files.

 3. A simple eye trace viewer

 4. It's multithreaded -- it loads the records using a background
   thread, so while you're browsing, it continues to load the data for
   when you get there.

 5. The load is threaded, but the numerical crunching is not. This is
   to make it easier to skip towards the end of the file. Once the
   file's all loaded, it goes back and starts to crunch from the
   beginning

- Things to do:

 1. Set up easy way to subclass the viewer for code-reuse

 2. standardize on how to convert pix->dva

Mon Feb  7 21:15:12 2000 mazer

- split off from pview.py

- loadable classes for handling pype data files

Tue Feb 15 15:05:09 2000 mazer 

- Added PypeFile.extradata[] to hold everything not parsed by standard
  processing scheme

Fri Sep 15 13:00:47 2000 mazer

- Made extradata into a class for easier decoding..

Tue Apr  3 12:31:51 2001 mazer

- Removed pix_to_dva option for PypeRecord.compute() method
  I decided this must be done explicitly -- policy decision to
  keep everything in units of pixels unless explicted converted
  using the pix2deg() function.

Fri Apr 13 11:52:19 2001 mazer

- Added support for shifting eye traces on load (for iscan lag).
  From my notes ::
  
 > Just got off phone with Rikki.  There's definitely an unaccounted
 > for latency problem in our iscan, could be as much as 24ms at 120hz
 > (ie, 3 frames).
 > 
 > Here's the deal: T
 > 
 > The camera in our system does not do progressive scan.  Instead of
 > clocking out each scanline as it's aquired, like a normal tube
 > video camera, it acquires an entire video frame (8ms) and holds it.
 > That frame is then clocked out over the next 8ms while the next
 > frame is being acquired by the CCD.  Second, the frame grabber
 > hardware on the iscan board (inside pc) takes another 8ms to
 > acquire each video frame.  Computation time is negliable.  These
 > 8ms values are actually frame periods (ie, at 240hz, assume 4ms etc)
 > 
 > According to Tim Gawne there's one more frame in there (he got a 12ms
 > lag at 240hz; Rikki is checking into this for me now).
 > 
 > This means that the eye trace is actually telling us where the eye
 > was 16-24ms BEFORE the actual time..  So the eye trace should be
 > shifted forward (to the left) in time by at least 16ms.

Thu Feb 27 17:27:36 2003 mazer

- Added 'realt' --> this is the original time signal, 'eyet' is the
  lag-corrected time signal.  This allows you to use 'realt' to look
  at the photo diode and spike traces correctly..

Sun Dec  4 19:17:27 2005 mazer

- Added support for ~/.pyperc/spikepattern to select a spike channel
  on load -- programs must call spikes() method to get correct spike
  timestmap list instead of looking at spike_times from now on.

Thu Dec 22 12:54:57 2005 mazer

- format for ~/.pyperc/spikepattern is a regular expression of the
  form: [0-9][0-9][0-9][a-z] (number refers to electrode/amplifier
  channel number, starting at ONE, lowercase letters indicate neuron
  on that electrode, starting with 'a'. To look at all neurons on
  channel 4 you can use '004.' etc..
  
"""

import sys, types, string, thread, os
import math, Numeric, time
from vectorops import *
from pype import *
import re

from pypedebug import keyboard

class PypedataTimeError(Exception):
	"""Serious bad voodoo in the datafile!

	This error gets raised when time seems to run
	backwards.  This represents a SERIOUS problem
	with the datafile...
	"""
	pass

class Note:
	def __init__(self, rec):
		self.id = rec[1]
		self.data = rec[2:]

class PypeRecord:
	_reportcorrection = 1
	_reportchannel = 1
	def __init__(self, rec, taskname=None,
				 trialtime=None, parsed_trialtime=None,
				 userparams=None, threaded=None,
				 tracker_guess=('iscan', 120, 24)):
		#
		# Wed Sep 11 14:36:42 2002 mazer
		#
		# this just cache's the record until it's really needed..
		#
		#  rec[0]		record type STRING: ('ENCODE' usually)
		#  rec[1]		info TUPLE: (trialresult, rt, paramdict, taskinfo)
		#						taskinfo can be ANYTHING user wants to
		#						save in the datafile
		#  rec[2]		event LIST: [(time, event), (time, event) ...]
		#  rec[3]		time VECTOR (numeric array)
		#  rec[4]		eye x-pos VECTOR (numeric array)
		#  rec[5]		eye y-pos VECTOR (numeric array)
		#  rec[6]		LIST of photodiode time stamps
		#  rec[7]		LIST of spike time stamps
		#  rec[8]		record_id (SCALAR; auto incremented after each write)
		#  rec[9]		raw photodiode response VECTOR
		#  rec[10]		raw spike response VECTOR
		#  rec[11]		TUPLE of raw analog channel data
		#				(chns: 0,1,2,3,4,5,6), but 2 & 3 are same as
		#				rec[9] and rec[10], so they're just None's in
		#				this vector to save space. c5 and c6 aren't
		#				currently implemented
		#  rec[12]		pupil area data (if available) in same format
		#			    as the eye [xy]-position data above. This is new
		#				as of 08-feb-2003 (JAM)
		# 
		#  ** added rec[13] 31-oct-2005 (JAM) **
		#  rec[13]		on-line plexon data via PlexNet. This should be
		#				a list of (timestamp, unit) pairs, with timestamps
		#				in ms and unit's following the standard plexon
		#				naming scheme (01a, 02a, 02b etc..)
		
		self.rec = rec
		self.taskname = taskname
		self.trialtime = trialtime
		self.parsed_trialtime = parsed_trialtime
		self.userparams = userparams
		self.computed = None
		if threaded:
			self._lock = thread.allocate_lock()
		else:
			self._lock = None

		# these things are fast, the rest of the recording will
		# be filled in by the compute() method..
		# task specific data
		self.info = self.rec[1]

		# these should be standard..
		self.result = self.info[0]
		self.rt = self.info[1]
		self.params = self.info[2]
		if not 'eyetracker' in self.params.keys():
			self.params['eyetracker'] = tracker_guess[0]
			self.params['eyefreq'] = tracker_guess[1]
			self.params['eyelag'] = tracker_guess[2]

		# the rest of self.info is totally task dependent, see the
		# compute() method below
		self.rest = self.info[3:]

	def __repr__(self):
		return "<PypeRecord: r='%s'>" % self.result

	def printevents(self, fp=sys.stdout):
		lastt = None
		for (t, e) in self.events:
			if not lastt is None:
				dt = t - lastt
			else:
				dt = 0
			fp.write("   %6dms\t(%6dms)\t%s\n" % (t, dt, e))
			lastt = t

	def pp(self, file=sys.stdout):
		self.debugprint(file=file)
		
	def debugprint(self, params=1, events=1, rest=1, spikes=1, syncs=1,
				   file=sys.stderr):
		from pypedebug import ppDict
		
		file.write("================================\n")
		file.write("taskname='%s'\n  %s\n" % (self.taskname,
											  type(self.taskname)))
		file.write("trialtime='%s'\n  %s\n" % (self.trialtime,
											   type(self.trialtime)))
		file.write("result='%s'\n  %s\n" % (self.result, type(self.result)))
		file.write("rt='%s'\n  %s\n" % (self.rt, type(self.rt)))

		if params:
			file.write("--------------------------------\n")
			klist = self.userparams.keys()
			klist.sort()
			for k in klist:
				file.write("userparams['%s']=<%s>\n  %s\n" % \
						   (k, self.userparams[k], type(self.userparams[k])))
			file.write("--------------------------------\n")
			klist = self.params.keys()
			klist.sort()
			for k in klist:
				file.write("params['%s']=<%s>\n  %s\n" %\
					  (k, self.params[k], type(self.params[k])))
		if rest:
			file.write("--------------------------------\n")
			file.write("rest=<%s>\n" % (self.rest,))
		if events:
			file.write("--------------------------------\n")
			file.write("events:\n")
			try:
				e = self.events
			except AttributeError:
				e = None
				file.write('  No events.\n');
			if e:
				self.printevents()
		if spikes:
			file.write("--------------------------------\n")
			file.write("spike_times:\n")
			try:
				st = self.spike_times
			except AttributeError:
				st = None
			if st:
				for t in st:
					file.write("   %8dms\n" % t)
			else:
				file.write("  No spikes.\n")
				
		if syncs:
			file.write("--------------------------------\n")
			file.write("photo_times:\n")
			try:
				pt = self.photo_times
			except AttributeError:
				pt = None
			if pt:
				for t in pt:
					file.write("   %8dms\n" % t)
			else:
				file.write("  No photo events.\n")
				
		file.write("================================\n")


	def compute(self, velocity=None, gaps=None, raw=None, nooffset=None):
		"""
		Note: All eye info is maintained here in PIXELS.
		      Use pix2deg() and deg2pix() below to convert.
		"""
		if self._lock: self._lock.acquire()

		if not self.computed:
			# this is new 13-apr-2001:
			try:
				lag = float(self.params['eyelag'])
			except NameError:
				lag = 0
			# all pype files (may be [] if not collected)
			self.events = self.rec[2]
			self.eyet = Numeric.array(self.rec[3], 'f') # ms
			dt = diff(self.eyet)
			if sum(Numeric.where(Numeric.less(dt, 0), 1, 0)) > 0:
				raise PypedataTimeError
			self.realt = Numeric.array(self.rec[3], 'f') # ms
			self.eyex = Numeric.array(self.rec[4], 'f') # dva
			self.eyey = Numeric.array(self.rec[5], 'f')	# dva
			if lag > 0:
				# correct for eye tracker delay, if any..
				self.eyet = self.eyet - lag
				if PypeRecord._reportcorrection:
					# report this correction only ONCE!!
					sys.stderr.write('NOTE: fixed eye lag (only warning!)\n')
					PypeRecord._reportcorrection = None
			self.params['lagcorrected'] = 1
			self.eyevalid = None
			self.photo_times = Numeric.array(self.rec[6], 'i')
			self.spike_times = Numeric.array(self.rec[7], 'i')

			if len(self.rec) > 13 and self.rec[13] is not None:
				plist = self.rec[13]
				times, channels, units, ids = [], [], [], []
				for (t, c, u) in plist:
					times.append(t)
					channels.append(c)
					units.append(u)
					ids.append("%03d%c" % (c, chr(ord('a')+u-1)))
				self.plex_times = Numeric.array(times, 'i')
				self.plex_channels = Numeric.array(channels, 'i')
				self.plex_units = Numeric.array(units, 'i')
				self.plex_ids = ids[:]
			else:
				self.plex_times = None
				
			t = find_events(self.events, START)
			if len(t) == 0:
				sys.stderr.write('warning: no START event, guessing..\n')
				# just use the first event as a reference point...
				self.t0 = self.events[0][0]
			else:
				self.t0 = t[0]
			self.eyet = self.eyet - self.t0
			self.realt = self.realt - self.t0
			self.photo_times = self.photo_times - self.t0
			self.spike_times = self.spike_times - self.t0

			# Sun Dec  4 10:08:01 2005 mazer -- NOTE:
			# not necessary to align -- it's already been
			# done by the PlexNet.py module (START code is
			# same time as the TTL trigger/gate linegoing high and
			# all timestamps are stored in the data file relative to
			# that trigger event)
			#
			# self.plex_times = self.plex_times - self.t0
				

			self.events = align_events(self.events, self.t0)

			if gaps:
				gaps = Numeric.nonzero(Numeric.where(Numeric.greater(dt, 1),
													 1,0))
				self.gaps_t = Numeric.take(self.eyet, gaps)
				self.gaps_y = self.gaps_t * 0
				self.gapdurs = Numeric.take(self.eyet, gaps+1) - self.gaps_t
			else:
				self.gaps_t = None
				self.gaps_y = None

			if raw and self.params.has_key('@eye_rot'):
				if self.params['@eye_rot'] != 0:
					self.israw = None
				else:
					if nooffset:
						self.eyex = self.eyex / self.params['@eye_xgain']
						self.eyey = self.eyey / self.params['@eye_ygain']
						self.israw = 1
					else:
						self.eyex = (self.eyex + self.params['@eye_xoff']) / \
									self.params['@eye_xgain']
						self.eyey = (self.eyey + self.params['@eye_yoff']) / \
									self.params['@eye_ygain']
						self.israw = 1
			else:
				self.israw = None

			if velocity:
				dt = dt / 1000.
				dx = diff(self.eyex) / dt
				dy = diff(self.eyey) / dt
				dxy = ((dx**2) + (dy**2))**0.5

				self.eyedxdt = dx
				self.eyedydt = dy
				self.eyedxydt = dxy
			else:
				self.eyedxdt = None
				self.eyedydt = None
				self.eyedxydt = None

			self.computed = 1

		if self._lock: self._lock.release()
		return self

	def spikes(self, pattern=None):
		# select spikes from specified channel; channel is specified
		# in ~/.pyperc/spikechannel (users should use the 'pypespike'
		# sh script to select a channel)
		#   None --> TTL input (old style)
		#   regexp --> PlexNet datastream (001a, 001b, 002b etc..)
		if pattern is None:
			try:
				pattern = string.strip(open(pyperc('spikepattern'),
											'r').readline())
			except IOError:
				pattern = None
				
		if pattern is None or self.plex_times is None:
			ts = self.spike_times[:]
			pattern = 'TTL'
		else:
			p = re.compile(pattern)
			ts = []
			for n in range(len(self.plex_times)):
				if p.match(self.plex_ids[n]) is not None:
					ts.append(self.plex_times[n])

		if PypeRecord._reportchannel:
			sys.stderr.write('spikepattern=%s\n' % pattern)
			PypeRecord._reportchannel = None
					
		return pattern, ts

class PypeFile:
	def __init__(self, fname, filter=None, status=None, threaded=None):
		flist = string.split(fname, '+')
		if len(flist) > 1:
			import posix
			if flist[0][-3:] == '.gz':
				cmd = 'gunzip -c %s ' % string.join(flist,' ')
			else:
				cmd = 'cat %s ' % string.join(flist,' ')
			self.fp = posix.popen(cmd, 'r')
			sys.stderr.write('compositing: %s\n' % fname)
			self.fname = fname
		elif fname[-3:] == '.gz':
			# it appears MUCH faster to open a pipe to gunzip
			# than to use the zlib/gzip module..
			import posix
			self.fp = posix.popen('gunzip <%s' % fname, 'r')
			sys.stderr.write('decompressing: %s\n' % fname)
			self.fname = fname[:-3]
			self.zfname = fname[:]
		elif not posixpath.exists(fname) and \
			 posixpath.exists(fname+'.gz'):
			import posix
			# if .gz file exists and the named file does not,
			# try using the .gz file instead...
			self.fname = fname
			self.zfname = fname+'.gz'
			self.fp = posix.popen('gunzip <%s' % self.zfname, 'r')
			sys.stderr.write('decompressing: %s\n' % self.zfname)
		else:
			self.fname = fname
			self.zfname = None
			self.fp = open(self.fname, 'r')
		self.cache = []
		self.status = status
		self.filter = filter
		self.userparams = None
		self.threaded = threaded
		self.taskname = None
		self.extradata = []
		if self.threaded:
			self._lock = thread.allocate_lock()
			self.backload()
		else:
			self._lock = None

	def backload(self):
		self.loading = 1
		thread.start_new_thread(self._backload2, (None,))

	def _backload2(self, arglist):
		if self.status:
			self.status.configure(text='background load going')
		else:
			sys.stderr.write('(background load started)\n')
		self._lock.acquire()
		self.loading = 1
		self._lock.release()
		while self._next():
			pass
		self._lock.acquire()
		self.loading = 0
		self._lock.release()
		if self.status:
			self.status.configure(text='(loaded %d recs [0-%d])' % \
								  (len(self.cache)-1, len(self.cache)-1))
		else:
			sys.stderr.write('(loaded %d recs [0-%d])\n' % (len(self.cache)-1,
															len(self.cache)-1))
		n=0
		for p in self.cache:
			p.compute()
			if self.status:
				self.status.configure(text='crunching #%d' % n)
			n = n + 1

		if self.status:
			self.status.configure(text='%d (all) available' % n)
		else:
			sys.stderr.write('(all computed)\n')

	def __repr__(self):
		return '<PypeFile:%s (%d recs)>' % (self.fname, len(self.cache))

	def close(self):
		if not self.fp is None:
			try:
				self.fp.close()
			except IOError:
				# not sure why this happens, something sort of pipe
				# and thread interaction?
				pass
			self.fp = None

	def _next(self, cache=1, runinfo=None):
		if self.fp is None:
			return None

		trialtime = None
		while 1:
			try:
				label, rec = labeled_load(self.fp)
			except EOFError:
				label, rec = None, None
			except ImportError:
				# this is a fatal error!!!
				exc_type, exc_value, exc_traceback = sys.exc_info()
				sys.stderr.write('***************************************\n')
				sys.stderr.write('Missing module required for unpickling:\n')
				sys.stderr.write('  %s\n' % exc_value)
				sys.stderr.write('***************************************\n')
				sys.stderr.write('You must find the original module that is\n')
				sys.stderr.write('and add it to your PYTHONPATH in order to\n')
				sys.stderr.write('access this datafile.\n')
				sys.stderr.write('***************************************\n')
				sys.stderr.write('This almost certainly means that the \n')
				sys.stderr.write('missing module imported Numeric.  If you\n')
				sys.stderr.write('can not find the original module, make\n')
				sys.stderr.write('a dummy file of the same name containing:\n')
				sys.stderr.write('\n')
				sys.stderr.write('from Numeric import * \n')
				sys.stderr.write('\n')
				sys.stderr.write('***************************************\n')
				sys.stderr.write('Currently:\n')
				sys.stderr.write(' PYTHONPATH=%s\n' % os.environ['PYTHONPATH'])
				sys.stderr.write('***************************************\n')

				sys.stderr.write(get_traceback())
								 
				sys.exit(1)

			if label == None:
				self.close()
				return None
			if label == WARN:
				sys.stderr.write('WARNING: %s\n' % rec)
			if label == ANNOTATION:
				# for the moment, do nothing about this..
				pass
			elif rec[0] == ENCODE:
				try:
					xxx=trialtime2
				except UnboundLocalError:
					trialtime2 = 'nd'
				try:
					xxx=tracker_guess
				except UnboundLocalError:
					tracker_guess = 'nd'
				p = PypeRecord(rec, trialtime=trialtime,
							   parsed_trialtime=trialtime2,
							   tracker_guess=tracker_guess,
							   userparams=self.userparams,
							   taskname=self.taskname,
							   threaded=self.threaded)
				trialtime = None
				if not self.filter or (p.result == self.filter):
					if cache:
						if self._lock: self._lock.acquire()
						self.cache.append(p)
						if self._lock: self._lock.release()
				return p
			elif rec[0] == 'NOTE' and rec[1] == 'task_is':
				self.taskname = rec[2]
			elif rec[0] == 'NOTE' and \
				 rec[1] == 'pype' and rec[2] == 'run starts':
				if runinfo:
					return 1
			elif rec[0] == 'NOTE' and \
				 rec[1] == 'pype' and rec[2] == 'run ends':
				pass
			elif rec[0] == 'NOTE' and rec[1] == 'trialtime':
				(n, trialtime) = rec[2]
				# for some reason unclear to me, trialtime is an 'instance'
				# and not a string.. the % hack makes it into a string..
				trialtime = "%s" % trialtime
				# year, month, day, hour, min, sec, 1-7, 1-365, daylight sav?
				trialtime2 = time.strptime(trialtime, '%d-%b-%Y %H:%M:%S')
				# try to detect if this is an iscan file? Anything after
				# 01-jun-2000.  After 13-apr-2001, there should be an
				# eye tracker parameter stored in the datafile..
				# only do this on first record.
				year = trialtime2[0]
				month = trialtime2[1]
				if (year > 2000) or (year == 2000 and month >= 6):
					tracker_guess = ('iscan', 120, 24)
				else:
					tracker_guess = ('coil', 1000, 0)
			elif rec[0] == 'NOTE' and rec[1] == 'userparams':
				self.userparams = rec[2]
			else:
				#sys.stderr.write('stashed: <type=%s>\n' % label)
				self.extradata.append(Note(rec))

	def nth(self, n):
		"""Load or return (if cached) nth record."""

		if self._lock:
			while 1:
				self._lock.acquire()
				loading = self.loading
				l = len(self.cache)
				self._lock.release()
				if l > n:
					return self.cache[n]
				elif not loading:
					return None
		else:
			while len(self.cache) <= n:
				if self._next() is None:
					return None
			return self.cache[n]


	def freenth(self, n):
		if n < len(self.cache):
			self.cache[n] = 'freed'
			
	def last(self):
		"""Get last record."""
		if self._lock:
			while 1:
				self._lock.acquire()
				loading = self.loading
				self._lock.release()
				if not loading: break
			return (self.cache[-1], len(self.cache)-1)
		else:
			while 1:
				d = self._next()
				if d is None: break
			return (self.cache[-1], len(self.cache)-1)

def count_spikes(spike_times, start, stop):
	n = 0
	for t in spike_times:
		if (t >= start) and (t < stop):
			n = n + 1
	return n

def extract_spikes(spike_times, start, stop, fromzero=None, offset=0):
	"""Pull out a subset of spikes -- the ones in the specified time window"""
	v = []
	for t in spike_times:
		if (t >= start) and (t < stop):
			if fromzero:
				v.append(t - start + offset)
			else:
				v.append(t)
	return v

def fixvel(d, start=None, stop=None, kn=2):
	"""
	Extract velocity trace from eye record data.  By default, this
	smooths the result with a simple running average kernel using
	the vectorops.smooth().
	"""
	
	if start is None:
		start = 0
	if stop is None:
		stop = len(d.eyet)
	dt = d.eyet[(start+1):stop] - d.eyet[start:(stop-1)]
	dx = d.eyex[(start+1):stop] - d.eyex[start:(stop-1)]
	dy = d.eyey[(start+1):stop] - d.eyey[start:(stop-1)]
	dxy = (dx**2 + dy ** 2) ** .5
	if kn:
		return start, stop, smooth(dxy / dt, kn=kn)
	else:
		return start, stop, dxy / dt

def pix2deg(d, pix):
	"""Try to convert from pixels to degrees visual angle."""
	try:
		return float(pix) / float(d.params['mon_ppd'])
	except:
		return float(pix) / float(d.params['pix_per_dva'])

def deg2pix(d, deg):
	"""Try to convert from degrees visual angle to pixels."""
	try:
		return float(deg) * float(d.params['mon_ppd'])
	except:
		return float(deg) * float(d.params['pix_per_dva'])

def find_saccades(d, thresh=2, mindur=25, maxthresh=None):
	"""
	Thu Apr  5 13:33:12 2001 mazer
	
	Find all saccades in a trial.
	This function is carefully hand tuned. The steps are as follows:
	  1. decimates eye signal back down to 120hz (iscan speed)
	  2. compute the velocity signal
	  3. smooth velocity with a running average (5pt)
	  4. find velocity spikes that exceed thresh
	  5. Two saccades within <mindur>ms are essentially considered to
	     be one noisy saccade and the second one is discarded.
		 
            /\                   /\                     /\
     v: ___/  \_________________/  \___________________/  \_____....
               <-------------------------------------->
               |                |   |                 |
               t0               t1  t2                t3
                                    <-------------------------------
                                    |                 |   |          
                                    t0                t1  t2

    So, to compute a real fixation triggered PSTH, you allign
	all the rasters up on 't2' and only count spikes from t0-t3.

	The output of this function is a complicated list:
	  [
	  (t0,t1,t2,t3,t0i,t1i,t2i,t3i,fx,fy,fv,l_fx,l_fy,l_fv),
	  (t0,t1,t2,t3,t0i,t1i,t2i,t3i,fx,fy,fv,l_fx,l_fy,l_fv),
	  (t0,t1,t2,t3,t0i,t1i,t2i,t3i,fx,fy,fv,l_fx,l_fy,l_fv),
	  ....
	  ]
	tN's are the times of the events shown in the diagram above,
	while tNi's the indices of those events back into the
	d.eye[xyt] arrays.
	fx,fy are the mean x & y positions between t2-t3 and l_fx,
	l_fy are the position of the last fixation.  fv and l_fv refer
	to the calibration state of fx/fy and l_fx/l_fy respectively.
	If fv is TRUE, then this is a 'calibrated' fixation.  Which
	means inside the calibration field, or,
		OR *NO* EYE CALIBRATION DATA WAS SUPPLIED.

	Mon Oct  7 10:59:13 2002 mazer
	Added maxthresh -- if (vel > maxthresh), assume it's a blink and
	don't put it in the list..
	"""
	
	start = 0
	stop = len(d.eyet)

	# calculate good v (velocity profile from XY position)

	# calc how to decimate down to 120hz (ie, 8ms sampling period)
	if 0:
		for ix in range(1, len(d.eyet)):
			decimate_by = (d.eyet[ix]-d.eyet[ix-1])
			if decimate_by > 0:
				decimate_by = int(0.5 + 8.0 / float(decimate_by))
				break
		if ix == len(d.eyet):
			sys.stderr.write('decimate_by time failure!!\n')
			sys.exit(1)
	else:
		# guess at sampling period in ms:
		fs = mean(diff(d.eyet))
		decimate_by = int(0.5 + (8.0 / fs))
		
	if decimate > 1:
		t = decimate(d.eyet[start:stop], decimate_by)
		x = decimate(d.eyex[start:stop], decimate_by)
		y = decimate(d.eyey[start:stop], decimate_by)
	else:
		t = d.eyet[start:stop]
		x = d.eyex[start:stop]
		y = d.eyey[start:stop]

	dx = x[1:] - x[0:-1]
	dy = y[1:] - y[0:-1]
	dt = t[1:] - t[0:-1]
	
	dxy = ((dx**2 + dy ** 2) ** .5) / dt
	dxy = smooth(dxy, 2)

	# t0[i] = start of last fixation
	# t1[i] = start of this saccade
	# t2[i] = start of this fixation (end this saccade)
	# t3[i] = start of next saccade
	#  tN is the time in ms, tNi is index into d.eye[txy]
	# state = 1 --> in saccade
	# state = 2 --> in fixation

	if maxthresh is None:
		# this will NEVER be exceeded..
		maxthresh = max(dxy) * 10

	# find a fixation to get started..
	realti = None
	for ix in range(0, len(dxy)):
		if dxy[ix] < thresh and dxy[ix] < maxthresh:
			realix = ix * decimate_by
			realti = t[ix]
			ix0 = ix
			break
		
	if realti is None:
		# no fixations found..
		return []


	t2 = realti
	t2i = realix
	state = 2
	SList = [];
	fx, fy, fv, lfx, lfy, lfv = None, None, None, None, None, None
	#keyboard()
	for ix in range(ix0, len(dxy)):
		realix = ix * decimate_by
		realti = t[ix]
		if (state == 2) and (dxy[ix] > thresh) and (dxy[ix] < maxthresh):
			# we were in a fixation (or at start) and just entered a saccade
			t3 = realti
			t3i = realix
			# SList this fixation and last fixation positions
			if d.eyevalid:
				v = (sum(d.eyevalid[t2i:t3i]) == 0)
			else:
				v = 1
			fx, fy, fv, lfx, lfy, lfv = \
				mean(d.eyex[t2i:t3i]), mean(d.eyey[t2i:t3i]), v, fx, fy, fv
			try:
				if t3-t2 > 0:
					SList.append((t0,  t1,  t2,  t3,
								  t0i, t1i, t2i, t3i,
								  fx, fy, fv, lfx, lfy, lfv))
			except NameError:
				pass
			(t0, t1, t2, t3) = (t2, realti, None, None)
			(t0i, t1i, t2i, t3i) = (t2i, realix, None, None)
			state = 1
		elif (state == 1) and (dxy[ix] <= thresh):
			# make sure we're staying below thresh for a ~<mindur>ms
			skip = 0
			for i in range(1, int(0.5+float(mindur)/decimate_by)):
				j = ix + i
				if j < len(dxy) and dxy[j] > thresh and dxy[ix] < maxthresh:
					skip = 1
					break
			if not skip:
				# we were in a saccade and now in a stable fixation period
				t2 = realti
				t2i = realix
				state = 2

	# try to catch that last saccade that ran out..
	if (state == 2) and (dxy[ix] <= thresh):
		t3 = realti
		t3i = realix
		try:
			if t3-t2 > 0:
				SList.append((t0,  t1,  t2,  t3,
							  t0i, t1i, t2i, t3i,
							  fx, fy, fv, lfx, lfy, lfv))
		except NameError:
			pass

	return SList


def findfix(d, thresh=2, dur=50, anneal=10, start=None, stop=None):
	"""
	Find fixation periods in trial. Threshold is velocity (pix/ms)
	below which will be called a fixation, if it's maintained for
	more than dur ms.  Fixations separated by gaps of less than
	anneal ms will be merged together to form single fixation
	events.

	NOTE: start and stop are index values, NOT TIMES!
	Returns list of tuples:
	  [(start_ix, stop_ix, start_ms, stop_ms, mean_xpos, mean_ypos),
	   (start_ix, stop_ix, start_ms, stop_ms, mean_xpos, mean_ypos),
       .......
	   (start_ix, stop_ix, start_ms, stop_ms, mean_xpos, mean_ypos)]

    Note: 100 deg/sec -> 1800pix/sec -> 1.8pix/ms
	"""

	# calculate v (velocity profile from XY position)
	start, stop, v = fixvel(d, start=start, stop=stop)

	fix_ix = []
	infix = 0
	for i in range(0, len(v)):
		if (not d.eyevalid is None) and (not d.eyevalid[i]):
			# outside valid calibration range -- discard completely
			infix = 0
		elif not infix and (v[i] <= thresh):
			infix = 1
			fstart = start + i
		elif infix and ((v[i] > thresh) or i == (len(v)-1)):
			infix = 0
			fstop = start + i - 1
			if (d.eyet[fstop]-d.eyet[fstart]) > dur:
				fix_ix.append(fstart)
				fix_ix.append(fstop)

	if len(fix_ix) > 2:
		merged = fix_ix[:1]
		for i in range(2, len(fix_ix), 2):
			if d.eyet[fix_ix[i]] - d.eyet[fix_ix[i-1]] > anneal:
				merged.append(fix_ix[i-1])
				merged.append(fix_ix[i])
		merged.append(fix_ix[-1])
		fix_ix = merged

	fixations = []
	for i in range(0, len(fix_ix), 2):
		a = fix_ix[i]
		b = fix_ix[i+1]
		xp = Numeric.sum(d.eyex[a:b]) / float(len(d.eyex[a:b]))
		yp = Numeric.sum(d.eyey[a:b]) / float(len(d.eyey[a:b]))
		fixations.append((a, b, d.eyet[a], d.eyet[b], xp, yp))

	return fixations

def parseargs(argv, **kw):
	newargv = []
	newargv.append(argv[0])
	
	for arg in argv[1:]:
		if arg[0] == '-':
			l = string.split(arg, '=')
			if (len(l) > 1) and (l[0][0] == '-'):
				kw[l[0][1:]] = string.join(l[1:], '=')
			else:
				kw[l[0][1:]] = 1
		else:
			newargv.append(arg)

	return newargv, kw

if __name__ == '__main__':
	v = PypeFile(sys.argv[1])
	v.last()
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
		

