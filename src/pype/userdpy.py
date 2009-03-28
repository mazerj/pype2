# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**User display window**

Functions and classes in this module implement the user display
window. This includes all mouse & key inputs, display of shadow
stimuli on the user display (to mirror what the subject sees), etc.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

- Wed Aug 14 13:09:50 2002 mazer

  - removed scrollbar junk: no need, never used it.

- Wed Mar  5 19:26:47 2003 mazer

  - added import points (from ascii file)

- Thu Jun 16 15:20:45 2005 mazer

  - added ben willmore's changes for mac-support

- Sun Jul 24 21:47:12 2005 mazer

  - made fx,fy automatically propagate back to pype.py via self.app.set_fxfy()

- Mon Jan 16 11:18:57 2006 mazer

  - added callback option to the UserDisplay class to support time
    marking from pype.py (see notes in pype.py)

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

import math
import os
import sys
import types
from Tkinter import *
from guitools import *
import Pmw
from pype_aux import lastfile, nextfile, Timestamp
from filebox import Open, SaveAs
from beep import beep


class UserDisplay:
	def __init__(self, master, cwidth=1024, cheight=768,
				 pix_per_dva=1.0, blocked=None, app=None, callback=None):
		"""UserDisplay Class.

		The UserDisplay is a pype local window on the user's computer
		screen that shows a shadow/copy of what the subject is viewing
		plus other useful information and fiduciary marks.

		**master** -- parent window (None for make new toplevel window)

		**cwidth,cheight** -- width and height of framebuffer we're
		shadowing.

		**pix_per_dva** -- pixels per degree visual angle

		**blocked** -- x,y coords of the upper left corner of the *blocked*
		region of the display (blocked by photodiode). This is just marked
		out so the user doesn't forget...

		**app** -- PypeApp handle

		**NOTE:** Just because most of these arguments are keywords
		(and therefore optional), doesn't mean they're not
		required. You should really supply all the parameters to this
		function each time it's called.

		"""

		self.app = app

		if master:
			self.master = master
		else:
			self.master = Toplevel()
			self.master.title('UserDisplay')
			self.master.iconname('UserDisplay')
			if sys.platform == 'darwin':
				self.master.geometry('-0+20')
			else:
				self.master.geometry('-0-0')

			self.visible = 1
			self.master.protocol("WM_DELETE_WINDOW", self.showhide)

		self.frame = Frame(self.master)
		self.frame.pack(expand=1, fill=BOTH)

		# this is used by pype to stick marks in the encode stream
		# for debugging purposes...
		self.callback = callback

		f = Frame(self.frame)
		f.pack(expand=1, fill=X)

		mb = Pmw.MenuBar(f)
		mb.pack(side=LEFT, expand=0, fill=X)
		mb.addmenu('Fidmarks', '', '')
		mb.addmenuitem('Fidmarks', 'command',
					   label='Help', command=self.help)
		mb.addmenuitem('Fidmarks', 'command',
					   label='Clear all marks (C)', command=self._clearfidmarks)
		mb.addmenuitem('Fidmarks', 'command',
					   label='Save (s)', command=self.savefidmarks)
		mb.addmenuitem('Fidmarks', 'command',
					   label='Load (l)', command=self.loadfidmarks)
		mb.addmenuitem('Fidmarks', 'command',
					   label='View (v)', command=self._showfidmarks)

		mb.addmenu('Eyecal', '', '')
		mb.addmenuitem('Eyecal', 'command',
					   label='Clear all points', command=self.clearpoints)
		mb.addmenuitem('Eyecal', 'separator')
		mb.addmenuitem('Eyecal', 'command',
					   label='Load .pts file',
					   command=lambda s=self: s.loadpoints(merge=None))
		mb.addmenuitem('Eyecal', 'command',
					   label='Merge .pts file',
					   command=lambda s=self: s.loadpoints(merge=1))
		mb.addmenuitem('Eyecal', 'command',
					   label='Save .pts file', command=self.savepoints)
		mb.addmenuitem('Eyecal', 'separator')
		mb.addmenuitem('Eyecal', 'command',
					   label='Load ascii file',
					   command=lambda s=self: s.loadpoints_ascii(merge=None))
		mb.addmenuitem('Eyecal', 'command',
					   label='Merge ascii file',
					   command=lambda s=self: s.loadpoints_ascii(merge=1))

		mb.addmenu('Display', '', '')
		self._photomode_tvar = IntVar()
		self._photomode_tvar.set(0)		# photo mode starts up OFF!!
		self._photomode = self._photomode_tvar.get()
		mb.addmenuitem('Display', 'checkbutton',
					   label='Photo mode', command=self._phototoggle,
					   variable=self._photomode_tvar)

		mb.addmenuitem('Display', 'command',
					   label='clear trace',
					   command=lambda s=self: s.eye_clear())

		mb.addmenu('Help', '', '')
		mb.addmenuitem('Help', 'command',
					   label='show shortcuts', command=self.help)


		self.scount = Button(f, text="<>", command=self.showsprites)
		self.scount.pack(side=RIGHT)

		self.info = Label(f, text="", fg='red')
		self.info.pack(side=RIGHT, padx=20)

		self._stopbutton = Button(f, bg='red', fg='white', text='STOP')
		self._stopbutton.pack(side=RIGHT, padx=20)
		self._stopbutton.forget()

		self._canvas = Canvas(self.frame)
		self._canvas.pack()
		self._canvas.configure(width=cwidth, height=cheight,
							   cursor='tcross', bg='grey80')

		f = Frame(self.frame)
		f.pack(expand=1, side=BOTTOM, fill=X)

		self.xypos = Label(f, text="")
		self.xypos.pack(side=LEFT)
		self._mouse_motion(ev=None)

		self.gridinterval = pix_per_dva
		l = Label(f, text="%d pix/div" % self.gridinterval)
		l.pack(side=RIGHT)

		self.mousex = 0
		self.mousey = 0
		self.xoffset = 0
		self.yoffset = 0

		self.popup = Menu(self._canvas, tearoff=0)

		self.popup.add_command(label="User Display Menu")
		self.popup.add_command(label="Fixspot here",
							   command=self._fixset)
		self.popup.add_command(label="Set fixspot to (0,0)",
							   command=self._fixzero)
		self.popup.add_command(label="Enter fixspot coords",
							   command=self._fixxy)
		self.popup.add_command(label="Set a box corner (/)",
							   command=self.setbox)
		self.popup.add_command(label="Clear box",
							   command=self.clearbox)
		self._canvas.bind("<Button-1>", self.do_popup)

		self._canvas.bind("<Motion>", self._mouse_motion)
		self._canvas.bind("<Enter>", self._mouse_enter)
		self._canvas.bind("<Leave>", self._mouse_leave)
		self._canvas.bind("<KeyPress>", self._key)
		self._canvas.pack(expand=0)
		self._iconlist = []
		self._displaylist_icons = []
		self._fid_list = []
		self._fidstuff = []
		self._axis = []
		self.markstack = []
		self.markbox = None

		self.w = int(self._canvas.configure("width")[4])
		self.h = int(self._canvas.configure("height")[4])
		self.w2 = int(round(self.w / 2.0))
		self.h2 = int(round(self.h / 2.0))

		self._blocked = blocked
		self._axis = []
		self._drawaxis(0, 0, self.w, self.h)

		self._eye_trace = []
		self._eye_trace_maxlen = 50
		self._eye_lx = None
		self._eye_ly = None

		self.fix_x = 0
		self.fix_y = 0
		self.eye = self._canvas.create_rectangle(0, 0, 0, 0,
												 fill="black", outline="")

		self.userhook = None
		self.userhook_data = None

		self.eye_clear()
		self.eye_at(0,0)

		self.points = []

		self.msg_label = None
		self.msg_win = None

		self.set_taskpopup()

		self.bind_but3(fn=None, arg=None)
		self._canvas.bind("<Button-3>", self.invoke_but3)

	def showhide(self):
		if self.visible:
			self.master.withdraw()
			self.visible = 0
		else:
			self.master.deiconify()
			self.visible = 1

	def stop(self, command=None):
		if command:
			self._stopbutton.configure(command=command)
			self._stopbutton.pack()
		else:
			self._stopbutton.forget()
			self._stopbutton.configure(command=None)

	def note(self, msg):
		if msg is None or len(msg) == 0:
			if self.msg_win:
				self._canvas.delete(self.msg_win)
				self.msg_win = None
			if self.msg_label:
				self.msg_label.destroy()
				self.msg_label = None
		else:
			if self.msg_win is None:
				font = "-*-lucidatypewriter-medium-r-normal-*-12-*-*-*-*-*-*-*"
				f = Frame(self._canvas, borderwidth=1)
				self.msg_win = self._canvas.create_window(5, 25,
													  window=f, anchor=NW)
				self.msg_label = Label(f, text=msg, font=font, justify=LEFT,
									   bg=None, fg='black')
				self.msg_label.pack()
				self._placenote()
			else:
				self.msg_label.configure(text=msg)


	def _placenote(self, x=None, y=None):
		if self.msg_win is None:
			return
		if x is None:
			x = int(self.app.rig_common.queryv('note_x'))
		if y is None:
			y = int(self.app.rig_common.queryv('note_y'))
		self._canvas.coords(self.msg_win, x, y)
		self.app.rig_common.set('note_x', x)
		self.app.rig_common.set('note_y', y)

	def help(self):
		warn('help',
			 "Fiduciary marks (aka fidmarks)\n"+
			 "-----------------------------------------\n"+
			 "Arrows  Move all fidmarks left, right etc\n"+
			 "f  Set fidmark at cursor\n"+
			 "<  Shrink fidmarks in\n"+
			 ">  Expand fidmarks out\n"+
			 "c/C  Clear nearest-one/all fidmark(s)\n"+
			 "s  Save fidmarks to file\n"+
			 "l  Load fidmarks from file\n"+
			 "\n"+
			 "Eyecal marks\n"+
			 "-----------------------------------------\n"+
			 ".  Set eyecal point (period) at cursor\n"+
			 ",  Delete nearest eyecal point (comma)\n"+
			 "\n"+
			 "Other\n"+
			 "-----------------------------------------\n"+
			 "/  Mark box corner (twice to set box)\n"+
			 "x  postion message window at cursor\n"+
			 "L-mouse access fixspot menu\n"+
			 "M-mouse access task-specific dropdown\n"+
			 "R-mouse simulate bar up/down",
			 fixed=1, astext=1)

	def deltags(self, taglist):
		for tag in taglist:
				self._canvas.delete(tag)
		return []

	def eye_clear(self, autotrace=None):
		"""Note: autotrace does NOTHING."""
		self._eye_trace = self.deltags(self._eye_trace)
		self._eye_trace = []

		self._eye_lx = None
		self._eye_ly = None

	def eye_at(self, x, y):
		sz = 3
		(x, y) = self.fb2can(x, y)
		if x < -self.w2 or x > self.w2 or y < -self.h2 or y > self.h2:
			sx = 2 * sz

		# elif self._eye_lx != x or self._eye_ly != y:
		if (self._eye_lx is None) or (self._eye_ly is None):
			pass
		else:
			tag = self._canvas.create_line(self._eye_lx, self._eye_ly, x, y,
										   fill="red")
			self._eye_trace.append(tag)
			if len(self._eye_trace) > self._eye_trace_maxlen:
				self._canvas.delete(self._eye_trace[0])
				del self._eye_trace[0]
		self._eye_lx = x
		self._eye_ly = y
		self._canvas.coords(self.eye, x-sz, y-sz, x+sz, y+sz);

		from sprite import Sprite
		self.scount.config(text="%d sprites" % len(Sprite.__list__))


	def showsprites(self):
		from sprite import Sprite
		for n in range(0, len(Sprite.__list__)):
			Logger('%d: "%s"\n' % (n, Sprite.__list__[n]))

	def fb2can(self, x, y=None):
		"""convert frame buffer coords to canvas coords"""
		if y is None:
			(x, y) = x
		return (self.w2 + x, self.h2 - y)

	def can2fb(self, x, y):
		"""convert canvas/event coords to frame buffer coords"""
		if y is None:
			(x, y) = x
		return(x - (self.w2), (self.h - y) - self.h2)

	def _drawaxis(self, x, y, cw, ch):
		cardinal = 'yellow'
		major = 'grey50'
		minor = 'grey75'
		r = 20 * self.gridinterval;

		if self._blocked:
			(x1, y1) = self.fb2can(self._blocked[0], self._blocked[1])
			self._canvas.create_line(x1, ch, x1, y1, width=3, fill='black')
			self._canvas.create_line(x1, y1, cw, y1, width=3, fill='black')

		n = 0
		for i in range(0, 20):
			xx = self.gridinterval * i
			(x1, y1) = self.fb2can(xx, 0)
			(x2, y2) = self.fb2can(-xx, 0)
			if xx == 0:
				self._axis.append(
					self._canvas.create_line(x1, 0, x1, ch,
											 width=2, fill=cardinal))
			elif n == 0:
				self._axis.append(
					self._canvas.create_line(x1, 0, x1, ch,
											 width=1, fill=major))
				self._axis.append(
					self._canvas.create_line(x2, 0, x2, ch,
											 width=1, fill=major))
			else:
				self._axis.append(
					self._canvas.create_line(x1, 0, x1, ch,
											 width=1, fill=minor))
				self._axis.append(
					self._canvas.create_line(x2, 0, x2, ch,
											 width=1, fill=minor))
			n = (n + 1) % 5

		n = 0
		for i in range(0, 20):
			yy = self.gridinterval * i
			(x1, y1) = self.fb2can(0, yy)
			(x2, y2) = self.fb2can(0, -yy)
			if yy == 0:
				self._axis.append(
					self._canvas.create_line(0, y1, cw, y1,
											 width=2, fill=cardinal))
			elif n == 0:
				self._axis.append(
					self._canvas.create_line(0, y1, cw, y1,
											 width=1, fill=major))
				self._axis.append(
					self._canvas.create_line(0, y2, cw, y2,
											 width=1, fill=major))
			else:
				self._axis.append(
					self._canvas.create_line(0, y1, cw, y1,
											 width=1, fill=minor))
				self._axis.append(
					self._canvas.create_line(0, y2, cw, y2,
											 width=1, fill=minor))
			n = (n + 1) % 5

	def clearbox(self):
		self.setbox(clear=1)

	def setbox(self, clear=None):
		if clear is None:
			# mouse position in retinal coords (re fixspot)
			mx = self.mousex + self.xoffset - self.fix_x
			my = self.mousey + self.yoffset - self.fix_y
			self.markstack.append((mx, my))
			self.markstack = self.markstack[-2:]
		else:
			self.markstack = []
		self.drawbox()

	def drawbox(self):
		if self.markbox:
			self._canvas.delete(self.markbox)
			self.markbox = None
		if len(self.markstack) == 1:
			x1, y1 = self.markstack[0][0], self.markstack[0][1]
			x1 = self.fix_x + x1
			y1 = self.fix_y + y1
			x1,y1 = self.fb2can(x1, y1)
			self.markbox = self._canvas.create_rectangle(x1-1,y1-1,x1+1,y1+1,
														 fill='black',
														 outline="black")
		elif len(self.markstack) == 2:
			x1, y1 = self.markstack[0][0], self.markstack[0][1]
			x1 = self.fix_x + x1
			y1 = self.fix_y + y1
			x1,y1 = self.fb2can(x1, y1)

			x2, y2 = self.markstack[1][0], self.markstack[1][1]
			x2 = self.fix_x + x2
			y2 = self.fix_y + y2
			x2,y2 = self.fb2can(x2, y2)

			self.markbox = self._canvas.create_rectangle(x1,y1,x2,y2,
														 fill=None,
														 outline="red",
														 dash=(5,5))

	def _key(self, ev):
		c = ev.keysym
		# NOTE:
		#  state == 0 --> no modifier
		#  state == 4 --> control key
		if ev.state == 0 and c == 'Left':
			self._movefidmarks(xoff=-1, yoff=0)
		elif ev.state == 0 and c == 'Right':
			self._movefidmarks(xoff=1, yoff=0)
		elif ev.state == 0 and c == 'Up':
			self._movefidmarks(xoff=0, yoff=1)
		elif ev.state == 0 and c == 'Down':
			self._movefidmarks(xoff=0, yoff=-1)
		elif ev.state == 4 and c == 'Left':
			# control-left
			self.app.eyeshift(x=1,y=0)
		elif ev.state == 4 and c == 'Right':
			# control-right
			self.app.eyeshift(x=-1,y=0)
		elif ev.state == 4 and c == 'Up':
			# control-up
			self.app.eyeshift(x=0,y=-1)
		elif ev.state == 4 and c == 'Down':
			# control-down
			self.app.eyeshift(x=0,y=1)
		elif c == 'less':
			self._scalefidmarks(-1)
		elif c == 'greater':
			self._scalefidmarks(1)
		if c == 'f':
			self._putfidmark()
		elif c == 'c':
			self._clearfidmark()
		elif c == 'C':
			self._clearfidmark(all=1)
		elif c == 's':
			self.savefidmarks()
		elif c == 'l':
			self.loadfidmarks()
		elif c == 'x':
			self._placenote(ev.x, ev.y)
		elif c == 'v':
			self._showfidmarks()
		elif c == 'h':
			self.help()
		elif c == 'period':
			self.addpoint(ev.x, ev.y)
		elif c == 'comma':
			self.deletepoint(ev.x, ev.y)
		elif c == 'slash':
			self.setbox()
		elif c == 'equal' and self.callback:
			self.callback(c, ev)
		elif not self.userhook is None:
			return self.userhook(self.userhook_data, c, ev)
		else:
			# print ev,ev.keysym,ev.state
			pass
		return 1

	def addpoint(self, x, y):
		"""(x, y) specifies point in CANVAS coords (0,0) is upper left"""
		(px, py) = (int(round(x - (self.w/2.0))), int(round((self.h/2.0) - y)))
		d = 2;
		t = self._canvas.create_text(x, y, anchor=CENTER, justify=CENTER, \
									 text='e', fill='blue')
		self.points.append((px, py, t))

	def deletepoint(self, x, y):
		"""
		Delete nearest point to (x, y) in CANVAS coords.
		(0,0) is upper left.
		"""
		px = int(round(x - (self.w/2.0)))
		py = int(round((self.h/2.0)) - y)
		nearest = None
		for n in range(len(self.points)):
			(x, y, t) = self.points[n]
			d = (px - x) ** 2 + (py - y) ** 2
			if n == 0 or d < dmin:
				dmin = d
				nearest = n
		if not nearest is None:
			(x, y, t) = self.points[nearest]
			self._canvas.delete(t)
			self.points.remove(self.points[nearest])
		else:
			beep(4000, 10)

	def querypoint(self, x, y):
		"""
		Identify nearest point to (x, y) in CANVAS coords.
		(0,0) is upper left.
		"""
		px = int(round(x - (self.w/2.0)))
		py = int(round((self.h/2.0) - y))
		nearest = None
		for n in range(len(self.points)):
			(x, y, t) = self.points[n]
			d = (px - x) ** 2 + (py - y) ** 2
			if n == 0 or d < dmin:
				dmin = d
				nearest = n
		if not nearest is None:
			return (x, y)
		else:
			return (None, None)

	def clearpoints(self):
		"""Clear all points"""
		for n in range(len(self.points)):
			(x, y, t) = self.points[n]
			self._canvas.delete(t)
		self.points = []

	def savepoints(self, filename=None):
		"""Save points to file"""
		import cPickle
		if filename is None:
			from filebox import SaveAs
			from pype import subjectrc
			(filename, mode) = SaveAs(initialdir=subjectrc(),
									  pattern="*.pts", append=None)
		if filename:
			file = open(filename, 'w')
			cPickle.dump(self.points, file)
			file.close()

	def loadpoints(self, filename=None, merge=None):
		"""Load points from file (pickle file make by savepoints)"""
		import cPickle
		if filename is None:
			from filebox import Open
			from pype import subjectrc
			(filename, mode) = Open(initialdir=subjectrc(),
									pattern="*.pts")
			if filename is None:
				return
		try:
			file = open(filename, 'r')
			newpoints = cPickle.load(file)
			file.close()
		except IOError:
			return
		except EOFError:
			return

		if not merge:
			self.clearpoints()

		for n in range(len(newpoints)):
			(px, py, t) = newpoints[n]
			x = int(round(px + (self.w/2.0)))
			y = int(round((self.h/2.0) - py))
			self.addpoint(x, y)

	def loadpoints_ascii(self, filename=None, merge=None):
		"""
		Load points from ascii file.
		One point per line containing X and Y position in
		pixels separated by commas or spaces
		"""
		import string

		if filename is None:
			from filebox import Open
			from pype import subjectrc
			(filename, mode) = Open(initialdir=subjectrc(),
									pattern="*.asc")
			if filename is None:
				return
		try:
			fp = open(filename, 'r')
		except IOError:
			return

		if not merge:
			self.clearpoints()

		while 1:
			l = fp.readline()
			if not l:
				break
			if string.find(l, ',') >= 0:
				l = string.split(l, ",")
			else:
				l = string.split(l)
			px = int(l[0])
			py = int(l[1])
			x = int(round(px + (self.w/2.0)))
			y = int(round((self.h/2.0) - py))
			self.addpoint(x, y)
		fp.close()

	def getpoints(self):
		"""
		Get vector of points in proper SCREEN/WORLD coords.
		(0,0) is center of the screen!!
		"""
		points = []
		for n in range(len(self.points)):
			(x, y, t) = self.points[n]
			points.append((x, y))
		return points

	def _phototoggle(self):
		self._photomode = self._photomode_tvar.get()

	def _mouse_motion(self, ev=None):
		if ev is None:
			# for initialization ONLY...
			(x, y, fx, fy) = (0, 0, 0, 0)
		else:
			(self.mousex, self.mousey) = self.can2fb(ev.x, ev.y)
			(x, y, fx, fy) = (self.mousex, self.mousey, self.fix_x, self.fix_y)
		s = "[%4d,%4d][rel %4d,%4d]" % (x, y, x-fx, y-fy)
		self.xypos.configure(text=s)

	def _mouse_enter(self, ev):
		self._canvas.focus_set()

	def _mouse_leave(self, ev):
		pass

	def display(self, displaylist=None):
		"""
		Autmoatically-draw a DisplayList object as a set of icons on the
		UserDisplay (faster than exact copies).

		**displaylist** -- DisplayList or None for clear all.

		"""

		# first clear previsou displaylist icons
		for icon in self._displaylist_icons:
			self.icon(icon)

		if displaylist is None:
			return

		self._displaylist_icons = []
		if not displaylist is None:
			for s in displaylist.sprites:
				if s._on:
					try:
						# is it a PolySprite?
						xy = s.screen_points;
						for n in range(1,len(xy)):
							(x0, y0) = self.fb2can(xy[n-1])
							(x1, y1) = self.fb2can(xy[n])
							i = self._canvas.create_line(x0, y0,
														 x1, y1,
														 width=s.width,
														 fill='black')
							self._displaylist_icons.append(i)
					except AttributeError:
						# otherwise... plain old sprite
						if self._photomode:
							(x, y) = self.fb2can(s.x-(s.w/2), s.y+(s.h/2))
							if s.w < 300 and s.h < 300:
								i = self._canvas.create_image(x, y, anchor=NW,
													  image=s.asPhotoImage())
							else:
								i = self.icon(s.x, s.y,
											  s.iw, s.ih, color=s.icolor)
						else:
							i = self.icon(s.x, s.y,
										  s.iw, s.ih, color=s.icolor)
						self._displaylist_icons.append(i)

	def icon(self, x=None, y=None, w=5, h=5, \
			 sym=None, color='black', type=1, dash=None):
		if y is None and x is None:
			self._iconlist = self.deltags(self._iconlist)
		elif y is None:
			# just delete x from iconlist
			self._canvas.delete(x)
		else:
			# create an icon
			(x, y) = self.fb2can(x, y)

			w = w / 2
			h = h / 2
			if not sym is None:
				txt = self._canvas.create_text(x, y-(1.5*h),
											   text=sym, fill='red',
											   dash=dash)
				self._iconlist.append(txt)
			if type == 1:
				tag = self._canvas.create_rectangle(x-w, y-h, x+w, y+h,
													fill='', outline=color,
													dash=dash)
			elif type == 2:
				tag = self._canvas.create_oval(x-w, y-h, x+w, y+h,
											   fill='', outline=color,
											   dash=dash)
			self._iconlist.append(tag)
			return tag

	def texticon(self, x=None, y=None, text=None, color='black'):
		if y is None and x is None:
			self._iconlist = self.deltags(self._iconlist)
		elif y is None:
			# just delete x from iconlist
			self._canvas.delete(x)
		else:
			# create an icon
			(x, y) = self.fb2can(x, y)
			tag = self._canvas.create_text(x, y, text=text, fill=color)
			self._iconlist.append(tag)
			return tag

	def _showfidmarks(self):
		s = ''
		n = 0
		for mark in self._fid_list:
			if mark:
				(tag, x, y) = mark
				s = s + ( '%3d%6d%6d\n' % (n, x, y) )
				n = n + 1
		if len(s) > 0:
			s = '### .XPOS. .YPOS.\n' + s + '\n'
		(xs, ys, r) = self.fidinfo()
		s = s + 'CTR=(%d,%d) R=%.1f px (%.1f deg)\n' % (xs, ys, r,
														r/self.gridinterval)
		s = s + 'ECC=%d px (%.1f deg)\n' % \
			(math.sqrt((xs * xs) + (ys * ys)),
			 math.sqrt((xs * xs) + (ys * ys)) / self.gridinterval)

		s = s + 'FIX=(%d, %d)\n' % (self.fix_x, self.fix_y)
		s = s + '>>> COORDS ARE RE:FIX <<<\n'

		warn('fidmarks', s, fixed=1, astext=1)


	def fidinfo(self, file=None):
		for f in self._fidstuff:
			try:
				self._canvas.delete(f)
			except AttributeError:
				pass
		self._fidstuff = []

		n = 0
		xs = 0.
		ys = 0.
		r = 0.
		for f in self._fid_list:
			if not f is None:
				(tag, x, y) = f
				xs = xs + x;
				ys = ys + y;
				n = n + 1
		if n > 0:
			xs = int(xs / n)
			ys = int(ys / n)
			r = 0.
			for f in self._fid_list:
				if not f is None:
					(tag, x, y) = f
					r = r + math.sqrt((xs - x) * (xs - x) + (ys - y) * (ys - y))
			r = int(r / n)

		if n > 1:
			_xs = self.fix_x + xs
			_ys = self.fix_y + ys
			(cx, cy) = self.fb2can(_xs, _ys)
			self._fidstuff = (
				self._canvas.create_text(cx, cy, anchor=CENTER, justify=CENTER,
										 fill='blue', text='o'),
				self._canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
										 fill='', outline='blue',
										 dashoffset=0,
										 dash=(10,10)),
				self._canvas.create_line(cx, cy-r, cx, cy+r, fill='blue',
										 dash=(10,10)),
				self._canvas.create_line(cx-r, cy, cx+r, cy, fill='blue',
										 dash=(10,10)),
				)
		if file:
			fp = open(file, 'w')
			fp.write('%% %s\n' % Timestamp())
			fp.write('% fiduciary mark data\n')
			fp.write('%\n')
			fp.write('% fix position (x,y) in framebuf coords:\n')
			fp.write('f\t%d\t%d\n' % (self.fix_x, self.fix_y))
			fp.write('% fids (x,y) in framebuf coords:\n')
			n = 0;
			for f in self._fid_list:
				if not f is None:
					(tag, x, y) = f
					fp.write('p\t%d\t%d\t%d\n' % (n, x, y))
					n = n + 1
			fp.write('%\n')
			fp.write('% rf center (x, y) framebuf coords + rad (pix):\n')
			fp.write('r\t%d\t%d\t%f\n' % (xs, ys, r))
			if len(self.markstack) > 0:
				fp.write('% markstack points (pix):\n')
				for n in range(len(self.markstack)):
					fp.write('m\t%d\t%d\t%d\n' % (n,
												  self.markstack[n][0],
												  self.markstack[n][1]))
			fp.close()

		return (xs, ys, r)

	def loadfidmarks(self, file=None):
		from string import split
		if file is None:
			(file, mode) = Open(initialdir=os.getcwd(),
								pattern='*.fid')
		if not (file is None):
			self._clearfidmarks()
			fp = open(file, 'r')
			while 1:
				l = fp.readline()
				if not l: break
				if l[0] == 'f':
					(foo, x, y) = split(l)
					self._fixset(x=int(x), y=int(y))
				elif l[0] == 'p':
					(foo, n, x, y) = split(l)
					self._putfidmark(int(x), int(y), update=0)
				if l[0] == 'm':
					(foo, n, x, y) = split(l)
					self.markstack.append((int(x), int(y)))
					self.markstack = self.markstack[-2:]
					self.drawbox()
			fp.close()
			self.fidinfo()

	def savefidmarks(self, file=None):
		if self.app:
			if self.app.use_elog:
				import elogapi
				animal = self.app.sub_common.queryv('subject')
				initf = "%s.fid" % (elogapi.GetExper(animal), )
			else:
				subj = self.app.sub_common.queryv('subject')
				cell = self.app.sub_common.queryv('cell')
				try:
					initf = "%s%04d.fid" % (subj, int(cell))
				except ValueError:
					initf = "%s%s.fid" % (subj, cell)
		else:
			initf=nextfile('marks.%04d.fid')

		if file is None:
			(file, mode) = SaveAs(initialdir=os.getcwd(),
								  pattern='*.fid',
								  initialfile=initf,
								  append=None)

		if not (file is None):
			self.fidinfo(file=file)

	def _redrawfidmarks(self):
		l = self._fid_list
		self._clearfidmarks()
		for mark in l:
			if mark:
				(tag, x, y) = mark
				self._putfidmark(mx=x, my=y, update=0)
		self.fidinfo()

	def _putfidmark(self, mx=None, my=None, update=1):
		if (mx is None) or (my is None):
			# convert current mouse position to retinal coords
			mx = self.mousex + self.xoffset - self.fix_x
			my = self.mousey + self.yoffset - self.fix_y

		# draw mark at absolute screen coords:
		ax = mx + self.fix_x
		ay = my + self.fix_y
		(cx, cy) = self.fb2can(ax, ay)
		tag = self._canvas.create_text(cx, cy, anchor=CENTER, justify=CENTER,
									   fill='black', text='f')

		# save mark in retinal coords
		self._fid_list.append((tag, mx, my))
		if update:
			self.fidinfo()
		return tag

	def _clearfidmarks(self):
		self._clearfidmark(all=1)

	def _clearfidmark(self, all=None):
		if all is None:
			d1 = None
			ix = None
			n = 0
			for i in self._fid_list:
				if not i is None:
					mx = self.mousex + self.xoffset
					my = self.mousey + self.yoffset
					# remember: coords are stored re:fix
					# so convert mx,my to re:fix
					mx = mx - self.fix_x
					my = my - self.fix_y
					(tag, x, y) = i
					if d1 is None:
						ix = n
						d1 = (mx - x) * (mx - x) + (my - y) * (my - y)
					else:
						d2 = (mx - x) * (mx - x) + (my - y) * (my - y)
						if d2 < d1:
							ix = n
							d1 = d2
				n = n + 1

			if not d1 is None:
				(tag, x, y) = self._fid_list[ix]
				self._canvas.delete(tag)
				self._fid_list[ix] = None
		else:
			for i in self._fid_list:
				if not i is None:
					tag = i[0]
					self._canvas.delete(tag)
			self._fid_list = []
		self.fidinfo()

	def _movefidmarks(self, xoff, yoff):
		x = self._fid_list[:]
		self._clearfidmarks()
		for mark in x:
			if mark:
				(tag, x, y) = mark
				self._putfidmark(x + xoff, y + yoff, update=0)
		self.fidinfo()

	def _scalefidmarks(self, delta):
		(xc, yc, r) = self.fidinfo()
		x = self._fid_list[:]
		self._clearfidmarks()
		for mark in x:
			if mark:
				(tag, x, y) = mark
				r = math.sqrt((x - xc)**2 + (y - yc)**2)
				t = math.atan2((y - yc), (x - xc))
				r = r + delta
				x = xc + (r * math.cos(t));
				y = yc + (r * math.sin(t));
				self._putfidmark(x, y, update=0)
		self.fidinfo()

	def _fixset(self, x=None, y=None):
		if x is None or y is None:
			x, y = self.mousex, self.mousey
		try:
			self._canvas.delete(self._fixtag)
		except AttributeError:
			pass
		self.fix_x = x
		self.fix_y = y
		if (not x is None) and (not y is None):
			(x, y) = self.fb2can(x, y)
			self._fixtag = self._canvas.create_rectangle(x-5, y-5, x+5, y+5,
														 fill='',
														 outline='blue')
		self._redrawfidmarks()
		self.drawbox()

		# automatically update application's fixspot location info
		if self.app:
			self.app.set_fxfy()

	def _fixzero(self, ev=None):
		self._fixset(x=0, y=0)

	def _fixxy(self, ev=None):
		from tkSimpleDialog import askstring
		from string import split

		s = askstring('fixspot', 'new fixspot:',
					  initialvalue='%d,%d' % (self.fix_x, self.fix_y))
		if s:
			s = split(s, ',')
			if len(s) == 2:
				self._fixset(x=int(s[0]), y=int(s[1]))

	def set_taskpopup(self, menu=None):
		if menu is None:
			self.taskpopup = Menu(self._canvas, tearoff=0)
			self.taskpopup.add_command(label="No taskpopup")
		else:
			self.taskpopup = menu
		self._canvas.bind("<Button-2>", self.do_taskpopup)

	def do_taskpopup(self, event):
		try:
			self.taskpopup.tk_popup(event.x_root, event.y_root, 0)
		finally:
			self.taskpopup.grab_release()

	def do_popup(self, event):
		try:
			self.popup.tk_popup(event.x_root, event.y_root, 0)
		finally:
			self.popup.grab_release()

	def bind_but3(self, fn=None, arg=None):
		self.but3_fn = fn
		self.but3_arg = arg

	def invoke_but3(self, event):
		if self.but3_fn:
			self.but3_fn(self.but3_arg, event)

class FID:
	def __init__(self, file=None):
		self.fx, self.fy = 0, 0
		self.cx, self.cy, self.r = 0, 0, 0
		self.x = []
		self.y = []
		self.file = None
		if file:
			self._load(file)
			self.file = file

	def _load(self, file):
		from string import split

		f = open(file, 'r')
		while 1:
			l = f.readline()
			if not l:
				break
			if l[0] == 'f':
				(foo, x, y) = split(l)
				self.fx = int(x)
				self.fy = int(y)
			elif l[0] == 'p':
				(foo, n, x, y) = split(l)
				self.x.append(int(x))
				self.y.append(int(y))
			elif l[0] == 'r':
				(foo, cx, cy, r) = split(l)
				self.cx = float(cx)
				self.cy = float(cy)
				self.r = float(r)
		f.close()

if __name__ == '__main__':
	from Tkinter import *
	tk = Tk()
	bb = BlackBoard(tk, 100, 100)
	bb.frame.pack()
	tk.mainloop()
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
