#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**Soundcard interface**

This basically provides a simple interace to pygame.mixer to generate
simple sounds using the soundcard. Simplified pure-python interace to
the pygame sound/mixer subsytem.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Fri Jan 15 13:50:04 2010 mazer

- rewrite/cleanup from scratch for numpy

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

import sys, os
import pygame
# force pygame.sndarray to use numpy for arrays instead of Numeric
pygame.sndarray.use_arraytype('numpy')

import numpy as _N

try:
	from guitools import Logger
except:
	def Logger(s):
		sys.stderr.write(s)

class SoundDevice:
	INIT = 1
	DISABLED = None
	CACHE = {}
	
	def __init__(self, disable=0):
		if SoundDevice.DISABLED:
			return
		elif disable:
			SoundDevice.DISABLED = 1
			Logger('beep: audio DISABLED\n')
			return
		elif SoundDevice.INIT:
			if not pygame.mixer.get_init() is None:
				Logger('beep: audio initialized more than once!\n')
			else:
				try:
					# nbit<0 -> signed samps
					pygame.mixer.init(22050, -16, 2, 8192)
					(SoundDevice.dafreq, SoundDevice.bits, \
					 SoundDevice.chans) = pygame.mixer.get_init()
					Logger('beep: %d hz, %d bits, chans=%d\n' % \
						   (SoundDevice.dafreq, SoundDevice.bits, \
							SoundDevice.chans))
					SoundDevice.fullrange = (2 ** (abs(SoundDevice.bits)-1)) - 1
				except pygame.error:
					Logger('beep: probable hardware access error -- DISABLED\n')
					SoundDevice.DISABLED = 1
			SoundDevice.INIT = 0
		
	def beep(self, freq, msdur, vol, risefall, wait, play):
		if not SoundDevice.DISABLED:
			try:
				s = SoundDevice.CACHE[freq,msdur,vol,risefall]
			except KeyError:
				s = self.synth(freq, msdur, vol, risefall)
				SoundDevice.CACHE[freq,msdur,vol,risefall] = s
			if play:
				while pygame.mixer.get_busy(): pass
				s.play()
				while wait and pygame.mixer.get_busy(): pass

	def synth(self, freq, msdur, vol, risefall):
		t = _N.arange(0, msdur / 1000.0, 1.0 / SoundDevice.dafreq)
		if (2*risefall) > msdur:
			risefall = msdur / 2.0
		env = -abs((t - (t[-1] / 2)) / (risefall/1000.0))
		env = env - min(env)
		env = _N.where(_N.less(env, 1.0), env, 1.0)

		if freq is None:
			y = _N.random.uniform(-1.0,1.0,t.shape)
		else:
			y = _N.sin(2.0 * _N.pi * t * freq / 2)
		y = (env * vol * SoundDevice.fullrange * y).astype(_N.int16)

		#for k in range(_N.shape(y)[0]):
		#	print k, env[k], y[k]
		
		if SoundDevice.chans == 2:
			y = _N.transpose(_N.array([y, y]))
		return pygame.sndarray.make_sound(y)
	
def __init(driver):
	if driver:
		os.environ['SDL_AUDIODRIVER'] = driver
		Logger("beep: initializing audio (driver=%s)\n" % driver)
	else:
		Logger("beep: initializing audio (driver=default)\n")
	SoundDevice()
	

def beep(freq=-1, msdur=-1, vol=1, risefall=20, wait=1, play=1,
		 init=0, driver=None):
	"""Beep the speaker using sound card.

	**freq** - tone frequency in Hz or None for a white noise burst
	
	**msdur** - tone duration in ms
	
	**vol** - tone volume (0-1)
	
	**risefall** - envelope rise and fall times (ms)

	**wait** - block until sound has been played?

	**play** - play now? if false, then just synthesize the tone pip and
	cache it to play quickly at another time

	**init** - initialize driver (default is 0/no)

	**driver** - override driver selection and force a particularly
	SDL_AUDIODRIVER device. Don't use this unless you know what you're
	doing!
	
	"""

	if init:
		__init(driver)
	else:
		SoundDevice().beep(freq, msdur,
						   vol=vol, risefall=risefall,
						   wait=wait, play=play)

def warble(base, t, volume=1, fmper=25, init=0, driver=None):
	"""Make a nice warbling sound - cheapo FM
	
	**base** - base frequency
	
	**t** - duration in ms
	
	**volume** - floating point volume (0-1)
	
	**fmper** - period of modulation frequency in ms
	
	"""

	if init:
		__init(driver)
	else:
		#beep(base, fmper, volume, play=0)
		#beep(1.01*base, fmper, volume, play=0)
		et = 0
		while et < t:
			beep(base, fmper, volume, wait=0)
			beep(1.01*base, fmper, volume, wait=0)
			et = et + (2 * fmper)

if  __name__ == '__main__':
	beep(init=1)
	
	#beep(init=1)
	#beep(440, 1000)
	#beep(None, 1000)
	warble(3*440, 100)
	#warble(500, 100)
	#warble(500, 250, volume=0)
	#warble(3*440, 100)
