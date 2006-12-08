# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""Pygame based sprite engine.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

- Mon Jan  6 18:03:09 2003 mazer

 - added userdict to Image/Sprite classes

- Tue Jul  5 12:28:24 2005 mazer

 - fastblit now pays attention to the on/off flag!

Sun Jul 24 15:46:53 2005 mazer

 - added synclevel=255 to FrameBuffer __init__ method.
 
Mon Nov 21 18:35:39 2005 mazer

 - Sprite.clone() method correctly sets the sprite name to avoid
   errors on deletion.
   
Tue Mar  7 09:26:05 2006 mazer

 - Added Sprite.rotateCW(0 and Sprite.rotateCCW() methods. This is
   because the standard pygame-based rotation method actually rotates
   CW, and really we want CCW rotation. This has previously been
   corrected at the task level..
 
Tue Mar  7 16:27:40 2006 mazer

 - oops -- missed one thing --> barsprite

Fri Mar 24 11:09:23 2006 mazer

 - fixed fb.show()/hide() methods -- I think these should work
   now, at least with the OPENGL driver..
"""

import os
import sys
import posix
import pwd
import types
import math
import copy

from Numeric import *
import pygame
import pygame.display
import pygame.event
import pygame.mouse
import pygame.image
import pygame.font
import pygame.draw
import pygame.surfarray
import pygame.transform
import pygame.movie
from pygame.constants import *
from spritetools import *

from rootperm import *
from pypedebug import keyboard

#Shinji added 17-Jan-2006:
try:
	from OpenGL.GL import *
	from OpenGL.GLU import *
	from OpenGL.GLUT import *
	GL_OK = 1
except ImportError:
	sys.stderr.write('WARNING: No PyOpenGL not installed!\n');
	GL_OK = 0

# some useful colors..
WHITE = (255, 255, 255)
BLACK = (1, 1, 1)
RED = (255, 1, 1)
GREEN = (1, 255, 1)
BLUE = (1, 1, 255)
YELLOW = (255, 255, 1)
CYAN = (1, 255, 255)
MAGENTA = (255, 1, 255)

# Get rid of the future warning (2.3) or error (2.4).
# What we really want is:
#	ALPHAMASKS = 0xff<<16, 0xff<<8, 0xff, 0xFF<<24
# but this causes a FutureWarning in Python 2.3 and a real Error
# with Python 2.4 and beyond, so instead, we do:
ALPHAMASKS = (16711680, 65280, 255, -16777216)

class PygameIncompleteError(Exception): pass
class SpriteError(Exception): pass

def _got_root():
	"""Test to see if we're running as root.
	"""
	return (posix.geteuid() == 0)

def genaxes(w, h=None, typecode=Float64, inverty=0):
	"""Generate two Numeric vectors describing the axis of a sprite
	of width w (and optional height h).

	**w, h** -- scalar values indicating the width and height of the
    sprite in needing axes in pixels
	
	**typecode** -- Numeric-style typecode for the output array
	
	**inverty** (boolean) --
	if true, then axes are matlab-style with
	0th row at the top, y increasing in the downward direction

	**returns** -- pair of vectors (xaxis, yaxis) where the dimensions of
    each vector are (w, 1) and (1, h) respectively.

    **NOTE**
	  By default the coordinate system is matrix/matlab, which means
	  that negative y-values are at the top of the sprite and increase
	  going down the screen. This is fine if all you use the function
	  for is to compute eccentricity to shaping envelopes, but wrong
	  for most math. Use inverty=1 to get proper world coords..
	"""
	if h is None:
		(w, h) = w						# size supplied as pair/tuple
	x = arange(0, w) - ((w - 1) / 2.0)
	if inverty:
		y = arange(h-1, 0-1, -1) - ((h - 1) / 2.0)
	else:
		y = arange(0, h) - ((h - 1) / 2.0)
	return x.astype(typecode)[:,NewAxis],y.astype(typecode)[NewAxis,:]

def gend(w, h=None, typecode=Float64):
	"""Same as genrad(), just here for backward compatibility.
		
	**w, h** -- width and height of sprite (height defaults to width)
	typecode: output type, defaults to Float64 ('d')
	  
	**returns** -- 2d matrix of dimension (w, h) containg a map of
	pixel eccentricity values.
	"""
	return genrad(w, h, typecode=typecode)

def genrad(w, h=None, typecode=Float64):
	"""Replaces old gend() function.
	  
	**w, h** -- width and height of sprite (height defaults to width)
	typecode: output type, defaults to Flaot65 ('d')
	  
	**returns** -- 2d matrix of dimension (w, h) containg a map of
	pixel eccentricity values.
	"""
	
	x, y = genaxes(w, h)
	return (((x**2)+(y**2))**0.5).astype(typecode)

def gentheta(w, h=None, typecode=Float64, degrees=None):
	"""Generate 2D theta map for sprite
	  
	**w, h** -- width and height of sprite (height defaults to width)
	typecode: output type, defaults to Flaot65 ('d')
	degrees: optionally convert to degrees (default is radians)
	  
	**returns** -- 2d matrix of dimension (w, h) containg a map of pixel theta
	values (polar coords). 0deg/0rad is 3:00 position, increasing
	values CCW, decreasing values CW.
	  
    **NOTE** --
	BE CAREFUL, IF YOU REQUEST AN INTEGER TYPECODE AND RADIANS,
	THE VALUES WILL RANGE FROM -3 TO 3 .. NOT VERY USEFUL!!!
	"""
	x, y = genaxes(w, h)
	t = arctan2(y, x)
	if degrees:
		t = 180.0 * t / pi
	return t.astype(typecode)

class FrameBuffer:
	def __init__(self, dpy, width, height, bpp, flags,
				 bg=1, sync=1,
				 syncsize=50, syncx=-1, syncy=-1, synclevel=255,
				 videodriver=None, dga=-1, fopengl=0):
		"""FrameBuffer class (SDL<-pygame<-pype).

		This class provides a simple wrapper for the pygame interface
		to the framebuffer device. In theory this could be an X11
		window, X11-DGA fullscreen buffer or even a raw framebuffer
		using /dev/fb0.

		**dpy** -- string containing name of X11 display to contact (None
		for default, taken from os.environ['DISPLAY']

		**width, height** -- width and height of requested display in pixels

		**bpp** -- bits per pixel, typically 24 or 32

		**flags** -- special flags defined in pygame.constants (if you imported
		this module, then you get pygame.constants for free!)
		Useful flags are: FULLSCREEN and DOUBLEBUF

		**bg** -- default background color. This can be a color tripple (r,g,b)
		or a grey scale value. Actually, it can be anything that the
		_C() function in this module can parse.

		(**dga** -- boolean flag indicating whether or not to use DGA
		mode to talk to the server. This only works on local displays
		and provides the fastest X11-based graphics performance.)
		DGA removed willmore 13-jul-2006 in favour of VIDEODRIVER

		**sync** -- boolean flag indicating whether or not to setup (and
		subsequently use) a sync pulse placed on the monkey's video
		display for external synchronization (this is to drive
		photodiode that can be used to detect the presence or
		absence of the syncpulse).

		**syncsize** -- size of sync pulse in pixels (sync pulse will be
		syncsize x syncsize pixels and located in the lower right
		corner of the screen.

		**fopengl** -- boolean flag indicating whether or not to run
		in OpenGL mode  (added 17-jan-2006 shinji)
			
		**returns** --
		None.

		**NOTE** --
		Only one instance allowed per application!
		"""

		if not dga == -1:
			sys.stderr.write('****************************************\n')
			sys.stderr.write('FrameBuffer: dga option is now obsolete!\n')
			sys.stderr.write('****************************************\n')

		self.keystack = []
		self.do_sync = sync

		if flags is None:
			flags = FULLSCREEN | DOUBLEBUF
			sys.stderr.write("Defaulted to FULLSCREEN|DOUBLEBUF mode.\n")


		# you can't have fullscreen unless you're root
		if (not _got_root()) and (flags & FULLSCREEN):
			sys.stderr.write('sprite: fullscreen only for root, ignored.\n')
			flags = flags & (~FULLSCREEN)

		self.opengl = 0
		if not GL_OK and fopengl:
			sys.stderr.write('PyOpenGL not available -- disabled GL mode.\n')
			fopengl = 0
			
		if fopengl:
			if sys.platform=='darwin':
				os.environ['SDL_VIDEODRIVER'] = 'Quartz'
			else:
				os.environ['SDL_VIDEODRIVER'] = 'x11'
			os.environ['__GL_SYNC_TO_VBLANK'] = '1'
			flags = flags | OPENGL
			self.opengl = 1
			sys.stderr.write('sprite: running in OPENGL mode\n')
			# added OpenGL mode 12-jan-2006 shinji
		elif os.environ.has_key('SDL_VIDEODRIVER'):
			if os.environ['SDL_VIDEODRIVER']=='dga' and not (flags & FULLSCREEN):
				sys.stderr.write('sprite/vid: dga from $SDL_VIDEODRIVER\n')
				sys.stderr.write('sprite/vid: dga only w/ FULLSCREEN mode\n')
				sys.stderr.write('sprite/vid: Falling back to <x11>\n')
				os.environ['SDL_VIDEODRIVER'] = 'x11'
			else:
				sys.stderr.write('sprite/vid: <%s> from $SDL_VIDEODRIVER\n' %
								 os.environ['SDL_VIDEODRIVER'])
		elif videodriver:
			if videodriver=='dga' and not (flags & FULLSCREEN):
				sys.stderr.write('sprite/vid: dga from config file...\n')
				sys.stderr.write('sprite/vid: dga only w/ FULLSCREEN mode.\n')
				sys.stderr.write('sprite/vid: Falling back to <x11>\n')
				videodriver = 'x11'
			else:
				sys.stderr.write('sprite/vid: <%s> from config file\n' %
								 videodriver)
			os.environ['SDL_VIDEODRIVER'] = videodriver
		else:
			if sys.platform=='darwin':
				videodriver = 'Quartz'
			elif (flags & FULLSCREEN):
				videodriver = 'dga'
			else:
				videodriver = 'x11'

			sys.stderr.write('sprite/vid: <%s> by default\n' %
								 videodriver)
			os.environ['SDL_VIDEODRIVER'] = videodriver

		if dpy:
			self.gui_dpy = os.environ['DISPLAY']
			self.fb_dpy = dpy
			
		self.driver = os.environ['SDL_VIDEODRIVER']

		try:
			os.environ['DISPLAY'] = self.fb_dpy
			pygame.init()
		finally:
			os.environ['DISPLAY'] = self.gui_dpy
		
		if width is None or height is None:
			modes = pygame.display.list_modes(bpp, flags)
			if len(modes) > 0:
				width = modes[0][0]
				height = modes[0][1]
				sys.stderr.write('sprite: autodetected %dx%d display size\n' %
								 (width, height))
			else:
				sys.stderr.write('sprite: can''t autodetected display size\n')
				sys.exit(1)
			
		self.w = width
		self.h = height
		self.hw = width / 2
		self.hh = height / 2
		
		try:
			maxbpp = pygame.display.mode_ok((self.w, self.h), flags, bpp)
		except pygame.error:
			sys.stderr.write("Error: Can't initialize pygame!\n")
			sys.stderr.write("       Usually this means the X server's dead!\n")
			sys.exit(1)
			
		if maxbpp == 0:
			sys.stderr.write('sprite: requested w=%d h=%d bpp=%d\n' % \
							 (self.w, self.h, bpp))
			sys.stderr.write('sprite: no joy -- mode not available\n')
			sys.exit(1)
		else:
			self.font = None
			self.flags = flags
			self.maxbpp = maxbpp
			self.fopengl = fopengl
			self.opendisplay()

		sys.stderr.write('sprite/vid: dev=<%s> (%dx%d; %d bbp)\n' % \
						 (os.environ['SDL_VIDEODRIVER'],
						  self.w, self.h, maxbpp))

		# note: for historical reasons, bg is a scalar -- grayscale only..
		self.bg = bg
		
		if self.do_sync:
			# pre-build sync/photodiode driving sprites:
			if syncx < -5000:
				self._sync_low = Sprite(syncsize, syncsize,
										(self.w/2)-(syncsize/2),
										-((self.h/2)-(syncsize/2)),
										name='sync_low',
										on=1, fb=self)
			else:
				self._sync_low = Sprite(syncsize, syncsize,
										syncx, syncy,
										name='sync_low',
										on=1, fb=self)
			self._sync_low.fill((1, 1, 1))

			if syncx < -5000:
				self._sync_high = Sprite(syncsize, syncsize,
										 (self.w/2)-(syncsize/2),
										 -((self.h/2)-(syncsize/2)),
										 name='sync_high',
										 on=1, fb=self)
			else:
				self._sync_high = Sprite(syncsize, syncsize,
										 syncx, syncy,
										 name='sync_high',
										 on=1, fb=self)
			self._sync_high.fill((synclevel, synclevel, synclevel))
		else:
			self._sync_low = None
			self._sync_high = None

		# initial sync state is OFF
		self.sync(0)

		# Timer initialized and used by flip() method for
		# checking for frame rate glitches. To enage the
		# timer check, set maxfliptime to some positive value
		# min ms in your task:
		self.maxfliptime = 0
		self.fliptimer = None


	def __del__(self):
		"""Cleanup function.
		
		Delete method here makes sure the SDL framebuffer
		will be properly closed up when pype or the current application
		closes or deletes the frame buffer.
		"""
		self.close()

	def opendisplay(self):
		if self.fopengl:
			self.screen = pygame.display.set_mode((self.w, self.h),
											  self.flags)
			# for unknown reason(s), we can not set_mode using
			# maxbpp in OpenGL mode. (shinji)
		else:
			self.screen = pygame.display.set_mode((self.w, self.h),
											  self.flags, self.maxbpp)
		pygame.display.set_caption('Pype Display (%dx%d; %d bbp)' % \
								   (self.w, self.h, self.maxbpp))

		# turn OFF the cursor!!
		self.cursor(0)

		if self.fopengl:
			glOrtho(0.0, self.w, 0.0, self.h, 0.0, 1.0)
			glEnable(GL_BLEND)
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		else:
			# set (0,0,0) to be transparent/colorkey
			self.screen.set_colorkey((0,0,0,0))
		#self.printinfo()
		
	def printinfo(self):
		vi = pygame.display.Info()
		sys.stderr.write('Video Info (driver=%s)\n' % \
						 pygame.display.get_driver())
		sys.stderr.write('  hardware accelerated=%s\n' % vi.hw)
		sys.stderr.write('  windowed modes available=%s\n' % vi.wm)
		sys.stderr.write('  video_mem=%s MB\n' % vi.video_mem)
		sys.stderr.write('  accel hardware blit=%s\n' % vi.blit_hw)
		sys.stderr.write('  accel hardware alpha blit=%s\n' % vi.blit_hw_A)
		sys.stderr.write('  accel hardware colorkey blit=%s\n' % vi.blit_hw_CC)
		
		sys.stderr.write('  accel software blit=%s\n' % vi.blit_sw)
		sys.stderr.write('  accel software alpha blit=%s\n' % vi.blit_sw_A)
		sys.stderr.write('  accel software colorkey blit=%s\n' % vi.blit_sw_CC)
		
		sys.stderr.write('  bits per pixel=%s\n' % vi.bitsize)
		
		sys.stderr.write('  bytes per pixel=%s\n' % vi.bytesize)
		sys.stderr.write('  RGBA masks=(0x%x, 0x%x, 0x%x, 0x%x)\n' % vi.masks)
		sys.stderr.write('  RGBA shifts=(0x%x, 0x%x, 0x%x, 0x%x)\n' % vi.shifts)
		sys.stderr.write('  RGBA losses=(0x%x, 0x%x, 0x%x, 0x%x)\n' % vi.losses)

		
	def calcfps(self, duration=1000):
		"""Estimate frames per second.
		
		Try to determine the approximate frame rate automatically.
		X11R6 doesn't provide a way to set or query the current video
		frame rate. To circumvent this, we just flip the page a few
		times and compute the median inter-frame interval.

		**duration** (ms) -- period of time to flip/test 

		**returns** -- float, current frame rate in Hz.
		

		**NOTE** --
		This is always going to be a rought estimate, you should
		always adjust the /etc/X11/XFConfig-4 file to set the
		exact frame rate and keep track of in with your data.
		"""
		from pype import Timer
		
		# try to estimate current frame rate
		oldsync = self.do_sync
		self.do_sync = 0
		self.clear((1,1,1))
		self.flip()
		self.clear((1,1,1))
		self.flip()

		intervals = []
		
		t = Timer()

		# page flip for up to a second..
		self.flip()
		a = t.ms()
		while t.ms() < duration:
			self.flip()
			b = t.ms()
			intervals.append(b-a)
			a = b
			
		self.do_sync = oldsync

		if len(intervals)<=1:
			sys.stderr.write('sprite: calcfps -- no photodiode? Assuming 60\n')
			return 60

		# compute estimated frame rate (Hz) based on median inter-frame
		# interval
		# this is ROUGH median -- if len(intervals) is odd, then it's
		# not quite right, but it should be close enough..
		from stats import mean, stdev
		sd = stdev(intervals)
		m = mean(intervals)
		k = []
		for i in intervals:
			if abs(i-m) < (2*sd):
				k.append(i)
		km = mean(k)
		if km == 0.0:
			sys.stderr.write('sprite: calcfps -- no photodiode? Assuming 60\n')
			return 60
		else:
			return round(1000.0 / km)

	def set_gamma(self, r, g=None, b=None):
		"""Set hardware gamma correction values (if possible).
		
		Set hardware display gammas using pygame/SDL gamma function.
		Not all hardware supports hardware gamma correction, so this
		may not always work.

		**r** -- if this is the only argument supplied, then this is the
		simply luminance gamma value and all three guns are set to
		this value.
		

		**g,b** -- green and blue gamma values. If you specify g, you'ld
		better specify b as well..
			
		Arguments are floating point numbers (1.0 is no gamma correction
		at all).
		  
	    **returns** -- TRUE on success (ie., if the hardware supports
		gamma correction)
		"""
		if g is None: g = r
		if b is None: b = r
		return pygame.display.set_gamma(r, g, b)

	def cursor(self, on=0):
		"""Turn display of the mouse cursor on or off.

		**on** -- boolean; 1 to turn the cursor on, 0 to turn it off
		  
	    **returns** -- None
		"""
		pygame.mouse.set_visible(on);

	def close(self):
		"""Close framebuffer device.
		
		Close the framebuffer and cleanup connections with the X server.
		The delete method calls this function automatically, so if you
		'del' the buffer or quit without closing, this method should
		get called automatically.
		"""
		import exceptions
		try:
			del self._sync_low
			del self._sync_high
		except AttributeError:
			pass
		pygame.display.quit()

	def _xy(self, x, y=None, sflip=None):
		"""INTERNAL
		
		Internal method for coordinate transformations
		pygame/SDL uses the standard device system used by
		most graphics libraries -- that is, (0,0) refers to
		the upper left corner of the screen, positive x values
		go to the right, positive y values down the screen. This
		takes an (x,y) pair in world coordinates ((0,0) at screen
		center, positive x to the right, positive y up the screen).

		**x, y** -- world coordinates

		**sflip** -- boolean; if true, then the y-coord is flipped (ie,
		stays in device coords).

	    **returns** -- x, y in coordinates

		**NOTE** -- users should never call this directly!!!
		"""
		if y is None:
			x, y = x
		if not sflip:
			x2 = x + (self.w / 2)
			y2 = y + (self.h / 2)
			return (x2, y2)
		else:
			x2 = (self.w / 2) + x
			y2 = (self.h / 2) - y
			return (x2, y2)

	def hide(self):
		"""hide framebuffer
		At the moment, all this does is pop out of FULLSCREEN mode
		"""
		if pygame.display.get_init():
			pygame.display.quit()

	def show(self):
		"""show framebuffer
		At the moment, all this does is restore the default pygame
		flag settings, which potentially will reactivate fullscreen
		mode.
		"""
		if not pygame.display.get_init():
			root_take()
			self.opendisplay()
			root_drop()
		
	def sync(self, state, flip=None):
		"""Draw/set sync pulse sprite
		
		Set the status of the sync pulse.
		
		**state** -- boolean; 1=light, 0=dark
		
		**flip** -- boolean; do a page flip afterwards?

		**returns** -- None
		"""
		self._sync_state = state
		if flip: 
			self.flip()

	def sync_toggle(self, flip=None):
		"""Toggle sync pulse state
		
		Toggle the status of the sync pulse. Light->dark; dark->light.

		**flip** -- boolean; do a page flip afterwards?

		**returns**
		  None
		"""
		self.sync(not self._sync_state, flip=flip)

	def clear(self, color=None, flip=None):
		"""Clear framebuffer
		
		Clear framebuffer to specified color (or default background
		color, if no color is specfied).

		**color** -- color to fill with (scalar pixel value for solid
		grey; triple scalars for an rgb value -- anything _C()
		in this module understands is ok). If no color is specified,
		then self.bg is used (set in the __init__ method).

		**flip** -- boolean; do a page flip afterwards?

		**returns** -- None
		"""
		if color is None:
			color = self.bg
		color = _C(color)
		
		if self.opengl:
			cl = [0.0]*4
			cl[0] = float(color[0])/255
			cl[1] = float(color[1])/255
			cl[2] = float(color[2])/255
			cl[3] = float(color[3])/255
			glClearColor(cl[0], cl[1], cl[2], cl[3])
			glClear(GL_COLOR_BUFFER_BIT)
		else:   
			self.screen.fill(color)
		# added OpenGL fill 12-jan-2006 shinji

		if flip:
			self.flip()

	def flip(self):
		"""Flip framebuffer (sync'd to vert-retrace, if possible)
		
		Draw the syncpulse sprite (if enabled) with the appropriate
		polarity, blit to the screen and then perform a page flip.

		In general, this method should block until the flip occurs,
		however, not all video hardware until linux supports blocking
		on page flips. So be careful and check your hardware. You
		should be able to use the calcfps() method to get a rough
		idea of the framerate, if it's very fast (>100 Hz), chances
		are that the hardware doesn't support blocking on flips.
		"""
		if self.do_sync:
			if self._sync_state == 1:
				self._sync_high.blit()
			elif self._sync_state == 0:
				self._sync_low.blit()

		if self.opengl:
			glFinish()
			# to make sure all stimuli are written to the surface.
			
		pygame.display.flip()
		if self.fliptimer is None:
			from pype import Timer
			self.fliptimer = Timer()
		else:
			elapsed = self.fliptimer.ms()
			self.fliptimer.reset()
			if (self.maxfliptime > 0) and (elapsed > self.maxfliptime):
				sys.stderr.write('warning: %dms flip\n' % elapsed)
			
		
		# JAM 12/10/2002 -- something on the sdl newsgroup suggested that
		#   flip doesn't actually block until you try to read or write
		#   the screen surface.. just in case that's true

		if self.opengl:
			pass
		else:
			self.screen.set_at((0,0), self.screen.get_at((0,0)))

	def string(self, x, y, s, color, flip=None, prefill=None, size=30):
		"""Draw string on framebuffer
		
		Write text string in default font on the framebuffer screen
		at the specified location. This is primarily useful for running
		psychophysical studies and debugging.

		**x, y** -- coordinates of string *CENTER*

		**s** -- string to write

		**color** -- RGB or greyscale color (anything _C() understands)

		**flip** -- boolean; flip after write

		**prefill** -- if specified then fill the string's bounding
		box  with the specified color (again good for _C())

		**size** -- font size in pixels
		  
	    **returns** -- None

		**NOTE** -- this requires the SDL_ttf package...
		"""
		color = _C(color)
		if self.font is None:
			pygame.font.init()
			self.font = {}

		# Try to use a cached copy of font if it's already been
		# loaded, otherwise load it and cache it. So, this can
		# be slow the first time it's called
		try:
			font = self.font[size]
		except KeyError:
			try:
				from pype import pypelib
				fontfile = pypelib('cour.ttf')
				self.font[size] = pygame.font.Font(fontfile, size)
			except ImportError:
				self.font[size] = pygame.font.Font(None, size)

		s = self.font[size].render(s, 0, color).convert()

		rawx, rawy = x, y   # need for prefill in OpenGL mode
		(x, y) = self._xy(x, -y)

		if prefill:
			if self.opengl:
				strw = s.get_width()
				strh = s.get_height()
				self.rectangle(rawx, rawy, strw*1.1, strh*1.1,
							   prefill, width=0)

			else:
				rect = (x - (1.1*s.get_width())/2, y-(1.1*s.get_height())/2,
						1.1*s.get_width(), 1.1*s.get_height())
				self.screen.fill(prefill, rect)

		if self.opengl:
			blitstr = pygame.image.tostring(s, 'RGBA', 1)
			self.pygl_setxy(x - (s.get_width()/2),
						  self.h - y - (s.get_height()/2))
                        
			glDrawPixels(s.get_width(), s.get_height(), GL_RGBA,
						 GL_UNSIGNED_BYTE, blitstr)
		else:
			self.screen.blit(s, (x - (s.get_width()/2),
                             (y - (s.get_height()/2))))

		#added OpenGL mode 12-jan-2006 shinji


		if flip:
			self.flip()

	def clearkey(self):
		"""Clear keyboard input queue
		
		Clear the keyboard buffer. The way things are currently setup
		any keystrokes coming into pype are pushed into a queue, the
		getkey() method below returns the next key in the queue
		"""
		while 1:
			if len(pygame.event.get()) == 0:
				return

	def getkey(self, wait=None, down=1):
		"""Get next keystroke from queue
		
		Return the next key in the keyboard input queue and pop
		the keystroke off the queue stack.

		**wait** -- boolean flag indicating whether or not to wait
		for a keystroke to occur.

		**down** -- boolean flag indicating whether to only accept
		downstrokes (default is true)
		
	    **returns** -- keystroke value; negative for key-up, positive
		for key-down, 0 if no keystrokes are available in the queue.
		"""
		if not pygame.display.get_init():
			return 0
		
		if len(self.keystack) > 0:
			c = self.keystack[0]
			self.keystack = self.keystack[1:]
		else:
			c = None
			while c is None:
				if not down:
					events = pygame.event.get([KEYUP,KEYDOWN])
				else:
					events = pygame.event.get([KEYDOWN])
				if len(events) > 0:
					if events[0] == KEYUP:
						c =  -(events[0].key)
					else:
						c = events[0].key
				elif not wait:
					c = 0
		if c == 19:
			# ESCAPE key for emergency exit..
			sys.stderr.write('User Requested Emergency Abort\n')
			sys.stderr.write('remember to run: pypekill\n')
			sys.exit(1)
			
		return c

	def ungetkey(self, c):
		"""unget keystroke
		
		Push a keystroke event back onto the keyboard queue. Keyboard queue
		is simulated in pype as a stack, see getkey() method for details.

		**c** -- keystroke to push back (same syntax as getkey() method above.
		"""
		self.keystack.append(c)

	def snapshot(self, filename, size=None):
		"""Save screen snapshot to file
		
		Take snapshot of the framebuffer and write it to the specified
		file.

		**filename** -- name of output file; PIL is used to write the
		file and PIL automatically determines the filetype from
		filename's extension.

		**size** -- optional size of the snapshot; PIL is used to rescale
		the image to this size. If size is left unspecified, then
		the snapshot is written at the screen's true resolution.
		"""
		import Image
		pil = Image.fromstring('RGBA', self.screen.get_size(),
							   pygame.image.tostring(self.screen, 'RGBA'))
		if size:
			pil.resize(size).save(filename)
			sys.stdout.write("Wrote %s screen to: %s\n" % (size,filename))
		else:
			pil.save(filename)
			sys.stdout.write("Wrote screen to: %s\n" % filename)

	def rectangle(self, cx, cy, w, h, color, width=0):
		"""Draw rectangle directly on framebuffer
		
		**cx, cy** -- world coords of the rectangle's **CENTER**

		**w, h** -- width and height of the rectangle in pixels

		**color** -- _C() legal color specification
		
		**width** -- 0 means fill the rectangle with the specfied color,
		anything else means draw the outline of the rectangle in
		the specified color with strokes of the specified width.
		"""
		(cx, cy) = self._xy((cx, cy), sflip=1)
		w = int(w / 2.0 + 0.5)
		h = int(h / 2.0 + 0.5)
		pointslist = (((cx - w), (cy - h)),
					  ((cx + w), (cy - h)),
					  ((cx + w), (cy + h)),
					  ((cx - w), (cy + h)),
					  ((cx - w), (cy - h)))


		if self.opengl:
			s = pygame.Surface((w*2, h*2), 32)
			s.set_colorkey((0,0,0,0))
			pygame.draw.rect(s, color, (0,0,w*2,h*2), width)
			blitstr = pygame.image.tostring(s, 'RGBA')
			self.pygl_setxy(cx-w, self.h - cy - h)
			glDrawPixels(w*2, h*2, GL_RGBA, GL_UNSIGNED_BYTE, blitstr)
		else:
			pygame.draw.polygon(self.screen, color, pointslist, width)
		#added OpenGL drawing 12-jan-2006 shinji

	def line(self, start, stop, color, width=1, flip=None):
		"""Draw line directly on framebuffer
		
		Use pygame primitive to draw a straight line on the framebuffer

		**start** -- (x,y) world coords of line's starting point

		**stop** -- (x,y) world coords of line's ending point

		**color** -- any color acceptable to _C()

		**width** -- width of line in  pixels

		**flip** -- boolean; flip after write
		"""
		color = _C(color)

		if self.opengl:
			glLineWidth(width)
			glColor3d(float(color[0])/255, float(color[1])/255,
                      float(color[2])/255)
			startpos = self._xy(start, sflip=1)
			stoppos = self._xy(stop, sflip=1)
			glBegin(GL_LINE_LOOP)
			glVertex2f(startpos[0], self.h-startpos[1])
			glVertex2f(stoppos[0], self.h-stoppos[1])
			glEnd()
		else:
			pygame.draw.line(self.screen, color,
                             self._xy(start, sflip=1), self._xy(stop, sflip=1),
                             width)

		#added OpenGL drawing 12-jan-2006

		if flip:
			self.flip()

	def circle(self, cx, cy, r, color, width=0):
		"""Draw circle directly on framebuffer

		**cx, cy** -- center coords of the circle

		**r** -- radius in pixels

		**color** -- anything _C() understands

		**width** -- width of circle in pixels. If width==0, then
		the circle gets filled instead of just drawing an outline

		Tue Apr 25 10:14:33 2006 mazer
		  GL coords are different!!! circles were flipped/mirrored
		  around the x-axis in GL-mode!!!!
		"""

		if self.opengl:
			(cx, cy) = self._xy((cx, -cy), sflip=1)
			surfsize = r*2+width
			s = pygame.Surface((surfsize, surfsize), 32)
			s.set_colorkey((0,0,0,0))
			pygame.draw.circle(s, color, (surfsize/2, surfsize/2), r, width)
			blitstr = pygame.image.tostring(s, 'RGBA')
			self.pygl_setxy(cx-surfsize/2, cy-surfsize/2)
			glDrawPixels(surfsize, surfsize, GL_RGBA, GL_UNSIGNED_BYTE, blitstr)
		else:
			(cx, cy) = self._xy((cx, cy), sflip=1)
			pygame.draw.circle(self.screen, color, (cx, cy), r, width)

		#added OpenGL drawing 12-jan-2006 shinji

	def pygl_setxy(self, x, y):
		glRasterPos2i(0,0)
		glBitmap(0, 0, 0, 0, x, y, '\0')
		# A trick for the OpenGL position setting to let us blit
		# image even if the part of sprite is outside the screen.
		# 24-jan-2006 shinji


def zoomdown(fb, cx, cy, width=100, height=100,
			 color=(255,255,255), nsteps=None):
	"""*Zoombox* handler
	
	Draw a zooming box around a fixspot location in order to draw
	the monkey's attention and make it easier to find the fixspot.
	Box starts large and bright and zooms down to the specified
	point (cx, cy).
	
	**NOTE** -- This function assumes a simple uniform background filled
	based on the fb.bg color. Boxes are drawn in the specified
	color and then erased by redrawing in the default bg color.

	**cx, cy** -- center of point to highlight/draw attention to

	**width, height** -- initial size of the highlight box

	**color** -- color of highlight box

	**nsteps** -- number of steps to highlight with; time for this
	function to execute should be roughly (nsteps*16ms)

	**returns**
	  None
	"""
	if nsteps is None:
		nsteps = round((width + height) / 4)
	dw = width / nsteps
	dh = height / nsteps
	for n in range(nsteps, 0, -1):
		fb.rectangle(cx, cy, round(dw*n), round(dh*n), color, width=2)
		fb.flip()
		fb.rectangle(cx, cy, round(dw*n), round(dh*n), fb.bg, width=2)
	fb.rectangle(cx, cy, round(dw*n), round(dh*n), fb.bg, width=2)
	fb.flip()
		

class _SurfArrayAccess:
	"""INTERNAL
	
	Surfarray accessor class for sprites.
	Makes sprite.array, sprite.alpha behave almost as though they 
	were direct references to the surfarray array3d Numeric arrays.

	For example:
	  array = self.array[:]
	  array = self.array[3:,4]
	  self.array[:] = newarray
	  self.array[4,3] = 12
	
	However, self.array is not really a Numeric array itself, so don't do:
	  BAD self.array = newarray (use self.array[:] = newarray)
	  BAD sz = size(self.array) (use size(self.array[:])).
	Similarly for self.alpha.  
	"""
	def __init__(self, im, get, set):
		self.im  = im
		self.getfn = get
		self.setfn = set

	def refresh(self, im):
		"""
		Underlying sprite array has changed -- update link/cache.
		This is for when the sprite is resized or rescaled, etc
		"""
		self.im = im
 
	def __getitem__(self, idx):
		array = self.getfn(self.im)
		return array[idx]

	def __setitem__(self, idx, value):
		array = self.setfn(self.im)
		if type(value) is arraytype:
			array[idx] = value.astype(array.typecode())
		else:
			array[idx] = value

class _ImageBase:
	"""INTERNAL -- do not instantiate!
	
	Simple base class for Sprites, Movies etc. The _ImageBase class
	simply provides a standard mechanism for implementing common
	coordinate transformations in one place.
	
	Methods for this class assume that several class variables
	are defined in the __init__ method that subclasses of this
	base class ::
	
		.centerorigin   boolean 
		.w              width in pixels
		.h              height in pixels

	**NOTE** -- This class is never intended to be instantiated by
	a user or anything other than the Sprite and MpegMovie
	classes.
	"""
	def __init__(self):
		raise SpriteError, "_ImageBase should never be instantiated directly."
	
	def XY(self, xy):
		if self.centerorigin:
			return ((self.w / 2) + xy[0], (self.h / 2) - xy[1])
		else:
			return xy
	
	def X(self, x):
		if self.centerorigin:
			return (self.w / 2) + x
		else:
			return x

	def Y(self, y):
		if self.centerorigin:
			return (self.h / 2) - y
		else:
			return y


class Sprite(_ImageBase):
	"""	
	Sprite object (wrapper for pygame surface class).

	This class was originally derrived from the Image class to
	provide a facility for Images without any direct attachment
	to hardware (namely a FrameBuffer). This is in part because
	the original version of pype used a home-grown Image class
	based on wrappers I wrote for SDL instead of pygame.

	Later when everything was switched over to use pygame instead
	of direct SDL access, the Image class was kept around. In
	Feb 2004 I cleaned up the sprite module and got rid of the
	Image class and moved everything into a single top-level
	sprite class.

	**WARNING** --
	
	- Don't access the .im member of this class directly -- this
	  is a pygame/pype internal member and shouldn't really be exposed
	  to the user.  Instead, use the .array and .alpha members and
	  standard *Numeric* functions/methods.
	"""
	
	# List of all live instantiated sprites. The list contains
	# just the sprite names, not pointers to the sprites themselves.
	# This is for debugging and garbage collection.
	__list__ = []
	
	# unique id for each sprite made:
	__id__ = 0
	
	def __init__(self, width=100, height=100, x=0, y=0, depth=0, \
				 fb=None, on=1, image=None, dx=0, dy=0, fname=None, \
				 name=None, icolor='black', centerorigin=0):
		"""Sprite instantiation function
		
		**width, height** -- width and height of sprite in pixels
		
		**x, y** -- initial sprite position (pixels in world coordinates)
		
		**depth** -- depth of sprite (for DisplayList below). The DisplayList
		class draws sprites in depth order, with large depths being
		draw first (ie, 0 is the top-most layer of sprites)

		**on** (boolean) -- sprite on or off. If the sprite is off, then
		the blit method won't actually perform the blit (see
		blit method for exceptions).

		**dx, dy** -- linear motion for sprite; if these are set, then
		each time the sprite is blitted, the position is changed
		by the specified amount.

		**fname** -- name of file to load pixel data from

		**name** -- debugging name (string) of the sprite; if not set, then
		either the filename or a unique random name is used instead.
		
		**icolor** -- color to draw icon on the UserDisplay
		
		**centerorigin** -- this determines whether the sprite's internal
		coordinate system has (0,0) at center or in the upper left
		corner. Default is origin in upper left corner!
		
	    **NOTE** --
		DEFAULT IS CENTERORIGIN=0, WHICH MEANS UPPER LEFT CORNER!
		"""
		
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy
		self.depth = depth
		self.fb = fb
		self._on = on
		self.icolor = icolor

		if fname:
			# load image data from file
			self.im = pygame.image.load(fname)
			self.userdict = {}
		elif image:
			# make a copy of the source sprite/image
			try:
				# pype Image object
				self.im = image.im.convert()
				self.userdict = copy.copy(image.userdict)
			except:
				# pygame image/surface
				self.im = image.convert()
				self.userdict = {}
		else:
			# new image from scratch
			# image/sprites should have 32 bits (RGBA)
			self.im = pygame.Surface((width, height), 0, 32)
			self.userdict = {}

		self.im = self.im.convert(ALPHAMASKS)
		self.im.set_colorkey((0,0,0,0))

		# Tue Jan 31 11:34:47 2006 mazer 
		# starting with pygame-1.6.2 pixels_alpha() pixel3d() cause
		# the surface to be locked, making it unblitable. According to
		# Pete Shinners, calling unlock after the surfarray calls
		# will solve this problem (so long as they're not RLE accelerated!)
		self.im.unlock()
		

		# generate array referencing the surface
		#self.old_array = pygame.surfarray.pixels3d(self.im)

		# Tue Jan 31 11:35:27 2006 mazer
		# see above comment re:surface locking
		self.im.unlock()

		self.w = self.im.get_width()
		self.h = self.im.get_height()
		self.iw = self.w
		self.ih = self.h
		self.centerorigin = centerorigin
		
		self.ax, self.ay = genaxes(self.w, self.h, inverty=0)
		self.xx, self.yy = genaxes(self.w, self.h, inverty=1)

		# make sure every sprite gets a name for debugging
		# purposes..
		if name:
			self.name = name
		elif fname:
			self.name = "file:%s" % fname
		else:
			self.name = "#%d" % Sprite.__id__

		# do not mess with _id!!!
		self._id = Sprite.__id__
		Sprite.__id__ = Sprite.__id__ + 1
		
		# add sprite to list of sprites (this also acts as a count,
		# since deleted sprites get deleted from the list too).
		Sprite.__list__.append(self._id)

		self.array = _SurfArrayAccess(self.im, 
									  get=pygame.surfarray.array3d,
									  set=pygame.surfarray.pixels3d)
		self.alpha = _SurfArrayAccess(self.im,
									  get=pygame.surfarray.array_alpha,
									  set=pygame.surfarray.pixels_alpha)
		

	def __del__(self):
		"""INTERNAL
		
		Clean up method. Remove the name of the sprite from the global
		list of sprites to facilitate detection of un-garbage
		collected sprites
		"""
		Sprite.__list__.remove(self._id)

	def __repr__(self):
		"""INTERNAL
		Print method. Return printable string composed of
		the name, position and depth of the sprite
		"""
		return '<Sprite "%s" @ (%d,%d) depth=%d>' % \
			   (self.name, self.x, self.y, self.depth)

	def __getitem__(self, key):
		"""INTERNAL
		
		Access method for reading single pixel from sprite.
		This allows reading pixel values from sprites using
		foo[x,y] syntax.
		  
		**x, y** -- x, y coords of pixel to read
		  
		**returns** --
		returns length 4 tuple: (r, g, b, alpha)

	    **NOTE** -- this is *very* slow!!
		"""
		(x, y) = self.XY((key[0], key[1]))
		return self.im.get_at((x, y))

	def __setitem__(self, key, value):
		"""INTERNAL
		
		Set method for single pixels. Inverse of __getitem__ above.
		This allows writing pixel values from spites using
		foo[x,y] syntax.
		  
		*x, y* -- x, y coords of pixel to read
		value - new color of pixel (r,g,b,alpha) quad..
		  
	    **NOTE** -- this is *very* slow!!
		"""
		(x, y) = self.XY((key[0], key[1]))
		return self.im.set_at((x, y), value)

	def asPhotoImage(self, alpha=None):
		"""Convert sprite to a Tkinter displayable PhotoImage

		This depends on the python imaging library (PIL)

		**alpha** -- (optional) alpha value for the PhotoImage
		  
		**returns** -- PhotoImage represenation of the sprite's pixels.
		"""
		import Image, ImageTk
		if alpha:
			im = self.im.convert()
			im.set_alpha(alpha)
		else:
			im = self.im
		self.pil_im = Image.fromstring('RGBA', im.get_size(),
									   pygame.image.tostring(im, 'RGBA'))
		self.pim = ImageTk.PhotoImage(self.pil_im)

		# NOTE: by making .pim this a object member, it keeps a handle
		#       on the PhotoImage to prevent GC..
		return self.pim

	def set_alpha(self, a):
		"""Set global alpha value

		Set transparency of the *entire* sprite to this value.
		  
		**a** -- alpha value (0-255; 0 is fully transparent, 255 is
		fully opaque).
		  
		**returns** -- None
		"""
		self.alpha[:] = a
	
	def line(self, x1, y1, x2, y2, color):
		"""Draw line of specified color in sprite
		  
		**x1,y1** -- starting coords of line in world coords
		
		**x2,y2** -- ending coords of line in world coords
		
		**color** -- line color in _C() parseable format
		
		**width** -- line width in pixels
		  
		**returns** -- None
		  
	    **NOTE** --
		  This is not the same syntaxis as the FrameBuffer.line() method!!
		"""
		color = _C(color)
		x1 = self.X(x1)
		x2 = self.X(x2)
		y1 = self.Y(y1)
		y2 = self.Y(y2)
		pygame.draw.line(self.im, color, (x1, y1), (x2, y2))

	def clear(self, color=(1,1,1)):
		"""Clear sprite to specified color

		Set's all pixels in the sprite to the indicated color, or black
		if no color is specified.
		  
		**color** -- _C() parseable color specification
		  
		**returns** -- None
		"""
		color = _C(color)
		self.im.fill(color)

	def fill(self, color):
		"""Fill sprite with specficied color
		
		Like clear method above, but requires color to be specified
		
		**color** -- _C() parseable color specification
		  
		**returns** -- None
		"""
		color = _C(color)
		self.im.fill(color)

	def noise(self, thresh=0.5):
		"""Fill sprite with noise
		
		Fill sprite with binary white noise. Threshold can be used
		to specified the DC level of the noise.
		  
		**thresh** -- threshold value [0-1] for binarizing the noise
		signal. Default's to 0.5 (half black/half white)
		  
		**returns** -- None
		"""
		from RandomArray import uniform
		
		if thresh is None:
			n = uniform(1, 255, shape=shape(self.alpha[:]))
		else:
			n = where(greater(uniform(0, 1, shape=shape(self.alpha[:])),
							  thresh), 255, 1)
		self.array[:] = transpose(array([n, n, n]),
								  axes=[1,2,0]).astype(UnsignedInt8)[:]

	def circlefill(self, color, r=None, x=None, y=None, width=0):
		"""Draw *filled* circle in sprite

		Only pixels inside the circle are affected.
		
		**color** -- _C() parseable color spec

		**r** -- circle radius in pixels

		**x, y** -- circle center position in world coords (defaults to 0,0)

		**width** -- pen width in pixels, if 0, then draw a filled circle
		  
		**returns** -- None

	    **NOTE** -- be careful about 'centerorigin'
		"""
		color = _C(color)
		if r is None:
			r = self.w / 2

		if x is None:
			x = self.w / 2
		else:
			x = self.X(x)

		if y is None:
			y = self.h / 2
		else:
			y = self.Y(y)

		pygame.draw.circle(self.im, color, (x, y), r, width)
		
	def circle(self, color, r=None, x=None, y=None):
		"""Draw circlular mask into sprite

		Pixels inside the circle are filled, rest of the sprite
		is make 100% transparent.

		**color** -- _C() parseable color spec

		**r** -- radius of circular mask

		**x, y** -- center coords of circular mask in pixels (world
		coordinates)
		  
		**returns** -- None
		"""
		color = _C(color)
		if r is None:
			r = self.w / 2

		if x is None:
			x = self.w / 2
		else:
			x = self.X(x)

		if y is None:
			y = self.h / 2
		else:
			y = self.Y(y)

		# make a circle with center color, rest transparent
		surf = pygame.Surface((r*2, r*2), 0, 8)
		try:
			surf.set_palette(((0, 0, 0), color))
		except TypeError:
			surf.set_palette(((0, 0, 0), color[0:3]))
		axis = (arange(r*2,typecode=Int)-(r-0.5))**2
		mask = sqrt(axis[NewAxis,:] + axis[:,NewAxis])
		mask = less(mask, r)

		pygame.surfarray.blit_array(surf, mask)			#apply circle data
		surf.set_colorkey(0, RLEACCEL)					#make transparent
		self.im.blit(surf, (x - r, y - r))

	def rect(self, x, y, w, h, color):
		"""Draw a *filled* rectangle of the specifed color on a sprite.

		**x, y** -- world coords for rectangle's center

		**w, h** -- width and height of rectangle in pixels

		**color** -- _C() parseable color spec
		  
		**returns** -- None

	    **NOTES** --
		
		 1. be careful about 'centerorigin'
				
		 2. parameter sequence is not the same order as circlefill()
		"""
		color = _C(color)
		x = self.X(x) - (w/2)
		y = self.Y(y) - (h/2)
		self.im.fill(color, (x, y, w, h))

	def pix(self, x, y, val=None):
		"""DO NOT USE
		
		Read/write single pixels from sprite. This is very slow!

		**x,y** -- world coords of pixel to read or write

		**val** -- if specified, then set the pixel at (x,y) to this
		value, otherwise, read the pixel at (x,y)
		  
		**returns** -- value of pixel at (x,y)

	    **NOTE** -- this is just a wrapper for pix_octr() below!
		"""
		return self.pix_octr(x, y, val=val)

	def pix_octr(self, x, y, val=None):
		"""DO NOT USE
		Read/write single pixels from sprite. This is very slow!
		"octr" stands for "object coordinates"

		**x, y** -- world coords of pixel to read or write

		**val** -- if specified, then set the pixel at (x,y) to this
		value, otherwise, read the pixel at (x,y)
		  
		**returns** -- value of pixel at (x,y)
		"""
		(x, y) = self.XY((x, y))
		if val is None:
			return self.im.get_at(x, y)
		else:
			self.im.set_at((x, y), val)
			return val

	def pix_rc(self, x, y, val=None):
		"""DO NOT USE
		Read/write single pixels from sprite. This is very slow!
		"rc" stands for "raw coords"


		**x, y** -- DEVICE coords of pixel to read or write

		**val** -- if specified, then set the pixel at (x,y) to this
		value, otherwise, read the pixel at (x,y)
		  
		**returns** -- value of pixel at (x,y)

	    **NOTE** --
		same as pix() & pix_octr() method, but uses DEVICE coords instead
		of world coords.
		"""
		if val is None:
			return self.im.get_at(x, y)
		else:
			self.im.set_at((x, y), val)
			return val

	def axisflip(self, xaxis, yaxis):
		"""flip sprite data around axes
		
		Flip image on x-axis or y-axis, whatever's true. Uses
		pygame.transform primitives, so it's fast.

		**xaxis,yaxis** (boolean) -- which axis to flip on
		  
		**returns** -- None
		"""
		new = pygame.transform.flip(self.im, xaxis, yaxis)
		self.im = new.convert(ALPHAMASKS)
		self.array.refresh(self.im)
		self.alpha.refresh(self.im)

		self.im.set_colorkey((0,0,0,0))
		self.w = self.im.get_width()
		self.h = self.im.get_height()
		self.iw = self.w
		self.ih = self.h

	def rotateCCW(self, angle, preserve_size=1, trim=0):
		self.rotate(-angle, preserve_size=preserve_size, trim=trim)

	def rotateCW(self, angle, preserve_size=1, trim=0):
		self.rotate(angle, preserve_size=preserve_size, trim=trim)
		
	def rotate(self, angle, preserve_size=1, trim=0):
		"""Lossy rotation of spite image data
		
		Rotate sprite image about the sprite's center.
		Uses pygame.transform primitives.

		**angle** -- angle of rotation in degrees

		**preserve_size** -- boolean; if true, the rotated sprite
		is clipped back down to the size of the original image.
		  
		**returns** -- None
		
		**NOTES** --
		
		 1. 'trim' ignored for now -- don't even remember what
		 it was for... totally obsolete now.

		 2. this is NOT invertable! Multiple rotations will accumulate
		 errors, so keep an original and only rotate copies. Ideal only
		 rotate things once!

		 3. 03/07/2006: note rotation direction is CW!!
		"""
		new = pygame.transform.rotate(self.im, -angle)
		if preserve_size:
			w = new.get_width()
			h = new.get_height()
			x = (w/2) - (self.w/2)
			y = (h/2) - (self.h/2)
			new = new.subsurface(x, y, self.w, self.h)
		self.im = new.convert(ALPHAMASKS)
		self.array.refresh(self.im)
		self.alpha.refresh(self.im)

		self.im.set_colorkey((0,0,0,0))
		self.w = self.im.get_width()
		self.h = self.im.get_height()
		self.iw = self.w
		self.ih = self.h
		
	def scale(self, new_width, new_height):
		"""Resize this sprite (fast).
		
		Resize a sprite using pygame/rotozoom to a new size. Can
		scale up or down equally well. Changes the data within
		the sprite, so it's not really invertable. If you want
		to save the original image data, first clone() and then
		scale().

		**new_width** -- new width in pixels

		**new_height** -- new height in pixels
		  
		**returns** -- None
		  
	    **NOTE** --
		this is NOT invertable! Scaling down and back up will
		not return the original sprite!!
		"""
		new = pygame.transform.scale(self.im, (new_width, new_height))
		self.im = new.convert(ALPHAMASKS)
		self.array.refresh(self.im)
		self.alpha.refresh(self.im)

		self.im.set_colorkey((0,0,0,0))
		self.w = self.im.get_width()
		self.h = self.im.get_height()
		self.iw = self.w
		self.ih = self.h
		
		self.ax, self.ay = genaxes(self.w, self.h, inverty=0)
		self.xx, self.yy = genaxes(self.w, self.h, inverty=1)

	def circmask(self, x, y, r):
		"""hard vignette in place --- was image_circmask"""
		mask = where(less(((((self.ax-x)**2)+((self.ay-y)**2)))**0.5, r), 1, 0)
		a = pygame.surfarray.pixels2d(self.im)
		a[:] = mask * a
		

	def alpha_aperture(self, r, x=0, y=0):
		"""Hard vignette
		
		Vignette the sprite using a hard, circular aperture.
		This method draws a hard circular mask of the specified
		size, at the specified position into the alpha channel
		of the sprite, so when it's blitted the region outside
		the aperture is masked out (fully transparent, alpha=0)

		**r** -- radius in pixels

		**x,y** -- optional aperture center in pixels (world coords)
		  
		**returns** -- None
		"""
		d = where(less((((self.ax-x)**2)+((self.ay-y)**2))**0.5, r),
				  255, 0).astype(UnsignedInt8)
		self.alpha[:] = d

	def alpha_gradient(self, r1, r2, x=0, y=0):
		"""Linear gradient vignette
		
		Vignette the sprite using a soft, linear, circular aperture.
		This method draws a linear ramped mask of the specified
		size, at the specified position into the **alpha** channel
		of the sprite, so when it's blitted the region outside
		the aperture is masked out (fully transparent, alpha=0)

		**r1,r2** -- inner,outer radii in pixels

		**x,y** -- optional aperture center in pixels (world coords)
		  
		**returns** -- None
		"""
		d = 255 - (255 * (((((self.ax-x)**2)+\
							((self.ay-y)**2))**0.5)-r1) / (r2-r1))
		d = where(less(d, 0), 0,
				  where(greater(d, 255), 255, d)).astype(UnsignedInt8)
		self.alpha[:] = d

	def alpha_gradient2(self, r1, r2, bg, x=0, y=0):
		"""Linear gradient vignette
		
		Similar to alpha_gradient() method. But the mask is applied
		*directly to the image data* (under the assumption that the
		background is a solid fill pattern with color 'bg').

		**r1,t2** -- inner,outer radii in pixels

		**bg** -- background color in _C() compatible format

		**x,y** -- coords of mask center; pixels in world coords
		  
		**returns** -- None
		"""
		d = 1.0 - ((hypot(self.ax-x, self.ay-y) - r1) / (r2 - r1))
		alpha = clip(d, 0.0, 1.0)
		i = pygame.surfarray.pixels3d(self.im)
		alpha = transpose(array((alpha,alpha,alpha)), axes=[1,2,0])
		if _is_seq(bg):
			bgi = zeros(i.shape)
			bgi[:,:,0] = bg[0]
			bgi[:,:,1] = bg[1]
			bgi[:,:,2] = bg[2]
		else:
			bgi = bg
		i[:] = ((alpha * i.astype(Float)) +
				((1.0-alpha) * bgi)).astype(UnsignedInt8)
		self.alpha[:] = 255;
	
	def dim(self, mult, meanval=128.0):
		"""Reduce sprite contrast
		
		Reduce sprite's contrast. Modifies sprite's image data.
		v = (1-mult)*(v-mean), where v is the pixel values.

		**mult** -- scale factor

		**meanval** -- assumed mean pixel value [0-255]
		  
		**returns** -- None

	    **NOTE** --
		this assumes the mean value of the image data is 'meanval',
		which is not always the case. If it's not, then you need to
		compute and pass in the mean value explicitly.
		"""
		pixs = pygame.surfarray.pixels3d(self.im)
		pixs[:] = (float(meanval) + ((1.0-mult) * \
			   (pixs.astype(Float)-float(meanval)))).astype(UnsignedInt8)
		
	def thresh(self, t):
		"""Threshold sprite image data
		
		Threshold (binarize) sprite's image data
		v =  (v > thresh) ? 255 : 1, where v is pixel value

		**t** -- threshold (0-255)
		  
		**returns** -- None
		"""
		pixs = pygame.surfarray.pixels3d(self.im)
		pixs[:] = where(less(pixs, t), 1, 255).astype(UnsignedInt8)

	def as_array(self):
		"""Return Numeric array linked to pixel data

		**This function is really obsolete -- you can access the
		same array through the '.array' field hanging off each
		instantiated sprite.**
		
		Return an array that accesses the raw pixels in the surface.
		Array is rank=3, dimensions of <Y, X, RGB>

		**returns** --
		(w, h, 3) Numeric array (type 'b') that references the raw
		sprite image data. Modifying the array modifies that image
		data.
		"""
		return pygame.surfarray.pixels3d(self.im)

	def on(self):
		"""Turn sprite on

		Sprite will get blitted.
		"""
		self._on = 1

	def off(self):
		""" Turn sprite off.

		Sprite won't be drawn, even when blit method is called.
		"""
		self._on = 0

	def toggle(self):
		"""Flip on/off flag.
		
		**returns** -- current state of flag.
		"""
		if self._on:
			self._on = 0
		else:
			self._on = 1
		return self._on

	def state(self):
		"""Get current on/off flag state.
		
		**returns** -- boolean on/off flag
		"""
		return self._on

	def moveto(self, x, y):
		"""Move sprite to new location

		**x,y** (pixels) -- framebuffer coords of new location

		  
		**returns** -- None
		"""
		self.x = x
		self.y = y

	def rmove(self, dx=0, dy=0):
		"""Relative move.

		Shifts sprite by dx,dy pixels relative to current position.

		**dx,dy** (pixels) -- framebuffer coords of new location
		  
		**returns** -- None
		"""
		self.x = self.x + dx
		self.y = self.y + dy

	def saveunder(self, restore=None):
		raise PygameIncompleteError, 'saveunder obsolete'

	def unblit(self):
		raise PygameIncompleteError, 'unblit obsolete'

	def blit(self, x=None, y=None, fb=None, flip=None, force=0, fast=None):
		"""Copy sprite to screen (block transfer)

		**x,y** (pixels) -- optional new screen location

		**fb** -- frame buffer

		**flip** (boolean) -- flip after blit?
		
		**force** (boolean) -- override on/off flag?

		**fast** -- ignored (use *flastblit()* instead)

		**NOTE** --
		
		 1. x,y,fb etc are all internal properties of each sprite. You
		   don't need to supply them here unless you want to change
		   them at the same time you blit
		   
		 2. Don't forget to **flip()** the framebuffer after blitting!!
		"""
		# note: fast is ignored now
		if not force and not self._on:
			return

		if fb is None:
			fb = self.fb
			
		if self.fb is None:
			sys.stderr.write("No fb associated with sprite on blit\n")
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
		if fb.opengl:
			scy = fb.hh + y - (self.h / 2)
			blitstr = pygame.image.tostring(self.im, 'RGBA', 1)
			fb.pygl_setxy(scx, scy)
			glDrawPixels(self.w, self.h, GL_RGBA, GL_UNSIGNED_BYTE,
                         blitstr)
		else:
			fb.screen.blit(self.im, (scx, scy))

		#added OpenGL blit 12-jan-2006 shinji

		if flip:
			fb.flip()

		# if moving sprite, move to next position..
		self.x = self.x + self.dx
		self.y = self.y + self.dy
		return 1

	def fastblit(self):
		"""Accelerated blit

		This method assumes that sprite pixels have be pre-rendered
		(using the *render()* method) to a video card native format.
		This allows pygame/SDL to do a one-to-one block transfer for
		fastest blit speed. The down sides are no alpha and you have
		to be sure to render() after each change to the image data.
		
		**NOTE** -- fastblit method does **NOT** support alpha channel
		            in the SDL mode. (OpenGL mode support alpha)
		"""
		x = self.fb.hw + self.x - (self.w / 2)
		y = self.fb.hh - self.y - (self.h / 2)
		if self.fb.opengl:
			y = self.fb.hh + self.y - (self.h / 2)
			self.fb.pygl_setxy(x, y)
			glDrawPixels(self.w, self.h, GL_RGBA, GL_UNSIGNED_BYTE,
                         self.fastim)
			return 1
		#added OpenGL fastblit(blit pre-calculated string) 12-jan-2006 shinji
		elif self._on:
			x = self.fb.hw + self.x - (self.w / 2)
			y = self.fb.hh - self.y - (self.h / 2)
			self.fb.screen.blit(self.fastim, (x, y))
			return 1
		else:
			return 0

	def render(self):
		"""Convert to image data hardware-compatible format
		
		Force coercion of internal bitmap to SDL format for speed.
		This method is really only useful in conjection with fastblit().
		
		**NOTE** --
		This may cause the bitmap to move to video memory, which is
		going to be limited!!
		"""
		if self.fb.opengl:
			self.fastim = pygame.image.tostring(self.im,'RGBA', 1)
		else:
			self.fastim = self.im.convert()

		#added opengl convert 12-jan-2006 shinji

	def unrender(self):
		"""Release memory allocated by render()
		
		See render() and fastblit() methods.
		"""
		try:
			del self.fastim
		except AttributeError:
			pass

	def subimage(self, x, y, w, h, center=None):
		"""Extract a sub-region
		
		Generates a **new** sprite from the specified sub-region of
		current sprite.

		**x,y** (pixels) -- coordinates of subregion (0,0) is upper
		left corner of parent/src sprite
		
		**w,h** (pixels) -- width and height of subregion

		**center** (boolean) -- Does (x,y) refer to the center or
		upper left corner of sprite?

		**returns** -- new sprite

		NOTE: Wed Apr 19 14:32:03 2006 mazer
		Despite what the pygame docs say about subsurface(), this
		function COPIES the image data. Changes to the subimage will
		**NOT** affect the parent!
		"""
		if center:
			x = self.X(x) - (w/2)
			y = self.Y(y) - (h/2)
		s = Sprite(image=self.im.subsurface((x, y, w, h)))
		s.x = self.x 
		s.y = self.y 
		s.dx = self.dx 
		s.dy = self.dy 
		s.depth = self.depth 
		s.fb = self.fb 
		s._on = self._on 
		return s
		
	def clone(self):
		"""Duplicate sprite
		
		Clone this sprite; make's a new instance of class Sprite
		with all data duplicated.

		NOTE: Wed Apr 19 14:32:03 2006 mazer
		Despite what the pygame docs say about subsurface(), this
		function COPIES the image data. Changes to the clone will
		**NOT** affect the parent!
		"""
		name = self.name
		s = Sprite(image=self.im.subsurface((0, 0, self.w, self.h)),
				   name = name)
		s.iw = self.iw
		s.ih = self.ih
		s.x = self.x 
		s.y = self.y
		s.dx = self.dx 
		s.dy = self.dy
		s.depth = self.depth
		s.fb = self.fb 
		s._on = self._on
		
		# copy the alpha mask too..
		s.alpha[:] = self.alpha[:]
		
		s.userdict = copy.copy(self.userdict)
		
		return s

	def setdir(self, angle, vel):
		"""Set direction of motion

		...nobody really uses this function...
		"""
		import math
		angle = math.pi * angle / 180.0
		self.dx = vel * math.cos(angle)
		self.dy = vel * math.sin(angle)

	####################
	# methods never ported to pygame (from home-brew SDL interface)
	####################

	def save(self, fname, mode='w'):
		# use pygame's save function to write image to file (PNG, JPG)
		return pygame.image.save(self.im, fname)

	def save_alpha(self, fname, mode='w'):
		"""DO NOT USE
		"""
		raise PygameIncompleteError, 'save_alpha not available'

	def save_ppm(self, fname, mode='w'):
		try:
			file = open(fname, mode)
			file.write('P6\n# pype save_ppm\n%d %d\n255\n' % (self.w, self.h))
			file.write(pygame.image.tostring(self.im, 'RGB'))
			file.close()
		except IOError:
			sys.stderr.write("Can't write %s.\n" % fname)
			return None

	def save_alpha_pgm(self, fname, mode='w'):
		try:
			file = open(fname, mode)
			file.write('P5\n# pype save_ppm\n%d %d\n255\n' % (self.w, self.h))
			a = self.alpha[:]
			file.write(a.tostring())
			file.close()
		except IOError:
			sys.stderr.write("Can't write %s.\n" % fname)
			return None


	def fix(self, w, h, color, x=None, y=None):
		"""DO NOT USE
		"""
		raise PygameIncompleteError, 'image.fix() method obsolete'

	def invert(self):
		"""DO NOT USE
		"""
		raise PygameIncompleteError, 'image.fix() method obsolete'

	def trim(self):
		"""DO NOT USE
		"""
		raise PygameIncompleteError, 'image.trim() method obsolete'

	def roll(self, dx, dy, wrap=0):
		"""DO NOT USE
		"""
		raise PygameIncompleteError, 'image.roll() method obsolete'

	####################
	# methods almost never used, thinking about deleting..
	####################

	def old_subimage(self, x, y, w, h, center=None):
		"""DO NOT USE
		
		This is the subimage method from the original Image class.
		"""
		if center:
			x = self.X(x) + (w/2) # this should be -
			y = self.Y(y) + (h/2) # this should be -
		return Image(image=self.im.subsurface((x, y, w, h)))
	
class MpegMovie(_ImageBase):
	"""Mpeg movie player

	This is a sprite-like object to knows how to open, read and
	display frames from an MPEG movie (using pygame and smpeg).
	It's not particularly powerful or flexible, but that's mostly
	due to the limitations of the smpeg library or the pygame
	interface to smpeg.
	"""
	def __init__(self, mpgfile,
				 x=0, y=0, fb=None, name=None, icolor='black'):
		"""MpegMovie instantiation function

		**mpgfile** -- full name (and path) of mpg file.

		**x,y** (pixels) -- location (center) where movie should
		be positioned on screen.

		**fb** -- framebuffer (required for playback).

		**name** -- spritge name for debugging
		
		**icolor** -- icon color for user display
		"""
		
		self.filename = mpgfile
		self.m = pygame.movie.Movie(self.filename)
		self.name = name
		self.icolor = icolor
		self.fb = fb
		(self.w, self.h) = self.m.get_size()

		(x, y) = self.fb._xy(x, y)
		x = round(x - self.w/2)
		y = round(y - self.h/2)
		self.xy = (x,y)
		self.m.set_display(self.fb.screen, self.xy)

	def getlength(self):
		"""Try to estimate number of frames in movie

		This is a hack (could fail for very long movies). It skips
		ahead 999,999 frames and then queries smpeg for the current
		video frame number.

		**returns** -- movie length in frames
		"""
		
		self.m.set_display(self.fb.screen,
				   (self.fb.w, self.fb.h, 1, 1))
		n = self.m.render_frame(999999)
		self.m.set_display(self.fb.screen, self.xy)
		return n

	def showframe(self, n):
		"""Render n-th frame directly to framebuffer.

		**n** -- frame number to render (starting with 0)

		**returns** -- current frame number or **None** at the end
		of the movie

		**NOTE** --
		This function does a page flip automatically (in fact, I don't
		know how to stop it from doing that).
		"""
		try:
			nout = self.m.render_frame(n)
		except AttributeError:
			sys.stderr.write("No MPEG in this version of pygame.\n")
			sys.exit(1)
			
		if nout == n:
			return n
		else:
			return None

class PolySprite:
	"""*Polygon* Sprite

	This is a special sprite that doesn't have image data. Instead
	it contains a bunch of points that define a polygon. I don't
	think anybody's really using this, it's something I was playing
	with.
	"""
	
	__id__ = 0
	
	def __init__(self, points, color, fb,
				 line=0, closed=0, width=1, on=1,
				 depth=0, name=None):
		"""PolySprite instantiation method

		**points** (pixels) -- polygon vertices. List of (x,y) pairs, where
		(0,0) is screen center, positive y is up, positive x is to the right.
		
		**color** -- line color
		
		**fb** -- framebuffer
		
		**line** (boolean) -- lines only? (otherwise draw filled polygon)
		
		**closed** (boolean) -- open or closed polygon?
		
		**width** (pixesl) -- line width
		
		**on** (boolean) -- just like regular Sprite class

		**depth** -- depth of sprite (for DisplayList below). The DisplayList
		class draws sprites in depth order, with large depths being
		draw first (ie, 0 is the top-most layer of sprites)

		**name** -- debugging name (string) of the sprite; if not set, then
		either the filename or a unique random name is used instead.
		"""

		if name:
			self.name = name
		else:
			self.name = "PolySprite%d" % PolySprite.__id__
		PolySprite.__id__ = PolySprite.__id__ + 1


		self.fb = fb
		self.points = []
		self.color = color
		self.line = line
		self.closed = closed
		self.width = width
		self._on = on
		self.depth = depth

		self.screen_points = []
		for (x,y) in points:
			self.screen_points.append((x,y))
			x = (self.fb.w/2) + x
			y = (self.fb.h/2) - y
			self.points.append((x,y))
			
		
	def blit(self, flip=None):
		"""Draw PolySprite
		"""
		
		if not self._on:
			return

		if self.fb and self.fb.opengl:
			if self.line:
				glLineWidth(self.width)
			glColor3d(float(self.color[0])/255,
					  float(self.color[1])/255,
					  float(self.color[2])/255)
			if self.line:
				if self.closed:
					glBegin(GL_LINE_LOOP)
				else:
					glBegin(GL_LINE_STRIP)
			else:
				glBegin(GL_POLYGON)
			for xy in self.screen_points:
				xy = self.fb._xy(xy, sflip=1)
				glVertex2f(xy[0], self.fb.h-xy[1])
			glEnd()
		else:
			if self.line:
				pygame.draw.lines(self.fb.screen, self.color, self.closed,
								  self.points, self.width);
			else:
				pygame.draw.polygon(self.fb.screen, self.color,
								  self.points, self.width);
		if flip:
			self.fb.flip()
	
	def on(self):
		"""Turn PolySprite on
		"""
		self._on = 1

	def off(self):
		"""Turn PolySprite off
		"""
		self._on = 0

class DisplayList:
	"""List of managed sprites

	A DisplayList collects and manages a set of Sprites so you
	can worry about other things.

	Each sprite is assigned a priority or stacking order. Low
	numbers on top, high numbers on the bottom. When you ask the
	display list to update, the list is sorted and blitted bottom
	to top (the order of two sprites with the same priority is
	undefined).

	The other useful thing is that the UserDisplay class (see
	userdpy.py) has a display() method that takes a display list
	and draws simplified versions of each sprite on the user display
	so the user can see (approximately) what the monkeys is seeing.

	**NOTE* -- sprites are only drawn when they are *on* (see on() and
	off() methods for Sprites).
	"""
	
	def __init__(self, fb, bg=None):
		"""Instantiation method

		**fb** -- framebuffer associated with this list. This is sort of
		redundant, since each sprite knows which framebuffer it lives
		on too. It's currently only used for clearing and flipping the
		framebuffer after updates.

		**bg** -- optional background color
		"""
		
		self.sprites = []
		self.fb = fb
		self.bg = bg

	def __del__(self):
		"""INTERNAL
		
		Called when the display list is deleted. Goes through and
		tries to delete all the member sprites. The idea is that if
		you delete the display list at the each of each trial, this
		function will clean up all your sprites automatically.
		"""
		for s in self.sprites:
			del s

	def add(self, s):
		"""Add sprite to display list
		"""
		import types
		if _is_seq(s):
			for i in s:
				self.add(i)
		else:
			for ix in range(0, len(self.sprites)):
				if s.depth > self.sprites[ix].depth:
					self.sprites.insert(ix, s)
					return
			self.sprites.append(s)

	def delete(self, s=None):
		"""Delete sprite from display list
		
		**s** (sprite) -- sprite (or list of sprites) to delete, or
		None for delete all sprites.
		
		**NOTE** -- Same as clear() and delete_all() methods if called
		with no arguments.
		"""
		if s is None:
			self.sprites = []
		elif _is_seq(s):
			for i in s:
				self.delete(i)
		else:
			self.sprites.remove(s)

	def clear(self):
		"""Delete all sprites from the display list.
		
		Same as delete_all().
		"""
		self.delete()

	def delete_all(self):
		"""Delete all sprites from display list.

		Same as clear().
		"""
		self.delete(None)

	def update(self, flip=None):
		"""Draw sprites on framebuffer

		1. Clear screen to background color (if specified)
		
		2. Draw all sprites (that are 'on') from bottom to top

		3. Optionally do a page flip.
		"""
		# clear screen to background..
		if self.bg:
			self.fb.clear(color=self.bg)
		else:
			self.fb.clear()

		# draw sprites in depth order
		for s in self.sprites:
			s.blit()

		# possibly flip screen..
		if flip:
			self.fb.flip()

	def _print(self):
		"""INTERNAL -- for debugging only
		"""
		for s in self.sprites:
			sys.stderr.write("%s\n" % s)

def _is_seq(x):
	"""INTERNAL

	Is x a sequence (list or tuple)

	**returns** -- boolean
	"""
	
	return (type(x) is types.ListType) or (type(x) is types.TupleType)

def barsprite(w, h, angle, color, **kw):
	"""Make a bar

	Front end for the Sprite instantiation method. This makes a sprite
	of the specificed width and hight, fills with the specified color
	(or noise) and rotates the sprite to the specified angle.

	This _really_ should be a class that inherits from Sprite().

	**return** -- sprite containing the requested bar
	"""
	s = apply(Sprite, (w, h), kw)
	if color == (0,0,0):
		s.noise(0.50)
	else:
		s.fill(color)
	s.rotate(angle, 0, 1)
	return s

def barspriteCW(w, h, angle, color, **kw):
	return apply(barsprite, (w, h, angle, color), kw)

def barspriteCCW(w, h, angle, color, **kw):
	return apply(barsprite, (w, h, -angle, color), kw)

def fixsprite(x, y, fb, fix_size, color, bg):
	"""fixation target sprite generator

	Generates a simple sprite containing an _industry standard_
	fixation target :-) Target is a solid filled circle of the
	specified color.

	**x,y** (pixels) -- location of target (center)

	**fb** -- frame buffer

	**fix_size** (pixels) -- radius of target (use _ZERO_ for single pixel
	target)

	**color** -- fill color

	**bg** -- background color

	**returns** -- new sprite containing the target
	"""
	if fix_size > 0:
		d = 2 * fix_size
		if (d % 2) == 0:
			d = d + 1						# make it odd..
		fixspot = Sprite(d, d, x, y, fb=fb, depth=0, on=0)
		fixspot.fill(bg)
		fixspot.circle(color=color, r=fix_size)
	else:
		fixspot = Sprite(1, 1, x, y, fb=fb, depth=0, on=0)
		fixspot.fill(color)
	return fixspot

def fixsprite2(x, y, fb, fix_size, fix_ring, color, bg):
	"""fancy fixation target sprite generator

	Generates a sprite containing a circular fixation target
	surrounded by an annulus of black (to increase detectability).

	**x,y** (pixels) -- location of target (center)

	**fb** -- frame buffer

	**fix_size** (pixels) -- radius of target (use _ZERO_ for single pixel
	target)

	**fix_ring** (pixels) -- radius of annulus

	**color** -- fill color

	**bg** -- background color

	**returns** -- new sprite containing the target
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
	if fix_size > 0:
		fixspot.circle(color=color, r=fix_size)
	else:
		fixspot.pix(fixspot.w/2, fixspot.h/2, color)

	return fixspot

def _C(color):
	"""INTERNAL

	Color specification normalization (used to be called _colorfix()_)

	Takes number of similar "color" specifications and tries to
	convert them all into a common format compatible with pygame.
	Currently that means a tuple of length 4:
		(red, green, blue, alpha)
	"""
	try:
		if len(color) == 1:
			# color is grayscale --> convert to rgba
			color = (color, color, color, 255)
		elif len(color) == 3:
			# color is list or tuple of length 3, add alpha=255
			color = color + (255,)
		elif len(color) == 4:
			# color is list or tuple of length 3, add nothing
			color = color
	except TypeError:
		# color is grayscale --> convert to rgba
		if color < 255:
			color = (color, color, color, 255)
		else:
			# this is ALSO python 2.4 fodder:
			##colorout = (color&0x00ff0000, \
			##			color&0x0000ff00, \
			##			color&0x000000ff, \
			##			color&0xff000000)
			# instead, let's try this:
			color = (color&ALPHAMASKS[0], \
					 color&ALPHAMASKS[1], \
					 color&ALPHAMASKS[2], \
					 color&ALPHAMASKS[3])
	return color

def color24(color):
	"""DO NOT USE; OBSOLETE
	"""
	raise PygameIncompleteError, 'sprite.color24() obsolete'

def grey24(g, alpha=255):
	"""DO NOT USE; OBSOLETE
	"""
	raise PygameIncompleteError, 'sprite.grey24() obsolete'

def gray24(g, alpha=255):
	"""DO NOT USE; OBSOLETE
	"""
	raise PygameIncompleteError, 'sprite.gray24() obsolete'

def quickinit(dpy=":0.0", w=100, h=100, bpp=32, flags=0, opengl=0):
	"""Quickly setup and initialize framebuffer

	**dpy** (string) -- display string
	
	**w,h** (pixels) -- width and height of display

	**bpp** (int) -- bits per pixel (display depth)

	**flags** -- pygame/SDL flags. If you have to ask, you shouldn't
	be using this feature or function...
	
	(**dga** (boolean) -- try to use dga (full screen) mode? Be careful,
	you can lock up the machine by getting into full screen mode with
	no way to get out!)
	DGA removed willmore 13-jul-2006 in favour of VIDEODRIVER

	**returns** -- live frame buffer
	"""
	return FrameBuffer(dpy, w, h, bpp, flags, sync=None, fopengl=opengl)


if __name__ == '__main__':
	sys.stderr.write('%s should never be loaded as main.\n' % __file__)
	sys.exit(1)
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass

