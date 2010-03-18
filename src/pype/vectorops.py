# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**Simple vector operations**

Implements a bunch of common but useful vector operations using
Numeric (if possible). If Numeric's not available, tries to fall
back to (slower) raw-python.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

- Sun Jan 23 22:09:04 2000 mazer

 - created
 
- Sat Apr 14 14:00:12 2001 mazer

 - added sparseness()
 
Fri Jan 15 09:53:24 2010 mazer

- migrated from Numeric to numpy

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

import numpy as _N

def find(boolvec):
	"""Find indices of all TRUE elements in boolvec.
	
	You can use like this::
	
	  take(x, find(greater(x, 0)))
	  
	to select all elements of x greater than zero..
	
	"""
	return _N.compress(boolvec, _N.arange(len(boolvec)))

def mean(v):
	"""Compute mean of vector."""
	if not type(v) == _N.ndarray:
		v = _N.array(v, 'f')
	return _N.sum(v) / float(len(v))

def std(v):
	"""Compute standard deviation of vector."""
	if len(v) > 0:
		if not type(v) == _N.ndarray:
			v = _N.array(v, 'f')
		m = _N.sum(v) / float(len(v))
		return _N.sum(((v-m)**2)/(float(len(v))-1))**0.5
	return 0.0

def sem(v, sig=None):
	"""Compute standard error of the mean of vector."""
	if len(v) > 1:
		if sig is None:
			sig = std(v)
		return sig/(float(len(v))**0.5)
	else:
		return 0.0

def zeros(v):
	"""Count number of zero entries in vector"""
	if not type(v) == _N.ndarray:
		v = _N.array(v, 'f')
	return len(v)-len(_N.nonzero(v))

def diff(v):
	"""Compute first derivate of vector."""
	if not type(v) == _N.ndarray:
		v = _N.array(v, 'f')
	return v[1::]-v[0:-1:]

def diff2(v):
	"""Compute first derivate of vector, but IN PLACE"""
	for i in range(1, len(v)):
		v[i-1] = v[i] - v[i-1]
	return v

def smooth1(yi, ksize=3):
	"""
	Simple smoothing function (eg, for PSTHs).
	NOTE: Kernel length is actually (2*ksize)+1
	"""
	yo = _N.array(yi)
	for i in range(0, len(yi)):
		a, b = max(0, i - ksize), min(len(yi), i + ksize)
		yo[i] = _N.sum(yo[a:b])/(b - a)
	return yo

def smooth(v, kn=1):
	"""Smooth vector kn=1 --> 3pt average."""
	if not type(v) == _N.ndarray:
		v = _N.array(v, 'f')
	n = len(v)
	vout = _N.zeros(v.shape)
	for ix in range(0, n):
		a = ix - kn
		if a < 0:
			a = 0
		b = ix + kn
		if b > n:
			b = n
		vout[ix] = mean(v[a:b])
	return vout

def decimate(v, n):
	"""Decimate/downsample vector by n"""
	if not type(v) == _N.ndarray:
		v = _N.array(v, 'f')
	return _N.take(v, range(0,len(v),n))

def sparseness(v):
	"""Compute sparseness of vector."""
	if not type(v) == _N.ndarray:
		v = _N.array(v, 'f')
	n = float(len(v));
	if _N.sum(v) == 0:
		return 0
	else:
		a = ((_N.sum(v) / n) ** 2.0) / (_N.sum((v**2.0) / n))
		return ((1.0 - a) / (1.0 - (1.0 / n)))

def nanround(n, digits=0):
	if n is None: return n
	return round(n, digits)

if __name__=='__main__' :
	pass
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass

