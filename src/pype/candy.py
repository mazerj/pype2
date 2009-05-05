# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**eye candy routines**

Routines to generate nice pictures on the monkey display to
entertain the animal during breaks etc.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Fri Mar 27 13:42:32 2009 mazer
- pulled out from pype.py as separate module

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

import pype
from Tkinter import *
from pype_aux import uniform
import posixpath
from sprite import *

def bounce(app):
	if app.running: return

	if not app.tk:
		raise GuiOnlyFunction, 'candy'

	# cancel candy if it's running..
	if app._candy:
		app.led(0)
		app._sbut1.config(state=NORMAL)
		app._sbut2.config(state=NORMAL)
		app.udpy.stop(command=None)

		app._candy = 0
		app.udpy_note('')
		return
	else:
		app.led(1)
		app._sbut1.config(state=DISABLED)
		app._sbut2.config(state=DISABLED)
		app.udpy.stop(command=lambda app=app: _bounce(app))

		app._candy = 1
		app.console.clear()
		app.console.writenl('bounce running')

	x, y, n = 0, 0, 0
	slist = []
	sync = 0
	while app._candy:
		if n == 0:
			dx = uniform(10, 20)
			dy = uniform(10, 20)
			sync = not sync
		n = (n + 1) % 50
		c = (int(uniform(1, 255)),int(uniform(1, 255)),int(uniform(1, 255)))
		s = Sprite(20, 20, x, y, fb=app.fb)
		s.fill(color=c)
		slist.append(s)
		app.fb.clear(color=(128,128,128))
		app.udpy.icon()
		for s in slist:
			s.blit()
			app.udpy.icon(s.x,s.y,s.w,s.h)

		app.fb.sync(sync)
		app.fb.flip()
		if len(slist) > 10:
			slist = slist[1:]
		app.idlefn()

		x = x + dx
		y = y + dy
		if (x > (app.fb.w/3)) or (x < -(app.fb.w/3)):
			dx = -dx
			x = x + dx
		if (y > (app.fb.h/3)) or (y < -(app.fb.h/3)):
			dy = -dy
			y = y + dy
	app.udpy.icon()
	for s in slist:
		del s
	app.fb.clear(color=(1, 1, 1), flip=1)
	app.idlefb()

def slideshow(app):
	if app.running: return

	if not app.tk:
		raise GuiOnlyFunction, 'candy'

	# cancel candy if it's running..
	if app._candy:
		app.led(0)
		app._sbut1.config(state=NORMAL)
		app._sbut2.config(state=NORMAL)
		app.udpy.stop(command=None)

		app._candy = 0
		app.udpy_note('')
		return
	else:
		app.led(1)
		app._sbut1.config(state=DISABLED)
		app._sbut2.config(state=DISABLED)
		app.udpy.stop(command=lambda app=app: _slideshow(app))

		try:
			f = open(pype.pyperc('candy.lst'), 'r')
			l = f.readlines()
			f.close()
		except IOError:
			warn('Error',
				 'make %s to use this feature.' % pype.pyperc('candy.lst'))
			return
		app._candy = 1
		app.console.clear()
		app.console.writenl('slideshow running')

	itag = None
	bg = Sprite(x=0, y=0, fb=app.fb,
				width=app.fb.w, height=app.fb.h)
	if app.sub_common.queryv('show_noise'):
		bg.noise(0.50)

	while app._candy:
		x = uniform(-200,200)
		y = uniform(-200,200)
		while 1:
			inum = int(uniform(0,len(l)))
			fname = l[inum][:-1]
			if not posixpath.exists(fname):
				continue
			app.console.writenl(fname)
			try:
				s = Sprite(fname=fname, fb=app.fb, x=x, y=x)
				if s.w > 10 and s.h > 10:
					break
			except:
				get_traceback(1)
				app.write('dud file: %s\n' % fname)
		maxd = 512.0
		if s.w > maxd:
			m = maxd / s.w
			s.scale(int(m * s.w), int(m * s.h))
		elif s.h > maxd:
			m = maxd / s.h
			s.scale(int(m * s.w), int(m * s.h))

		app.fb.clear(color=(1, 1, 1), flip=0)
		bg.blit()
		s.blit()
		app.fb.flip()
		if not itag is None:
			app.udpy.icon(itag)
		itag = app.udpy.icon(x, y, s.w, s.h, color='blue')
		app.idlefn(ms=5000)
		del s
	try:
		del s
	except NameError:
		pass

	app.udpy.icon()

	app.fb.clear(color=(1, 1, 1), flip=1)
	app.idlefb()

	if not itag is None:
		app.udpy.icon(itag)
