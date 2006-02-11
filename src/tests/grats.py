#!/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
New Numeric/pygame grating codes

Thu Mar  4 17:15:40 2004 mazer:
 these are all now in src/pype/spritetools.py .. partially documented
"""

import sys

from Numeric import *
from sprite import *
from pygame.constants import *
from spritetools import *
from psycho import *

def g2rgb(a):
    return transpose(array([a, a, a]), axes=[1,2,0])

def pixelize(a, rgb=None, norm=1):
    if norm:
        amin = min(ravel(a))
        amax = max(ravel(a))
        a = (255.0 * ((a - amin) / (amax - amin))).astype(UnsignedInt8)
    else:
        a = a.astype(UnsignedInt8)
    if rgb is None:
        return a
    else:
        return g2rgb(a)

def show(s):
    s.blit(flip=1)

def singrat(s, frequency, phase_deg, ori_deg, R=1.0, G=1.0, B=1.0):
    """Note: frequency are in cycles/sprite"""
    r = (((s.xx / s.w)**2) + ((s.yy / s.h)**2))**0.5
    t = arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0
	x, y = (r * cos(t), r * sin(t))

	i = 127.0 * sin((2.0 * pi * frequency * x) - (pi * phase_deg / 180.0))
    s.array[:] = transpose((array((R*i,G*i,B*i))+127).astype(UnsignedInt8),
                           axes=[1,2,0])

def cosgrat(s, frequency, phase_deg, ori_deg, R=1.0, G=1.0, B=1.0):
    """Note: frequency are in cycles/sprite"""
    r = (((s.xx / s.w)**2) + ((s.yy / s.h)**2))**0.5
    t = arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0
	x, y = (r * cos(t), r * sin(t))

	i = 127.0 * cos((2.0 * pi * frequency * x) - (pi * phase_deg / 180.0))
    s.array[:] = transpose((array((R*i,G*i,B*i))+127).astype(UnsignedInt8),
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
    s.array[:] = transpose((array((R*i,G*i,B*i))+127).astype(UnsignedInt8),
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
    t = arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0
	x, y = (r * cos(t), r * sin(t))

	z = sqrt(fabs((x * freq) ** 2 - (y * freq) ** 2))
	i = 127.0 * cos((2.0 * pi * z) - (pi * phase_deg / 180.0))
    s.array[:] = transpose((array((R*i,G*i,B*i))+127).astype(UnsignedInt8),
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
    """
    r = ((s.xx**2) + (s.yy**2))**0.5
    t = arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0
	x, y = (r * cos(t), r * sin(t))
	i = 255.0 * exp(-(x**2) / (2*xsigma**2)) * exp(-(y**2) / (2*ysigma**2))
    s.alpha[:] = i[:].astype(UnsignedInt8)    
    

N = 128

fb = PsychoFrameBuffer(None, 256, 256, 32, dga=None, gamma=1.0,
                       flags=DOUBLEBUF|HWSURFACE)

s = Sprite(width=N, height=N, x=0, y=0, depth=0, \
           fb=fb, on=1, image=None, dx=0, dy=0,
           fname=None, name="test")

while 1:
    for phi in arange(0, 360, 20):
        fb.clear()
        singrat(s, 3, phi, 45.0)
        alphaGaussian2(s, 20, 30, 45)
        #hypergrat(s, 3, 0, phi)
        #polargrat(s, 1, 10*phi/360, 0, 1)
        show(s)

fb.close()
