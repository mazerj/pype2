# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$
"""
**Assorted GUI-related functions**

Useful Tkinter and Pmw utility functions for GUI building
nd running. Things that get repeated over and over again
in the main pype code eventually end up here for
onsolidation.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Wed Apr  8 21:42:18 1998 mazer

- created

Thu Jan 27 15:27:15 2000 mazer

- added DockWindow class

Mon Jun 25 12:21:40 2007 mazer

- Container() class is obsolete... deleted it..

- Added SimpleDialog() class to replace use of the Tk builtin Dialog
  class (which is opaque and unchangable). This is much simpler..

Thu Jun 28 10:41:43 2007 mazer

- Switched use of ScrolledText to Pmw.ScrolledText -- didn't realize
  there was a Tkinter version (that doesn't properly resize!). Hmmm,
  actually this is a problem -- doesn't work for Tally window, so I
  reverted back to Tkinter's version..

"""

from Tkinter import *
import Pmw
import pypeversion

class DockWindow(Toplevel):
	"""
	This is a toplevel window class that's customized with
	hide/show functions so you can bind it's appearance to
	a button..
	"""
	def __init__(self, checkbutton=None, title=None, iconname=None, **kw):
		apply(Toplevel.__init__, (self,), kw)

		if title:
			self.title(title)

		if iconname:
			self.iconname(iconname)
		elif title:
			self.iconname(title)

		if checkbutton:
			self._checkbutton = checkbutton
			self._v = IntVar()
			self._checkbutton.configure(command=self.toggle, variable=self._v)
		else:
			self._checkbutton = None

		# first time: open window up in upper left corner
		# of parent..
		parent = self._nametowidget(self.winfo_parent())
		self.geometry("350x350+%d+%d" % (parent.winfo_rootx()+50,
								  parent.winfo_rooty()+50))


		self.protocol("WM_DELETE_WINDOW", self._hide)
		self.withdraw()

		self._visible = 0
		self._geom = None

	def _hide(self):
		self._geom = self.geometry()
		self.withdraw()
		self._visible = 0
		if self._checkbutton:
			self._v.set(self._visible)

	def _show(self):
		if self._geom:
			self.geometry(self._geom)
		self.deiconify()
		self._visible = 1
		if self._checkbutton:
			self._v.set(self._visible)

	def toggle(self):
		if self._visible:
			self._hide()
		else:
			self._show()

class TaskNotebook(DockWindow):
	def __init__(self, **options):
		apply(DockWindow.__init__, (self,), options)

		notebook = Pmw.NoteBook(self)
		notebook.pack(expand=1, fill=BOTH)
		self.notebook = notebook
		notebook.setnaturalsize(pageNames=None)
		
	def add(self, name, label):
		return self.notebook.add(label)

	def lift(self, name):
		self.notebook.lift(name)

class Logger:
	logwindow = None
	buffered = []
	msgs = {}
	def __init__(self, text=None, window=None, popup=None, once=None):
		import time

		if once:
			if Logger.msgs.has_key(text):
				return
			else:
				Logger.msgs[text] = 1

		if not text is None:
			(year, month, day,
			 hour, min, sec, x1, x2, x3) = time.localtime(time.time())
			text = '%02d:%02d:%02d -- %s' % (hour, min, sec, text)
		
		if window:
			Logger.logwindow = window
			# push buffered output into log window
			for s in Logger.buffered:
				Logger.logwindow.write(s)
			Logger.buffered = []
		else:
			if Logger.logwindow:
				Logger.logwindow.write(text)
			else:
				Logger.buffered.append(text)
			sys.stderr.write(text)
			sys.stderr.flush()
			
		if popup:
			warn('Logger', text)

class ConsoleWindow(Toplevel):
	def __init__(self, title='ConsoleWindow', iconname='Console',
				 font="-*-lucidatypewriter-medium-r-*-*-12-*-*-*-*-*-*-*",
				 bg='gray75', **kw):
		
		apply(Toplevel.__init__, (self,), kw)
		if title:
			self.title(title)
		if iconname:
			self.iconname(iconname)
		
		f = Frame(self)
		f.pack(expand=1, fill=BOTH)
		
		self.ptext = Pmw.ScrolledText(f)
		self.ptext.pack(expand=1, side=TOP, fill=BOTH)
		self.text = self.ptext.component('text')
		self.text.config(state=DISABLED, font=font, bg=bg, height=10)
		
		clear = Button(f, text='clear', command=self.clear)
		clear.pack(expand=0, side=TOP, anchor=W)

		self.visible = 1
		self.protocol("WM_DELETE_WINDOW", self.showhide)

	def write(self, str):
		self.text.config(state=NORMAL)
		self.text.insert(END, str)
		self.text.config(state=DISABLED)
		self.text.update()
		self.text.see(END)

	def clear(self):
		self.text.config(state=NORMAL)
		self.text.delete(0.0, END)
		self.text.config(state=DISABLED)

	def showhide(self):
		if self.visible:
			self.withdraw()
			self.visible = 0
		else:
			self.deiconify()
			self.visible = 1

class SimpleDialog(Toplevel):
	def __init__(self, msg, responses=('Ok',), default=None,
				 astext=None, title=None, iconname=None, grab=1,
				 **kw):

		apply(Toplevel.__init__, (self,), kw)

		if title:
			self.title(title)
		if iconname:
			self.iconname(iconname)

		self.parent = self._nametowidget(self.winfo_parent())
		
		self.transient(self.parent)
		
		f = Frame(self, relief=GROOVE, borderwidth=3)
		f.pack(side=TOP, expand=1, fill=BOTH)
		
		if astext:
			# use text box so message is copyable with mouse...
			m = Text(f, relief=RIDGE, borderwidth=3)
			m.insert(END, msg)
		else:
			m = Label(f, text=msg)
			
		m.pack(padx=25, pady=25)
		
		f = Frame(self)
		f.pack(side=TOP, expand=1, fill=X)
		n = 0
		for r in responses:
			b = Button(f, text=r, command=lambda n=n: self._respond(n))
			if n == default:
				b.configure(fg='blue')
			b.pack(side=LEFT, padx=10, pady=5)
			n = n + 1

		self.protocol("WM_DELETE_WINDOW", lambda n=None: self._respond(n))

		self.grab = grab

		if default:
			self.default = default
			self.bind('<Return>', self._return_event)

	def go(self, wait=1):
		screencenter(self)
		self.parent.bell()
			
		if wait:
			# don't grab, if we're not waiting!
			if self.grab:
				self.grab_set()
			self.wait_window(self)
			return self._choice

	def _respond(self, n):
		self._choice = n
		self.destroy()

	def _return_event(self, event):
		if self.default:
			self._choice = self.default
			self.destroy()
		
class Info:
	def __init__(self, parent, height=10, width=50, bg='white',
				 font="-*-lucidatypewriter-medium-r-*-*-10-*-*-*-*-*-*-*"):

		t = Pmw.ScrolledText(parent)
		t.pack(expand=1, side=TOP, fill=BOTH)
		self.text = t.component('text')
		self.text.config(bg=bg, font=font,
						 height=height,
						 width=width)
		
		#from ScrolledText import ScrolledText
		#self.text = ScrolledText(parent)
		#self.text.config(height=height,
		#					 width=width,
		#					 bg=bg, font=font)
		#self.text.pack(expand=1, fill=BOTH)
			
		self.text.config(state=DISABLED)
		self.next_tag = 0

	def write(self, line, color=None, update=1):
		self.text.config(state=NORMAL)
		if color:
			tag = "tag%d" % self.next_tag
			self.next_tag = self.next_tag + 1
			self.text.tag_config(tag, foreground=color)
			self.text.insert(END, line, tag)
		else:
			self.text.insert(END, line)
		self.text.config(state=DISABLED)
		if update:
			self.text.update()
		self.text.see(END)

	def writenl(self, line, color=None, update=1):
		self.write("%s\n" % line, color)

	def clear(self):
		self.text.config(state=NORMAL)
		self.text.delete(0.0, END)
		self.text.config(state=DISABLED)

	def update(self):
		self.text.update()

class EventQueue:
	# Note:
	#  useful ev.state flags:
	#    SHIFT = 1
	#    CTRL = 4
	
	def __init__(self, parent, ev='<Key>'):
		self.buffer = []
		parent.bind_all(ev, self._push)

	def _push(self, ev):
		self.buffer.append((ev.keysym, ev))

	def pop(self):
		if len(self.buffer) > 0:
			r = self.buffer[0]
			self.buffer = self.buffer[1:]
			return r
		else:
			return (None, None)

	def flush(self):
		self.buffer = []

def warn(title, message, wait=None, action=None, astext=0,
		 fixed=None, grab=1):
	"""
	Popup a dialog box and warn the user abotu something. Lots of
	options, but only one possible response: "Continue" or "Close"
	
	return: nothing.
	"""

	if action is None:
		if wait:
			action = 'Continue'
		else:
			action = 'Close'
	dialog = SimpleDialog(message,
						  title=title, iconname='warning', astext=astext,
						  default=0, responses=(action,), grab=grab)
	undermouse(dialog)
	dialog.go(wait=wait)

def ask(title, message, strings):
	"""
	Popup a dialog box and ask the user to choose one of several
	possible responses (strings is list of possible responses).
	
	return: NUMBER of the selected response (starting with 0)
		    or None if you close the box w/o selecting anything
	"""

	i = SimpleDialog(message, title=title,
					 default=0, responses=strings).go()
	return i

def undermouse(w):
	"""
	Position a window 'w' directly underneath the mouse
	"""
	rw, rh = w.winfo_reqwidth(), w.winfo_reqheight()
	x, y = w.winfo_pointerx()-(rw/2), w.winfo_pointery()-(rh/2)
	if x < 0:
		x = 0
	elif (x+rw) >= w.winfo_screenwidth():
		x = w.winfo_screenwidth() - rw
	if y < 0:
		y = 0
	elif (y+rh) >= w.winfo_screenheight():
		y = w.winfo_screenheight() - rh
	w.geometry("+%d+%d" % (x, y))

def screencenter(w):
	"""
	Position a window 'w' at the center of the screen
	"""
	sw = w.winfo_screenwidth()
	sh = w.winfo_screenheight()
	if sw > 1280:
		# this is to keep dialog boxes from getting
		# split across a dual screen layout..
		sw = 1280
		
	x, y = (sw/2) - (w.winfo_reqwidth()/2), (sh/2) - (w.winfo_reqheight() / 2)
	w.geometry("+%d+%d" % (x, y))

class AboutPype:
	"""
	Class for the About box.  This is just to make sure
	only one box per run gets built and reused.
	"""
	_w = None
	def __init__(self):
		from im_splash import splash
		
		if AboutPype._w is None:
			AboutPype._w = Toplevel()
			AboutPype._w.title('PypeAbout')
			AboutPype._w.iconname('PypeAbout')
			icon = Label(AboutPype._w,
						 relief=FLAT, image=splash, pady=10)
			icon.pack(expand=1, fill=BOTH)

			t = """
pype: python physiology environment
Copyright (c) 1999 Jamie Mazer
Version %s
Installed: %s""" % (PypeVersion, PypeInstallDate)
			text = Label(AboutPype._w, text=t)
			text.pack(expand=1, fill=BOTH)

			AboutPype._w.protocol("WM_DELETE_WINDOW", self._withdraw)
			b = Button(AboutPype._w, text='Close', command=self._withdraw)
			b.pack(expand=1, fill=X)
			undermouse(AboutPype._w)
		else:
			undermouse(AboutPype._w)
			AboutPype._w.deiconify()

	def _withdraw(self):
		AboutPype._w.withdraw()

def splash():
	"""
	Display a splash screen an destroy it after 10 secs.
	"""
	from im_splash import splash
	
	w = Toplevel()
	w.overrideredirect(1)
	w.withdraw()
	
	f = Frame(w, borderwidth=20, background='blue')
	f.pack(expand=1, fill=BOTH)
	icon = Label(f, relief=FLAT, image=splash)
	icon.pack(expand=1, fill=BOTH)
	w.update_idletasks()
	screencenter(w)
	w.deiconify()
	w.update_idletasks()
	w.after(3000, w.destroy)

if __name__ == '__main__':
	sys.stderr.write('%s should never be loaded as main.\n' % __file__)
	sys.exit(1)
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
		
