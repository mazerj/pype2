# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Sun Feb  6 00:01:48 2000 mazer -- created
  spot mapping
  
Sat Jun  3 22:45:37 2000 mazer
  added settable fixspot to get more screen real estate..

Wed Aug 16 14:40:26 2000 mazer
  spotmap3: added oriented bar support
"""

import sys, types
from pype import *
from Tkinter import *
from events import *
import math

def RunSet(app):
	app.console.clear()

	app.foo.trialnum = 0
	app.foo.ncorrect = 0
	app.foo.ntrials = 0

	if len(app.udpy.markstack) < 2:
		warn('Spotmap', 'Need at least two points for rectangle!')
		return 0

	# get bound marks in RETINAL coords
	"""
	x1 = app.udpy.markstack[0][0]
	y1 = app.udpy.markstack[0][1]
	x2 = app.udpy.markstack[1][0]
	y2 = app.udpy.markstack[1][1]
	xc = (x1 + x2) / 2.0
	yc = (y1 + y2) / 2.0
	dx = abs(x2 - x1)
	dy = abs(x2 - x1)
	"""
	
	x1 = float(min(app.udpy.markstack[0][0], app.udpy.markstack[1][0]))
	x2 = float(max(app.udpy.markstack[0][0], app.udpy.markstack[1][0]))
	y1 = float(min(app.udpy.markstack[0][1], app.udpy.markstack[1][1]))
	y2 = float(max(app.udpy.markstack[0][1], app.udpy.markstack[1][1]))
	
	P = app.params.check(mergewith=app.common.check())
	fx = P['fix_x']
	fy = P['fix_y']
	nx = P['n_x']
	ny = P['n_y']
	dx = float(x2 - x1) / float(nx-1)
	dy = float(y2 - y1) / float(ny-1)

	# grid is always in RETINAL coords!
	grid = []
	markers = []
	for x in frange(x1, x2, dx, inclusive=1):
		for y in frange(y1, y2, dy, inclusive=1):
			xx = int(round(x))
			yy = int(round(y))
			grid.append((xx, yy, 0))
			grid.append((xx, yy, 1))
			markers.append(app.udpy.icon(xx+fx, yy+fy, 3, 3, color='red'))

	if ask('Confirm', 'Grid ok?', ('Yes', 'No')) == 1:
		for tag in markers:
			app.udpy.icon(tag)
		return 0
	
	for tag in markers:
		app.udpy.icon(tag)

	app.foo.grid = grid

	app.record_note('task_is', __name__)

	app.paused = 0
	app.running = 1
	app.led(1)
	app.warn_run_start()

	try:
		repnum = 0
		while app.running and (app.nreps() == 0 or repnum < app.nreps()):
			app.repinfo('REP#: %d' % repnum)
			try:
				RunBlock(app, repnum)
			except UserAbort:
				pass					# no effect if finished run..
			repnum = repnum + 1
	except:
		error.reporterror()
	app.repinfo()


	app.running = 0
	app.warn_run_stop()
	app.record_done()
	app.led(0)

	con(app, 'Set done.')
	return 1

def RunBlock(app, repnum):
	P = app.params.check(mergewith=app.common.check())
	grid = []

	fx = P['fix_x']
	fy = P['fix_y']

	# grid is now computed above in RunSet
	grid = app.foo.grid
	gridavail = [1] * len(grid)
	print 'spotmap2: block of %d probes done.' % len(grid)

	while app.running and navailable(gridavail):
		if app.paused:
			app.led(2)
			while app.paused and app.running:
				app.idlefn(ms=10)
			app.led(1)
		if not app.running:
			# this allows user to pause and then stop..
			break

		P = app.params.check(mergewith=app.common.check())
		app.params.save()

		(result, new_gridavail) = RunTrial(app, repnum, grid, gridavail)

		# count them all.. spotmap analysis can use 'em
		gridavail = new_gridavail
#		if result == 1:
#			gridavail = new_gridavail

		con(app, "%d/%d to go" % (navailable(gridavail), len(gridavail)))
		con(app, "--> %d/%d = %.0f%% perf" % \
			(app.foo.ncorrect, app.foo.ntrials,
			 100.0*app.foo.ncorrect/app.foo.ntrials))
	con(app, 'rep %d done/halted' % repnum)


def RunTrial(app, repnum, grid, gridavail):
	while app.running:
		P = app.params.check(mergewith=app.common.check())

		app.foo.trialnum = app.foo.trialnum + 1
		app.record_note('trialtime', (app.foo.trialnum, Timestamp()))
		app.record_start()

		(r, rinfo, rt, trialinfo, P, new_gridavail) = \
			_RunTrial(app, repnum, P, grid, gridavail)

		app.record_stop()
		app.record_write(rinfo, rt, P, taskinfo=trialinfo)
		app.foo.ntrials = app.foo.ntrials + 1

		if r == 1:
			app.foo.ncorrect = app.foo.ncorrect + 1

		if rinfo == UNINITIATED_TRIAL:
			app.foo.uicount = app.foo.uicount + 1
			n = int(P['uimax'])
			if n and app.foo.uicount > n:
				warn('Warning',
					 'UI Count exceeded.\nTime: %s\nPlease intervene.\n' %
					 Timestamp(), wait=1)
				app.foo.uicount = 0
		else:
			app.foo.uicount = 0

		break
	return (r, new_gridavail)

def _RunTrial(app, repnum, P, grid, gridavail):
	trace_start = None
	trace_stop = None

	gridavail = gridavail[:]			# private copy to modify

	fx = P['fix_x']
	fy = P['fix_y']
	app.looking_at(fx, fy)
	

	trialinfo = (app.foo.trialnum)
	showparams(app, P)

	app.udpy.display(None)
	dlist = DisplayList(app.fb)

	fixspot = fixsprite2(fx, fy, app.fb,
						 P['fix_size'], P['fix_ring'],
						 color=P['fix_on'], bg=(P['bg'],P['bg'],P['bg']))

	dlist.add(fixspot)

	fix_dur = P['fix_dur']

	fixwin = FixWin(x=fx, y=fy, size=P['win_size'], app=app)
	fixwin.draw(color='grey')

	# build the spots/bars to use
	sl = P['spot_length']
	sw = P['spot_width']
	dir = P['spot_dir']
	ori = (-dir + 90.0)
	if ori < 0:
		ori = ori + 360.

	if sw <= 0:
		spot_on = Sprite(sl * 3, sl * 3, 0, 0, fb=app.fb, depth=1, on=0)
		if P['spot_on'] == (0,0,0):
			spot_on.noise(0.50)
		else:
			spot_on.fill(0)
			spot_on.circle(color=P['spot_on'], r=sl)
		dlist.add(spot_on)

		spot_off = Sprite(sl * 3, sl * 3, 0, 0, fb=app.fb, depth=1, on=0)
		if P['spot_off'] == (0,0,0):
			spot_off.noise(0.50)
		else:
			spot_on.fill((P['bg'], P['bg'], P['bg']))
			spot_on.circle(color=P['spot_off'], r=sl)
		dlist.add(spot_off)
	else:
		spot_on = barsprite(sl, sw, ori, P['spot_on'],
							fb=app.fb, depth=1, on=0)
		dlist.add(spot_on)

		spot_off = barsprite(sl, sw, ori, P['spot_off'],
							 fb=app.fb, depth=1, on=0)
		dlist.add(spot_off)

	spot_dur = P['spot_dur']

	testing = int(P['testing'])
	if testing:
		con(app, 'TESTING', 'red')

	app.fb.sync(None)
	
	rt = -1
	try:
		# wait some random time..
		app.encode(START_ITI)
		app.idlefn(ms=(P['iti'] / 2.0))
		app.encode(END_ITI)

		# wait for bar to be free..
		app.fb.bg = (P['bg'], P['bg'], P['bg'])
		app.fb.clear()
		app.fb.flip()
		app.warn_trial_start()

		# wait for free bar
		if (not testing) and app.bardown():
			info(app, "Waiting for free bar")
			while (not testing) and app.bardown(): 
				app.idlefn()
			info(app, "ok.")

		# turn on fixspot
		fixspot.on()
		dlist.update()
		app.fb.flip()
		app.udpy.display(dlist)
		app.encode(FIX_ON)

		# start recording eye postition
		app.eyetrace(1)

		# wait for bar to be grabbed, if too long, abort trial
		info(app, "waiting for bar down")
		t = Timer()
		while (not testing) and app.barup():			# remove NONE
			app.idlefn()
			if t.ms() > P['abortafter']:
				con(app, "uninitiated trial (no bar down)", 'red')
				app.fb.clear()
				app.fb.flip()
				rinfo = UNINITIATED_TRIAL
				beep(2000, 100)
				app.fb.clear((1, 1, 1))
				app.fb.flip()
				app.eyetrace(0)			# stop recording eyepos NOW
				app.idlefn(P['uitimeout'])
				raise MonkNoStart

		app.encode(BAR_DOWN)
		info(app, "bar down")

		# collect some spont activity..
		app.encode(START_SPONT)
		app.idlefn(500)
		app.encode(STOP_SPONT)

		# wait for eyes to go through fixwin
		info(app, "waiting fix acquisition")
		fixwin.draw(color='red')
		t.reset()
		fixwin.on()
		while (not testing) and not fixwin.inside():
			app.idlefn()
			if P['maxrt'] > 0 and t.ms() > P['maxrt']:
				fixwin.clear()
				app.warn_trial_incorrect(flash=1000)
				app.udpy.display(None)
				app.eyetrace(0)			# stop recording eyepos NOW
				con(app, "acquire fix timeout", 'blue')
				app.idlefn(P['timeout'] - 1000)
				rinfo = EARLY_RELEASE + '1'
				raise MonkError

		app.encode(FIX_ACQUIRED)
		trace_start = app.ts()
		fixwin.draw(color='blue')
		t.reset()
		dlist.update()
		app.fb.flip()
		gix = None
		on_at = app.ts()
		spot_last = None
		while t.ms() < fix_dur:
			if (app.ts() - on_at) > spot_dur:
				if spot_last is None:
					e = None
					spot_last = 0
					pass
				elif spot_last:
					spot_on.off()
					spot_off.off()
					spot_last = 0
					e = 'spot off'
				else:
					if not gix is None:
						gridavail[gix] = None
					gix = pick_one(grid, gridavail)
					if gix is None:
						# all done -- we can go home now..
						break
					(rx, ry, which) = grid[gix]
					
					# convert fixation relative position to absolute screen:
					x = fx + rx
					y = fy + ry
					if which == 1:
						spot_on.moveto(x, y)
						spot_on.on()
					elif which == 0:
						spot_off.moveto(x, y)
						spot_off.on()
					spot_last = 1
					# save the fixation RELATIVE position (ie, retinal coords):
					e = 'spot on %d %d %d' % (rx, ry, which)
				dlist.update()
				app.fb.flip()
				on_at = app.ts()
				# app.udpy.display(dlist)
				if e: app.encode(e)

			app.idlefn()
			if fixwin.broke():
				actualt = t.ms()
				app.encode(FIX_LOST)
				app.encode('exact_fix_lost=%d' % fixwin.break_time())
				fixwin.clear()
				app.warn_trial_incorrect(flash=1000)
				app.udpy.display(None)
				app.eyetrace(0)			# stop recording eyepos NOW
				con(app, "early break (%d/(%d+) ms)" % 
					(actualt, fix_dur), 'red')
				app.idlefn(P['timeout'] - 1000)
				rinfo = EARLY_RELEASE + '2'
				trace_stop = app.ts()
				raise MonkError
			elif (not testing) and app.barup():
				actualt = t.ms()
				app.encode(FIX_LOST)
				fixwin.clear()
				app.warn_trial_incorrect(flash=1000)
				app.udpy.display(None)
				app.eyetrace(0)			# stop recording eyepos NOW
				con(app, "early barup (%d/%d ms)" % 
					(actualt, fix_dur), 'red')
				app.idlefn(P['timeout'] - 1000)
				rinfo = EARLY_RELEASE + '2'
				trace_stop = app.ts()
				raise MonkError

		app.encode(FIX_DONE)
		# clear the fixwin to reduce dacq load..
		del fixwin

		con(app, "correct: actual hold= %d/(%d+) ms" % 
			(t.ms(), fix_dur), 'red')
		app.encode(BAR_UP)
		rinfo = CORRECT_RESPONSE
		app.warn_trial_correct()
		app.reward()
		app.encode(REWARD)
		app.fb.clear()
		app.fb.flip()
		app.udpy.display(None)
		trace_stop = app.ts()
		raise NoProblem

	except UserAbort:
		rinfo = USER_ABORT
		con(app, "Aborted.", 'red')
		result = 'abort'
	except MonkNoStart:
		result = None
	except MonkError:
		result = 0
	except NoProblem:
		result = 1
	except:
		error.reporterror()

	app.eyegraph.show(trace_start, trace_stop)
	app.eyetrace(0)						# make sure eye race is off..
	app.history(rinfo[0])

	app.fb.clear()
	app.fb.flip()
	app.udpy.display(None)

	app.plexon_state(0)

	app.encode(START_ITI)
	app.idlefn(ms=(P['iti'] / 2.0))
	app.encode(END_ITI)

	del dlist

	app.looking_at()
	
	return (result, rinfo, rt, trialinfo, P, gridavail)

def main(app):
	app.startfn = RunSet

	app.mybutton = app.taskbutton(text=__name__, check=1)
	app.notebook = TaskNotebook(title=__name__, checkbutton=app.mybutton)
	page = app.notebook.add('Params', 'Params')

	parfile = app.taskname()
	if parfile:
		parfile = parfile + '.par'

	app.params = ParamTable(page, (
		("spot_length",	"20",			is_int),
		("spot_width",	"20",			is_int),
		("spot_dir",	"0",			is_float),
		("spot_on",		"(255,255,255)", is_color),
		("spot_off",	"(1,1,1)",		is_color),
		("spot_dur",	"200",			is_int),
		("n_x",			"10",			is_int),
		("n_y",			"10",			is_int),
		("fix_dur",		"1000+-20%",	is_iparam),
		("fix_on",		"(255,255,255)",is_color),
		), file=parfile)

	app.notebook.lift('Params')

	app.foo = Holder();

def cleanup(app):
	app.params.save()
	app.mybutton.destroy()
	app.notebook.destroy()
	app.foo = None


if not __name__ == '__main__':
	print "Loaded %s" % __name__
else:
	print "Nothing to do."
