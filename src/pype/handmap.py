# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""Handmap engine.

This module was derived from hmapstim.py (10-jul-2005) and
intended to make it easy (although less flexible) for users
to incorporate handmap stimuli into their tasks.


From http://www.mlab.yale.edu/lab/index.php/Handmap ::
 
 In your task:
 
 * At the top of your module (taskfile.py), add:
  from handmap import *
 
 * In your ''main(app)'' function, add:
  hmap_install(app)
 
 * In your ''cleanup(app)'' function, add:
  hmap_uninstall(app)
 
 * Keep all the sprites you want to display within the task inside a single DisplayList (call in dlist) and tell hmap where to find it:
  ...
  dlist = DisplayList(fb=app.fb, ...)
  dlist.add(somesprite)
  dlist.add(someothersprite)
  ...
  hmap_set_dlist(app, dlist)
 
 * anywhere you want the handmap stimulus to be live on the monkey display (typically after fixation is acquired), call:
  hmap_show(app)
 
 * and when you don't want it to display (after an error or during the intertrial interval), call:
  hmap_hide(app)
 
 * at the end of each trial, it's probably a good idea to call:
   hmap_hide(app)
   hmap_set_dlist(app, None)

Sun Jul 24 16:30:25 2005 mazer

 - minor changes in cleanup code trying to figure out why Jon's tasks
   are leaving text and markers behind..
   
"""

import sys
import math

from pype import *
from Tkinter import *
from events import *

def _bool(state):
	if state:
		return 'ON'
	else:
		return 'OFF'
	

class _Probe:
	def __init__(self, app):
		self.lock = 0
		self.on = 1
		self.app = app
		self.s = None
		self.length = 100
		self.width = 10
		self.a = 0
		self.x = 100
		self.y = 100
		self.colorn = 0
		self.drift = 0
		self.drift_freq = 0.1;
		self.drift_amp = 50
		self.jitter = 0
		self.xoff = 0
		self.yoff = 0
		self.blinktime = app.ts()
		self.app.udpy.xoffset = self.xoff
		self.app.udpy.yoffset = self.yoff
		self.live = 0
		self.blink = 0
		self.cblink = 0
		self._blinkn = 0
		self.blinkper = 300
		self.inten = 100
		self.colorstr = None
		self.barmode = 0
		self.barmodes = ('bar', 'cart', 'hyper', 'polar')
		self.p1 = 1.0
		self.p2 = 0.0
		self.l = None
		self.l2 = None
		#self.txt = None
		self.bg = 128.0
		
		try:
			self.load()
		except:
			reporterror()
			#pass

	def __del__(self):
		print "info: deleted probe"
		self.clear()

	def save(self):
		import cPickle
		x = Holder()

		x.lock = self.lock
		x.on = self.on 
		x.length = self.length
		x.width = self.width 
		x.a = self.a 
		x.colorn = self.colorn
		x.drift = self.drift 
		x.drift_freq = self.drift_freq 
		x.drift_amp = self.drift_amp 
		x.jitter = self.jitter
		x.xoff = self.xoff
		x.yoff = self.yoff
		x.live = self.live
		x.blink = self.blink
		x.blinkper = self.blinkper
		x.inten = self.inten
		x.cblink = self.cblink
		x.barmode = self.barmode
		x.p1 = self.p1
		x.p2 = self.p2

		file = open(pyperc('hmapstim'), 'w')
		cPickle.dump(x, file)
		file.close()
		
	def load(self):
		import cPickle
		try:
			file = open(pyperc('hmapstim'), 'r')
			x = cPickle.load(file)
			file.close()
		except IOError:
			return None

		try:
			self.lock = x.lock
			self.on = x.on 
			self.length = x.length
			self.width = x.width 
			self.a = x.a 
			self.colorn = x.colorn 
			self.drift = x.drift 
			self.drift_freq = x.drift_freq 
			self.drift_amp = x.drift_amp 
			self.jitter = x.jitter
			self.xoff = x.xoff
			self.yoff = x.yoff
			self.app.udpy.xoffset = self.xoff
			self.app.udpy.yoffset = self.yoff
			self.live = x.live
			self.blink = x.blink
			self.blinkper = x.blinkper
			self.inten = x.inten
			self.cblink = x.cblink
			self.barmode = x.barmode
			self.p1 = x.p1
			self.p2 = x.p2
		except AttributeError:
			sys.stderr.write('** loaded modified probe **\n');
			
		if self.s:
			del self.s
			self.s = None

	def pp(self):
		# Tue Mar  7 15:44:49 2006 mazer
		# this little bug-fixer is no longer needed -- the grating
		# functions were fixed today!
		#   a = -(self.a-90)+180
		#   a1 = a % 180
		
		a1 = self.a % 180
		a2 = a1 + 180
		rx = self.x - self.app.udpy.fix_x
		ry = self.y - self.app.udpy.fix_y

		s =	        "  key action    value\n"
		s =	s +     "   z: lock_______%s\n" % _bool(self.lock)
		s =	s +     "   o: offset_____%s\n" % _bool(self.xoff)
		s =	s +     "   u: on/off_____%s\n" % _bool(self.on)
		s =	s +     "   M: bar mode___%s\n" % self.barmodes[self.barmode]
		if self.barmode > 0:
			s =	s + "      (p1 = %.1f)\n" % self.p1
			s =	s + "      (p2 = %.1f)\n" % self.p2
		s =	s +     " 8,9: a__________%d/%d\n" % (a1, a2)
		s =	s +     " n/m: rgb________%s\n" % repr(self.colorshow)
		s =	s +     "(1-6) color______%s\n" % self.colorname
		s =	s +     " q/w: len________%d\n" % self.length
		s =	s +     " e/r: wid________%d\n" % self.width
		s =	s +     "   d: drift______%s\n" % _bool(self.drift)
		s =	s +     " t/T: drift_amp__%d pix\n" % self.drift_amp
		s =	s +     " y/Y: drft_freq__%.1f Hz\n" % self.drift_freq
		s =	s +     "   b: blink______%s\n" % _bool(self.blink)
		s =	s +     "   B: clr blink__%s\n" % _bool(self.cblink)
		s =	s +     " p/P: blnk per___%d ms\n" % self.blinkper
		s =	s +     " i/I: inten______%d\n" % self.inten
		s =	s +     " RELPOS=(%4d,%4d)px\n" % (rx, ry)
		s =	s +     "    ECC=%3dpx / %.1fd\n" % \
			(round(math.sqrt(rx * rx + ry * ry)),
			 math.sqrt(rx * rx + ry * ry) / self.app.udpy.gridinterval)
		a = (180.0 * math.atan2(ry, rx) / math.pi)
		if a < 0:
			a = a + 360.0
		s =	s +     "     THETA=%.0fdeg" % round(a)
		return s
	
	def clear(self):
		if self.l:
			self.app.udpy._canvas.delete(self.l)
			self.l = None
		if self.l2:
			self.app.udpy._canvas.delete(self.l2)
			self.l2 = None
		#if self.txt:
		#	self.app.udpy._canvas.delete(self.txt)
		#	self.txt = None
		self.app.udpy_note('')

	def reset(self):
		"""force sprite to be redraw next cycle"""
		if self.s:
			del self.s
			self.s = None

	def color(self):
		colornames = ('noise', 'white', 'black', 'red', 'green', 'blue',
					  'yellow', 'aqua', 'purple')
		bg = self.bg
		maxi = max(255 - bg, bg)
		
		if self.colorn == 0:
			col = None
		elif self.colorn == 1:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (x, x, x)
		elif self.colorn == 2:
			x = int(bg - (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (x, x, x)
		elif self.colorn == 3:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (x, 1, 1)
		elif self.colorn == 4:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (1, x, 1)
		elif self.colorn == 5:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (1, 1, x)
		elif self.colorn == 6:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (x, x, 1)
		elif self.colorn == 7:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (1, x, x)
		elif self.colorn == 8:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (x, 1, x)
		return (col, colornames[self.colorn])

	def nextcolor(self, incr=1):
		self.colorn = (self.colorn + incr) % 9

	def showprobe(self):
		i = self.app.udpy._canvas.create_image(0, 0, anchor=NW,
											   image=self.s.asPhotoImage())
		
	def draw(self):
		t = self.app.ts()

		if self.blink and (t - self.blinktime) > self.blinkper:
			self.on = not self.on
			self._blinkn = (self._blinkn + 1) % 2
			self.blinktime = t
			if self.cblink and self._blinkn == 0:
				self.nextcolor()

		(color, name) = self.color()
		if color:
			rc = self.inten * (color[0]-1) / 254.0 / 100.0
			gc = self.inten * (color[1]-1) / 254.0 / 100.0
			bc = self.inten * (color[2]-1) / 254.0 / 100.0
		else:
			rc = 1.0
			gc = 1.0
			bc = 1.0
		self.colorshow = color
		self.colorname = name
		if (self.s is None) or (self.drift and (self.drift_amp < 1)):
			if self.barmode == 0:
				self.s = Sprite(width=self.width, height=self.length,
								fb=self.app.fb, depth=99)
				if color is None:
					self.s.noise(0.5)
				else:
					self.s.fill(color)
				self.s.rotateCCW(self.a, 0, 1)
			elif self.barmode == 1:
				l = self.length
				self.s = Sprite(width=l, height=l,
								fb=self.app.fb, depth=99)
				if sum(color) < 3:
					# 'black' is just 90deg phase shift of 'white'
					rc,gc,bc = -1.0,-1.0,-1.0
				if self.drift_amp < 1:
					phase = self.drift_freq * 180.0 * (t - self.drift) / 1000.0
				else:
					phase = 90.0;
				singrat(self.s, abs(self.p1), phase, self.a,
						1.0*rc, 1.0*gc, 1.0*bc)
				self.s.circmask(0, 0, self.length/2)
			elif self.barmode == 2:
				l = self.length
				self.s = Sprite(width=l, height=l,
								fb=self.app.fb, depth=99)
				if sum(color) < 3:
					# 'black' is just 90deg phase shift of 'white'
					rc,gc,bc = -1.0,-1.0,-1.0
				hypergrat(self.s, abs(self.p1), 0.0, self.a,
						  1.0*rc, 1.0*gc, 1.0*bc)
				self.s.circmask(0, 0, self.length/2)
			elif self.barmode == 3:
				l = self.length
				self.s = Sprite(width=l, height=l,
								fb=self.app.fb, depth=99)
				if self.p2 < 0:
					pol = -1
				else:
					pol = 1
				if sum(color) < 3:
					# 'black' is just 90deg phase shift of 'white'
					rc,gc,bc = -1.0,-1.0,-1.0
				polargrat(self.s, abs(self.p1), abs(self.p2), 0.0, pol,
						  1.0*rc, 1.0*gc, 1.0*bc)
				self.s.circmask(0, 0, self.length/2)
			if self.barmode > 0:
				self.showprobe()
			self.lastx = None
			self.lasty = None
				

		x = self.x
		y = self.y
		if self.drift:
			dt = t - self.drift;
			d = self.drift_amp * \
				math.sin(self.drift_freq * 2.0 * math.pi * dt / 1000.)

			# This was WRONG. Not sure why it ever worked!!!
			#y = y + d * math.sin(-math.pi * (90. + self.a) / 180.)
			#x = x + d * math.cos(-math.pi * (90. + self.a) / 180.)
			
			# This should now be correct:
			y = y + d * math.sin(math.pi * self.a / 180.)
			x = x + d * math.cos(math.pi * self.a / 180.)

		if self.jitter:
			x = x + (2 * uniform(-3, 3, integer=1))
			y = y + (2 * uniform(-3, 3, integer=1))


		if self.on and self.live:
			if self.lastx != x or self.lasty != y:
				# only actually blit if new sprite or it moved
				self.s.on()
				self.s.moveto(x, y)
				self.s.blit()
				self.lastx = x
				self.lastx = y
		else:
			self.s.off()

		(x, y) = self.app.udpy.fb2can(x, y)
		l2 = self.length / 2.0
		_tsin = l2 * math.sin(math.pi * (270.0 - self.a) / 180.0)
		_tcos = l2 * math.cos(math.pi * (270.0 - self.a) / 180.0)
		y1 = y + _tsin
		x1 = x + _tcos
		y2 = y - _tsin
		x2 = x - _tcos
		xx1 = x - l2
		xx2 = x + l2
		yy1 = y - l2
		yy2 = y + l2
			
		if self.l:
			if self.barmode == 0:
				self.app.udpy._canvas.coords(self.l, x1, y1, x2, y2)
			else:
				self.app.udpy._canvas.coords(self.l, xx1, yy1, xx2, yy2)
			self.app.udpy._canvas.coords(self.l2, x1, y1, x2, y2)
		else:
			if self.barmode == 0:
				self.l = self.app.udpy._canvas.create_line(x1, y1, x2, y2)
			else:
				self.l = self.app.udpy._canvas.create_oval(xx1, yy1, xx2, yy2)
			self.l2 = self.app.udpy._canvas.create_line(x1, y1, x2, y2,
														fill='pink', width=2)

		if color:
			fill = "#%02x%02x%02x" % color
		else:
			fill = 'orange'
			
		if self.barmode == 0:
			self.app.udpy._canvas.itemconfigure(self.l, fill=fill,
												width=self.width)
		else:
			self.app.udpy._canvas.itemconfigure(self.l, fill=None,
												width=2)

		if self.on and self.live:
			self.app.udpy._canvas.itemconfigure(self.l2, fill='pink')
		else:
			self.app.udpy._canvas.itemconfigure(self.l2, fill=fill)
		self.app.udpy_note(self.pp())

def _incr(x, by=1, min=1):
	x = x + by
	if x < min:
		return min
	else:
		return x

def _key_handler(app, c, ev):
	p = app.hmapstate.probe

	if c == 'z':
		p.lock = not p.lock
	elif c == 'M':
		p.barmode = (p.barmode + 1) % len(p.barmodes)
		app.udpy._canvas.delete(p.l)
		p.l = None
		app.udpy._canvas.delete(p.l2)
		p.l2 = None
		p.reset()
	elif c == 'bracketleft':
		p.p1 = p.p1 - 0.2
		p.reset()
	elif c == 'bracketright':
		p.p1 = p.p1 + 0.2
		p.reset()
	elif c == 'braceleft':
		p.p2 = round(p.p2 - 1.0)
		p.reset()
	elif c == 'braceright':
		p.p2 = round(p.p2 + 1.0)
		p.reset()
	elif c == 'B':
		p.cblink = not p.cblink
		p.reset()
	elif c == 'b':
		p.blink = not p.blink
		p.blinktime = app.ts()
		if not p.blink:
			p.on = 1
	elif c == 'i':
		p.inten = _incr(p.inten, -1)
		if p.inten < 1: p.inten = 1
		p.reset()
	elif c == 'I':
		p.inten = _incr(p.inten, 1)
		if p.inten > 100: p.inten = 100
		p.reset()
	elif c == 'p':
		p.blinkper = _incr(p.blinkper, -25)
	elif c == 'P':
		p.blinkper = _incr(p.blinkper, 25)
	elif c == 'u':
		p.on = not p.on
	elif c == '1':
		p.colorn = 1-1
		p.reset()
	elif c == '2':
		p.colorn = 2-1
		p.reset()
	elif c == '3':
		p.colorn = 3-1
		p.reset()
	elif c == '4':
		p.colorn = 4-1
		p.reset()
	elif c == '5':
		p.colorn = 5-1
		p.reset()
	elif c == '6':
		p.colorn = 6-1
		p.reset()
	elif c == 'n':
		p.nextcolor(-1)
		p.reset()
	elif c == 'm':
		p.nextcolor(1)
		p.reset()
	elif c == '8':
		p.a = (p.a + 15) % 360
		p.reset()
	elif c == '9':
		p.a = (p.a - 15) % 360
		p.reset()
	elif c == 'q':
		p.length = _incr(p.length, 1)
		p.reset()
	elif c == 'Q':
		p.length = _incr(p.length, 10)
		p.reset()
	elif c == 'w':
		p.length = _incr(p.length, -1)
		if p.length < 2:
			p.length = 2
		if p.width > p.length:
			p.width = p.length-1
		p.reset()
	elif c == 'W':
		p.length = _incr(p.length, -10)
		if p.length < 2:
			p.length = 2
		if p.width > p.length:
			p.width = p.length-1
		p.reset()
	elif c == 'e':
		p.width = _incr(p.width, 1)
		if p.width > p.length:
			p.length = p.width+1
		p.reset()
	elif c == 'E':
		p.width = _incr(p.width, 10)
		if p.width > p.length:
			p.length = p.width+1
		p.reset()
	elif c == 'r':
		p.width = _incr(p.width, -1)
		if p.width < 1:
			p.width = 1
		p.reset()
	elif c == 'R':
		p.width = _incr(p.width, -10)
		if p.width < 1:
			p.width = 1
		p.reset()
	elif c == 'd':
		if p.drift:
			p.drift = 0
		else:
			p.drift = p.app.ts()
	elif c == 'j':
		p.jitter = not p.jitter
	elif c == 'T':
		p.drift_amp = _incr(p.drift_amp, 10, 0)
	elif c == 't':
		p.drift_amp = _incr(p.drift_amp, -10, 0)
	elif c == 'Y':
		p.drift_freq = _incr(p.drift_freq, 0.1, min=0.1)
	elif c == 'y':
		p.drift_freq = _incr(p.drift_freq, -0.1, min=0.1)
	elif c == 'o':
		if app.hmapstate.probe.xoff:
			app.hmapstate.probe.xoff = 0
			app.hmapstate.probe.yoff = 0
		else:
			app.hmapstate.probe.xoff = -100
			app.hmapstate.probe.yoff =  100
		app.udpy.xoffset = app.hmapstate.probe.xoff
		app.udpy.yoffset = app.hmapstate.probe.yoff
	else:
		return 0
	return 1

def _hmap_idlefn(app):
	p = app.hmapstate.probe
	if not p.lock:
		p.x = app.udpy.mousex + app.hmapstate.probe.xoff
		p.y = app.udpy.mousey + app.hmapstate.probe.yoff

	if app.running:
		# if running, then may need to draw fixspot etc..
		if app.hmapstate.dlist:
			app.hmapstate.dlist.update()
		else:
			app.fb.clear()
	p.draw()
	if app.running:
		app.fb.flip()

def hmap_set_dlist(app, dlist):
	app.hmapstate.dlist = dlist

def hmap_show(app, update=None):
	app.hmapstate.probe.live = 1
	if update:
		_hmap_idlefn(app)

def hmap_hide(app, update=None):
	app.hmapstate.probe.live = 0
	if update:
		_hmap_idlefn(app)

def hmap_install(app):
	app.hmapstate = Holder()
	app.hmapstate.dlist = None
	app.hmapstate.probe = _Probe(app)
	app.hmapstate.hookdata = app.set_canvashook(_key_handler, app)
	app.taskidle = _hmap_idlefn

def hmap_uninstall(app):
	app.udpy.xoffset = 0
	app.udpy.yoffset = 0
	app.taskidle = None
	app.hmapstate.probe.save()
	app.hmapstate.probe.clear()
	app.set_canvashook(app.hmapstate.hookdata[0], app.hmapstate.hookdata[1])
	del app.hmapstate
	
if not __name__ == '__main__':
	loadwarn(__name__)
else:
	pass
