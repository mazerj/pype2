# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**Simple 'config' file parser class**

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Tue Aug 13 17:23:06 2002 mazer

- removed save method from UserParams class
 
- renamed UserParams to Config

Tue Jun 26 14:20:10 2007 mazer

- added show() method

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

import sys
import os
import posixpath
import string
import types

class Config:
	def __init__(self, fname):
		self.dict = self.load(fname)

	def get(self, name, default=None):
		try:
			return self.dict[name]
		except KeyError:
			return default

	def iget(self, name, default=None):
		try:
			value = self.dict[name]
		except KeyError:
			value = default
		try:
			return int(value)
		except ValueError:
			return None

	def fget(self, name, default=None):
		try:
			value = self.dict[name]
		except KeyError:
			value = default
		try:
			return float(value)
		except ValueError:
			return None

	def set(self, key, value, override=None):
		k = self.dict.has_key(key)
		if (k and override) or (not k):
			self.dict[key] = value

	def show(self, f):
		keys = self.dict.keys()
		keys.sort()
		for k in keys:
			v = self.dict[k]
			vt = type(v)
			if (vt is types.StringType) and len(v) == 0:
				f.write('\t%s=<empty string>\n' % k)
			else:
				f.write('\t%s=%s %s\n' % (k, v, vt))

	def load(self, fname):
		d = {}
		if posixpath.exists(fname):
			f = open(fname, 'r')
			while 1:
				l = f.readline()
				if not l: break
				l = l[:-1]
				try:
					ix = string.index(l, '#')
					l = l[0:ix]
				except ValueError:
					pass
				try:
					ix = string.index(l, ':')
					name = string.strip(l[0:ix])
					value = string.strip(l[(ix+1):])
					d[name] = value
				except ValueError:
					pass
			f.close()
		return d
	
if __name__=='__main__' :
	pass
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass

