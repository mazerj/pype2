# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**Default Configuration Variables**

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Tue Jun 26 14:21:36 2007 mazer 

- abstract out from pype.py to put all config vars in a single
  file for documentation/code-clarity purposes.

Tue Mar 31 13:59:22 2009 mazer

- added TESTPAT

"""
__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

import os
import config

def defaults(srcfile):

    # load config directory from source file (usually Config.$HOSTNAME)
    c = config.Config(srcfile)

    # merge with list of default/initial values -- these values will
    # NOT override what's in the config file (override=None), so they
    # will only be set if not set in the config file (ie, these are
    # the default values).

    #####################################################
    # general settings
    
    c.set('DEBUG', '0')                 # debug mode
    c.set('SPLASH', '1')                # show splash screen on startup
    
    #####################################################
    # physical hardware (i/o) settings
    
    c.set('DACQ_SERVER',
          'comedi_server')              # name of DACQ executable
    c.set('ARANGE',	'10.0')             # set analog input volt. range (+-V)
    c.set('PPORT', '-1')                # enable parallel port access
                                        # specific 1 for default or
                                        # 0xNNN for non-default
    c.set('FLIP_BAR', '0')              # flip response  bar input polarity
    c.set('FLIP_SW1', '0')              # flip user switch 1 input polarity
    c.set('FLIP_SW2', '0')              # flip user switch 1 input polarity
    c.set('ENABLE_SW1', '1')            # enable/disable SW1
    c.set('REWARD_BEEP', '1')           # beep when giving rewards?
    c.set('SOUND', '1')                 # access to sound card?
    
    c.set('USB_JS_DEV',	'')             # enable USB joystick -- device file

    #####################################################
    # graphics display screen parameters

    c.set('MONW', '-1')                 # physical monitor width (cm)
    c.set('MONH', '-1')                 # physical monitor height (cm)
    c.set('VIEWDIST', '-1')             # physical viewing distance (cm)
    c.set('MON_ID', '')                 # ID string for data file

    c.set('DPYW', '1024')               # display width (pix)
    c.set('DPYH', '768')                # display height (pix)
    c.set('DPYBITS', '32')              # bit-depth for display
    c.set('FPS', '0')                   # desired frame rate (frames/sec)
    c.set('GAMMA', '1.0')               # default gamma value
    c.set('FULLSCREEN', '1')            # full screen mode?
    
    c.set('OPENGL',	 '0')               # enable OpenGL graphics
    
    c.set('SYNCSIZE', '50')             # size of sync pulse square (pix)
    c.set('SYNCX', None)                # X location of sync square CENTER (pix)
    c.set('SYNCY', None)                # Y location of sync square CENTER (pix)
                                        #  (None means autoconfig to lower right)
    c.set('SYNCLEVEL', '255')           # gray scale value of sync-on
    c.set('TESTPAT', None)              # filename for test pattern

    if os.environ.has_key('DISPLAY'):   # display device for graphics
        c.set('SDLDPY', os.environ['DISPLAY'])
    else:
        c.set('SDLDPY', ':0.1')

    if not c.iget('FULLSCREEN'):
        # if not using FULLSCREEN mode, then force the graphics to
        # be displayed locally (in a window)
        if os.environ.has_key('DISPLAY'):
            c.set('SDLDPY', os.environ['DISPLAY'])
        
    #####################################################
    # eye tracker parameters
    
    c.set('EYETRACKER', 'ANALOG')       # eye tracker mode; can be:
                                        # ANALOG, ISCAN, EYELINK or NONE
    c.set('EYETRACKER_DEV', '')         # serial port or IP address
    c.set('SWAP_XY', '0')               # swap X & Y on eye tracker

                                        # EYELINK SPECIFIC OPTIONS
    c.set('EYELINK_XTALK', '0,-0.001')  # crosstalk adjustment between pupil
                                        # position and size
    c.set('EYELINK_OPTS', '')           # any extra options to pass to API
    c.set('EYELINK_CAMERA',	'1')        # left or right camera (0, 1)

    #####################################################
    # plexon interface
    
    c.set('PLEXHOST', '')               # PlexNet Host IP number
    c.set('PLEXPORT', '6000')           # PlexNet Host Tcp Port

    #####################################################
    # TDT interface

    c.set('TDTHOST', '')                # name or IP number of windows
                                        # machine running tdt.py server

    return c

def defaults_info():
	return """
Sound & Video
-------------
FULLSCREEN      (0|1)   enable full screen mode
DPYBITS         (#)     number of display bits (typically 24 or 32)
DPYH            (#)     display height in pixels
DPYW            (#)     display width in pixels
GAMMA           (float) scalar gamma correction for monitor (luminance)
MONH            (#)     monitor height in cm
MONW            (#)     monitor width in cm
MON_ID          (str)   identifier string for monitor (brand etc)
VIEWDIST        (#)     viewing distance (eye to monitor) in cm
AUDIODRIVER     (str)   name of pygame SDL_AUDIODRIVER
REWARD_BEEP     (0|1)   beep on each reward
SOUND           (0|1)   sound on/off (default is on)
SYNCLEVEL       (#)     intensity (0-255) of sync pulse signal
SYNCSIZE        (#)     size (pixels) of sync pulse sprite (width & height)
SYNCX           (#)     x-location (pixels) of sync pulse sprite
SYNCY           (#)     y-location (pixels) of sync pulse sprite

Eye Tracking
------------
EYETRACKER      (str)   eyetracker device: ANALOG, ISCAN or EYELINK
EYETRACKER_DEV  (str)   device file (IP # for eyelink)
SWAP_XY         (0|1)   swap x and y channels on eyetracker
EYELINK_CAMERA  (0,1)   left or right eyelink (EL2) camera to read
EYELINK_OPTS    (str)   extra options for the eyelink API
EYELINK_XTALK   (#,#)   luminance-position cross talk correction for eyelink

Data Acquisition
----------------
FLIP_BAR        (0|1)   flip sign of monkey bar (sw0)
FLIP_SW1        (0|1)   flip sign of user switch 1
FLIP_SW2        (0|1)   flip sign of user switch 2
ENABLE_SW1      (0|1)   enable switch 1 for manual rewards
PPORT           (hex#)  parallel port (cage trainer); should start with 0x

Remote Data Acquisition
-----------------------
PLEXHOST        (str)   IP # or name of machine running PlexNet
PLEXPORT        (#)     port # for PlexNet
TDTHOST         (str)   name or IP number of machine running tdt.py

Other
-----
DEBUG           (0|1)   enables debug mode
SPLASH          (0|1)   display splash screen

Environment Vars (use setenv, not config file!)
-----------------------------------------------
TTANK           (0/1)   if 0, then forces skipping to TTANK queries
TTANKSERVER     (str)   hostname for ttank server (overrides pypefile)
TTANKDIR        (str)   directory for ttanks (overrides pypefile)

Note: TTANKHOST/DIR are useful when the data get stored directly
      to a local disk, but later moved to a new location for
      permanent storage (like a RAID).
"""
