# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$
"""Assorted GUI-related functions

Useful Tkinter and Pmw utility functions for GUI building
nd running. Things that get repeated over and over again
in the main pype code eventually end up here for
onsolidation.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

- Wed Apr  8 21:42:18 1998 mazer

 - created

- Thu Jan 27 15:27:15 2000 mazer

 - added DockWindow class

- Mon Jun 25 12:21:40 2007 mazer

 - got rid of beepwarn() and added 'audible' optional arg to warn()
 
 - Container() class is obsolete... deleted it..

"""

from Tkinter import *
import Pmw
from ScrolledText import ScrolledText

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

class SimpleDialog(Toplevel):
	def __init__(self, msg, responses=('Ok',),
				 default=None, title=None, iconname=None, **kw):

		apply(Toplevel.__init__, (self,), kw)

		if title:
			self.title(title)
		if iconname:
			self.iconname(title)

		parent = self._nametowidget(self.winfo_parent())
		self.transient(parent)
		
		f = Frame(self, relief=GROOVE, borderwidth=3)
		f.pack(side=TOP, expand=1, fill=BOTH)
		l = Label(f, text=msg)
		l.pack(padx=25, pady=25)
		
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

		if default:
			self.default = default
			self.bind('<Return>', self._return_event)

	def go(self):
		screencenter(self)
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
	def __init__(self, parent=None, height=10, width=50, bg='white',
				 font=None):
		if parent is None:
			self.parent = Tk()
			self.parent.title('Info')
		else:
			self.parent = parent;

		if font is None:
			font = "-*-lucidatypewriter-medium-r-*-*-10-*-*-*-*-*-*-*"
		self.text = ScrolledText(self.parent,
								 height=height,
								 width=width,
								 bg=bg,
								 font=font)
		self.text.config(state=DISABLED)
		self.text.pack(expand=1, fill=BOTH)
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
		 fixed=None, audible=None):
	"""
	Popup a dialog box and warn the user abotu something. Lots of
	options, but only one possible response: "Ok"
	
	return: if wait=1, then nothing is returned, otherwise, the toplevel
		   widget containing the dialogbox is returned so you can kill
		   or close it manually
	"""

	from Dialog import DIALOG_ICON
	from beep import beep

	dialog = Toplevel()
	dialog.title(title)
	dialog.iconname('PypeDialog')
	dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

	parent = dialog._nametowidget(dialog.winfo_parent())

	f = Frame(dialog)
	f.pack(expand=1, fill=BOTH)

	icon = Label(f, bitmap=DIALOG_ICON)

	if astext:
		text = Text(f, relief=RIDGE, borderwidth=3)
		text.insert(END, message)
	else:
		if fixed:
			font="-*-courier-*-r-*-*-12-*-*-*-*-*-*-*"
		else:
			font="-*-helvetica-*-r-*-*-12-*-*-*-*-*-*-*"
		text = Label(f, text=message,
					 justify=LEFT, relief=GROOVE, borderwidth=10, font=font)
	icon.grid(row=0, column=0, padx=10, pady=10)
	text.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5)

	if wait:
		if action is None:
			action = 'Continue'
		b = Button(dialog, text=action, command=dialog.destroy)
	else:
		if action is None:
			action = 'Close'
		b = Button(dialog, text=action, command=dialog.destroy)
	b.pack(expand=1, fill=X)

	b.bind('<Return>', lambda e, w=dialog: w.destroy())
	b.bind('<Escape>', lambda e, w=dialog: w.destroy())
	b.focus_set()

	# position the widget under the mouse
	undermouse(dialog)

	if wait:
		dialog.update()
		dialog.tkraise()
		if audible:
			while not dialog.done:
				beep(1000, 10)
				dialog.update()		
		dialog.wait_window(dialog)
	else:
		if audible:
			while not dialog.done:
				beep(1000, 10)
				dialog.update()
		return dialog

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

if __name__ == '__main__':
	sys.stderr.write('%s should never be loaded as main.\n' % __file__)
	sys.exit(1)
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
		
