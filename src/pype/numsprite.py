# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**Numeric-based sprite object**


Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Tue Apr  7 10:34:35 2009 mazer

- started work..

"""

import os
import sys
import posix
import pwd
import types
import math
import copy
import exceptions
import time

from Numeric import *
import RandomArray
from PIL import Image

#import pygame.image
#import pygame.surfarray

from sprite import *
from sprite import _C
from sprite import _pygl_setxy

from pypedebug import keyboard

class NumSprite:
	"""
	Numeric-based Sprite object.
	"""

	_count = 0
	
	def __init__(self, width=100, height=100, x=0, y=0, depth=0, \
				 fb=None, on=1, image=None, dx=0, dy=0, fname=None, \
				 name=None, icolor='black', centerorigin=0):
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy
		self.depth = depth
		self.fb = fb
		self._on = on
		self.icolor = icolor
		self.centerorigin = centerorigin
		self.array = None
		self.alpha = None
		
		if fname:
			# load image data from file using pygame tools
			self.frompil(Image.open(fname))

			""" with pygame:
			s = pygame.image.load(fname)
			array = pygame.surfarray.array3d(s).copy()
			self.array = array.astype(UnsignedInt8)
			alpha = pygame.surfarray.array_alpha(s).copy()
			self.alpha = alpha.astype(UnsignedInt8)
			"""

			""" with numpy:
			a = PIL.Image.open(fname)
			self.array = numpy.array(a)
			...
			"""
		elif image:
			# make a copy of the source sprite/image
			self.array = image.array.copy()
			self.alpha = image.alpha.copy()
		else:
			# new RGBA image from scratch
			self.array = zeros((width, height, 3), UnsignedInt8)
			self.alpha = zeros((width, height), UnsignedInt8)
			self.alpha[:] = 255

		# set dimensions based on loaded shape
		self.setdims()

		if name:
			self.name = name
		elif fname:
			self.name = "file:%s" % fname
		else:
			self.name = "numsprite%d" % NumSprite._count
		NumSprite._count = NumSprite._count + 1

	def setdims(self):
		(self.w, self.h) = self.alpha.shape
		(self.iw, self.ih) = (self.w, self.h)

		self.ax, self.ay = genaxes(self.w, self.h, inverty=0)
		self.xx, self.yy = genaxes(self.w, self.h, inverty=1)

	

	def __repr__(self):
		return '<NumSprite "%s" @ (%d,%d) depth=%d>' % \
			   (self.name, self.x, self.y, self.depth)

	def __getitem__(self, key):
		return self.array[key]

	def __setitem__(self, key, value):
		self.array[key] = value

	def asPhotoImage(self, alpha=None):
		m = self.array.copy()
		a = self.alpha.copy()
		if alpha:
			a[:] = alpha
			
		m = concatenate((self.array, self.alpha[:,:,NewAxis]),
						axis=2)
		s = m.tostring()
		#?? s = transpose(m, axes=[1,0,2])[::-1,:,:].tostring()
		self.pil_im = PIL.Image.fromstring('RGBA', (self.w, self.h), s)
		self.pim = PIL.ImageTk.PhotoImage(self.pil_im)
		return self.pim

	def set_alpha(self, alpha):
		self.alpha[:] = alpha

	def clear(self, color=(1,1,1)):
		rgba = _C(color)
		for n in range(3):
			self.array[:,:,n] = rgba[n]
		self.alpha[:] = rgba[3]

	def fill(self, color):
		self.clear(color=color)

	def noise(self, thresh=0.5, color=None):
		for n in range(3):
			if color or n == 0:
				m = RandomArray.uniform(1, 255, shape=shape(self.array)[0:2])
				if not thresh is None:
					m = where(greater(m, thresh*255), 255, 1)
			self.array[:,:,n] = m[:]

	def circlefill(self, color, r, x=0, y=0, width=0):
		ar = (((self.ax-x)**2)+((self.ay+y)**2))**0.5
		mask = less_equal(ar, r)
		rgba = _C(color)
		for n in range(3):
			self.array[:,:,n] = where(mask, rgba[n], self.array[:,:,n])
		self.alpha[:] = rgba[3]

	def circle(self, color, r, x=0, y=0, width=1):
		ar = abs((((self.ax-x)**2)+((self.ay+y)**2))**0.5 - r)
		mask = less_equal(ar, width)
		rgba = _C(color)
		for n in range(3):
			self.array[:,:,n] = where(mask, rgba[n], self.array[:,:,n])		
		self.alpha[:] = rgba[3]

	def axisflip(self, xaxis, yaxis):
		if xaxis:
			self.array = self.array[::-1,:,:]
			self.alpha = self.alpha[::-1,:]
		if yaxis:
			self.array = self.array[:,::-1,:]
			self.alpha = self.alpha[:,::-1]

	def topil(self):
		m = concatenate((self.array, self.alpha[:,:,NewAxis]),
						axis=2)
		s = transpose(m, axes=[1,0,2])[:,:,:].tostring()
		return PIL.Image.fromstring('RGBA', (self.w, self.h), s)

	def frompil(self, i):
		a = array(i.tostring()).astype(UnsignedInt8)
		bpp = a.shape[0] / i.size[1] / i.size[0]
		if bpp == 4:
			# RGBA
			a = reshape(a, (i.size[1], i.size[0], 4))
			a = transpose(a, axes=[1,0,2])
			self.array = a[:,:,0:3]
			self.alpha = a[:,:,3]
		elif bpp == 3:
			# RGB
			a = reshape(a, (i.size[1], i.size[0], 3))
			self.array = transpose(a, axes=[1,0,2])
			self.alpha = zeros(self.array.shape[0:2], UnsignedInt8)
			self.alpha[:] = 255

	def rotate(self, angle, preserve_size=1, trim=0):
		self.frompil(self.topil().rotate(-angle, expand=(not preserve_size)))
		self.setdims()

	def rotateCCW(self, angle, preserve_size=1, trim=0):
		self.rotate(angle=angle, preserver_size=preserve_size, trim=trim)

	def rotateCW(self, angle, preserve_size=1, trim=0):
		self.rotate(angle=-angle, preserver_size=preserve_size, trim=trim)

	def scale(self, new_width, new_height):
		self.frompil(self.topil().resize((new_width, new_height),
										 Image.NEAREST))
		self.setdims()

	def circmask(self, r, x=0, y=0):
		d = (((self.ax-x)**2)+((self.ay+y)**2))**0.5
		mask = where(less(d, r), 1, 0)
		for n in range(3):
			self.array[:,:,n] = self.array[:,:,n] * mask

	def alpha_aperture(self, r, x=0, y=0):
		mask = where(less(((((self.ax-x)**2)+\
							((self.ay+y)**2)))**0.5, r), 255, 0)
		self.alpha[:,:] = mask[:,:].astype(UnsignedInt8)

	def alpha_gradient(self, r1, r2, x=0, y=0):
		d = 255 - (255 * (((((self.ax-x)**2)+\
							((self.ay+y)**2))**0.5)-r1) / (r2-r1))
		d = where(less(d, 0), 0, where(greater(d, 255), 255, d))
		self.alpha[:,:] = d[:,:].astype(UnsignedInt8)

	def alpha_gradient2(self, r1, r2, bg, x=0, y=0):
		raise Error

	def dim(self, mult, meanval=128.0):
		self.array = meanval + ((1.0-mult) * (self.array-meanval))

	def thresh(self, t):
		raise Error

	def on(self):
		self._on = 1

	def off(self):
		self._on = 0

	def toggle(self):
		self._on = not self._on
		return self._on

	def state(self):
		return self._on

	def moveto(self, x, y):
		self.x = x
		self.y = y

	def rmove(self, dx=0, dy=0):
		self.x = self.x + dx
		self.y = self.y + dy

	def save(self, fname):
		"""Use PIL to save image."""
		self.topil().save(fname)
		
	def blit(self, x=None, y=None, fb=None, flip=None, force=0, fast=None):
		# note: fast is ignored now
		if not force and not self._on:
			return

		if fb is None:
			fb = self.fb

		if self.fb is None:
			Logger("No fb associated with sprite on blit\n")
			return None

		# save position, if specified, else used saved position
		if x is None:	x = self.x
		else:			self.x = x

		if y is None:	y = self.y
		else:			self.y = y

		# x,y coords specify destination of sprite CENTER.
		# Convert to FB coords (place (0,0) corner in (0,0)@UL coords)
		scx = fb.hw + x - (self.w / 2)
		scy = fb.hh - y - (self.h / 2)

		# blit and optional page flip..
		scy = fb.hh + y - (self.h / 2)
		_pygl_setxy(scx, scy)

		m = concatenate((self.array, self.alpha[:,:,NewAxis]), axis=2)
		s = transpose(m, axes=[1,0,2])[::-1,:,:].tostring()
			
		glDrawPixels(self.w, self.h, GL_RGBA, GL_UNSIGNED_BYTE, s)
		
		if flip:
			fb.flip()

		# if moving sprite, move to next position..
		self.x = self.x + self.dx
		self.y = self.y + self.dy
		return 1

	def setdir(self, angle, vel):
		import math
		angle = math.pi * angle / 180.0
		self.dx = vel * math.cos(angle)
		self.dy = vel * math.sin(angle)

	def fastblit(self):
		raise Error

	def render(self, clear=None):
		raise Error

	def subimage(self, x, y, w, h, center=None):
		raise Error

	def clone(self):
		raise Error

	def line(self, x1, y1, x2, y2, color, width=1):
		raise Error

	def rect(self, x, y, w, h, color):
		raise Error

	def rotozoom(self, scale=1.0, angle=0.0):
		raise Error

fb = quickinit(dpy=":0.0", w=512, h=512, bpp=32, fullscreen=0, opengl=1)

import copy

if 1:
	s = NumSprite(x=0, y=0, fname='testpat.png', fb=fb)
	#s.save('foo.jpg')
	#s.scale(50,50)
	s.rotate(45, preserve_size=0)
	s.blit(flip=1)
	keyboard()

if 0:
	s = NumSprite(x=0, y=0, width=200, height=100, fb=fb)
	s.fill((128,128,128,255))
	s.array[:,0:30,0]=255
	s.array[:,30:60,1]=255
	s.array[:,60:,2]=255
	
	#s.circmask(25)
	#s.alpha_aperture(25)
	s.alpha_gradient(25,45)
	#s.dim(0.50)
	
	s.blit(flip=1)
	keyboard()

if 0:
	s = NumSprite(x=0, y=-200, width=200, height=200, fb=fb)
	cosgrat(s, 5, 0, 45)
	alphaGaussian(s, 50)
	s.blit()

	o = Sprite(x=0, y=200, width=200, height=200, fb=fb)
	cosgrat(o, 5, 0, 45)
	alphaGaussian(o, 50)
	o.blit()

if 0:
	print 'starting'
	for i in [1, 0]:
		for b in [1, 0]:
			for f in [1, 0]:
				if i:
					s = NumSprite(x=0, y=0, width=200, height=200, fb=fb)
					print 'numsprite', 'blit=%d' % b, 'flip=%d' % f
				else:
					s = Sprite(x=0, y=0, width=200, height=200, fb=fb)
					print 'sprite', 'blit=%d' % b, 'flip=%d' % f
				nf = 100
				phi = 0
				cosgrat(s, 5, phi, 45)
				start = time.time()
				for n in range(nf):
					cosgrat(s, 5, phi, 45)
					alphaGaussian(s, 25)
					if b:
						fb.clear((0,0,0))
						s.blit()
					if f:
						fb.flip()
					phi = (phi + 10) % 360
				stop = time.time()
				print ' ', nf/(stop-start), 'fps'
