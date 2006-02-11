#!/usr/bin/python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Sun Jul 10 13:19:49 2005 mazer
  -- sample handmap module (from hmapstim.py & ztouch13.py)
"""

import sys
import types
from pype import *
from Tkinter import *
from events import *
from handmap import *

def RunTask(app):
	app.record_note('task_is', __name__)
	
	app.globals.ntrials = 0
	app.globals.uicount = 0
	
	app.console.clear()
	
	P = app.params.check(mergewith=app.getcommon())
	app.params.save()
	
	app.tally(clear=1)
	
	app.set_state(running=1)
	app.warn_run_start()
	try:
		while app.isrunning():
			try:
				RunTrial(app)
			except UserAbort:
				pass
	except:
		reporterror()
	app.warn_run_stop()
	app.set_state(running=0)
	
	# clear info and status windows
	app.repinfo()

	# add terminal end-of-set stamp and close datafile
	app.record_done()

	return 1
		
def RunTrial(app):
	# get parameters fresh at the start of each trial, in
	# case the user's changed them:
	P = app.params.check(mergewith=app.getcommon())
	app.params.save()

	app.record_note('trialtime', (app.globals.ntrials, Timestamp()))
	app.record_start()
	(correct, resultcode, rt, P) = RunTrial2(app, P)
	app.record_stop()
	app.record_write(result=resultcode, rt=rt, pdict=P, taskinfo=None)
	
	if resultcode == UNINITIATED_TRIAL:
		app.globals.uicount = app.globals.uicount + 1
		if app.globals.uicount > P['uimax']:
			warn('Warning',
				 'UI Count exceeded @ %s\nPlease intervene.\n' % now(), wait=1)
			app.globals.uicount = 0
	else:
		app.globals.uicount = 0

def RunTrial2(app, P):
	try:
		dlist = DisplayList(fb=app.fb, bg=(128,128,128))
		app.eyetrace(1)
		spot = Sprite(width=10, height=10, x=0, y=0, depth=10, fb=app.fb)
		spot.fill((255,1,1))
		spot.on()
		dlist.add(spot)
		dlist.update()
		app.fb.flip()

		hmap_set_dlist(app, dlist)
		hmap_show(app)
		app.idlefn(P['hold'])
		hmap_hide(app)
		
		rinfo = CORRECT_RESPONSE
		
		raise NoProblem

		
	except UserAbort:
		rinfo = USER_ABORT
		result = 'abort'
	except NoProblem:
		result = 1
	except:
		reporterror()

	# clear everything before exiting!
	app.eyetrace(0)
	hmap_hide(app)
	hmap_set_dlist(app, None)
	
	spot.off()
	dlist.update()
	app.fb.flip()
	app.udpy.display(None)

	return (result, rinfo, -1, P)

def main(app):
	app.globals = Holder()

	app.startfn = RunTask

	app.mybutton = app.taskbutton(text=__name__, check=1)
	app.notebook = DockWindow(title=__name__, checkbutton=app.mybutton)

	parfile = app.taskname()
	if parfile:
		parfile = parfile + '.par'

	app.params = ParamTable(app.notebook, (
		("hold",		"2000",				is_int),
		), file=parfile)

	hmap_install(app)
		
def cleanup(app):
	# these cleanup the handmap idle stuff
	hmap_uninstall(app)
	app.params.save()
	app.mybutton.destroy()
	app.notebook.destroy()
	del app.globals



if not __name__ == '__main__':
	loadwarn(__name__)
