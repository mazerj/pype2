#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""
**Interface to pygame.mixer**

New sound I/O module. Simplified pure-python interace to the pygame
sound/mixer subsytem.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Thu Dec  8 13:10:49 2005 mazer

- This is a complete replacement for the old beep.py module. It
  provides a very simple interface to the pygame mixer subsystem.
  Basically there are only two user-accessible functions: beep()
  and nobeep().

  beep(freq=-1, msdur=-1, vol=0.5, risefall=20, wait=1, play=1)
  
  - beep(-1, -1) will initialize the pygame subsystem
	
  - beep(freq=None,...) generates a noise burst
	
  - beep(freq=int,...) generates a tone pip

  nobeep() disables the sound subsystem; if called before beep(), then
  the pygame sound system won't be initialized at all (this
  is useful in case of problems).
 
Tue Jan 27 12:16:59 2009 mazer

- minor cleanup/simplification and testing

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

import sys, os
import pygame, pygame.mixer, pygame.sndarray
from Numeric import *

try:
	from guitools import Logger
except:
	def Logger(s):
		sys.stderr.write(s)

class _Beeper:
	_init = 1
	_disabled = None
	
	def __init__(self, disable=0):
		if _Beeper._disabled:
			return
		elif disable:
			_Beeper._disabled = 1
			Logger('_Beeper: audio disabled\n')
			return
		elif _Beeper._init:
			if pygame.mixer.get_init() is not None:
				Logger('_Beeper: audio was initialized!\n')
			try:
				# negative values for word size indicates to driver
				# that samples are 'signed'
				pygame.mixer.init(22050, -16, 1, 8192)
			except pygame.error:
				Logger('_Beeper: probable hardware access error -- disabled\n')
				_Beeper._disabled = 1
				return
				
			i = pygame.mixer.get_init()
			Logger('_Beeper: %d hz, %d bits, stereo=%d\n' % i)
			(_Beeper.dafreq, _Beeper.bits, _Beeper.stereo) = i
			_Beeper.cache = {}
			_Beeper._init = 0
		
	def beep(self, freq, msdur, vol, risefall, wait, play):
		if _Beeper._disabled:
			#print '[beep]'
			return
		try:
			s = _Beeper.cache[freq,msdur,vol,risefall]
		except KeyError:
			s = self.synth(freq, msdur, vol, risefall)
			_Beeper.cache[freq,msdur,vol,risefall] = s
		if play:
			# wait for free mixer...
			while pygame.mixer.get_busy():
				pass
			s.play()
			if wait:
				while pygame.mixer.get_busy():
					pass

	def synth(self, freq, msdur, vol, risefall):
		t = arange(0, msdur / 1000.0, 1.0 / _Beeper.dafreq)
		s = zeros((t.shape[0], 2))
		# use trapezoidal envelope with risefall (below) time
		if msdur < 40:
			risefall = msdur / 2.0
		env = -abs((t - (t[-1] / 2)) / (risefall/1000.0))
		env = env - min(env)
		env = where(less(env, 1.0), env, 1.0)

		fullrange = power(2, abs(_Beeper.bits)-1)

		if freq is None:
			import RandomArray
			y = (env * vol * fullrange * \
				 RandomArray.random(t.shape)).astype(Int16)
		else:
			y = (env * vol * fullrange * \
				 sin(2.0 * pi * t * freq)).astype(Int16)

		if _Beeper.stereo:
			s[:,0] = y
			s[:,1] = y
			s = pygame.sndarray.make_sound(s)
		else:
			s = pygame.sndarray.make_sound(y)
			k = pygame.sndarray.samples(s)
		return s
	
def beep(freq=-1, msdur=-1, vol=0.5, risefall=20, wait=1, play=1, driver=None):
	if not driver is None:
		if len(driver) > 0:
			# empty string is use default..
			os.environ['SDL_AUDIODRIVER'] = driver
			Logger("beep: initializing '%s' audio\n" % driver)
		else:
			Logger("beep: initializing default audio\n")
		_Beeper()
	else:
		_Beeper().beep(freq, msdur,
					  vol=vol, risefall=risefall, wait=wait, play=play)

def nobeep():
	_Beeper(disable=1)
	Logger('nobeep: audio disabled by user config\n')


def warble(base, t, volume=1, fmper=25):
	beep(base, fmper, volume, play=0)
	beep(1.01*base, fmper, volume, play=0)
	et = 0
	while et < t:
		beep(base, fmper, volume, wait=0)
		beep(1.01*base, fmper, volume, wait=0)
		et = et + (2 *fmper)

if  __name__ == '__main__':
	beep(driver='')
	warble(500, 100)
	warble(500, 250, volume=0)
	warble(3*440, 100)
	
	
