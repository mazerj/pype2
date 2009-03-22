# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""
**Debugging tools for python and pype**

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Sat Feb  8 14:37:50 2003 mazer

- created from scratch

"""

def keyboard(banner='Type EOF/^D to continue'):
	"""Clone of the matlab keyboard() function.
	
	Drop down into interactive shell for debugging
    Use it like the matlab keyboard command -- dumps you into
    interactive shell where you can poke around and look at
	variables in the current stack frame
	
    The idea and code are stolen from something Fredrick
	Lundh posted on the web a while back.
    """

	import code, sys

	# use exception trick to pick up the current frame
	try:
		raise None
	except:
		frame = sys.exc_info()[2].tb_frame.f_back

	# evaluate commands in current namespace
	namespace = frame.f_globals.copy()
	namespace.update(frame.f_locals)

	code.interact(banner=banner, local=namespace)

def get_traceback(show=None):
	"""Stack dump to stdout.
	
	Collect the current exception information (after catching
	the exception) as a string so it can be reported to the
	user or logged.
	This is an internal function, don't call it directly, use
	the reporterror() function instead.
	
	Stolen from the Pmw source code.
	"""
	import sys, traceback, types
	# Fetch current exception values.
	exc_type, exc_value, exc_traceback = sys.exc_info()

	# Give basic information about the callback exception.
	if type(exc_type) == types.ClassType:
		# Handle python 1.5 class exceptions.
		exc_type = exc_type.__name__

	# in python-2.5 exc_type is not a string, must be coerced into one..
	msg = 'Exception (value): %s\n' % exc_value
	msg = 'Exception (type): %s\n' % exc_type

	# Add the traceback.
	stack = traceback.extract_tb(exc_traceback)

	depth = 1
	for frame in stack:
		(file, line, fn, text) = frame
		#prefix = '>' * depth + ' '
		prefix = '%d> ' % (1+len(stack)-depth)
		msg = msg + prefix + 'File "%s", line %s, in %s:\n' % (file, line, fn)
		msg = msg + prefix + ' %s\n' % text
		depth = depth + 1
	if show:
		sys.stderr.write(msg)
	return msg


def reporterror(gui=None):
	"""Pretty printer for error messages.
	
	Pretty print a timestamped error message on the console
	or popup a dialog window based on the current exception
	state in the current stack frame.  This is really just
	for debugging.
	"""
	import sys
	if gui:
		from pype import warn
		warn('Python Error', get_traceback(), 1)
	else:
		sys.stderr.write('-' * 70 + '\n')
		sys.stderr.write(get_traceback())
		sys.stderr.write('-' * 70 + '\n')


def ppDict(d):
	"""Pretty print a dictionary
	"""
	import types
	
	ks = d.keys()
	ks.sort()
	for k in ks:
		print '%-20s %15s=<%s>' % (type(d[k]), k, d[k])
		
def get_exception():
	"""
	This returns the most recent exception -- useful for an
	'except:' clause with no matching exception pattern (not
	recommended!).

	In general, the value turned by this function will be something
	like <type 'exceptions.EXCEPTION_NAME'>, since exceptions are
	supposed to be classes. For example:
	    try:
	         x = 1/0
		except:
		     print get_exception()
	will yeild:
      <type 'exceptions.ZeroDivisionError'>
	which can be imported from the 'exceptions' module if you want
	to check the value against something..
	"""
	import sys
	
	(etype, evalue, tb) = sys.exc_info()
	return etype

