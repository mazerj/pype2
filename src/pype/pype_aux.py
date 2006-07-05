# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""Auxiliary functions for pype.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

- Wed Apr  8 21:42:18 1998 mazer

 - created

- Mon Jan 24 23:15:29 2000 mazer

 - added tic/toc functions

- Sun Nov  6 13:06:34 2005 mazer

 - added stat:stop:step slice syntax to param_expand

- Wed Jul  5 16:16:19 2006 mazer

 - added =start:stop:step for inclusive ranges
"""

import random, sys, time, posixpath

_tic = None

def tic():
	"""Start timer.
	
	Benchmark function: start a simple timer (like
	matlab tic/toc)
	"""
	global _tic
	_tic = time.time()

def toc(label=None):
	"""Stop/lap timer (and perhaps print value).
	
	Benchmark function: stop & print simple timer (like
	matlab tic/toc)
	"""
	global _tic
	if label:
		sys.stderr.write(label)
	if _tic: 
		t = time.time()-_tic
		sys.stderr.write("%d secs" % t)
		return t
	else:
		return None

def nextfile(s):
	"""Next available file in sequence.
	
	Return next available file from pattern. For example:
	  fname = nextfile('foo.%04d.dat')
	  will return 'foo.0000.dat', then 'foo.0001.dat' etc..
	"""
	n = 0
	while 1:
		fname = s % n
		if not posixpath.exists(fname):
			return fname
		n = n + 1
		
def lastfile(s):
	"""Last existing file in sequence.
	
	Return last opened file from pattern (like nextfile,
	but returns the last existing file in the sequence).
	"""
	n = 0
	f = None
	while 1:
		fname = s % n
		if not posixpath.exists(fname):
			return f
		f = fname
		n = n + 1

class Timestamp:
	def __init__(self, dateonly=None, sortable=None):
		months = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
				  'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
				  'Nov', 'Dec' ]
		(self.y, self.mon, self.d, self.h, self.min, self.s,
		 x1, x2, x3) = time.localtime(time.time())
		self.monstr = months[self.mon - 1]
		self.sortable = sortable
		self.dateonly = dateonly

	def __repr__(self):
		if self.sortable:
			s = "%04d-%02d-%02d" % (self.y, self.mon, self.d)
		else:
			s = "%02d-%s-%04d" % (self.d, self.monstr, self.y)
		if not self.dateonly:
			s = "%s %02d:%02d:%02d" % (s, self.h, self.min, self.s)
		return s

class Logfile:
	def __init__(self, filename, autodate=None, autonum=None):
		import os

		if filename:
			if autodate:
				filename = "%s.%s" % (filename,
									  Timestamp(dateonly=1, sortable=1))
			if autonum:
				n = 0
				while 1:
					f = "%s.%03d" % (filename, n)
					if not posixpath.exists(f):
						filename = f
						break
					n = n + 1
		self.filename = filename
		self.write("")

	def write(self, line):
		if self.filename:
			f = open(self.filename, "a")
			f.write(line)
			f.close()

def frange(start, stop, step, inclusive=None):
	"""Floating point version of range().
	"""
	r = []
	if inclusive:
		stop = stop + step
	while start < stop:
		r.append(start)
		start = start + step
	return r

def vrandint(center, pvar):
	"""Random variable generator.

	Generate a uniformly distributed random
	number in range [center-var, center+var].
	"""
	return random.randint(center - (pvar * center), center + (pvar * center))

def pickints(lo, hi, n):
	"""Pick n integers.

	Select n random integers in the range [lo,hi].
	"""
	if (n > (hi - lo + 1)):
		n = hi - lo + 1
	l = []
	for i in range(0, n):
		while 1:
			i = random.randint(lo, hi)
			if l.count(i) == 0:
				l.append(i)
				break
	return l

def uniform(min=0, max=1.0, integer=None):
	"""Generate uniformly distributed random numbers.

	**min,max** -- specific range

	**integer** (boolean) -- if true, only return integers
	"""
	if integer:
		return int(round(uniform(min, max, integer=None)))
	else:
		return min + (max - min) * random.random()

def normal(mean=0, sigma=1.0, integer=None):
	"""Generate normally distributed random numbers.

	**mean,sigma** -- mean and standard deviation of the
	distribution.

	**integer** (boolean) -- if true, only return integers
	"""
	if integer:
		return int(round(normal(mean, sigma, integer=None)))
	else:
		return random.normalvariate(mean, sigma)

def from_discrete_dist(v):
	"""Generate random numbers from a discrete distribution.
	
	Assume v represents somethine like a probability density
    function, with each scalar in v representing the prob. of
    that index, choose an index from that distribution.  Note,
	the sum(v) MUST equal 1!!!

	**NOTE** -- Returned values start from 0, i.e. for v=[0.5, 0.5]
	possible return values are 0 or 1, with 50/50 chance..
	"""

	# compute cummulative density function
	u = uniform(0.0, 1.0)
	pcumm = 0.0
	ix = 0
	for i in range(0, len(v)):
		pcumm = pcumm + v[i]
		if u < pcumm:
			return i
	return None


def fuzzy(mean, plus, minus=None, integer=None):
	"""Fuzzy random number geneator (REALLY INTERNAL USE ONLY)
	
	Generate random number between around mean +/- plus/minus.
	This means [mean-minus, mean+plus], distribution is
	flat/uniform.
	"""
	if integer:
		return int(round(fuzzy(mean, plus, minus, integer=None)))
	else:
		if minus is None:
			minus = plus
		return uniform(mean - minus, mean + plus)

def permute(vector):
	"""Return a random permutation of the input vector.
	"""
	l = range(0,len(vector))
	out = []
	while len(l) > 0:
		ix = random.randint(0, len(l)-1)
		out.append(vector[l[ix]])
		del l[ix]
	return out

def pick_one(vector, available=None):
	"""Pick on element from a vector

	**vector** -- vector/list of elements to select from

	**available** (boolean vector) -- mask specifying which elements
	are actually available for selection. This can be used to mask out
	stimuli that have already been presented etc.

	**returns** -- _INDEX_ of the selected element!!!
	Returns INDEX if choice!!

	**NOTE** --
	*Tue Jan 7 19:15:43 2003 mazer*: This used to return a random
	element of vector, when available==None, but that was
	inconsistent with the other junk in this file.  Now it always
	returns an INDEX (small int).
	"""

	
	if available is None:
		# return vector[random.randint(0, len(vector)-1)]
		return random.randint(0, len(vector)-1)
	else:
		i = random.randint(0, len(vector)-1)
		j = i;
		while not available[i]:
			i = (i + 1) % len(vector)
			if j == i:
				return None
		return i

def navailable(available):
	"""Count number of available slots; see pick_one()

	**available** -- same availablity vector used in pick_one().
	This just tallies the number of availabel (non-zero) elements
	left in the list.
	"""
	n = 0;
	for i in range(0, len(available)):
		if available[i]:
			n = n + 1
	return n

def pick_n(vector, n):
	"""Randomly pick n-elements from vector

	Elements are selected **without replacement**.

	**returns** -- vector length N containing **indices** of
	all selected elements.
	"""
	if n > len(vector):
		raise ValueError, 'pick_n from short vector'
	v = permute(vector)
	return v[0:n]

def pick_n_replace(vector, n):
	"""Randomly pick n-elements from vector

	Elements are selected **with replacement**.

	**returns** -- vector length N containing selected elements.

	**NOTE** -- 11-Jul-2005 changed this back to replace returning
	the selected elements, not the indicies; returning indicies is
	incompatible with pick_n() and broke zvs10.py ...
	"""

	v = []
	for i in range(0, n):
		v.append(vector[pick_one(vector)])
	return v

def param_expand(s, integer=None):
	"""Expand parameter strings

	**s** -- parameter string (from ptable) ::

	  - X+-Y -- uniform dist'd number in range [X-Y, X+Y]
	  
	  - X+-Y% -- uniform dist'd number in range [X-(X*Y/100), X+(X*Y/100)]
	  
	  - X+-Y% -- uniform distributed random number in range [X-(X*Y/100), X+(X*Y/100)]
	  
	  - N[mu,sigma] -- normal dist'd num with mean=mu, var=sigma
	  
	  - U[min,max] -- uniform dist'd num between min and max

	  - start:step[:stride] -- generate non-inclusive range (python style) and
	    pick one at random; default stride is 1

	  - =start:step[:stride] -- generate inclusive range (matlab style) and
	    pick one at random; default stride is 1
	  
	  - X -- just X..
	  
	**integer** (boolean) -- if true, return nearest integer

	**returns** -- float or integer matching parameter string
	specification.
	"""
	import re, string

	if integer:
		return int(round(param_expand(s, integer=None)))

	s = string.strip(s)
	if len(s) < 1:
		return None

	if s[0] == 'n' or s[0] == 'N':
		try:
			(a, b) = eval(s[1:])
			return normal(a, b)
		# was except NameError: but this doesn't catch synatx errors
		# associated with unclosed brackets -- need to find better way.. 
		except:
			pass

	if s[0] == 'u' or s[0] == 'U':
		try:
			(a, b) = eval(s[1:])
			return uniform(a, b)
		# was except NameError: but this doesn't catch synatx errors
		# associated with unclosed brackets -- need to find better way.. 
		except:
			pass

	# if 'slice' syntax is used, generate the slice using range
	# and pick one element randomly. e.g., '1:10:2' would pick
	# 1, 3, 5, 7 or 9 with equal prob.
	if s[0] == '=':
		inc = 1
		l = string.split(s[1:], ':')
	else:
		inc = 0
		l = string.split(s, ':')
	if len(l) > 1:
		if len(l) == 3:
			start, stop, step = map(int, l)
		elif len(l) == 2:
			start, stop = map(int, l)
			step = 1
		if inc:
			l = range(start, stop+step, step)
		else:
			l = range(start, stop, step)
		return l[pick_one(l)]
			
	l = re.split('\+\-', s)
	if len(l) == 2:
		a = float(l[0])
		if len(l[1]) > 0 and l[1][-1] == '%':
			b = float(l[1][0:-1]) / 100.0
			b = a * b
		else:
			b = float(l[1])
		return fuzzy(a, b)

	return float(s)

def open_dumpfile(fname, mode, header=None):
	"""Open a 'dump' file (header up to \014)"""
	if mode[0] == 'r':
		f = open(fname, mode)
		header = ''
		while 1:
			c = f.read(1)
			if c == '\014':
				break
			else:
				header = header + c
		return f, header
	elif mode[1] == 'w':
		f = open(fname, mode)
		if header:
			f.write(header + '\014')
		return f
	else:
		f = open(fname, mode)
		return f

def labeled_dump(label, obj, f, bin=0):
	"""Wrapper for cPickle.dump.

	Prepends ascii tag line and then dumps a pickled
	version of the object.
	"""
	from cPickle import dump
	f.write('<<<%s>>>\n' % label)
	dump(obj, f, bin)

def labeled_load(f):
	"""Wrapper for cPickle.load.

	Inverse of labeled_dump().
	"""
	from cPickle import load
	while 1:
		l = f.readline()
		if not l:
			return None, None
		elif l[:3] == '<<<' and l[-4:] == '>>>\n':
			return l[3:-4], load(f)

def pp_encode(e):
	"""Pretty-print an event list.

	**e** -- list of events
	
	**returns** -- sting containing a printable
	version of the event table.
	"""
	s = ''
	for t, c in e:
		if s is '':
			s = '%10d %10d %s\n' % (-1, t, c)
		else:
			s = s + '%10d %10d %s\n' % (t-lastt, t, c)
		lastt = t
	return s


def con(app, msg=None, color='black', nl=1):
	"""Write message to _console_ window

	**app** (PypeApp) -- appliation handle

	**msg** (string) -- message to print
	
	**color** (string) -- color to use
	
	**nl** (boolean) -- add newline at end?

	This is the continuously running log window
	in the pype gui.
	"""
	if msg is None:
		app.console.clear()
	else:
		if nl:
			app.console.writenl(msg, color)
		else:
			app.console.write(msg, color)

def info(app, msg=None, color='black', nl=1):
	"""Write message to _info_ window

	**app** (PypeApp) -- appliation handle

	**msg** (string) -- message to print
	
	**color** (string) -- color to use
	
	**nl** (boolean) -- add newline at end?

	This is the per-trial info window in the
	pype gui. It gets cleared at the start of
	each new trial.
	"""
	if msg is None:
		app.info.clear()
	else:
		if nl:
			app.info.writenl(msg, color)
		else:
			app.info.write(msg, color)

def showparams(app, P, clearfirst=1):
	"""Pretty-print a parameter table into the _info_ window

	**app** (PypeApp) -- appliation handle
	
	**P** -- parameter dictionary

	See info() function, same module.
	"""
	if clearfirst:
		info(app)
	keys = P.keys()
	keys.sort()
	n = 0
	while n < len(keys):
		s = ''
		while n < len(keys) and len(s) < 25:
			s = s + "%12s: %-10s" % (keys[n], P[keys[n]])
			n = n + 1
		info(app, s)

def log(app, msg, color='black'):
	app.logfile.write(msg+'\n')

def ppdict(dict, f=sys.stdout):
	klist = dict.keys()
	klist.sort()
	for k in klist:
		f.write('%s=%s\n' % (k, dict[k]))

def ppevents(events, f=sys.stdout):
	f.write('     ms\tevent\n')
	f.write('-------\t-----\n')
	for (t, e) in events:
		f.write('%7d\t%s\n' % (t, e))

def find_events(events, event):
	"""Return a list of times (ms) at which 'event' occurred
	""" 
	if event[-1] == '*':
		event = event[0:-1]
		chop = len(event)
	else:
		chop = -1

	tlist = []
	for (t, e) in events:
		if chop > 0: e = e[:chop]
		if e == event:
			tlist.append(t)
	return tlist

def find_events2(events, event):
	"""Returns a list of actual events (pairs) which match pattern.
	""" 
	if event[-1] == '*':
		event = event[0:-1]
		chop = len(event)
	else:
		chop = -1

	elist = []
	for (t, e) in events:
		e0 = e
		if chop > 0: e = e[:chop]
		if e == event:
			elist.append((t, e0))
	return elist

def align_events(events, t0):
	"""Returns a 're-aligned' event list.
	""" 

	new_events = []
	for (t, e) in events:
		new_events.append(((t - t0), e))
	return new_events

def dir2ori(dir):
	"""Convert stimulus DIRECTION to an ORIENTATION.
	"""
	ori = (-dir + 90.0)
	if ori < 0:
		ori = ori + 360.
	return ori


if __name__ == '__main__':
    print pick_n([1, 2, 3, 4], 3);
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
		

