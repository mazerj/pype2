#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Module of tools I use a lot
"""

import sys
from pype   import *
from sprite import *

def make_mirror(s,key):
    mir=s.clone()
    mir.userdict['itype']=key
    mir.name="%d%s"%(mir.userdict['inum'],key)
    if key=='b':
        mir.axisflip(0,0) #no flip
    elif key=='d':
        mir.axisflip(1,0) #horiz flip
    elif key=='p':
        mir.axisflip(0,1) #vert flip
    elif key=='q':
        mir.axisflip(1,1) #both
    else:
        warn("Mirror", "Mirror key %s invalid, use b,d,p,q"%key,wait=1)
    mir.ih = mir.userdict['r']*2
    mir.iw = mir.userdict['r']*2
    
    return mir


def fixsprite_log(x, y, fb, fix_size, fix_ring, color, bg):
	"""
	From fixsprite2 in sprite.py
	Fixspot of radius fix_size pixels, 0 for one pixel.
	fix_ring species an annulus of black around the center 'color' patch
	ring grades linearly from black to bg color
	"""
	d = 2 * fix_size
	if (d % 2) == 0:
		d = d + 1

	ringd = 2 * fix_ring
	if (ringd % 2) == 0:
		ringd = ringd + 1

	fixspot = Sprite(ringd, ringd, x, y, fb=fb, depth=0, on=0)
	fixspot.fill(bg)

	fixspot.circle(color=(1,1,1), r=fix_ring)

	#replace call to alpha_gradient
	# taking log, need no zeros
	ax=where(fixspot.ax!=0,fixspot.ax,1)
	ay=where(fixspot.ay!=0,fixspot.ay,1)
	
	d = 255 - (255 * (log(((ax**2)+(ay**2))**0.5) \
					  / log(fix_ring)))
	d = where(less(d, 0), 0,
			  where(greater(d, 255), 255, d)).astype(UnsignedInt8)

	fixspot.alpha[:] = d
	#make fix spot or pixel
	if fix_size > 0:
		fixspot.circle(color=color, r=fix_size)
	else:
		fixspot.pix(fixspot.w/2, fixspot.h/2, color)

	return fixspot

def makenoise(mod_depth,mod_image,side):
    from RandomArray import uniform
    if len(mod_image) == 0:
        # no image supplied
        # returns uniform white noise [0-1] as 3-d array
        noise = uniform(0, mod_depth, shape=(side,side))
        tmp = zeros((side,side,3), Float)
        tmp[:,:,0] = noise[:]
        tmp[:,:,1] = noise[:]
        tmp[:,:,2] = noise[:]
        noise = tmp;
    else:
        # image file supplied
        # returns an image scaled to [0-1] as 3-d array
        tmp = Sprite(fname=mod_image)
        tmp = tmp.subimage(0, 0, side, side, center=1)
        noise = mod_depth * (tmp.astype(Float) - 128.0) / 128.0
    return noise

def noisemask(mod_depth,mod_image,sprites):
    for s in sprites:
        noise=makenoise(mod_depth,mod_image,max([s.h, s.w]))
        s.array[:] = (s.array[:].astype(Float) * noise[:]).astype(UnsignedInt8)
    return sprites


fb = quickinit(dpy=":0.0", w=256, h=256, bpp=32, fullscreen=0, opengl=1)

N=128
s = Sprite(width=N, height=N, x=0, y=0, depth=0, \
           fb=fb, on=1, image=None, dx=0, dy=0,
           fname=None, name="test")

s.clear((255,255,255))
noisemask(1.0, '', [s])


keyboard()

fb.close()
