#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Sun Feb 16 15:07:54 2003 mazer
  pype file expander -- takes a data file and *E X P L O D E S* it into
  something that matlab might be able to read..

  This is intented to be a generic tool that works with ANY pype task

Thu Nov  3 16:59:59 2005 mazer
  added dumping of PlexNet timestamp data

Sun May 21 08:22:08 2006 mazer
  Made matlabify a little more strict: varnames can ONLY contain
  [a-zA-Z0-9_]. Somehow some spaces snuck into some var names which
  broke p2m. Now anything illegal is replaced by a '_' and p2m.m
  should report the error more usefully!

Sun May 21 13:44:57 2006 mazer
  Added 'startat' support so you can convert from the middle of a
  file to the end. This is for appending new data...
  
Mon Jan 26 11:00:53 2009 mazer
  Optimizing writeVector() to use matlab's load function seems to
  roughly cut conversion times in half -- but all the improvement
  is really on the matlab side..

Thu Jan 29 14:05:22 2009 mazer
  more optimizing to use fread() in matlab and numeric.array.tostring()
  for fast python-side i/o
  
"""
import sys, types, string, math
from Numeric import *
from pype import *
from events import *
from pypedata import *
from tempfile import mktemp

__TMPVAR__ = 0;

def tmpvar():
	global __TMPVAR__
	__TMPVAR__ = __TMPVAR__ + 1
	return 'xpx%d' % __TMPVAR__
	

def printify(fp, vname, v):
	# convert a "value" into a matlab safe function
	if type(v) is types.IntType:
		# If it's an int, just use the integer
		fp.write("%s=%d;\n" % (vname, v))
	elif type(v) is types.FloatType:
		# If it's an float, just use the float
		fp.write("%s=%f;\n" % (vname, v))
	elif type(v) is types.ListType or type(v) is types.TupleType:
		if len(v) > 0:
			tv = tmpvar();
			for n in range(len(v)):
				printify(fp, '%s{%d}' % (tv, n+1), v[n])
			fp.write('%s=%s;\n' % (vname, tv))
			fp.write('clear %s;\n' % tv)
		else:
			fp.write('%s=[];\n' % vname)
	else:
		# Otherwise, treat like string (this works for strings and
		# lists.  Replaces single-quotes with double quotes to keep
		# strings intact, but this is NOT ROBUST -- ie, won't handle
		# escaped quotes!!
		s = '%s' % (v,)
		s = string.join(string.split(s, "'"), "''")
		# strip trailing \n's
		s = string.join(string.split(s, "\n"), "")
		s = "'%s'" % (s,)
		fp.write("%s=%s;\n" % (vname, s))

def matlabify(m):
	"""Convert pype/worksheet variable names to something matlab-safe"""
	# no leading underscores allowed
	if m[0] == '_':
		m = 'X' + m;
		
	# replace '@' with INT (for internal)
	m = string.join(string.split(m, '@'), 'INT')

	# replace '*' with STAR(for internal)
	m = string.join(string.split(m, '*'), 'STAR')

	# This one's because Ben Hayden messed up.  Just delete
	# colons..
	m = string.join(string.split(m, ':'), '')

	# matlab wants [a-zA-Z0-9_] only in varnames -- so replace everything
	# else with '_'
	s = []
	for c in m:
		if c in string.letters+string.digits+'_':
			s.append(c)
		else:
			s.append('_')
	m = string.join(s, '')
	return m
	

def writeDict(fp, objname, name, dict):
	for k in dict.keys():
		# massage the pype dictionary name into a matlab safe
		# variable name -- replace leading underscores with 'X_'
		# and '@' with 'XX'
		m = matlabify(k);
		if type(dict[k]) is types.StringType:
			n = 0
		else:
			try:
				n = len(dict[k])
			except TypeError:
				n = 0
		if n == 0:
			# this is a string or other atomic type (int/float etc)
			printify(fp, '%s.%s.%s' % (objname, name, m), dict[k])
		else:
			# this is some sort of list..
			v = dict[k]
			for j in range(n):
				printify(fp, "%s.%s.%s{%d}" % \
						 (objname, name, m, j+1), v[j])

def writeVector(fp, objname, name, v, format):
	# Mon Jan 26 10:58:21 2009 mazer
	#  spent some time profile and trying to speed this up...  best was
	#  to use tempfile and matlab-load() instead of matlab-eval(). This
	#  fn is still the main cycle stealer for this module..
	#
	# Thu Jan 29 13:51:03 2009 mazer
	#  by writing vectors out as strings, the python code becomes
	#  significantly faster. more than factor of two I think..
	
	if v is None or len(v) == 0:
		# empty vector
		fp.write("%s.%s=[];" % (objname, name));
	else:
		vs = Numeric.array(v, 'd').tostring()
		if len(vs)/len(v) == 8:
			# 8 bytes/item is correct, otherwise we're on some hardware
			tmp = mktemp()
			t = open(tmp,'w');
			t.write(Numeric.array(v, 'd').tostring())
			t.close()
		
			fp.write("fid=fopen('%s','r');\n" % tmp)
			fp.write("%s.%s=fread(fid, 'float64');\n" % (objname, name))
			fp.write("fclose(fid); delete('%s');\n" % tmp)
		else:
			tmp = mktemp()
			fp.write("%s.%s=load('-ascii', '%s')'; delete('%s');\n" % \
					 (objname, name, tmp, tmp))
			fp = open(tmp,'w');
			fp.write(string.join([format % x for x in v], '\n'))
			fp.close()
		
def expandExtradata(fname, prefix, extradata):
	fp = open('%s_xd.m' % prefix, 'w')
	for n in range(len(extradata)):
		printify(fp, "extradata{%d}.id" % (n+1),
				 extradata[n].id)
		for k in range(len(extradata[n].data)):
			printify(fp, "extradata{%d}.data{%d}" % (n+1, k+1), \
					 extradata[n].data[k])
	fp.close()

def expandRecord(fname, prefix, n, d, xd):
	outfile = '%s_%04d.m' % (prefix, n)
	fp = open(outfile, 'w')
	
	objname = 'rec(%d)' % (n+1)
	d.compute()	

	fp.write("%s.pype_recno=%d;\n" % (objname, n))
	fp.write("%s.taskname='%s';\n" % (objname, d.taskname))
	fp.write("%s.trialtime='%s';\n" % (objname, d.trialtime))
	fp.write("%s.result='%s';\n" % (objname, d.result))
	try:
		fp.write("%s.rt=%d;\n" % (objname, d.rt))
	except TypeError:
		fp.write("%s.rt='%s';\n" % (objname, d.rt))
	fp.write("%s.record_id=%d;\n" % (objname, d.rec[8]))

	writeDict(fp, objname, 'userparams', d.userparams)
	writeDict(fp, objname, 'params', d.params)

	for n in range(len(d.rest)):
		vname = "%s.rest{%d}" % (objname, n+1);
		printify(fp, vname, d.rest[n]);

	n = 1;
	for (t, e) in d.events:
		fp.write("%s.ev_t(%d)=%d;\n" % (objname, n, t))
		fp.write("%s.ev_e{%d}='%s';\n" % (objname, n, e))
		n = n + 1
	
	try:
		v = d.spike_times
	except AttributeError:
		v = []
	writeVector(fp, objname, 'spike_times', v, '%d')

	try:
		v = d.photo_times
	except AttributeError:
		v = []
	writeVector(fp, objname, 'photo_times', v, '%d')

	try:
		v = d.realt
	except AttributeError:
		v = []
	writeVector(fp, objname, 'realt', v, '%d')

	try:
		v = d.eyet
	except AttributeError:
		v = []
	writeVector(fp, objname, 'eyet', v, '%d')

	try:
		v = d.rec[9]
	except IndexError:
		v = []
	writeVector(fp, objname, 'raw_photo', v, '%d')

	try:
		v = d.rec[10]
	except IndexError:
		v = []
	writeVector(fp, objname, 'raw_spike', v, '%d')


	# Thu Nov  3 16:59:55 2005 mazer 
	# write PlexNet timestamps, if present.
	# note: 'times' is timestamp in ms re standard pype time
	#       'channels' is electrode #, starting with 0
	#       'units' is sorted unit # on this electrode, starting with 0
	#
	# Fri Jan 25 13:02:10 2008 mazer 
	#   modified to work with both plexon and tdt data
	# 
	if d.plex_times:
		writeVector(fp, objname, 'plx_times', d.plex_times, '%d')
		writeVector(fp, objname, 'plx_channels', d.plex_channels, '%d')
		writeVector(fp, objname, 'plx_units', d.plex_units, '%d')
	elif len(d.rec) > 13:
		plist = d.rec[13]
		if plist is not None:
			times = []
			channels = []
			units = []
			for (t, c, u) in plist:
				times.append(t)
				channels.append(c)
				units.append(u)
			writeVector(fp, objname, 'plx_times', times, '%d')
			writeVector(fp, objname, 'plx_channels', channels, '%d')
			writeVector(fp, objname, 'plx_units', units, '%d')
		

	# handle analog data channels:
	for chn in range(0, 7):
		cname = 'c%d' % chn
		try:
			v = d.rec[11][chn]
		except IndexError:
			v = []
		writeVector(fp, objname, cname, v, '%d')

	try:
		v = d.eyex
	except AttributeError:
		v = []
	writeVector(fp, objname, 'eyex', v, '%d')

	try:
		v = d.eyey
	except AttributeError:
		v = []
	writeVector(fp, objname, 'eyey', v, '%d')

	# look for pupil data from eyelink, if any..
	try:
		v = d.rec[12]
	except IndexError:
		v = []
	writeVector(fp, objname, 'eyep', v, '%d')

	fp.close()

	return outfile

def expandFile(fname, prefix, startat=0):
	pf = PypeFile(fname, filter=None)

	recno = 0
	expanded = 0
	while 1:
		d = pf.nth(recno)
		if d is None:
			break
		elif recno >= startat:
			o = expandRecord(fname, prefix, recno, d, pf.extradata)
			if math.fmod(recno,10) == 0:
				sys.stderr.write('.')
				sys.stderr.flush()
		else:
			if math.fmod(recno,10) == 0:
				sys.stderr.write('x')
				sys.stderr.flush()
		recno = recno + 1
	expandExtradata(fname, prefix, pf.extradata)
	pf.close()
	if recno > 0:
		sys.stderr.write('\n')
	

if __name__ == '__main__':
	PROFILE = 0
	if len(sys.argv) < 3:
		sys.stderr.write("Usage: pype_expander pypefile prefix [startat]\n")
		sys.exit(1)
	if len(sys.argv) > 3:
		n = int(sys.argv[3])

	if not PROFILE:
		expandFile(sys.argv[1], sys.argv[2], startat=n)
		sys.exit(0)
	else:
		from cProfile import *
		import pstats
		
		prof = Profile()
		prof = prof.run('expandFile(sys.argv[1], sys.argv[2], startat=n)')
		prof.dump_stats('profile.out')

		"""
		to look at the profile try this:

		import pstats
		p=pstats.Stats('profile.out');
		p.sort_stats('cumulative').print_stats()
		"""
		
		p=pstats.Stats('profile.out');
		p.sort_stats('cumulative').print_stats(10)
