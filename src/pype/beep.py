#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""Interface to pygame.mixer

New sound I/O module. Simplified pure-python interace to the pygame
sound/mixer subsytem.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

- Thu Dec  8 13:10:49 2005 mazer

 - This is a complete replacement for the old beep.py module. It
   provides a very simple interface to the pygame mixer subsystem.
   Basically there are only two user-accessible functions:

   beep(freq=-1, msdur=-1, vol=0.5, risefall=20, wait=1, play=1):
	   beep(-1, -1) will initialize the pygame subsystem
	   beep(freq=None,...) generates a noise burst
	   beep(freq=int,...) generates a tone pip

   nobeep()
       disables the sound subsystem; if called before beep(), then
	   the pygame sound system won't be initialized at all (this
	   is useful in case of problems).
 
"""

import sys
import pygame, pygame.mixer, pygame.sndarray
from Numeric import *

from guitools import Logger

class _Beeper:
	_init = 1
	_disabled = None
	
	def __init__(self, disable=0):
		if _Beeper._disabled:
			return
		elif disable:
			_Beeper._disabled = 1
			Logger('_Beeper.init: audio disabled\n')
			return
		elif _Beeper._init:
			if pygame.mixer.get_init() is not None:
				Logger('_Beeper.init: audio was initialized!\n')
			try:
				pygame.mixer.init(22050, -16, 1)
			except:
				import pypedebug
				pypedebug.get_traceback(1)
				sys.stderr.write('_Beeper.init: audio disabled -- no access!\n')
				_Beeper._disabled = 1
				return
				
			i = pygame.mixer.get_init()
			Logger('_Beeper.init: %d hz, %d bits, stereo=%d\n' % i)
			(_Beeper.daf, _Beeper.bits, _Beeper.stereo) = i
			_Beeper.cache = {}
			_Beeper._init = 0

			#for n in range(3):
			#	self.beep(440, 25, 0.5, 20, 1, 1)
			#	self.beep(540, 25, 0.5, 20, 1, 1)
		
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
			s.play()
			if wait:
				while pygame.mixer.get_busy() > 0:
					pass
				#pygame.mixer.stop()
		
	def synth(self, freq, msdur, vol, risefall):
		t = arange(0, msdur / 1000.0, 1.0 / _Beeper.daf)
		s = zeros((t.shape[0], 2))
		# use trapezoidal envelope with risefall (below) time
		if msdur < 40:
			risefall = msdur / 2.0
		env = -abs((t - (t[-1] / 2)) / (risefall/1000.0))
		env = env - min(env)
		env = where(less(env, 1.0), env, 1.0)

		if freq is None:
			import RandomArray
			y = (env * vol * pow(2, abs(_Beeper.bits)-1) * \
				 RandomArray.random(t.shape)).astype(Int16)
		else:
			y = (env * vol * pow(2, abs(_Beeper.bits)-1) * \
				 sin(2.0 * pi * t * freq)).astype(Int16)
		if _Beeper.stereo:
			s[:,0] = y
			s[:,1] = y
			s = pygame.sndarray.make_sound(s)
		else:
			s = pygame.sndarray.make_sound(y)
		return s
	
def beep(freq=-1, msdur=-1, vol=0.5, risefall=20, wait=1, play=1):
	if freq < 0:
		# just initialize pygame mixer and return
		_Beeper()
	else:
		_Beeper().beep(freq, msdur,
					  vol=vol, risefall=risefall, wait=wait, play=play)

def nobeep():
	_Beeper(disable=1)
	

if  __name__ == '__main__':
	beep(-1,-1)
	#nobeep()
	beep(440, 25, 0.2, play=0)
	beep(540, 25, 0.2, play=0)
	for n in range(25):
		beep(440, 25, 0.2, wait=1)
		beep(540, 25, 0.2, wait=1)
