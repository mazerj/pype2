# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**OBSOLETE**

Interface/wrapper for BLT (Tk plotting widget)

Wrappers for BLT plotting widgets.  BLT is a Tk package/extension
that provides XY plotting widgets, along with some other assorted
junk. BLT doesn't play well with Tkinter, without some sort of
wrapper.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Unknown Date; Derived from blt2_1.py ::

 >> 	This file is based on blt.py developed by  Peter J. Godman.
 >> 	Modification to work with BLT2.1 was made by 
 >> 	 Noboru Yamamoto (noboru.yamamoto@kek.jp)
 >> 	 KEK, Accelerator Dept.
 >> 	 JAPAN
 >> 
 >>  Test environment:
 >>  Host OS: Digital Unix (aka DEC OSF1) 3.2c
 >>  Python 1.4
 >>  Tcl 7.6/Tk 4.2/ blt2.1

Unknown Date; Changes for BLT version 2.4 ::

 removed vector support
 changed Widget init code to use blt:: naming (tcl packages)
 dynamically loads blt package.. must be available..
 setup proper subclassing to remove redundant methods..
 fixed legend_configure
"""
__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

from Tkinter import *
import string

XAXIS = 'xaxis'
YAXIS = 'yaxis'
X2AXIS = 'xaxis'
Y2AXIS = 'yaxis'


def _loadblt(root):
	if _BLT._bltloaded is None:
		try:
			root.tk.call('load', '', 'Blt')
			_BLT._bltloaded = 1
		except TclError:
			try:
				root.tk.call('package', 'require', 'BLT')
				_BLT._bltloaded = 1
			except TclError:
				raise ImportError, 'BLT class requires BLT extensions'


def busy(w, release=None):
	"""
	Lock w and all children as busy..
	"""
	_loadblt(w)
	if not release:
		w.tk.call('blt::busy', 'hold', w._w)
	else:
		w.tk.call('blt::busy', 'release', w._w)

class _BLT(Widget):
	"""
	underylying generic plot widget
	"""

	_bltloaded = None

	def __init__(self, master, cnf={}, **kw):
		sys.stderr.write('_BLT:__init__ should never be called\n')
		sys.exit(1)

	def _loadblt(self, root):
		if _BLT._bltloaded is None:
			try:
				root.tk.call('load', '', 'Blt')
				_BLT._bltloaded = 1
			except TclError:
				try:
					root.tk.call('package', 'require', 'BLT')
					_BLT._bltloaded = 1
				except TclError:
					raise ImportError, 'BLT class requires BLT extensions'


	def _down(self, ev):
		(self.__x, self.__y) = self.invtransform(ev.x, ev.y)
		self.configure(cursor='bottom_right_corner')

	def _up(self, ev):
		try:
			foo = self._x_axis
		except AttributeError:
			self._x_axis = self.axis_limits(XAXIS)
			self._y_axis = self.axis_limits(YAXIS)
		(x, y) = self.invtransform(ev.x, ev.y)
		self.axis_configure(XAXIS, min=self.__x)
		self.axis_configure(YAXIS, max=self.__y)
		self.axis_configure(XAXIS, max=x)
		self.axis_configure(YAXIS, min=y)
		del self.__x
		del self.__y
		self.configure(cursor='crosshair')

	def _reset(self, ev):
		try:
			self.axis_configure(XAXIS,
								min=float(self._x_axis[0]),
								max=float(self._x_axis[1]))
			self.axis_configure(YAXIS,
								min=float(self._y_axis[0]),
								max=float(self._y_axis[1]))
		except:
			# effort to remove all unnamed exceptions:
			import pypedebug
			pypedebug.get_traceback(1)
			
			self.axis_configure(XAXIS, min='', max='')
			self.axis_configure(YAXIS, min='', max='')

	def bindzoom(self):
		self.bind('<ButtonPress-1>', self._down)
		self.bind('<ButtonRelease-1>', self._up)
		self.bind('<ButtonPress-2>', self._reset)
		self.bind('<ButtonPress-3>', self._reset)
		self.bind('<Escape>', self._reset)

	def crosshairs_configure(self, cnf={}, **kw):
		return apply(self.tk.call, 
					 (self._w, 'crosshairs', 'configure')
					 + self._options(cnf, kw))

	def crosshairs_toggle(self):
		self.tk.call(self._w, 'crosshairs', 'toggle')

	def crosshairs_on(self):
		self.tk.call(self._w, 'crosshairs', 'on')

	def crosshairs_off(self):
		self.tk.call(self._w, 'crosshairs', 'off')

	def element_activate(self, name, index=None):
		return self.tk.call, (self._w, 'element',
							  'activate', name, index)

	def element_closest(self, x, y, cnf={}, name=None):
		return apply(self.tk.call, (self._w, 'element', 'closest', x, y)+
					 self._options(cnf)+(name))

	def element_configure(self, name, cnf={}, **kw):
		apply(self.tk.call,
		      (self._w, 'element', 'configure', name)
		      + self._options(cnf, kw))

	def element_create(self, name, cnf={}, **kw):
		apply(self.tk.call, 
		      (self._w, 'element', 'create', name)
		      + self._options(cnf, kw))

	def element_deactivate(self, name, *names):
		apply(self.tk.call, (self._w, 'element', 'deactivate',
				    name) + names)

	def element_delete(self, name, *names):
		apply(self.tk.call, (self._w, 'element', 'delete',
				    name) + names)

	def element_names(self):
		return string.split(self.tk.call(self._w, 'element', 'names'))

	def element_show(self, *names):
		return apply(self.tk.call, (self._w, 'element', 'show') + names)

	def invtransform(self, winx, winy):
		return string.split(self.tk.call(self._w, 'invtransform', winx, winy))

	def legend_activate(self, name, *names):
		apply(self.tk.call, (self._w, 'legend', 'activate', name) + names)

	def legend_configure(self, cnf={}, **kw):
		apply(self.tk.call, 
		      (self._w, 'legend', 'configure')
		      + self._options(cnf, kw))

	def legend_deactivate(self, name):
		self.tk.call(self._w, name)

	def legend_get(self, x, y):
		self.tk.call(self._w, x, y)

	def postscript(self, filename=None):
		import tkFileDialog, os
		if filename == None:
			filename = tkFileDialog.SaveAs(initialdir=os.getcwd(),
										   title="Save PS to...").show()
			if len(filename) == 0:
				return None
		return self.tk.call(self._w, 'postscript', 'output', filename)

	def psconfigure(self, cnf={}, **kw):
		apply(self.tk.call, 
			  (self._w, 'postscript', 'configure')
			  + self._options(cnf, kw))

	def psget(self, cnf={}, **kw):
		return apply(self.tk.call, 
					 (self._w, 'postscript', 'cget')
					 + self._options(cnf, kw))

	def tag_after(self, tagid1, tagid2=None):
		self.tk.call(self._w, 'tag', 'after', tagid1, tagid2)

	def tag_before(self, tagid1, tagid2=None):
		self.tk.call(self._w, 'tag', 'before', tagid1, tagid2)

	def tag_configure(self, tagid, cnf={}, **kw):
		apply(self.tk.call, 
		     (self._w, 'tag', 'configure', name)
		      + self._options(cnf, kw))

	def tag_coords(self, tagid, coords=None):
		return string.split(self.tk.call(self._w, tagid, coords))

	def tag_create(self, type, coords=None):
		self.tk.call(self._w, 'tag', 'create', coords)

	def tag_delete(self, tagid, *tagids):
		apply(self.tk.call, (self._w, 'tag', 'delete',
				    tag) + tags)

	def tag_ids(self, pattern=None):
		return string.split(self.tk.call(self._w, 'tag', 'ids', 
						 pattern))

	def tag_type(self, tagid):
		return self.tk.call(self._w, 'tag', 'type')

	def transform(self, x, y):
		self.tk.call(self._w, 'transform', x, y)

	def axis_configure(self, axis, cnf={}, **kw):
		apply(self.tk.call, 
		     (self._w, axis, 'configure')
		      + self._options(cnf, kw))

	def axis_limits(self, axis):
		return string.split(self.tk.call(self._w, axis, 'limits'))

	def image_create(self, cnf={}, **kw):
		apply(self.tk.call, 
		      (self._w, 'marker', 'create',  'image')
		      + self._options(cnf, kw))

	def marker_create(self, mtype, cnf={}, **kw):
		apply(self.tk.call, 
		      (self._w, 'marker', 'create', mtype)
		      + self._options(cnf, kw))

class Graph(_BLT):
	"""
	blt_graph widget
	"""

	def __init__(self, master, cnf={}, **kw):
		_loadblt(master)
		Widget.__init__(self, master, 'blt::graph', cnf, kw)
		self.bindzoom()

class Barchart(_BLT):
	"""
	blt_barchart widget
	"""

	def __init__(self, master, cnf={}, **kw):
		_loadblt(master)
		Widget.__init__(self, master, 'blt::barchart', cnf, kw)
		self.bindzoom()

class Histogram(_BLT):
	def __init__(self, min, max, nbins=10):
		self.min = min
		self.max = max
		self.nbins = nbins
		self.binwidth = (max - min) / nbins
		self.x = []
		self.y = []
		self.data = []
		self.outleft = 0
		self.outright = 0
		self.count = 0
		f = min + (self.binwidth/2.0)
		while f < self.max:
			self.x.append(f)
			self.y.append(0)
			f = f + self.binwidth

	def __repr__(self):
		return "<Histogram: [%f,%f] nbins=%d>" % (self.min, self.max,
												  self.nbins)

	def add(self, v=None):
		if v is None:
			self.outleft = 0
			self.outright = 0
			self.count = 0
			self.data = []
			for i in range(0, len(self.y)):
				self.y[i] = 0
		else:
			if v < self.min:
				self.outleft = self.outleft + 1
			elif v >= self.max:
				self.outright = self.outright + 1
			else:
				n = int(round((v - self.min) / self.binwidth, 0))
				self.y[n] = self.y[n] + 1
			self.count = self.count + 1
			self.data.append(v)

	def clear(self):
		self.add(None)

	def display(self, bargraph, name, percent=0, cnf={}, **kw):
		x = tuple(self.x)
		if percent:
			y = []
			for d in self.y:
				if self.count > 0:
					y.append(100.0 * float(d) / float(self.count))
				else:
					y.append(0)
			y = tuple(y)
		else:
			y = tuple(self.y)

		kw['xdata'] = x
		kw['ydata'] = y
		kw['barwidth'] = self.binwidth

		try:
			apply(bargraph.element_configure, (name,), kw)
		except:
			# effort to remove all unnamed exceptions:
			import pypedebug
			pypedebug.get_traceback(1)
			apply(bargraph.element_create, (name,), kw)

	def stats(self):
		import math
		mean = 0.0;
		var = 0.0
		if self.count > 0:
			for d in self.data:
				mean = mean + d
			mean = mean / self.count
			if self.count > 1:
				var = 0.0;
				for d in self.data:
					var = var + ((d - mean)**2)
				var = var / (self.count - 1)
		return (mean, var, math.sqrt(var))

class _Quick:
	def __init__(self):
		sys.stderr.write('_Quick:__init__ should never be called\n')
		sys.exit(1)

	def wait(self):
		"""Wait for graph to go away.."""
		try:
			self.g.wait_window(self.g)
		except:
			# effort to remove all unnamed exceptions:
			import pypedebug
			pypedebug.get_traceback(1)
			pass
		

class QuickGraph(_Quick):
	def __init__(self, root, datasets, symbol="", \
				 xlabel="", ylabel="", title=""):
		if root is None:
			root = Toplevel()
			root.protocol("WM_DELETE_WINDOW", root.destroy)
			
		g = Graph(root, title=title)
		self.g = g
		g.pack(expand=1, fill=BOTH)
		g.axis_configure(XAXIS, title=xlabel)
		g.axis_configure(YAXIS, title=ylabel)
		colors = ['red', 'green', 'blue', 'black']
		n = 0
		for ds in datasets:
			ss = 3
			if len(ds) == 2:
				(x, y) = ds
				name = "l%d" % n
				lw = 1
				_symbol=symbol
			elif len(ds) == 3:
				(x, y, name) = ds
				_symbol=symbol
				lw = 1
			elif len(ds) == 4:
				(x, y, name, _symbol) = ds
				lw = 1
			elif len(ds) == 5:
				(x, y, name, _symbol, lw) = ds
			elif len(ds) == 6:
				(x, y, name, _symbol, lw, ss) = ds
			else:
				raise TypeError, 'QuickGraph: invalid dataset spec'

			if y is None:
				y = range(0,len(x))
			if x is None:
				x = range(0,len(y))
			g.element_create(name)
			g.element_configure(name, symbol=_symbol, color=colors[n],
								xdata=tuple(x), ydata=tuple(y),
								linewidth=lw, pixels=ss)
			n = (n + 1) % len(colors)
		if len(datasets) < 2:
			g.legend_configure(hide=1)

class QuickGraphXYE(_Quick):
	def __init__(self, root, datasets, xlabel="", ylabel="", title=""):
		if root is None:
			root = Toplevel()
		g = Graph(root, title=title)
		self.g = g
		g.pack(expand=1, fill=BOTH)
		g.axis_configure(XAXIS, title=xlabel)
		g.axis_configure(YAXIS, title=ylabel)
		colors = ['red', 'green', 'blue', 'black']
		symbols = ['circle', 'square', 'diamond', 'plus', 'cross', 'triangle']
		n = 0
		for (x, y, e, name) in datasets:
			if y is None:
				y = range(0,len(x))
			if x is None:
				x = range(0,len(y))
			g.element_create(name)
			g.element_configure(name, xdata=tuple(x), ydata=tuple(y),
								symbol=symbols[n%len(symbols)],
								color=colors[n%len(colors)])
			for i in range(len(x)):
				foo = "e%d" % i
				g.element_create(foo)
				g.element_configure(foo,
									xdata=(x[i], x[i]),
									ydata=(y[i] - e[i], y[i] + e[i]),
									symbol='', color=colors[n%len(colors)])
			n = n + 1

		if len(datasets) < 2:
			g.legend_configure(hide=1)

class QuickGraphXYZ(_Quick):
	def __init__(self, root, xd, yd, zd, xlabel="", ylabel="", title=""):
		if root is None:
			root = Toplevel()
		g = Graph(root, title=title)
		self.g = g
		g.pack(expand=1, fill=BOTH)
		xv = self._uniq(xd)
		yv = self._uniq(yd)
		dx2 = (xv[1] - xv[0]) / 2.0
		dy2 = (yv[1] - yv[0]) / 2.0
		g.axis_configure(XAXIS, title=xlabel, min=xv[0]-dx2, max=xv[-1]+8*dx2)
		g.axis_configure(YAXIS, title=ylabel, min=yv[0]-dy2, max=yv[-1]+dy2)
		zmax = None
		zmin = None
		for n in range(0, len(zd)):
			if zmax is None or zd[n] > zmax:
				zmax = zd[n]
			if zmin is None or zd[n] < zmin:
				zmin = zd[n]
		if zmin < 0 and zmax > 0:
			if -zmin > zmax:
				zmax = -zmin
			else:
				zmin = -zmax
		cmap = self._cmap(256)
		for n in range(0, len(zd)):
			x = xd[n]
			y = yd[n]
			z = int(255.0 * (zd[n] - zmin) / (zmax - zmin))
			fill = cmap[z]
			coords=(x-dx2, y-dy2, x+dx2, y-dy2, x+dx2, y+dy2, x-dx2, y+dy2)
			g.marker_create('polygon', fill=fill,
							coords=coords, linewidth=1, outline='black')

			
		x = xv[-1]+3*dx2
		for i in range(0, len(yv)):
			z = int(255.0 * (i / (len(yv)-1.0)))
			fill = cmap[z]
			coords = (x-dx2,yv[i]-dy2,x+dx2,yv[i]-dy2,
					  x+dx2,yv[i]+dy2,x-dx2,yv[i]+dy2)
			g.marker_create('polygon', fill=fill,
							coords=coords, linewidth=1, outline='black')
			coords = (x+2*dx2,yv[i])
			z = (z/255.0) * (zmax-zmin) + zmin
			g.marker_create('text', coords=coords,
							text='%0.2f'%z, anchor=W)
			
	def _uniq(self, v):
		d = {}
		for e in v: d[e] = 1
		v = d.keys()
		v.sort()
		return v

	def _cmap(self, n):
		cmap = []
		for x in range(128, 0, -1):
			r = 255.0 * (1.0 - (x/128.0))
			g = 255.0 * (1.0 - (x/128.0))
			b = 255.0
			cmap.append("#%02x%02x%02x" % (r, g, b))
		for x in range(0, 128):
			r = 255.0
			g = 255.0 * (1.0 - (x/128.0))
			b = 255.0 * (1.0 - (x/128.0))
			cmap.append("#%02x%02x%02x" % (r, g, b))
		return cmap

	def _cmap2(self, n):
		cmap = []
		for x in range(128, 0, -1):
			r = 255.0 * (1.0 - (x/128.0))
			g = 255.0
			b = 255.0 * (1.0 - (x/128.0))
			cmap.append("#%02x%02x%02x" % (r, g, b))
		for x in range(0, 128):
			r = 255.0
			g = 255.0 * (1.0 - (x/128.0))
			b = 255.0 * (1.0 - (x/128.0))
			cmap.append("#%02x%02x%02x" % (r, g, b))
		return cmap

	def _cmap1(self, n):
		cmap = []
		for i in range(0, n):
			r = i
			g = i
			b = n-i-1
			cmap.append("#%02x%02x%02x" % (r, g, b))
		return cmap

	def _cmap0(self, n):
		cmap = []
		for i in range(0, n):
			r = int(255.0 * ((n - i) / float(n)))
			g = 255 - int(255.0 * ((n - i) / float(n)))
			b = 0
			cmap.append("#%02x%02x%02x" % (r, g, b))
		return cmap

class QuickHist(_Quick):
	def __init__(self, root, min, max, nbins, data, \
				 xlabel="", ylabel="", title=""):
		if root is None:
			root = Toplevel()
		g = Barchart(root, title=title)
		self.g = g
		g.pack(expand=1, fill=BOTH)
		g.axis_configure(XAXIS, title=xlabel)
		g.axis_configure(YAXIS, title=ylabel)
		h = Histogram(min, max, nbins)
		self.h = h
		for d in data:
			h.add(d)
		h.display(g, 'hist', 0)

if __name__=='__main__' :
	import Tkinter, math, sys, math

	def demo1():
		root=Tkinter.Tk()
		g=Barchart(root,barmode="aligned")
		g.pack()
		xy=Graph(root)
		xy.pack()
		xdata = []
		ydata = []
		g.axis_configure(XAXIS, hide=1)
		g.axis_configure(YAXIS, title="energy")
		g.element_create('stacey')
		g.legend_configure(hide=1)
		xy.element_create('stacey')
		xy.axis_configure(XAXIS, title="time")
		xy.axis_configure(YAXIS, title="energy")
		xy.legend_configure(hide=1)
		for i in range(1,1000,50):
			xdata.append(i)
			ydata.append(math.sin(i/100.0))
			g.element_configure('stacey', xdata=tuple(xdata), ydata=tuple(ydata))
			xy.element_configure('stacey', xdata=tuple(xdata), ydata=tuple(ydata))
			root.update()
			root.after(100)

		root.mainloop()

	def demo2():
		import random
		global run
		run = 1

		def quit():
			global run
			run = 0

		root=Tkinter.Tk()

		root.protocol("WM_DELETE_WINDOW", quit)
		g=Barchart(root, title='stats in action')
		g.legend_configure(hide=1)
		g.pack(expand=1, fill=BOTH)
		h1 = Histogram(0, 100, 50)
		h2 = Histogram(0, 100, 50)
		h3 = Histogram(0, 100, 50)
		g.axis_configure(XAXIS, rotate=90.0, stepsize=5*h1.binwidth)
		g.axis_configure(YAXIS, title="Frequency")

		while run:
			s = 0
			for j in range(0, 100):
				s = s + random.randint(0, 100)
				if j == 2:
					h2.add(s/3)
				if j == 9:
					h3.add(s/10)
			s = s / 100
			h1.add(s)
			h1.display(g, 'h1', 1, fg='green')
			h2.display(g, 'h2', 1, fg='red')
			h3.display(g, 'h3', 1, fg='blue')
			mean1, var1, std1 = h1.stats()
			mean2, var2, std2 = h2.stats()
			mean3, var3, std3 = h3.stats()
			g.axis_configure(XAXIS,
							 title="%.0f+-%.0f,%.0f+-%.0f,%.0f+-%.0f"%
							 (mean1, std2, mean2, std2, mean3, std3))

			root.update()

	def demo3():
		root=Tkinter.Tk()
		root.protocol("WM_DELETE_WINDOW", sys.exit)
		x = []
		y = []
		z = []
		for ix in range(0, 10):
			for iy in range(0, 10):
				x.append(ix)
				y.append(iy)
				z.append(ix * iy - 20)
		QuickGraphXYZ(root, x, y, z)
		root.mainloop()

	demo1()
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
		
	
