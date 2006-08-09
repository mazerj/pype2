# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""
Various image manipulation functions to supplement **sprite.py**

Note that most of these (all?) work on existing sprites or
images and many that the image itself (sprite.im), not the
sprite!!!

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Tue Aug 23 11:01:19 2005 mazer
  changed ori in singrat,cosgrat etc, such that 0deg -> vertical; convention
  is that motion to left is 0deg, motion up is 90deg, orientation follow
  along orthogonally. Not sure alphaGaussian2() is correct now!!

Tue Mar  7 09:28:03 2006 mazer
  change noted above was not correct. I changed the arctan2() calls:
      t = arctan2(s.yy, s.xx) - (pi * (90-ori_deg)) / 180.0
  to
      t = arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0
  which should give the correct orientations now. Note that the
  real problem is that these functions have been broken from the
  very beginning, but handmap.py and spotmap.py (which uses the
  sprite rotate method) have corrected for this.

Tue Aug  8 14:04:36 2006 mazer
  added alphabar() function -- generates a bar stimulus from a sprite
  by filling the sprite with the specified color and then setting the
  alpha channel to let the specified bar stimulus show through.

Wed Aug  9 13:15:34 2006 mazer
  Added _unpack_rgb() to make all the stimulus generators use a common
  color specification. And documented all the grating generators.
"""

import math
import sys
from Numeric import *

import pygame.surfarray
from pygame.constants import *
import sprite

##########################################################################
# new, faster, clean support functions added 04-mar-2004 JAM .. stop
# using the old versions..
##########################################################################

def _unpack_rgb(R, G, B):
	# if R is a 3-tuple, assume it's a standard pype color spec (0-255)
	# and convert to grating RGB (0-1) values. This one's for Jon T.


	try:
		R, G, B = array(R)/255.0
	except TypeError:
		pass
	except ValueError:
		pass

	return R, G, B
    
def g2rgb(a):
	"""
	Covert a single plane (grayscale: shape=(W, H)) numeric array
	into an RGB array (shape=(W, H, 3)).
	"""
    return transpose(array([a, a, a]), axes=[1,2,0])

def pixelize(a, rgb=None, norm=1):
	"""
	Convert a floating point array into an UnsignedInt8 array suitable
	for assigning to <sprite>.alpha or <sprite>.array.
	  a: array to be converted
	  rgb: if true, then promote from 1 plane to 3 planes using g2rgb
	  norm: if true, scale min-max into range 1-255
	"""
    if norm:
        amin = min(ravel(a))
        amax = max(ravel(a))
        a = (1.0 + 254.0 * ((a - amin) / (amax - amin))).astype(UnsignedInt8)
    else:
        a = a.astype(UnsignedInt8)
    if rgb is None:
        return a
    else:
        return g2rgb(a)

def singrat(s, frequency, phase_deg, ori_deg, R=1.0, G=1.0, B=1.0):
    """
	2D sine grating generator (odd symmetric)
	
	INPUT
		s = Sprite object
		frequency = frequency in cycles/sprite
		phase_deg = phase in degrees
		ori_deg = grating orientation in degrees
		R = red channel value (0-1) or standard pype RGB color triple
		G = green channel value (0-1)
		B = blue channel value (0-1)
	
	OUTPUT
		None.
	"""
	R, G, B = _unpack_rgb(R, G, B)
    r = (((s.xx / s.w)**2) + ((s.yy / s.h)**2))**0.5
    t = arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.
	x, y = (r * cos(t), r * sin(t))

	i = 127.0 * sin((2.0 * pi * frequency * x) - (pi * phase_deg / 180.0))
    s.array[:] = transpose((array((R*i,G*i,B*i))+128).astype(UnsignedInt8),
                           axes=[1,2,0])

def cosgrat(s, frequency, phase_deg, ori_deg, R=1.0, G=1.0, B=1.0):
    """
	2D cosine grating generator (even symmetric)
	
	INPUT
		s = Sprite object
		frequency = frequency in cycles/sprite
		phase_deg = phase in degrees
		ori_deg = grating orientation in degrees
		R = red channel value (0-1) or standard pype RGB color triple
		G = green channel value (0-1)
		B = blue channel value (0-1)
	
	OUTPUT
		None.
	"""
	R, G, B = _unpack_rgb(R, G, B)
    r = (((s.xx / s.w)**2) + ((s.yy / s.h)**2))**0.5
    t = arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0
	x, y = (r * cos(t), r * sin(t))

	i = 127.0 * cos((2.0 * pi * frequency * x) - (pi * phase_deg / 180.0))
    s.array[:] = transpose((array((R*i,G*i,B*i))+128).astype(UnsignedInt8),
                           axes=[1,2,0])

def polargrat(s, cfreq, rfreq, phase_deg, polarity, 
             R=1.0, G=1.0, B=1.0, logpolar=0):
	"""
	2D polar (non-Cartesian) grating generator
	
	INPUT
		s = Sprite object
		cfreq = concentric frequency (cycles/sprite)
		rfreq = concentric frequency (cycles/360deg)
		phase_deg = phase in degrees
		polarity = 0 or 1 -> really just a 180 deg phase shift
		R = red channel value (0-1) or standard pype RGB color triple
		G = green channel value (0-1)
		B = blue channel value (0-1)
	
	OUTPUT
		None.
	"""
	R, G, B = _unpack_rgb(R, G, B)
    if polarity < 0:
        polarity = -1.0
    else:
        polarity = 1.0
    x, y = (polarity * s.xx/s.w, s.yy/s.h)

    if logpolar:
        z = (log(hypot(x,y)) * cfreq) + (arctan2(y,x) * rfreq / (2.0 * pi))
    else:
        z = (hypot(x,y) * cfreq) + (arctan2(y,x) * rfreq / (2.0 * pi))
	i = 127.0 * cos((2.0 * pi * z) - (pi * phase_deg / 180.0))
    s.array[:] = transpose((array((R*i,G*i,B*i))+128).astype(UnsignedInt8),
                           axes=[1,2,0])    

def logpolargrat(s, cfreq, rfreq, phase_deg, polarity, 
                 R=1.0, G=1.0, B=1.0):
	"""
	2D log polar (non-Cartesian) grating generator
	
	INPUT
		s = Sprite object
		cfreq = concentric frequency (cycles/sprite)
		rfreq = concentric frequency (cycles/360deg)
		phase_deg = phase in degrees
		polarity = 0 or 1 -> really just a 180 deg phase shift
		R = red channel value (0-1) or standard pype RGB color triple
		G = green channel value (0-1)
		B = blue channel value (0-1)
	
	OUTPUT
		None.
		
	Note: frequencies are in cycles/sprite or cycles/360deg
	"""
    polargrat(s, cfreq, rfreq, phase_deg, polarity, 
             R=R, G=G, B=B, logpolar=1)

def hypergrat(s, freq, phase_deg, ori_deg,
              R=1.0, G=1.0, B=1.0):
	"""
	2D hyperbolic (non-Cartesian) grating generator
	
	INPUT
		s = Sprite object
		freq = frequency (cycles/sprite)
		phase_deg = phase in degrees
		ori_deg = orientation in degrees
		polarity = 0 or 1 -> really just a 180 deg phase shift
		R = red channel value (0-1) or standard pype RGB color triple
		G = green channel value (0-1)
		B = blue channel value (0-1)
	
	OUTPUT
		None.

	Note: frequencies are in cycles/sprite or cycles/360deg
	"""

	R, G, B = _unpack_rgb(R, G, B)
    r = (((s.xx / s.w)**2) + ((s.yy / s.h)**2))**0.5
    t = arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0
	x, y = (r * cos(t), r * sin(t))

	z = sqrt(fabs((x * freq) ** 2 - (y * freq) ** 2))
	i = 127.0 * cos((2.0 * pi * z) - (pi * phase_deg / 180.0))
    s.array[:] = transpose((array((R*i,G*i,B*i))+128).astype(UnsignedInt8),
                           axes=[1,2,0])

def alphabar(s, bw, bh, ori_deg, R=1.0, G=1.0, B=1.0):
	"""
	Generate a bar stimulus in an existing sprite using the alpha channel.

	This fills the sprite with 'color' and then puts a [bw x bh] transparent
	bar of the specified orientation in the alpha channel.

	INPUT
		s = Sprite()
		bw,bh = bar width and height in pixels
		ori_deg = bar orientation in degrees
		R = standard color triple (0-255) or R channel value (0-1)
		G = optional G channel value
		B = optional B channel value
	
	OUTPUT
		None.
	"""
	R, G, B = (array(_unpack_rgb(R, G, B)) * 255.0).astype(Int)
	r = sprite.genrad(s.w, s.h)
	t = sprite.gentheta(s.w, s.h) + (pi * ori_deg / 180.0)
	x = r * cos(t)
	y = r * sin(t)
	s.fill((R,G,B))
	mask = where(less(abs(x), (bw/2.0)) * less(abs(y), (bh/2.0)), 255, 0)
	s.alpha[:] = mask[:].astype(UnsignedInt8)
	

def alphaGaussian(s, sigma):
    """
    Note: sigma in pixels
    Note: alpha's have peak value of fully visible (255),
          low end depends on sigma
    """
    r = ((s.xx**2) + (s.yy**2))**0.5
	i = 255.0 * exp(-((r) ** 2) / (2 * sigma**2))
    s.alpha[:] = i[:].astype(UnsignedInt8)

def alphaGaussian2(s, xsigma, ysigma, ori_deg):
    """
    Note: sigmas in pixels (xsigma and ysigma refer to x and y when ori=0)
    Note: alpha's have peak value of fully visible (255),
          low end depends on sigma
    NOTE: this is a hack -- it's not quite a Gabor anymore..
    """
    r = ((s.xx**2) + (s.yy**2))**0.5
    t = arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0
	x, y = (r * cos(t), r * sin(t))
	i = 255.0 * exp(-(x**2) / (2*xsigma**2)) * exp(-(y**2) / (2*ysigma**2))
    s.alpha[:] = i[:].astype(UnsignedInt8)    


##########################################################################
# old clunky support functions below.. try not to use if you can help
# it..
##########################################################################

def Make_2D_Sine(freq, phase, rot, rc, gc, bc, im):
	"""
	freq		cycles/image
	phase		phase (0=cos; deg)
	rot			rotation angle (deg)
	rc,gc,bc	red, green, blue contrast (float)
	im			target image (typically sprite.im)
	"""
	
	sys.stderr.write("Warning: use singrat instead of Make_2D_Sine!\n")
	
	w, h = im.get_size()
	x, y = sprite.genaxes(w, h, Float)
	x = x / w
	y = y / h

	r = (x**2 + y**2)**0.5
	t = arctan2(y, x) - (math.pi * (rot-90) / 180.0)
	x = r * cos(t)
	y = r * sin(t)

	# convert sin->cos phase:
	phase = phase - 90
		
	g = 127.0 * sin((2.0 * math.pi * freq * x) -
					(math.pi * phase / 180.0))
	gg = transpose(array((rc*g,gc*g,bc*g)).astype(Int),
				   axes=[1,2,0])
	pygame.surfarray.blit_array(im, gg+127)
	pygame.surfarray.pixels_alpha(im)[:] = 255

def Make_2D_Cnc_Rdl(Cord, Rord, Phase, Polarity,
					Logflag, rc, gc, bc, im):
	"""
	Cord: Concentric frequency
	Rord: Radial frequendcy
	
	NOTE: spirals have both Cord != & Rord != 0)
	
	Phase: in degrees
	Logflag:
	Polarity: -1 or +1.  This really only applies to spirals, +1
				is CCW out from center.
	im: target image (typically sprite.im)
	"""

	sys.stderr.write("Warning: use polargrat instead of Make_2D_Cnc_Rdl!\n")
	
	w, h = im.get_size()
	x, y = sprite.genaxes(w, h, Float)

	x = x * Polarity
	
	x = x / w
	y = y / h

	try:
		if Logflag:
			x = (log(hypot(x,y)) * Cord) + \
				(arctan2 (y,x) * Rord / (2.0 * math.pi))
		else:
			x = (hypot (x,y) * Cord) + \
				(arctan2 (y,x) * Rord / (2.0 * math.pi))
	except:
		print "*** PYPE ERROR ***"
		return
	
	# convert sin->cos phase:
	Phase = Phase - 90

	g = 127.0 * sin((2.0 * math.pi * x) - (math.pi * Phase / 180.0))
	
	gg = transpose(array((rc*g,gc*g,bc*g)).astype(Int),
				   axes=[1,2,0])
	pygame.surfarray.blit_array(im, gg+127)
	pygame.surfarray.pixels_alpha(im)[:] = 255

def Make_2D_Hyperbolic(Pf, Phase, Rot, rc, gc, bc, im):
	
	sys.stderr.write("Warning: use hypergrat instead of Make_2D_Hyperbolic!\n")
	
	w, h = im.get_size()
	x, y = sprite.genaxes(w, h, Float)
	x = x / w
	y = y / h

	r = (x**2 + y**2)**0.5
	t = arctan2(y, x) - (math.pi * (Rot-90) / 180.0)
	x = r * cos(t)
	y = r * sin(t)

	x = sqrt(fabs((x * Pf) ** 2 - (y * Pf) ** 2))
	
	# convert sin->cos phase:
	Phase = Phase - 90

	g = 127.0 * sin((2.0 * math.pi * x) - (math.pi * Phase / 180.0))

	gg = transpose(array((rc*g,gc*g,bc*g)).astype(Int),
				   axes=[1,2,0])
	pygame.surfarray.blit_array(im, gg+127)
	pygame.surfarray.pixels_alpha(im)[:] = 255

def gaussianEnvelope(s, sigma):
	w, h = s.im.get_size()
	x, y = sprite.genaxes(w, h, Float)
	r = ((x**2)+(y**2))**0.5
	g = exp(-((r) ** 2) / (2 * sigma**2)) / sqrt(2 * pi * sigma**2);
	
	# note: sum(z(:)) = 1.0
	#g = exp(-((x**2)) / (2 * sigma**2)) * \
	#exp(-((y**2)) / (2 * sigma**2)) / (2*math.pi*sigma**2)
	gmax = max(reshape(g, [multiply.reduce(g.shape), 1]))
	g = array(255.0 * g / gmax).astype('b')
	pygame.surfarray.pixels_alpha(s.im)[:] = g

def image_circmask(im, x, y, r, apply):
	(ax, ay) = sprite.genaxes(im.get_width(), im.get_height())
	mask = where(less(((((ax-x)**2)+((ay-y)**2)))**0.5, r), 1, 0)
	if apply:
		a = pygame.surfarray.pixels2d(im)
		a[:] = mask * a
	else:
		raise PygameIncompleteError, 'image_circmask: !apply not implemented'

def surfinfo(img):
	"""this used to be sprite::idump()"""
	import sys
	
	sys.stderr.write("%s\n" % img)
	sys.stderr.write(" colorkey:%s\n" %\
					 img.get_colorkey())
	sys.stderr.write(" get_alpha:%s\n" %\
					 img.get_alpha())
	sys.stderr.write(" HWSURFACE:%s\n" %\
					 ['no','yes'][img.get_flags()&HWSURFACE!=0])
	sys.stderr.write(" RESIZABLE:%s\n" %\
					 ['no','yes'][img.get_flags()&RESIZABLE!=0])
	sys.stderr.write(" ASYNCBLIT:%s\n" %\
					 ['no','yes'][img.get_flags()&ASYNCBLIT!=0])
	sys.stderr.write(" OPENGL:%s\n" %\
					 ['no','yes'][img.get_flags()&OPENGL!=0])
	sys.stderr.write(" OPENGLBLIT:%s\n" %\
					 ['no','yes'][img.get_flags()&OPENGLBLIT!=0])
	sys.stderr.write(" HWPALETTE:%s\n" %\
					 ['no','yes'][img.get_flags()&HWPALETTE!=0])
	sys.stderr.write(" DOUBLEBUF:%s\n" %\
					 ['no','yes'][img.get_flags()&DOUBLEBUF!=0])
	sys.stderr.write(" FULLSCREEN:%s\n" %\
					 ['no','yes'][img.get_flags()&FULLSCREEN!=0])
	sys.stderr.write(" RLEACCEL:%s\n" %\
					 ['no','yes'][img.get_flags()&RLEACCEL!=0])
	sys.stderr.write(" SRCALPHA:%s\n" %\
					 ['no','yes'][img.get_flags()&SRCALPHA!=0])


if __name__ == '__main__':
	pass
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass

