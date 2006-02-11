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
"""

import math
from Numeric import *

import pygame.surfarray
from pygame.constants import *
import sprite

##########################################################################
# new, faster, clean support functions added 04-mar-2004 JAM .. stop
# using the old versions..
##########################################################################

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
    """Note: frequency are in cycles/sprite"""
    r = (((s.xx / s.w)**2) + ((s.yy / s.h)**2))**0.5
    t = arctan2(s.yy, s.xx) - (pi * (90-ori_deg)) / 180.0
	x, y = (r * cos(t), r * sin(t))

	i = 127.0 * sin((2.0 * pi * frequency * x) - (pi * phase_deg / 180.0))
    s.array[:] = transpose((array((R*i,G*i,B*i))+128).astype(UnsignedInt8),
                           axes=[1,2,0])

def cosgrat(s, frequency, phase_deg, ori_deg, R=1.0, G=1.0, B=1.0):
    """Note: frequency are in cycles/sprite"""
    r = (((s.xx / s.w)**2) + ((s.yy / s.h)**2))**0.5
    t = arctan2(s.yy, s.xx) - (pi * (90-ori_deg)) / 180.0
	x, y = (r * cos(t), r * sin(t))

	i = 127.0 * cos((2.0 * pi * frequency * x) - (pi * phase_deg / 180.0))
    s.array[:] = transpose((array((R*i,G*i,B*i))+128).astype(UnsignedInt8),
                           axes=[1,2,0])

def polargrat(s, cfreq, rfreq, phase_deg, polarity, 
             R=1.0, G=1.0, B=1.0, logpolar=0):
	"""Note: frequencies are in cycles/sprite or cycles/360deg"""
    if polarity < 0:
        polarity = -1
    else:
        polarity = 1
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
	"""Note: frequencies are in cycles/sprite or cycles/360deg"""
    polargrat(s, cfreq, rfreq, phase_deg, polarity, 
             R=1.0, G=1.0, B=1.0, logpolar=1)
    
    
def hypergrat(s, freq, phase_deg, ori_deg,
              R=1.0, G=1.0, B=1.0):
	"""Note: frequencies are in cycles/sprite or cycles/360deg"""
    r = (((s.xx / s.w)**2) + ((s.yy / s.h)**2))**0.5
    t = arctan2(s.yy, s.xx) - (pi * (90-ori_deg)) / 180.0
	x, y = (r * cos(t), r * sin(t))

	z = sqrt(fabs((x * freq) ** 2 - (y * freq) ** 2))
	i = 127.0 * cos((2.0 * pi * z) - (pi * phase_deg / 180.0))
    s.array[:] = transpose((array((R*i,G*i,B*i))+128).astype(UnsignedInt8),
                           axes=[1,2,0])

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

