# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""
**Progress bar**

Standalone progress bar (like the matlab waitbar function) for
GUI tasks that take a long time. This is the same idea as the
dancing bear functions in *pype.py*, but for when you _know_ the
Tkinter GUI will be active.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

"""

from Tkinter import *
from Tkinter import _default_root
from sys import argv
from posixpath import basename

class ProgressBar:
	"""
	This is for when you know how long something is going to
	take -- you can specify the percentage done.
	"""

	def __init__(self, width=200, height=22,
				 doLabel=None, labelText="",
				 value=0, title=None, min=0, max=100):

		if _default_root is None:
			root = Tk()
			root.withdraw()
		
		self.master = Toplevel()
		self.master.title('Working')
		self.master.iconname('Working')
		self.master.lift()
		#self.master.overrideredirect(1)
		self.min=min
		self.max=max
		self.width=width
		self.height=height
		self.doLabel=doLabel
		
		fillColor="red"
		labelColor="black"
		background="lightgreen"
		self.labelFormat="%d%%"
		self.value=value
		f = Frame(self.master, bd=3, relief=SUNKEN)
		f.pack(expand=1, fill=BOTH)
		if title is None:
			title = "Working"
		Label(f, text=title).pack(expand=1, fill=Y, side=TOP)
		self.frame=Frame(f, relief=SUNKEN, bd=4, background='black')
		self.frame.pack(fill=BOTH)
		self.canvas=Canvas(self.frame, height=height, width=width, bd=0,
						   highlightthickness=0, background=background)
		self.scale=self.canvas.create_polygon(0, 0, width, 0,
											  width, height, 0, height,
											  fill=fillColor)
		self.label=self.canvas.create_text(self.canvas.winfo_reqwidth() / 2,
										   height / 2, text=labelText,
										   anchor="c", fill=labelColor)
		self.update()
		self.canvas.pack(side=TOP, fill=X, expand=NO)
		
		self.master.update_idletasks()
		sw = self.master.winfo_screenwidth()
		sh = self.master.winfo_screenheight()
		self.master.geometry("+%d+%d" % \
							 (sw/2 - (self.master.winfo_reqwidth()/2),
							  sh/2 - (self.master.winfo_reqheight() / 2)))
		self.master.update_idletasks()

	def __del__(self):
		self.master.withdraw()
		self.update()
		self.master.destroy()
		
	def set(self, newValue, newMax=None):
		if newMax:
			self.max = newMax
		self.value = newValue
		self.update()

	def update(self):
		# Trim the values to be between min and max
		value=self.value
		if value > self.max:
			value = self.max
		if value < self.min:
			value = self.min

		# Adjust the rectangle
		self.canvas.coords(self.scale, 0, 0, 0, self.height,
						   float(value) / self.max * self.width, self.height,
						   float(value) / self.max * self.width, 0)

		# And update the label
		if self.doLabel:
			self.canvas.itemconfig(self.label)
			if value:
				if value >= 0:
					pvalue = int((float(value) / float(self.max)) * 100.0)
				else:
					pvalue = 0
				self.canvas.itemconfig(self.label, text=self.labelFormat
									   % pvalue)
			else:
				self.canvas.itemconfig(self.label, text='')
		self.canvas.update_idletasks()

class DanceBar(ProgressBar):
	"""
	This is for when you DON'T know how long, but just want to
	let the user know you're still alive & running.
	"""
	def set(self, newValue=None):
		if newValue:
			self.value = newValue
		else:
			self.value = (self.value + 1) % 100
		self.update()

	def update(self):
		value = self.value % 25
		x1 = (float(value) / 25.0 * self.width)
		x2 = (float(value+1) / 25.0 * self.width)

		self.canvas.coords(self.scale, x1, 0, x1-10, self.height,
						   x2-10, self.height, x2, 0)
		self.canvas.update_idletasks()
		
if __name__ == '__main__':
	bar = DanceBar()
	foo = ProgressBar(doLabel=1)
	for n in range(0,100,1):
		foo.set(n)
		bar.set()
		foo.canvas.after(100)
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
		



