# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**Useful sprite functions**

These function are intended to supplement or complement the
**sprite.py** module.

**WARNING** Most of these tools work on existing sprites or images and
many directly on the image itself (sprite.im), not the sprite, so be
careful you use them correctly

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Tue Aug 23 11:01:19 2005 mazer

- changed ori in singrat,cosgrat etc, such that 0deg -> vertical; convention
  is that motion to left is 0deg, motion up is 90deg, orientation follow
  along orthogonally. Not sure alphaGaussian2() is correct now!!

Tue Mar 7 09:28:03 2006 mazer

- change noted above was not correct. I changed the arctan2() calls::

    >> t = arctan2(s.yy, s.xx) - (pi * (90-ori_deg)) / 180.0

  to::

    >> t = arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0

  which should give the correct orientations now. Note that the
  real problem is that these functions have been broken from the
  very beginning, but handmap.py and spotmap.py (which uses the
  sprite rotate method) have corrected for this.

Tue Aug  8 14:04:36 2006 mazer

- added alphabar() function - generates a bar stimulus from a sprite
  by filling the sprite with the specified color and then setting the
  alpha channel to let the specified bar stimulus show through.

Wed Aug  9 13:15:34 2006 mazer

- Added _unpack_rgb() to make all the stimulus generators use a common
  color specification. And documented all the grating generators.

Fri Jun 13 15:24:57 2008 mazer

- added ppd=, meanlum=, moddepth= and color=  options to sin, cos,
  polar, logpolar and hyper grating functions

Wed Jun 18 13:54:46 2008 mazer

- removed old grating generator functions: Make_2D_XXXX()

Mon Jan  5 14:49:56 2009 mazer

- moved gen{axes,d,rad,theta} axes generator from sprite.py to this
  file (spritetools.py) - gend() function is now officially obsolete..

Fri May 22 15:27:42 2009 mazer

- added simple_rdp() function for Random Dot Patterns

Fri Jan 15 09:53:24 2010 mazer

- migrated from Numeric to numpy

  - NOTE: simple_rdp seed argument changed from 2-tuple to a MT state
    vecotr

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

import sys
import math
import numpy as _N
pi = _N.pi

# force pygame.surfarray to use numpy instead of Numeric
from pygame.constants import *
import pygame.surfarray
pygame.surfarray.use_arraytype('numpy')

import sprite
from guitools import Logger

##########################################################################
# new, faster, clean support functions added 04-mar-2004 JAM .. stop
# using the old versions..
##########################################################################

def _unpack_rgb(R, G, B):
	# if R is a 3-tuple, assume it's a standard pype color spec (0-255)
	# and convert to grating RGB (0-1) values. This one's for Jon T.

	try:
		R, G, B = _N.array(R)/255.0
	except TypeError:
		pass
	except ValueError:
		pass

	return R, G, B

def g2rgb(a):
	"""Convert a single grayscale image into a numeric array.

	This converts a shape=(W,H) array into an RGB shape=(W, H, 3) array.

	"""
	return _N.transpose(_N.array([a, a, a]), axes=[1,2,0])

def pixelize(a, rgb=None, norm=1):
	"""Convert a floating point array into an UnsignedInt8 array.

	**a** - array to be converted

	**rgb** - if true, then promote from 1 plane to 3 planes using g2rgb

	**norm** - if true, scale min-max into range 1-255

	**returns** - pixelized version of input array; result is suitable
	for assigning to <sprite>.alpha or <sprite>.array.

	"""
	if norm:
		amin = min(ravel(a))
		amax = max(ravel(a))
		a = (1.0 + 254.0 * ((a - amin) / (amax - amin))).astype(_N.uint8)
	else:
		a = a.astype(_N.uint8)
	if rgb is None:
		return a
	else:
		return g2rgb(a)

def genaxes(w, h=None, typecode=_N.float64, inverty=0):
	"""Generate two Numeric vectors for sprite axes.

	**w, h** - scalar values indicating the width and height of the
	sprite in needing axes in pixels

	**typecode** - Numeric-style typecode for the output array

	**inverty** (boolean) - if true, then axes are matlab-style with 0th
	row at the top, y increasing in the downward direction

	**returns** - pair of vectors (xaxis, yaxis) where the dimensions of
	each vector are (w, 1) and (1, h) respectively.

	**NOTE:**
	By default the coordinate system is matrix/matlab, which
	means that negative y-values are at the top of the sprite and
	increase going down the screen. This is fine if all you use the
	function for is to compute eccentricity to shaping envelopes, but
	wrong for most math. Use inverty=1 to get proper world coords..

	"""
	if h is None:
		(w, h) = w						# size supplied as pair/tuple
	x = _N.arange(0, w) - ((w - 1) / 2.0)
	if inverty:
		y = _N.arange(h-1, 0-1, -1) - ((h - 1) / 2.0)
	else:
		y = _N.arange(0, h) - ((h - 1) / 2.0)
	return x.astype(typecode)[:,_N.newaxis],y.astype(typecode)[_N.newaxis,:]


def genrad(w, h=None, typecode=_N.float64):
	"""Replaces old gend() function.

	**w, h** - width and height of sprite (height defaults to width)
	typecode: output type, defaults to Flaot65 ('d')

	**returns** - 2d matrix of dimension (w, h) containg a map of
	pixel eccentricity values.

	"""

	x, y = genaxes(w, h)
	return (((x**2)+(y**2))**0.5).astype(typecode)

def gend(w, h=None, typecode=_N.float64):
	"""OBSOLETE"""
	raise SpriteObsolete, 'gend function obsolete - use genrad'

def gentheta(w, h=None, typecode=_N.float64, degrees=None):
	"""Generate 2D theta map for sprite

	**w, h** - width and height of sprite (height defaults to width)

	**typecode** - output type, defaults to Flaot65 ('d')

	**degrees** - optionally convert to degrees (default is radians)

	**returns** - 2d matrix of dimension (w, h) containg a map of pixel theta
	values (polar coords). 0deg/0rad is 3:00 position, increasing
	values CCW, decreasing values CW.

	**NOTE:**
	Be careful, if you request an integer typecode and
	radians, the values will range from -3 to 3 .. not very
	useful!

	"""
	x, y = genaxes(w, h)
	t = _N.arctan2(y, x)
	if degrees:
		t = 180.0 * t / pi
	return t.astype(typecode)

def singrat(s, frequency, phase_deg, ori_deg, R=1.0, G=1.0, B=1.0,
			meanlum=0.5, moddepth=1.0, ppd=None, color=None):
	"""2D sine grating generator (odd symmetric)

	**s** - Sprite object

	**frequency** - frequency in cycles/sprite (or cyc/deg, if ppd is
	given)

	**phase_deg** - phase in degrees (nb: 0deg phase centers the sine
	function at sprite ctr)

	**ori_deg** - grating orientation in degrees

	**R** - red channel value (0-1) or standard pype RGB color triple

	**G** - green channel value (0-1)

	**B** - blue channel value (0-1)

	**ppd** - pixels/degree-visual-angle; if included, then it
	means that freq is being specified in cycles/degree

	**meanlum** - mean (DC) value of grating (0-1); default is 0.5

	**moddepth** - modulation depth (0-1)

	**color** - RGB triple (alternative specification of color vector)

	**NOTE:**
	Verified frequency is really cycles/sprite JM 17-sep-2006.

	"""

	if not ppd is None:
		# convert cycles/deg into cycles/sprite:
		d = (s.w + s.h) / 2.0
		frequency = d / ppd * frequency
	meanlum = 256.0 * meanlum
	moddepth = 127.0 * moddepth

	if color:
		R, G, B = color
	else:
		R, G, B = _unpack_rgb(R, G, B)
	r = (((s.xx / s.w)**2) + ((s.yy / s.h)**2))**0.5
	t = _N.arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.
	x, y = (r * _N.cos(t), r * _N.sin(t))

	i = moddepth * _N.sin((2.0 * pi * frequency * x) - (pi * phase_deg / 180.0))
	s.array[:] = _N.transpose((_N.array((R*i,G*i,B*i))+meanlum).astype(_N.uint8),
						   axes=[1,2,0])

def cosgrat(s, frequency, phase_deg, ori_deg, R=1.0, G=1.0, B=1.0,
			meanlum=0.5, moddepth=1.0, ppd=None, color=None):
	"""2D cosine grating generator (even symmetric)

	**s** - Sprite object

	**frequency** - frequency in cycles/sprite

	**phase_deg** - phase in degrees (nb: 0deg phase centers the
	cosine function at sprite ctr)

	**ori_deg** - grating orientation in degrees

	**R** - red channel value (0-1) or standard pype RGB color triple

	**G** - green channel value (0-1)

	**B** - blue channel value (0-1)

	**ppd** - pixels/degree-visual-angle; if included, then it
	means that freq is being specified in cycles/degree

	**meanlum** - mean (DC) value of grating (0-1); default is 0.5

	**moddepth** - modulation depth (0-1)

	**color** - RGB triple (alternative specification of color vector)

	**NOTE:**
	Verified frequency is really cycles/sprite JM 17-sep-2006.

	"""
	if not ppd is None:
		# convert cycles/deg into cycles/sprite:
		d = (s.w + s.h) / 2.0
		freq = d / ppd * freq
	meanlum = 256.0 * meanlum
	moddepth = 127.0 * moddepth

	if color:
		R, G, B = color
	else:
		R, G, B = _unpack_rgb(R, G, B)
	r = (((s.xx / s.w)**2) + ((s.yy / s.h)**2))**0.5
	t = _N.arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0
	x, y = (r * _N.cos(t), r * _N.sin(t))

	i = moddepth * _N.cos((2.0 * pi * frequency * x) - (pi * phase_deg / 180.0))
	s.array[:] = _N.transpose((_N.array((R*i,G*i,B*i))+meanlum).astype(_N.uint8),
						   axes=[1,2,0])

def polargrat(s, cfreq, rfreq, phase_deg, polarity, 
			  R=1.0, G=1.0, B=1.0, logpolar=0,
			  meanlum=0.5, moddepth=1.0, ppd=None, color=None):
	"""2D polar (non-Cartesian) grating generator

	**s** - Sprite object

	**cfreq** - concentric frequency (cycles/sprite or cyc/deg - see ppd)

	**rfreq** - concentric frequency (cycles/360deg)

	**phase_deg** - phase in degrees

	**polarity** - 0 or 1 -> really just a 180 deg phase shift

	**R** - red channel value (0-1) or standard pype RGB color triple

	**G** - green channel value (0-1)

	**B** - blue channel value (0-1)

	**ppd** - pixels/degree-visual-angle; if included, then it
	means that freq is being specified in cycles/degree - for
	cfreq only

	**meanlum** - mean (DC) value of grating (0-1); default is 0.5

	**moddepth** - modulation depth (0-1)

	**color** - RGB triple (alternative specification of color vector)

	**NOTE:**
	Verified frequencies are really cycles/sprite JM 17-sep-2006.

	"""

	if not ppd is None:
		# convert cycles/deg into cycles/sprite:
		d = (s.w + s.h) / 2.0
		cfreq = d / ppd * cfreq
	meanlum = 256.0 * meanlum
	moddepth = 127.0 * moddepth

	if color:
		R, G, B = color
	else:
		R, G, B = _unpack_rgb(R, G, B)
	if polarity < 0:
		polarity = -1.0
	else:
		polarity = 1.0
	x, y = (polarity * s.xx/s.w, s.yy/s.h)

	if logpolar:
		z = (log(_N.hypot(x,y)) * cfreq) + (_N.arctan2(y,x) * rfreq / (2.0 * pi))
	else:
		z = (_N.hypot(x,y) * cfreq) + (_N.arctan2(y,x) * rfreq / (2.0 * pi))
	i = moddepth * _N.cos((2.0 * pi * z) - (pi * phase_deg / 180.0))
	s.array[:] = _N.transpose((_N.array((R*i,G*i,B*i))+meanlum).astype(_N.uint8),
						   axes=[1,2,0])

def logpolargrat(s, cfreq, rfreq, phase_deg, polarity,
				 R=1.0, G=1.0, B=1.0,
				 meanlum=0.5, moddepth=1.0, ppd=None, color=None):
	"""2D log polar (non-Cartesian) grating generator

	**s** - Sprite object

	**cfreq** - concentric frequency (cycles/sprite or cycles/deg see ppd)

	**rfreq** - concentric frequency (cycles/360deg)

	**phase_deg** - phase in degrees

	**polarity** - 0 or 1 -> really just a 180 deg phase shift

	**R** - red channel value (0-1) or standard pype RGB color triple

	**G** - green channel value (0-1)

	**B** - blue channel value (0-1)

	**ppd** - pixels/degree-visual-angle; if included, then it
	means that freq is being specified in cycles/degree

	**meanlum** - meanlum (DC) value of grating (0-1); default is 0.5

	**moddepth** - modulation depth (0-1)

	**color** - RGB triple (alternative specification of color vector)

	**NOTE:**
	Frequencies are in cycles/sprite or cycles/360deg

	**NOTE:**
	Verified frequenies are really cycles/sprite JM 17-sep-2006.

	"""
	polargrat(s, cfreq, rfreq, phase_deg, polarity,
			  R=R, G=G, B=B, logpolar=1,
			  meanlum=meanlum, moddepth=moddepth, ppd=ppd)

def hypergrat(s, freq, phase_deg, ori_deg,
			  R=1.0, G=1.0, B=1.0,
			  meanlum=0.5, moddepth=1.0, ppd=None, color=None):
	"""2D hyperbolic (non-Cartesian) grating generator

	**s** - Sprite object

	**freq** - frequency (cycles/sprite or cyc/deg - see ppd)

	**phase_deg** - phase in degrees

	**ori_deg** - orientation in degrees

	**polarity** - 0 or 1 -> really just a 180 deg phase shift

	**R** - red channel value (0-1) or standard pype RGB color triple

	**G** - green channel value (0-1)

	**B** - blue channel value (0-1)

	**ppd** - pixels/degree-visual-angle; if included, then it
	means that freq is being specified in cycles/degree

	**meanlum** - mean (DC) value of grating (0-1); default is 0.5

	**moddepth** - modulation depth (0-1)

	**color** - RGB triple (alternative specification of color vector)

	**NOTE:**
	frequencies are in cycles/sprite or cycles/360deg

	**NOTE:**
	verified frequencies are really cycles/sprite JM 17-sep-2006

	"""
	if not ppd is None:
		# convert cycles/deg into cycles/sprite:
		d = (s.w + s.h) / 2.0
		freq = d / ppd * freq
	meanlum = 256.0 * meanlum
	moddepth = 127.0 * moddepth

	if color:
		R, G, B = color
	else:
		R, G, B = _unpack_rgb(R, G, B)
	r = (((s.xx / s.w)**2) + ((s.yy / s.h)**2))**0.5
	t = _N.arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0
	x, y = (r * _N.cos(t), r * _N.sin(t))

	z = _N.sqrt(_N.fabs((x * freq) ** 2 - (y * freq) ** 2))
	i = moddepth * _N.cos((2.0 * pi * z) - (pi * phase_deg / 180.0))
	s.array[:] = _N.transpose((_N.array((R*i,G*i,B*i))+meanlum).astype(_N.uint8),
						   axes=[1,2,0])


def simple_rdp(s, dir=None, vel=None, fraction=0.25,
			   fgcolor=(255,255,255), bgcolor=(128,128,128),
			   rseed=None):
	if rseed:
		old_seed = _N.random.get_state()
		_N.random.set_state(rseed)
	if dir is None:
		for n in range(3):
			if n == 0:
				m = _N.random.uniform(0.0, 1.0, (s.w, s.h))
			mc = _N.where(_N.greater(m, fraction), bgcolor[n], fgcolor[n])
			s.array[:,:,n] = mc.astype(_N.uint8)[:]
	else:
		dx = -int(round(vel * math.cos(math.pi * dir / 180.0)))
		dy = int(round(vel * math.sin(math.pi * dir / 180.0)))
		a = s.array[:,:,:]
		a = _N.concatenate((a[dx:,:,:],a[:dx,:,:]), axis=0)
		a = _N.concatenate((a[:,dy:,:],a[:,:dy,:]), axis=1)
		s.array[:,:,:] = a[:]
		
	if rseed:
		_N.random.set_state(old_seed)
		

def alphabar(s, bw, bh, ori_deg, R=1.0, G=1.0, B=1.0):
	"""Generate a bar into existing sprite using the alpha channel.

	This fills the sprite with 'color' and then puts a [bw x bh] transparent
	bar of the specified orientation in the alpha channel.

	**s** - Sprite()

	**bw,bh** - bar width and height in pixels

	**ori_deg** - bar orientation in degrees

	**R** - standard color triple (0-255) or R channel value (0-1)

	**G** - optional G channel value

	**B** - optional B channel value

	"""
	R, G, B = (_N.array(_unpack_rgb(R, G, B)) * 255.0).astype(_N.int)
	r = sprite.genrad(s.w, s.h)
	t = sprite.gentheta(s.w, s.h) + (pi * ori_deg / 180.0)
	x = r * _N.cos(t)
	y = r * _N.sin(t)
	s.fill((R,G,B))
	mask = _N.where(_N.less(abs(x), (bw/2.0)) * _N.less(abs(y), (bh/2.0)), 255, 0)
	s.alpha[:] = mask[:].astype(_N.uint8)

def alphaGaussian(s, sigma):
	"""Put symmetric Gaussian envelope into sprite's alpha channel.

	**s** - sprite

	**sigma** - standard deviation in pixels

	**NOTE:**
	alpha's have peak value of fully visible (255), low end
	depends on sigma

	"""
	r = ((s.xx**2) + (s.yy**2))**0.5
	i = 255.0 * _N.exp(-((r) ** 2) / (2 * sigma**2))
	s.alpha[:] = i[:].astype(_N.uint8)

def alphaGaussian2(s, xsigma, ysigma, ori_deg):
	"""Put non-symmetric Gaussian envelope into sprite's alpha channel.

	**s** - existing sprite

	**xsigma, ysigma** - standard deviations in pixels (think of this as the
	Gaussian's generated with ori=0 and then rotated)

	**ori_deg** - orientation of Gaussian in degrees

	**NOTE:**
	alpha's have peak value of fully visible (255), low end
	depends on sigma

	"""
	r = ((s.xx**2) + (s.yy**2))**0.5
	t = _N.arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0
	x, y = (r * _N.cos(t), r * _N.sin(t))
	i = 255.0 * _N.exp(-(x**2) / (2*xsigma**2)) * _N.exp(-(y**2) / (2*ysigma**2))
	s.alpha[:] = i[:].astype(_N.uint8)

def gaussianEnvelope(s, sigma):
	w, h = s.im.get_size()
	x, y = sprite.genaxes(w, h, _N.float)
	r = ((x**2)+(y**2))**0.5
	g = _N.exp(-((r) ** 2) / (2 * sigma**2)) / _N.sqrt(2 * pi * sigma**2);

	# note: sum(z(:)) = 1.0
	#g = _N.exp(-((x**2)) / (2 * sigma**2)) * \
	#_N.exp(-((y**2)) / (2 * sigma**2)) / (2*math.pi*sigma**2)
	gmax = max(reshape(g, [multiply.reduce(g.shape), 1]))
	g = _N.array(255.0 * g / gmax).astype(_N.uint8)
	pygame.surfarray.pixels_alpha(s.im)[:] = g

def image_circmask(im, x, y, r, apply):
	(ax, ay) = sprite.genaxes(im.get_width(), im.get_height())
	mask = _N.where(_N.less(((((ax-x)**2)+((ay-y)**2)))**0.5, r), 1, 0)
	if apply:
		a = pygame.surfarray.pixels2d(im)
		a[:] = mask * a
	else:
		raise PygameIncompleteError, 'image_circmask: !apply not implemented'

if __name__ == '__main__':
	#pass
	fb = quickinit(dpy=":0.0", w=512, h=512, bpp=32, fullscreen=0, opengl=1)
	s = Sprite(x=0, y=0, width=100, height=100, fb=fb, on=1)
	simple_rdp(s, fraction=0.05, fgcolor=(255,255,1))
	for n in range(100):
		fb.clear()
		s.blit(flip=1)
		simple_rdp(s, dir=-45, vel=2)
	
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
