#!/usr/bin/python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys
from pype import *
import math

def RunSet(app):
	print "foo"
	app.console.clear()

	P = app.params.check(mergewith=app.getcommon())
	app.params.save()
	app.warn_run_start()
	app.running, app.paused = 1, 0
	try:
		while app.running:
			app.idlefn(1000)
			# meat goes here..
			con(app, "%s: tell me about it.." % now())
	except:
		error.reporterror()
	app.running, app.paused = 0, 0
	app.warn_run_stop()
	return 1


def main(app):
	app.startfn = RunSet

	app.mybutton = app.taskbutton(text=__name__, check=1)
	app.notebook = TaskNotebook(title=__name__, checkbutton=app.mybutton)
	page = app.notebook.add('Params', 'Params')

	parfile = app.taskname()
	if parfile:
		parfile = parfile + '.par'
	app.params = ParamTable(page, (
		("p1",			"1",				is_int),
		("p2",			"1",				is_int),
		("p3",			"1",				is_int),
		), file=parfile)
	app.notebook.lift('Params')

def cleanup(app):
	app.params.save()
	app.mybutton.destroy()
	app.notebook.destroy()


if not __name__ == '__main__':
	loadwarn(__name__)
else:
	dump(sys.argv[1])
