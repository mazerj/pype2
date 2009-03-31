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
    c.set('JUICEBUTTON', '1')           # if 1, SW1 triggers a *reward*
    c.set('JUICESWITCH', '1')           # if 1, SW1 opens/closes solenoid
    c.set('REWARD_BEEP', '1')           # beep when giving rewards?
    c.set('DACQ_TESTMODE', '0')         # testing mode for DAQ cards
    c.set('NO_AUDIO', '0')              # disable audio?
    
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
    c.set('SYNCX', '-10000')            # X location of sync square CENTER (pix)
    c.set('SYNCY', '-10000')            # Y location of sync square CENTER (pix)
    c.set('SYNCLEVEL', '255')           # gray scale value of sync-on

    c.set('TESTPAT', None)              # filename for test pattern
    

    # BLOCKED should probably just go away or be figured out automatically
    # based on SYNC{X,Y,SIZE}
    c.set('BLOCKED', '')                # region of screen blocked by photodiode

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
    c.set('PUPILXTALK', '0,-0.001')     # crosstalk adjustment between pupil
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
