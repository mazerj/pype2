# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**Parameter tables with type validation**

PMW (Python MegaWidgets) based parameter tables (aka worksheets)
for use by the pype GUI. Most of these functions are **INTERNAL**
only and should never be called directly, except by "power users"!

The exceptions are the *is_????* functions to be used as validators
for task worksheets.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Mon Aug 14 13:46:27 2006 mazer

- Added field locking buttons ('X' to left of entry fields) to let
  user lock individual entries to avoid accidental changes.. For
  Jon Touryan... should work ok with runlock'ing, but I haven't
  tested it. Is anybody using runlock??

Fri Feb 13 11:15:35 2009 mazer

- changed load/save format to a human-readable (non-pickled) version
  change should be transparent - old pickle versions will get read
  and new text versions written from now on..

Wed Mar 11 11:08:19 2009 mazer

- when parameter tables are evaluated, added storage of the raw
  unevaluated string version of the var for future reference..

Sun May 31 15:13:23 2009 mazer

- changed load/save of param tables to use standard pythong ConfigParser
  object -- this makes it easier to have external programs generate
  params files..

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

from Tkinter import *
import Pmw
import string
import types
import os, posixpath
import cPickle


import pype
import pype_aux
from guitools import *
from filebox import Open, SaveAs

_KEEPLOCKED = -1

# these are made available for custom validation functions,
# so the user doesn't have to know how Pmw works (it's just
# too ugly/complicated for the average user & me).

VALID = Pmw.OK
INVALID = Pmw.PARTIAL

def is_dir(s, evaluate=None):
	"""
	entry must be a directory
	"""
	if posixpath.isdir(s):
		r = VALID
	else:
		r = INVALID
	if evaluate:
		return (r, s)
	return r

def is_file(s, evaluate=None):
	"""
	entry must be name of an EXISTING file
	"""
	if posixpath.exists(s):
		r = VALID
	else:
		r = INVALID
	if evaluate:
		return (r, s)
	return r

def is_newfile(s, evaluate=None):
	"""
	entry must be name of NON-EXISTING file
	"""
	if posixpath.exists(s):
		r = INVALID
	else:
		r = VALID
	if evaluate:
		return (r, s)
	return r

def is_any(s, evaluate=None):
	"""
	No type checking --> always returns true
	"""
	r = VALID
	if evaluate:
		return (r, s)
	return r

def is_boolean(s, evaluate=None):
	"""
	entry must be some sort of boolean flag

	- 1,yes,on,true -> 1

	- 0,no,off,false -> 0

	"""
	try:
		x = string.lower(s)
		if (x == 'yes') or (x == 'on') or (x == 'true'):
			r = VALID
			i = 1
		elif (x == 'no') or (x == 'off') or (x == 'false'):
			r = VALID
			i = 1
		else:
			i = int(s)
			if (i == 0) or (i == 1):
				r = VALID
			else:
				i = 0
				r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

# alias for is_boolean:
is_bool = is_boolean

def is_int(s, evaluate=None):
	"""
	entry must be simple integer (positive, negative or zero)
	"""

	try:
		i = int(s)
		r = VALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_posint(s, evaluate=None):
	"""
	entry must be positive (> 0) integer
	"""
	try:
		i = int(s)
		if i > 0:
			r = VALID
		else:
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_negint(s, evaluate=None):
	"""
	entry must be negative (< 0) integer
	"""
	try:
		i = int(s)
		if i > 0:
			r = VALID
		else:
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_gteq_zero(s, evaluate=None):
	"""
	entry must be greater than or equal to zero.
	"""
	
	try:
		i = int(s)
		if i >= 0:
			r = VALID
		else:
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_lteq_zero(s, evaluate=None):
	"""
	entry must be less than or equal to zero.
	"""

	try:
		i = int(s)
		if i <= 0:
			r = VALID
		else:
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_color(s, evaluate=None):
	"""
	entry must be a properly formed color triple
	of the form (R,G,B), were R G and B are all
	in the range 0-255
	
	"""
	l = None
	try:
		l = eval(s)
		if len(l) == 3 and \
			   (l[0] >= 0 and l[0] < 256) and \
			   (l[1] >= 0 and l[1] < 256) and \
			   (l[2] >= 0 and l[2] < 256):
			r = VALID
		elif len(l) == 1 and \
			 (l[0] >= 0 and l[0] < 256):
			r = VALID
			l = (l[0],l[0],l[0])
		else:
			r = INVALID
	except:
		r = INVALID
	if evaluate:
		return (r, l)
	return r

def is_rgb(s, evaluate=None):
	"""
	same as is_color()
	"""
	l = None
	try:
		l = eval(s)
		if len(l) == 3 and \
			   (l[0] >= 0 and l[0] < 256) and \
			   (l[1] >= 0 and l[1] < 256) and \
			   (l[2] >= 0 and l[2] < 256):
			r = VALID
		elif len(l) == 1 and \
			 (l[0] >= 0 and l[0] < 256):
			r = VALID
			l = (l[0],l[0],l[0])
		else:
			r = INVALID
	except:
		r = INVALID
	if evaluate:
		return (r, l)
	return r

def is_rgba(s, evaluate=None):
	"""
	like is_color()/is_rgb(), but allows for alpha channel

	**note: doesn't handle (G) grey scale input**
	"""
	l = None
	try:
		l = eval(s)
		if len(l) == 3 and \
		   (l[0] >= 0 and l[0] < 256) and (l[1] >= 0 and l[1] < 256) and \
		   (l[2] >= 0 and l[2] < 256):
			r = VALID
		elif len(l) == 4 and \
		   (l[0] >= 0 and l[0] < 256) and (l[1] >= 0 and l[1] < 256) and \
		   (l[2] >= 0 and l[2] < 256) and (l[3] >= 0 and l[3] < 256):
			r = VALID
		else:
			r = INVALID
	except:
		r = INVALID
	if evaluate:
		return (r, l)
	return r

def is_gray(s, evaluate=None):
	"""
	entry must be a valid 8-bit grayscale value (0-255)
	"""
	try:
		i = int(s)
		if (i >= 0) and (i <= 255):
			r = VALID
		else:
			i = 0
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_float(s, evaluate=None):
	"""
	entry must be a valid floating point number
	"""
	try:
		f = float(s)
		r = VALID
	except ValueError:
		f = 0.0
		r = INVALID
	if evaluate:
		return (r, f)
	return r

def is_percent(s, evaluate=None):
	"""
	entry must be valid percentage (ie, float in range 0-1)
	"""
	try:
		f = float(s)
		if (f >= 0.0) and (f <= 1.0):
			r = VALID
		else:
			f = 0.0
			r = INVALID
	except ValueError:
		f = 0.0
		r = INVALID
	if evaluate:
		return (r, f)
	return r

def is_angle_degree(s, evaluate=None):
	"""
	entry must be valid angle in degrees (ie, float in range 0-360)
	"""
	try:
		f = float(s)
		if (f >= 0.0) and (f <= 360.0):
			r = VALID
		else:
			f = 0.0
			r = INVALID
	except ValueError:
		f = 0.0
		r = INVALID
	if evaluate:
		return (r, f)
	return r

def is_param(s, evaluate=None):
	"""
	entry must be special 'parameter' string; see pype_aux.py for
	complete information on parameter string format
	"""
	try:
		x = pype_aux.param_expand(s)
		if x is None:
			r = INVALID
		else:
			r = VALID
	except ValueError:
		x = 0.0
		r = INVALID
	if evaluate:
		return (r, x)
	return r

def is_iparam(s, evaluate=None):
	"""
	like is_param, but for integer params
	"""
	try:
		x = pype_aux.param_expand(s)
		if x is None:
			r = INVALID
		else:
			r = VALID
	except ValueError:
		x = 0
		r = INVALID
	if evaluate:
		try:
			return (r, int(round(x)))
		except TypeError:
			return (INVALID, 0)
	return r

def is_cdf(s, evaluate=None):
	"""
	entry must describe a **cummulative distribution function**.

	Basically, ensure that value is an integer or a vector
	describing a valid cummulative PDF.	 If an integer, then
	return a n-length cdf of uniform prob (eg, [1/n, 1/n .. 1/n])
	Otherwise, normalize the vector to have unity area.

	IMPROVED: 23-mar-2002 JM --> changed so you don't have
	to make stuff add to 1.0, evaluating divides by the
	sum to force it to add up to 1.0...
	"""
	try:
		i = int(s)
		if evaluate:
			val = []
			for n in range(i):
				val.append(1.0 / float(i))
		r = VALID
	except ValueError:
		try:
			i = eval(s)
			val = []
			if type(i) is types.ListType:
				sum = 0.0
				for f in i:
					sum = sum + float(f)
				for f in i:
					val.append(float(f) / sum)
			r = VALID
		except:
			val = 0
			r = INVALID
	if evaluate:
		return (r, val)
	return r

def is_list(s, evaluate=None):
	"""
	Entry must be a list/vector or range:
		'=start:stop:step' (inclusive: both start and stop in list)
		'start:stop:step' (stop is not included in the list)
		[1,2,3,...4]
	"""

	try:
		v = string.split(s, ':')
		if len(v) > 1:
			if s[0] == '=':
				inc = 1
				v = map(int, string.split(s[1:], ':'))
			else:
				v = map(int, string.split(s, ':'))
				inc = 0
			if len(v) < 3:
				stride = 1
			else:
				stride = v[2]
			r = VALID
			if inc:
				val = range(v[0], v[1]+1, stride);
			else:
				val = range(v[0], v[1], stride);
			if evaluate:
				return (r, val)
			return r
	except:
		pass

	try:
		val = eval(s)
		if type(val) == types.ListType:
			r = VALID
		else:
			r = INVALID
			val = []
	except:
		r = INVALID
		val = []

	if evaluate:
		return (r, val)

	return r

def _unpack_slot(slot):
	"""
	**INTERNAL FUNCTION** (do not use)
	"""
	(name, default, validate, descr, runlock) = [None] * 5
	try:
		name = slot[0]
		default = slot[1]
		validate = slot[2]
		descr = slot[3]
		runlock = slot[4]
	except IndexError:
		pass
	if name is None:
		raise FatalPypeError, 'ptable:_unpack_slot bad worksheet slot'

	return (name, default, validate, descr, runlock)

# helper functions for creating rows in the parameter table:

# standard slot/row:
def slot(name, default=None, val=None, info=None, lockonrun=None):
	return (name, default, val, info, lockonrun)

# dropdown choice list:
def pick(name, default=None, choices=None, info=None, lockonrun=None):
	return (name, default, val, info, lockonrun)

# title/section-delimiter
def title(name):
	return (name, None, None, None, None)

class ParamTable:
	def __init__(self, parent, table, file=None, altfile=None,
				 decorate=1, locks=1):
		"""Parameter management table class"""
		self._table = table
		self._entries = {}
		self._locks = {}

		self.tablename = 'noname'

		if file:
			try:
				self._file = pype.subjectrc(file)
			except KeyError:
				self._file = file
			self.tablename = file
		else:
			self._file = None

		self.altfile = altfile

		f = Frame(parent)
		f.pack(expand=0, fill=X, side=TOP)
		self.frame = f
		if self._file:
			Button(f, text='Save',
				   command=self.save).pack(expand=0, fill=X, side=LEFT)

		if decorate:
			Button(f, text="View",
				   command=self.view).pack(expand=0, fill=X, side=LEFT)

		f = Pmw.ScrolledFrame(parent, usehullsize=1)

		f.pack(expand=1, fill=BOTH)
		self.balloon = Pmw.Balloon(parent, master=1, relmouse='both')

		entries = []
		self.names = []
		for slot in self._table:
			(name, default, validate, descr, runlock) = _unpack_slot(slot)
			lf = Frame(f.interior())
			lf.pack(expand=1, fill=X)
			if default is None:
				e = Label(lf, text=name, bg='yellow', anchor=W)
				e.pack(expand=1, fill=X)
			elif None and type(validate) is types.TupleType:
				e = Pmw.RadioSelect(lf,
								   labelpos = 'w',
								   label_text = name + ':')
				e.pack(expand=0, fill=X)
				for o in validate:
					e.add(o)
				e.invoke(default)
			elif type(validate) is types.TupleType:
				e = Pmw.ComboBox(lf,
								 labelpos = 'w',
								 label_text = name + ':',
								 scrolledlist_items = validate)
				e.pack(anchor=W)
				e.selectitem(default)
				self._entries[name] = e
				e.component('entry').configure(state=DISABLED)
			else:
				e = Pmw.EntryField(lf,
								   labelpos = 'w',
								   label_text = name + ':',
								   validate = validate,
								   value = default)
				if descr:
					self.balloon.bind(e, descr)
				else:
					self.balloon.bind(e, "???")
				e.component('entry').configure(bg='white', width=75)
				tmpf = Frame(lf, height=12, width=12)
				tmpf.pack_propagate(0)
				tmpf.pack(side=LEFT)
				if locks:
					if runlock == _KEEPLOCKED:
						lockbut = Label(tmpf, text = '')
					else:
						lockbut = Button(tmpf, text = '',\
										 command=lambda n=name: \
										 self.lockfield(n, toggle=1))
					lockbut.pack(fill=BOTH, expand=1)

					if runlock == _KEEPLOCKED:
						# usr can NEVER set this value!
						e.component('entry').configure(state=DISABLED)
						e.component('label').configure(fg='red')
						lockbut.configure(state=DISABLED)
				self._entries[name] = e
				entries.append(e)
				self.names.append(e)
				e.pack(expand=1, anchor=W, fill=X, side=RIGHT)

		f.update_idletasks()
		h = f.component('frame').winfo_reqheight()
		sh = f.component('frame').winfo_screenheight()
		x = int(min(0.75 * sh, 1.20*h))
		f.configure(hull_width=500, hull_height=x)

		Pmw.alignlabels(entries)

		if self._file:
			self.load()

	def get(self, evaluate=1, mergewith=None, readonly=1):
		"""Lookup value from parameter table.

		Returns a dictionary containing all the values in
		the parameter table.  Dictionary keys are the slot
		names.	Default is to evaluate the parameters, which
		means they should come back correctly) typed (ie,
		is_int's should come back as Integers).

		**evaluate** - Enable or disable calling of validation
		functions. All values will probaly be strings if this is
		disabled.

		**mergewith** - optional existing dictionary and results will
		be merged into the existing dictionary, new merged dictionary
		is returned.

		**readonly[=1]** - validate readonly fields?

		**NOTE:**
		THIS DICTIONARY WILL HAVE PRIORITY

		"""

		if mergewith:
			d = mergewith
		else:
			d = {}

		for slot in self._table:
			(name, default, validate, descr, runlock) = _unpack_slot(slot)
			if default is None:
				continue
			v = self.query(name)
			if evaluate:
				# Wed Mar 11 11:08:13 2009 mazer
				# store raw string version of param in dictionary in addition
				# to the evaluated version for future reference..  only do
				# this if evaluating
				d[name+'_raw_'] = v
				if not (type(validate) is types.TupleType) and validate:
					(r, v) = apply(validate, (v,), {"evaluate": 1})
					if (runlock == _KEEPLOCKED) and not readonly:
						continue
					elif r != VALID:
						return (0, name)
			d[name] = v
		return (1, d)

	def lockfield(self, name, toggle=None, state=DISABLED):
		try:
			w = self._entries[name].component('entry')
		except KeyError:
			# obsolete field...
			return
		
		if toggle:
			if w.cget('state') == DISABLED:
				state = NORMAL
			else:
				state = DISABLED
		w.configure(state=state)
		self._locks[name] = state

	def keys(self):
		return self._entries.keys()

	def query(self, name):
		"""
		Query a single value from the parameter table by name.
		NO VALIDATION
		"""
		return self._entries[name].get()

	def queryv(self, qname):
		"""
		Query current value by name.  This automatically does
		validation & typecasting
		"""
		for slot in self._table:
			(name, default, validate, descr, runlock) = _unpack_slot(slot)
			if default is None:
				continue
			if name is qname:
				v = self.query(name)
				if not (type(validate) is types.TupleType) and validate:
					(r, v) = apply(validate, (v,), {"evaluate": 1})
					if r != VALID:
						(r, v) = apply(validate, (default,), {"evaluate": 1})
						#warn('Warning', 'Using default for slot "%s".' % qname)
				return v
		warn('Warning',
			 'No parameter value associated with slot "%s".' % qname)
		return None

	def set(self, name, value):
		self._entries[name].setentry(value)

	def save(self, file=None):
		"""
		Save a dictionary containing the values from the table/worksheet.
		Uses plain ascii file format - no pickle anymore..
		"""
		if file is None:
			file = self._file

		f = open(file, 'w')

		(ok, x) = self.get(evaluate=0)

		if 0:
			# old style cpickle version
			(ok, x) = self.get(evaluate=0)
			cPickle.dump(x, f)
			cPickle.dump(self._locks, f)

		if 0:
			# new human-readable text version
			for k in x.keys():
				if self._locks.has_key(k):
					lock = self._locks[k]
				else:
					lock = ''
				f.write('%s!!%s!!%s!!%s\n' % (posixpath.basename(file)[:-4],
											  k, lock, x[k]))
		if 1:
			# new standard config-file version
			import ConfigParser
			c = ConfigParser.ConfigParser()
			c.add_section('params')
			c.add_section('locks')
			for k in x.keys():
				c.set('params', k, x[k])
				if self._locks.has_key(k):
					if self._locks[k] == DISABLED:
						c.set('locks', k, 1)
						lock = 1
			c.write(f)

		f.close()

	def load(self, file=None):
		"""
		Load pickled table database - note that the pickled dictionary
		will be unpickled, but only those values referenced in the table
		will actually be used.	The rest (ie, obsolete) are discarded.
		This way you can safely inherit from previous modules w/o
		accumulating excess garbage.
		"""
		if file is None:
			file = self._file

		if self._load(file=file) == 1:
			return

		if self.altfile:
			if self._load(file=pype.subjectrc(self.altfile)) == 1:
				Logger('warning: loaded %s\n' % \
					   pype.subjectrc(self.altfile))
				return

		try:
			initialdir = pype.subjectrc('')
		except KeyError:
			initialdir = os.getcwd()

		while 1:
			(file, mode) = Open(initialdir=initialdir,
									 initialfile=self.tablename)
			if file is None:
				warn('Warning',
					 'Using defaults for "%s".\n' % self.tablename)
				return
			if self._load(file=file) == 1:
				sys.stderr.write("Loaded params from '%s'\n" % file)
				return

	def _load(self, file=None):
		# try all the load methods in order until one works..
		# or if none work, return 0..
		for method in (self._loadc, self._loadt, self._loadp):
			if method(file=file):
				if not method  == self._loadc:
					sys.stderr.write("Warning: updating '%s'\n" % file)
				return 1
		return 0

	def _loadp(self, file=None):
		"""
		This is the actual load function - the load() method is
		a wrapper that lets the user select alternative files in
		the event the application-specficied file doesn't exist.
		"""
		try:
			f = open(file, 'r')
			x = cPickle.load(f)
			try:
				locks = cPickle.load(f)
			except EOFError:
				locks = {}
			f.close()
			for slot in self._table:
				(name, default, validate, descr, runlock) = _unpack_slot(slot)
				if default is None:
					continue
				if type(validate) is types.TupleType:
					try:
						self._entries[name].selectitem(x[name])
					except IndexError:
						# invalid string..
						pass
				else:
					try:
						self._entries[name].setentry(x[name])
					except KeyError:
						pass

			for k in locks.keys():
				self.lockfield(k, state=locks[k])
				
			return 1
		except IOError:
			return 0

	def _loadt(self, file=None):
		"""Load text-based param file.
		
		New load as text function (replaces pickle version).
		State is saved as ascii file with one table-slot per line and
		each line of the form::
		
		  slotname!!lockstate!!value\n
		  
		"""
		try:
			x = {}
			locks = {}
			
			f = open(file, 'r')
			while 1:
				line = f.readline()
				if not line: break
				source, key, lockstate, value = string.split(line, '!!')
				# value has trailing \n
				x[key] = value[:-1]
				locks[key] = lockstate
			f.close()
			
			for slot in self._table:
				(name, default, validate, descr, runlock) = _unpack_slot(slot)
				if default is None:
					continue
				if type(validate) is types.TupleType:
					try:
						self._entries[name].selectitem(x[name])
					except IndexError:
						# invalid string..
						pass
				else:
					try:
						self._entries[name].setentry(x[name])
					except KeyError:
						pass
			for k in locks.keys():
				if len(locks[k]) > 0:
					self.lockfield(k, state=locks[k])
			return 1
		except IOError:
			return 0
		except ValueError:
			return 0

	def _loadc(self, file=None):
		"""Load config-file base param file.
		New load as text function (replaces !! version). Uses standard
		python ConfigParser tools.
		"""
		import ConfigParser
		
		c = ConfigParser.ConfigParser()
		try:
			f = open(file, 'r')
		except IOError:
			return 0
		
		try:
			c.readfp(f)
		except:
			c = None
		f.close()
		if c is None:
			return 0
		
		for slot in self._table:
			(name, default, validate, descr, runlock) = _unpack_slot(slot)
			if default is None:
				continue
			if type(validate) is types.TupleType:
				try:
					self._entries[name].selectitem(c.get('params', name))
				except IndexError:
					# invalid string..
					pass
			else:
				try:
					self._entries[name].setentry(c.get('params', name))
				except ConfigParser.NoOptionError:
					self._entries[name].setentry(default)
				except ConfigParser.NoSectionError:
					self._entries[name].setentry(default)
				except KeyError:
					pass

		try:
			for (name, lockstate) in c.items('locks'):
				if int(lockstate):
					self.lockfield(name)
		except ConfigParser.NoSectionError:
			pass

		return 1
			

	def view(self):
		(ok, x) = self.get(evaluate=0)
		s = ''

		for slot in self._table:
			(name, default, validate, descr, runlock) = _unpack_slot(slot)
			if default is None: continue
			try:
				s = s + '%20s: %s\n' % (name, x[name])
			except KeyError:
				s = s + '%20s: %s\n' % (name, '<undefined>')
		warn('Parameters', s, wait=None, astext=1)

	def check(self, mergewith=None):
		while 1:
			(ok, P) = self.get(mergewith=mergewith)
			if self.tablename:
				w = "Check parameter table '%s'.\n" % self.tablename
			else:
				w = "Check parameter tables.\n"
			if not ok:
				warn('Warning', w +
					 "Field '%s' contains invalid data.\n\n" % P +
					 "Please fix and then click Continue.",
					 wait=1, grab=None)
			else:
				break
		return P

	def runlock(self, lock=1):
		for slot in self._table:
			(name, default, validate, descr, runlock) = _unpack_slot(slot)
			if default:
				e = self._entries[name].component('label')
				if runlock == 1:
					if lock:
						e.configure(state=DISABLED)
					else:
						try:
							e.configure(state=self._locks[name])
						except KeyError:
							e.configure(state=NORMAL)


if __name__ == '__main__':
	root = Tk()
	Pmw.initialise(root)
	exitButton = Button(root, text = 'Exit', command = root.destroy)
	exitButton.pack(side = 'bottom')
	p = ParamTable(root,
				   (title('test'),
					slot('a', default='500+-10%', val=is_param),
					slot('l', default='', val=is_list),
					slot('b', default='3', val=None),
					slot('choice', default=1, val=('yes', 'no')),
					slot('c', default='4', val=None)), file='foobar')
	p.load('foobar')
	root.mainloop()
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
		

