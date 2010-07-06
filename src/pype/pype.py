# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**pype: python physiology environment**

This is the main module for pype.  It gets imported by
both data collection and data analysis programs/tasks.
In general, any pype-related program or task should
probably import this module as early on as possible

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Thu Jun 16 15:20:45 2005 mazer

 - added ben willmore's changes for mac-support

- Thu Jul  7 15:19:43 2005 mazer

 - added support for ':' delimited PYPETASKPATH; all .py files
   in each of the indicated directories will be added to the menu
   bar, with the basename of each directory used as the text in
   the dropdown menu.

Sat Jul  9 13:03:54 2005 mazer

 - moved the root take/drop stuff to a separate module & cleaned
   up the import structure for this module

 - removed eyegraph/tkplotcanvas stuff, replaced with iplot/grace

Sun Jul 24 15:46:07 2005 mazer

 - added SYNCLEVEL option to set intensity of on for syncpulse

 - added plotskip to rig menu -- if plotskip > 1, then it specifies
   the stride for plotting the eyetraces in the iplot window.

 - added plotall to rig menu to turn off plotting of s0, p0 and
   raster (for speed), if so desired..

 - full task dir and record_file are now shown when you mouse over
   the labels, instead of having long names in the GUI, which screws
   up the widths..

 - mouse-over balloons can be added to any widget using, eg::

    {app|self}.balloon.bind(widget, 'balloon message goes here...')

 - made DEBUG a Config file variable instead of an enviornment
   value (ie, use pypeconfig to add "DEBUG: 1" to enable debugging
   messages).

Sun Jul 24 21:48:44 2005 mazer

 - use fx,fy button deleted -- not needed any longer, it's automatic..

Thu Jul 28 18:40:56 2005 mazer

 - PypeApp.bar_genint() and FixWin.genint() should be thought of
   as allowing bar transitions and fixwin breaks to generate interupts,
   but not allowing pype to received them. When your task is ready to
   actually receive those interupts, you now have to tell pype by
   setting "app.allow_ints = 1" and then unsetting it when you're done.

Sun Aug 28 10:11:09 2005 mazer

- added safe_to_load() method to PypeApp -- there was problem with
  tasks getting loaded before they actually halted -- it's not
  sufficient to just check the running flag -- this get's cleared when
  you hit to the stop button, but it may take some time for the
  current trial to actually terminate and the task to halt.

Wed Aug 31 17:36:25 2005 mazer

- changed safe_to_load() to a state var, instead of method

Sat Sep  2 ??:??:?? 2005 mazer

- removed safe_to_load and just disabled the load options in the
  main file menu..

Sat Sep  3 16:59:49 2005 mazer

- Changed the whole FixBreak/BarTransition interupt handling scheme
  so that the actual interrupt handler only sets a flag indicating
  that an interupt occured. The next time app.idlefn() is called
  the appropriate exception will get raised. This shouldn't really
  have much of an affect on tasks, so long as they call idlefn()
  or idlefn(fast=1) regularly. However, it should prevent FixBreak
  and BarTransition exceptions from getting raised while the Tkinter
  handlers are running (which locks up parts of the pype gui).

Sat Nov  5 20:01:02 2005 mazer

- got rid of heatbeat code.. who uses this?? also cleaned up the
  eyelink interface a bit to make it simpler and easier to understand

Thu Nov 10 15:35:13 2005 mazer

- modified PypeApp.encode() to optionally take tuple and encode each
  item of the tuple with the same timestamp.

Mon Jan 16 11:18:57 2006 mazer

- added marktime() method for debugging --> hitting '=' in userdpy
  window sticks a MARK event into the encode stream, if running..

Mon Jan 23 10:11:46 2006 mazer

- added vbias option to FixWin to turn the fixwin into an ellipse. See
  comments in the fixwin class for more details.

Thu Mar 23 11:45:11 2006 mazer

- changed candy1/candy2 -> bounce/slideshow and added rig parameter
  to disable the noise background during slideshows..

Thu Mar 30 10:18:18 2006 mazer

- deleted framebuffer arg to PypeApp() and added psych arg

Tue Apr  4 11:47:37 2006 mazer

- added arguments to eyeset() to allow tasks to muck with the
  xgain,ygain,xoffset and yoffset values

Fri Apr 14 09:21:34 2006 mazer

- added LandingZone class -- see notes in class definition

Mon Apr 17 09:32:06 2006 mazer

- added SectorLandingZone and PypeApp method eye_txy() to
  query time, x and y position of last eye position sample.
  This is just like the eyepos() method, but also returns
  the sample time.

Tue Apr 25 14:13:14 2006 mazer

- set things up so environment var $(PYPERC) can override the default
  ~/.pyperc config files. This is for when multiple users want to share
  a common .pyperc directory for a single animal.

Mon May  1 11:10:29 2006 mazer

- check permission on the config directory 1st thing when pype is
  fired up and exit if you don't have write access to save state.
  Again, this is really for shared config/pyperc dirs

Mon May 22 10:24:25 2006 mazer

- added train start button that writes to a "0000" datafile.

- added tally tab on notebook and started maintaining tallys
  across sessions and on a per-task basis. You can clear
  these with a button or programmatically using app.tally().
  Note that a lot of tasks have a app.clear(clear=1) at the
  start of each run, which will defeat this mechanism...

Thu Sep 28 10:16:02 2006 mazer

- 'final' modification to the runstats() code... the current system
  should be simple for most people. There are now three termination
  parameters:

  - max_trials -- maximum number of trials to run before stopping.
    only correct and error trials count.

  - max_correct -- maximum number of CORRECT trials to run before stopping.

  - max_ui -- maximum number of SEQUENTIAL ui trials before stopping.

  - uimax -- still exists and all the associated code, but this is
    really used only by the task -- user's responsible for coding
    up the handler. the max_* parameters are handled directly by
    pype and the run is terminated automatically when the stopping
    conditions are met.

  In all cases, setting these values to zero means they won't be used.
  Either max_trials should be set OR max_correct, but not both!

Mon Dec  4 09:26:10 2006 mazer

- added set_alarm() method -- this provides a mechanism to generate
  an alarm signal after a fixed # of ms. Use in conjunction with
  app.allow_ints (must be true to alarm to get raised). When the
  alarm goes off an 'Alarm' exception is raised the next time idlefn()
  gets called, just like Bar events::

    usage: app.set_alarm(ms=##) or app.set_alarm(clear=1)

Tue Apr  3 10:41:33 2007 mazer

- Added support for setting "EYETRACKERDEV: NONE" in config file to
  disable eyetracking in the comedi/das server. This is really to free
  up analog channels 0 and 1 for other things (ie, acute data)

Mon May 21 10:28:23 2007 mazer

- Added 'acute' parameter to the sub_common worksheet for experiments
  going in collaboration with the mccormick lab. Note that this is in
  a worksheet, instead of the Config file so that it's easy for tasks to
  be conditionalize based on the current setting!

Sun May 27 15:08:51 2007 mazer

- Added 'save_tmp' to sub_common worksheet -- this will let you write
  the temp files to /dev/null, which should massively accelerate
  handmappng with the acutes (long trials)

Wed Jun 27 11:01:12 2007 mazer

- Moved all the default Config.$HOST stuff to configvars.py; this should
  make it easier to keep track of the options and defaults for users.

Thu Jun 28 10:40:41 2007 mazer

- Converted almost everything over to using Logger() class for logging
  error message. This will put things in a scrollable console window,
  (if available) and also log to sys.stderr. The Logger class is in
  guitools.py

Wed Jul 18 08:20:22 2007 mazer

- Getting rid of the "train" button in favor a per animal "training"
  variable in the animal worksheet.

Mon Sep 10 15:48:27 2007 mazer

- loadwarn() was not correctly finding the source of the module
  based on filename (aka __file__). It turns out this isn't really
  possible, since tasks get loaded using an explicit combination
  of (dir,file). This means that the actual source of 'file' may
  NOT be the first one on the path, so loadwarn() was failing (ie,
  it always reported the 1st module named 'file' on the path).

Thu Sep 27 17:16:55 2007 mazer

- adding TDT support:

  - plexstate -> record_led (LED)
  
  - plexon_state() -> record_state()

Tue Dec 11 16:20:50 2007 mazer

- got rid of synctest() built in -- never used and problematic..

Mon Oct 27 12:57:50 2008 mazer

- added TOD_START and TOD_STOP events to store real time-of-day
  for these events to facilitate sync-checking in future

Mon Jan 26 13:44:01 2009 mazer

- added KEYBAR option for config file to allow leftshift key to
  generate BarTransition interupts like a regular bar input.. Mouse
  must be the display window!

Tue Jan 27 12:18:09 2009 mazer

- cleaned and simplified up audio initialization procedure

Fri Mar 13 16:25:24 2009 mazer

- clean up of code, function names (privatizing stuff) and docs

- removed the gui=1 arg for pype -- this is NEVER used..

Fri Mar 27 17:50:18 2009 mazer

- moved eye candy routines (bounce & slideshow) into separate module.

Tue Mar 31 12:48:08 2009 mazer

- new test pattern! automatically scaled to fit the display buffer

- added TESTPAT config-file option for user/rig-specific test pattern

Mon Apr 27 16:20:55 2009 mazer

- removed KEYBAR stuff. This was slightly problematic/deceptive -- it
  depended on calling idlefn() at the right times and the timing is
  completely deceptive.. if you want to debug plug in a joystick or
  joypad and do it the right way..

- likewise, also got rid of the lshiftsown/rshiftdown PypeApp methods

Mon May 25 17:02:17 2009 mazer

- settled on TASKPATH for adding things to the task search path. Again,
  this is a colon-deliminate list of directories. Each directory name
  (terminal node of path) must be unique!! (This is a PMW/Tkinter issue).
  You can specified as both a config var in ~/.pyperrc AND/OR using the
  enviornment var..

Thu Jun 25 16:01:42 2009 mazer

- changed 'dropvar' to really specify VARIANCE instead of STD!!

- got rid of trial_XXX functions and trialstats{}

Tue Jul  7 10:25:03 2009 mazer

- got rid of BLOCKED -- automatically computed from sync info..


Thu Jan  7 17:31:33 2010 mazer

- added explicit typeing for c0,c1..cN numeric arrays so they
  get properly saved/pickled by labeled_load.

- At the same time changed s0 (ttl spike channel) and p0 (photo diode
  channel) to be a list (should have been all along) to avoid problems
  in the future.
  
"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

#####################################################################
#  system level imports
#####################################################################
import sys
import os
import re
import socket
import traceback
import imp
import exceptions
import glob
import string
import posixpath, posix
import signal
import socket
import time
import math
import cPickle
import thread
from types import *
from Tkinter import *
try:
	import Pmw
except ImportError:
	Pmw = None

try:
	from Numeric import *
except ImportError:
	sys.stderr.write('missing `Numeric` package.\n' % __name__)
	sys.exit(1)

#####################################################################
#  import frequently accessed pype modules
#####################################################################
from pypedebug import *
from rootperm import *
from pype_aux import *
from ptable import *
from beep import *
from sprite import *
from events import *
from guitools import *
from dacq import *
from pypeerrors import *
from candy import bounce, slideshow
import PlexHeaders, PlexNet, pype2tdt
from info import print_version_info
import filebox
import userdpy
import pypeversion
import configvars

import prand
if not prand.validate():
	sys.stderr.write('Invalid Mersenne Twister implmentation!!!!\n')
	sys.exit(1)

def pypeapp():
	"""
	In case you don't have the application handle -- you can use
	pypeapp() to retrieve it from a global store. This usually
	means you're doing something the wrong way. Consider yourself
	warned
	"""
	return PypeApp.__handle

class PypeApp:
	"""Pype Application Class.

	Toplevel class for all pype programs -- one instance of this
	class is instantiated when the pype control gui is loaded. More
	than one of these per system is a fatal error.

	The PypeApp class has methods & instance variables for just about
	everything a user would want to do.
	"""

	__handle = None

	def __init__(self, psych=0):
		"""
		Initialize a PypeApp instance, with side effects:

		- FrameBuffer instance is created, which means the hardware
		  screen will be opened automatically.  Right now, PypeApp
		  guesses about the size & depth of the display to simplify
		  things for the user.  This could change.

		- The DACQ hardware is opened, if possible.

		- PypeApp gui is built and opened on screen

		Don't initialize more than one instance of this class.  If you
		do an exception will be raised.  An alternative (for later
		consideration) would be to allow multiple instances which share
		an underlying framebuffer & dacq hardware; however, this would
		really require some sort of underlying locking method to prevent
		collision.
		"""

		# need Pmw (python megawidgets Tkinter addon) for gui
		if Pmw is None:
			sys.stderr.write('%s: missing `Pmw` package\n' % __name__)
			raise FatalPypeError

		# no console window to start with..
		self.conwin = None

		# save handle for this instance as a pseudo-global (this
		# is really just for the functions in helper.py
		PypeApp.__handle = self

		# check to see if ~/.pyperc or $PYPERC is accessible
		# by the user before going any further:
		statefile = self.__get_statefile_name(accesscheck=0)
		try:
			statefile = self.__get_statefile_name(accesscheck=1)
		except IOError:
			Logger("pype: No access to statefile '%s'\n" % statefile +
				   "      Check permissions in %s\n" % pyperc())
			raise FatalPypeError

		# make sure we're the only pype running!
		_CanOnlyBeOne()

		# Load user/host-specific config data and set appropriate
		# defaults for missing values.

		cfgfile = pype_hostconfigfile()
		Logger("pype: loading config from '%s'\n" % cfgfile)
		self.config = pype_hostconfig()

		# you can set debug mode by:
		#   - running with --debug argument
		#   - setenv PYPEDEBUG=1
		#   - setting DEBUG: 1 in the Config.$HOST file
		if os.environ.has_key('PYPEDEBUG'):
			Logger("pype: running in debug mode")
			self.config.set('DEBUG', '1', override=1)
		debug(self.config.iget('DEBUG'))
		if debug():
			sys.stderr.write('config settings:\n')
			self.config.show(sys.stderr)

		# Thu Mar  1 20:53:51 2007 mazer
		# started hooking pype into elog-sql system
		#   $ELOG should be set to point to the path for the elog
		#   library or source code for elog (wherever elogapi.py
		#   lives). By default use the tradition method..
		if os.environ.has_key('ELOG'):
			_addpath(os.environ['ELOG'])
			try:
				import elogapi
				self.use_elog = 1
				Logger("pype: connecting to ELOG database system.\n")
			except ImportError:
				Logger("pype: warning -- ELOG api not available.\n")
				self.use_elog = 0
		else:
			self.use_elog = 0

		# these MUST be set from now on..
		monw = self.config.fget('MONW', -1)
		if monw < 0:
			Logger('pype: set MONW in Config file\n')
			raise FatalPypeError
		monh = self.config.fget('MONH', -1)
		if monh < 0:
			Logger('pype: set MONH in Config file\n')
			raise FatalPypeError
		viewdist = self.config.fget('VIEWDIST', -1)
		if viewdist < 0:
			Logger('pype: set VIEWDIST in Config file\n')
			raise FatalPypeError

		mon_id = self.config.get('MON_ID', '')
		if len(mon_id) == 0:
			Logger('pype: warning -- MON_ID field in Config file unset.\n')

		# GFX_TESTMODE is now obsolete, replaced by FULLSCREEN
		if self.config.iget('GFX_TESTMODE', default=-666) != -666:
			Logger("pype: CONFIG ERROR: GFX_TESTMODE is obsolete" +
				   "      Try FULLSCREEN instead.\n")
			raise FatalPypeError

		state = self.__readstate()
		if state is None:
			# no state file -- make sure tallycount's initialized..
			self.tallycount = {}

		self.psych = psych
		self.terminate = 0
		self.paused = 0
		self.running = 0
		self.startfn = None
		self.dropcount = 0
		self.record_id = 1
		self.record_buffer = []
		self.record_file = None
		self._last_eyepos = 0
		self._allowabort = 0
		self._rewardlock = thread.allocate_lock()
		self._eye_x = 0
		self._eye_y = 0
		self._eyetarg_x = 0
		self._eyetarg_y = 0
		self._eyetrace = 0
		self.taskidle = None

		#Thu Jun 25 16:07:42 2009 mazer OBSOLETE:
		#self.trialstats = {}
		#self.trial_clear()

		self.tk = Tk()
		self.tk.resizable(0, 0)

		import im_left, im_right, im_up, im_down
		self.icons = {}
		self.icons['left'] = im_left.left
		self.icons['right'] = im_right.right
		self.icons['up'] = im_up.up
		self.icons['down'] = im_down.down

		if self.config.iget('SPLASH'):
			splash()

		if sys.platform == 'darwin':
			self.tk.geometry("+0+20")
		else:
			self.tk.geometry("+0+0")
		self.tk.title('Pype')
		self.tk.protocol("WM_DELETE_WINDOW", self.shutdown)

		Pmw.initialise(self.tk, useTkOptionDb=1)

		self.conwin = ConsoleWindow()
		self.conwin.showhide()

		# setup global log/console window (see guitools.py)
		# all queued (ie, old) Logger messages will get pushed
		# into the console window are this point..
		Logger(window=self.conwin)

		f1 = Frame(self.tk, borderwidth=1, relief=GROOVE)
		f1.pack(expand=0, fill=X)

		self.balloon = Pmw.Balloon(self.tk, master=1, relmouse='both')

		self.show_eyetrace_start = None
		self.show_eyetrace_stop = None
		self.show_eyetraces = IntVar()
		self.show_eyetraces.set(0)
		self.testpat = IntVar()
		self.testpat.set(1)
		self._eyetrace_window = None

		mb = Pmw.MenuBar(f1)
		mb.pack(side=LEFT, expand=0)

		mb.addmenu('File', '', '')
		mb.addmenuitem('File', 'command',
					   label='Toggle console view',
					   command=self.conwin.showhide)
		mb.addmenuitem('File', 'command',
					   label='Toggle user display view',
					   command=self.udpy_showhide)
		mb.addmenuitem('File', 'separator')
		mb.addmenuitem('File', 'command',
					   label='Keyboard debugger', command=self.keyboard)
		mb.addmenuitem('File', 'command',
					   label='Graphics info',
					   command=lambda s=self: s.fb.printinfo())
		mb.addmenuitem('File', 'command',
					   label='Show sprites',
					   command=lambda s=self:s.showsprites())
		mb.addmenuitem('File', 'separator')
		mb.addmenuitem('File', 'command',
					   label='Save state', command=self.__savestate)
		mb.addmenuitem('File', 'command',
					   label='Quit', command=self.shutdown)

		mb.addmenu('Set', '', '')
		mb.addmenuitem('Set', 'checkbutton',
					   label='Show traces',
					   variable=self.show_eyetraces)
		mb.addmenuitem('Set', 'checkbutton',
					   label='show test pattern',
					   variable=self.testpat)
		mb.addmenuitem('Set', 'command',
					   label='Toggle TRAINING mode',
					   command=self.tog_training)

		# make top-level menubar for task loaders that can be
		# disabled when it's not safe to load new tasks...
		self._loadmenu = Pmw.MenuBar(f1)
		self._loadmenu.pack(side=RIGHT, expand=1, fill=X)
		self.make_taskmenu(self._loadmenu)

		self._loadmenu.addmenu('Help', '', side=RIGHT)
		self._loadmenu.addmenuitem('Help', 'command',
								   label='About Pype', command=AboutPype)


		f1b = Frame(self.tk, borderwidth=1, relief=GROOVE)
		f1b.pack(expand=0, fill=X)

		self.taskmod = None
		tmp = Frame(f1b, borderwidth=1, relief=GROOVE)
		tmp.pack(expand=1, fill=X)
		self.__taskname = Label(tmp)
		self.__taskname.pack(side=LEFT)

		self.task_name = None
		self.task_dir = None
		self.taskname(None, None)

		# record state is the TTL line used to sync pype to
		# and external recording system (plexon, etc)
		self.record_led = Label(tmp, text="*", bg='white')
		self.record_led.pack(side=RIGHT)
		self.balloon.bind(self.record_led, "blue=record;red=pause)")

		if os.environ.has_key('LOGNAME'):
			self.uname = os.environ['LOGNAME']
		else:
			self.uname = '???'
		self.userinfo = Label(tmp, text="usr=%s subj=%s" % \
							  (self.uname, subject()))
		self.userinfo.pack(side=RIGHT)

		self.training = Label(tmp, text="", fg='blue')
		self.training.pack(side=RIGHT)
		self.balloon.bind(self.training, "training/recording mode")

		f = Frame(f1b, borderwidth=1, relief=GROOVE)
		f.pack(expand=1, fill=X)

		self.__recfile = Label(f)
		self.__recfile.pack(side=LEFT)
		self._recfile()

		self.__repinfo = Label(f, text=None)
		self.__repinfo.pack(side=RIGHT)

		self.__ledbar = Label(f, text=None)
		self.__ledbar.pack(side=RIGHT)

		f2 = Frame(self.tk)				# entire lower section.. not visible!
		f2.pack(expand=1)

		f = Frame(f2)
		f.grid(row=0, column=0, sticky=N+S)		
		
		c1pane = Frame(f, borderwidth=1, relief=RIDGE)
		c1pane.pack(expand=0, fill=X, side=TOP)

		hostname = self.__gethostname()
		b = Checkbutton(c1pane, text='subj parm', relief=RAISED, anchor=W)
		b.pack(expand=0, fill=X, side=TOP, pady=4)

		sub_common = DockWindow(checkbutton=b, title='subj/cell')
		self.sub_common = ParamTable(sub_common,
		(
			("Session Data", None, None),
			("training",	0,	 is_boolean,	"training mode (#0000 files)"),
			("subject",		"",  is_any,		"subject id (prefix/partial)"),
			("full_subject", "", is_any,		"full (unique) subject name"),
			("owner",		"",  is_any,		"datafile owner"),
			("cell",		"",  is_any,		"unique (per subj) cell id #"),
			("acute",		"0", is_bool,		"acute experiment"),
			("save_tmp",	"1", is_bool,		"0 to write to /dev/null"),
			("fast_tmp",	"1", is_bool,		"super fast tmp mode"),

			("Fixation Window Params", None, None),
			# these are global params, but should be handled by tasks:
			("win_size",	"50",  is_int,		"default fixwin radius (pix)"),
			("win_scale",	"0.0", is_float,	"additive eccentricity adjustment for win_size (rad-pixels/ecc-pixels)"),
			("vbias",	    "1.0", is_float,	"fixwin vertical elongation factor (1.0=none)"),
			
			("Recording Info", None, None),
			("site.well",	"", is_any,			"well number"),
			("site.probe",	"", is_any,			"probe location"),
			("site.depth",	"", is_any,			"electrode depth (um)"),
			
			("Reward Params", None, None),
			("dropsize",	"100", is_int,		"mean drop size in ms (for continuous flow systems)"),
			("dropvar",		"10", is_int,		"reward variance (sigma^2)"),
			("maxreward",	"500", is_gteq_zero,"maximum reward duration (hard limit)"),
			("minreward",	"0", is_gteq_zero,	"minimum reward duration (hard limit)"),

			("Pype Blocking Params", None, None),
			# these are handled automatically by pype!
			("max_trials",	"0",   is_int,		"trials before stopping (0 for no limit)"),
			("max_correct",	"0",   is_int,		"correct trials before stopping (0 for no limit)"),
			("max_ui",		"0",   is_int,		"sequential UI's before stopping (0 for no limit)"),

			#("Task Blocking Params", None, None),
			# global, but handled by task -- soon to go away
			#("uimax",		"3",   is_int, "maximum # conseq. UI trial's before halting"),
			#("nreps",		"100", is_int, "number of blocks per rep"),
			#("blocksize",	"100", is_int, "number of trials per block"),

			("Fixation and Appearence", None, None),
			("fix_size",	"2", is_int, "size of fixspot (radius in pixels)"),
			("fix_ring",	"10", is_int, "size of annular ring around fixspot for ++visibility"),
			("fix_x",		"0", is_int, "default X position of fixspot (pix)"),
			("fix_y",		"0", is_int, "default Y position of fixspot (pix)"),
			#("win_size",	"20", is_int, "default fixation window size (radius in pixels)"),
			#("win_scale",	"0.0053", is_float, "multiplier to scale win_size w/eccentricity (gain/pix"),
			("bg",			"80", is_gray, "default background color of screen"),

			("Timing Params", None, None),
			("abortafter",	"2000", is_int, "not sure?"),
			("maxrt",		"600", is_int, "maximum allowed reaction time (ms)"),
			("iti",			"4000+-20%", is_iparam, "inter-trial interval (ms)"),
			("timeout",		"10000+-20%", is_iparam, "penalty timeout for errors (ms)"),
			("uitimeout",	"20000+-20%", is_iparam, "uninitiated trial timeout (ms)"),
			
			("Eye Candy Params", None, None),
			("show_noise", 1, is_boolean, 'noise background during slides'),
			), file='subject.par', altfile='common-%s.par' % hostname)

		if self.use_elog:
			# the cell field (exper in elog database) is not
			# user setable in elog mode!
			self.sub_common.lockfield('cell')

		# training field should be set via the menu...
		self.sub_common.lockfield('training')
		# set warning label if training mode
		self.tog_training(toggle=0)

		b = Checkbutton(c1pane, text='rig parm', relief=RAISED, anchor=W)
		b.pack(expand=0, fill=X, side=TOP, pady=4)
		rig_common = DockWindow(checkbutton=b,
								title='rig (%s)' % hostname)
		self.rig_common = ParamTable(rig_common,
		(
			("Run Modes", None, None),
			("testing",		0,				is_boolean),

			("Monitor Info", None, None),
			("mon_id",		"n/a",			is_any, "", -1),
			("viewdist",	"37",			is_float, "", -1),
			("mon_width",	"0",			is_float, "", -1),
			("mon_height",	"0",			is_float, "", -1),
			("mon_dpyw",	"0",			is_int, "", -1),
			("mon_dpyh",	"0",			is_int, "", -1),
			("mon_h_ppd",	"10",			is_float, "", -1),
			("mon_v_ppd",	"10",			is_float, "", -1),
			("mon_ppd",		"10",			is_float, "", -1),
			("mon_fps",		"0",			is_float, "", -1),

			("Eye Tracker Info", None, None),
			("eyetracker",	"",				is_any, "", -1),
			("eyefreq",		"",				is_int),
			("eyelag",		"0",			is_int, "", -1),
			("plotskip",	"1",			is_int,
			 "number points to skip when plotting for speed"),
			("plotall",		"1",			is_bool,
			 "if set, then also plot spikes & photodiode traces"),

			("UserDpy Settings", None, None),
			("note_x",		"0",			is_int, "", -1),
			("note_y",		"0",			is_int, "", -1),

			("DACQ Params", None, None),
			("fixbreak_tau",	"5",		is_int,
			 "# 1khz samples outside fixwin it counts as break -- UPDATE to take effect"),
			("eye_smooth",		"3",		is_int,
			 "length of running average used to smooth eye traces -- UPDATE to take effect"),
			("dacq_pri",		"-10",		is_int,
			 "priority of DACQ process (nice value)"),
			("rt_sched",		"0",		is_bool,
			 "boolean: try to use rt_scheduler??"),
			("fb_pri",			"-10",		is_int,
			 "priority of the framebuffer process (nice value)"),
			("photo_thresh",	"500",		is_int,
			 "threshold for photodiode detection"),
			("photo_polarity",	"1",		is_int,
			 "sign of threshold for photodiode detection"),
			("spike_thresh",	"500",		is_int,
			 "threshold for spike detection"),
			("spike_polarity",	"1",		is_int,
			 "sign of threshold for spike detection"),
			("save_chn_0",		"0",		is_int,
			 "analog horizontal eye pos (coil only)"),
			("save_chn_1",		"0",		is_int,
			 "analog vertical eye pos (coil only)"),
			("save_chn_2",		"0",		is_int,
			 "analog photodiode signal (redundant!)"),
			("save_chn_3",		"0",		is_int,
			 "analog TTL psike signal (redundant!)"),
			("save_chn_4",		"0",		is_int,
			 "un used analog channel"),
		), file='rig-%s.par' % hostname,
		   altfile='common-%s.par' % hostname)

		# JAM 07-feb-2003: Compute ppd values based on current setup.
		# Then place these in the rig menu automatically.

		s = 180.0 * 2.0 * math.atan2(monw/2, viewdist) / math.pi
		xppd = self.config.fget("DPYW") / s;

		s = 180.0 * 2.0 * math.atan2(monh/2, viewdist) / math.pi
		yppd = self.config.fget("DPYH") / s;

		ppd = (xppd + yppd) / 2.0

		self.rig_common.set('mon_id', self.config.get('MON_ID', ''))
		self.rig_common.set('viewdist', '%g' % viewdist)
		self.rig_common.set('mon_width', '%g' % monw)
		self.rig_common.set('mon_height', '%g' % monh)
		self.rig_common.set('mon_dpyw', self.config.iget('DPYW'))
		self.rig_common.set('mon_dpyh', self.config.iget('DPYH'))
		self.rig_common.set('mon_h_ppd', '%g' % xppd)
		self.rig_common.set('mon_v_ppd', '%g' % yppd)
		self.rig_common.set('mon_ppd', '%g' % ppd)

		et = self.config.get('EYETRACKER', 'ANALOG')
		if et == 'ISCAN':
			self.rig_common.set('eyetracker', et)
			self.rig_common.set('eyelag', '16')
		elif et == 'EYELINK':
			self.rig_common.set('eyetracker', et)
			self.rig_common.set('eyelag', '0')
		elif et == 'ANALOG':
			self.rig_common.set('eyetracker', et)
			self.rig_common.set('eyelag', '0')
		elif et == 'EYEJOY':
			self.rig_common.set('eyetracker', et)
			self.rig_common.set('eyelag', '0')
		elif et == 'NONE':
			self.rig_common.set('eyetracker', et)
			self.rig_common.set('eyelag', '0')
		else:
			Logger("pype: %s is not a valid EYETRACKER.\n" % et)
			raise FatalPypeError

		c2pane = Frame(f, borderwidth=3, relief=RIDGE)
		c2pane.pack(expand=0, fill=X, side=TOP)

		self._realstart = Button(c2pane, text="start",
								 command=self.__start, bg='light green')
		self._realstart.pack(expand=0, fill=X, side=TOP, pady=2)
		self.balloon.bind(self._realstart, 'save data to file')

		self._tmpstart = Button(c2pane, text="temp",
								command=self.__starttmp, bg='light green')
		self._tmpstart.pack(expand=0, fill=X, side=TOP, pady=2)
		self.balloon.bind(self._tmpstart, "save to temp file (ie, don't save)")
		
		self._stop = Button(c2pane, text="stop",
							   command=self.__start_helper, bg='red',
							   state=DISABLED)
		self._stop.pack(expand=0, fill=X, side=TOP, pady=2)
		self.balloon.bind(self._stop, "stop run at end of trial")

		c3pane = Frame(f, borderwidth=3, relief=RIDGE)
		c3pane.pack(expand=0, fill=X, side=TOP)

		b = Button(c3pane, text="new cell", command=self.new_cell)
		b.pack(expand=0, fill=X, side=TOP, pady=2)
		self.balloon.bind(b, "create a new cell number")

		b = Button(c3pane, text="reward",
				   command=self.reward)
		b.pack(expand=0, fill=X, side=TOP, pady=2)
		self.balloon.bind(b, "give reward (same as F4)")

		b = Button(c3pane, text="beep",
				   command=lambda s=self: s.warningbeep(1))
		b.pack(expand=0, fill=X, side=TOP, pady=2)
		self.balloon.bind(b, "play start sound w/o starting")

		self._candy = 0
		b = Button(c3pane, text="bounce",
				   command=lambda s=self: bounce(s),
				   bg='white')
		b.pack(expand=0, fill=X, side=TOP, pady=2)
		self.balloon.bind(b, "following the bouncing ball")
		self._button_bounce = b

		b = Button(c3pane, text="slides",
				   command=lambda s=self: slideshow(s),
				   bg='white')
		b.pack(expand=0, fill=X, side=TOP, pady=2)
		self.balloon.bind(b, "slide show from $(PYPERC)/candy.lst")
		self._button_slideshow = b

		self.eyegraph = _EyeGraph(self)

		self._cpane = c3pane

		book = Pmw.NoteBook(f2)
		book.grid(row=0, column=1, sticky=N+S+E)
		console = book.add('Console')
		info = book.add('Info')
		stats = book.add('Performance')
		tally = book.add('Tally')
		setables = book.add('I-Tracker')

		# INFO CONSOLES ######################################
		self.console = Info(console, bg='white')
		self.info = Info(info, bg='gray80')

		# STATS WINDOW ######################################
		self.statsw = Label(stats, text='', anchor=W, justify=LEFT,
							font="Courier 10")
		self.statsw.pack(expand=0, fill=BOTH, side=TOP)

		# TALLY WINDOW ######################################
		tf = Frame(tally)
		tf.pack(side=BOTTOM, fill=X)
		
		b = Button(tf, text="clear all",
				   command=lambda s=self: s.tally(clear=1))
		b.pack(side=LEFT, pady=0)
		self.balloon.bind(b, "clear tally statistics for all tasks")

		b = Button(tf, text="clear task",
				   command=lambda s=self: s.tally(cleartask=1))
		b.pack(side=LEFT, pady=0)
		self.balloon.bind(b, "clear tally statistics just for current task")


		self.tallyw = Info(tally, bg='gray90', height=30)

		self.__runstats_update(clear=1)
		self.tally(type=None)

		# EYE COIL PARAMS ######################################
		f = Frame(setables)
		f.pack(expand=0, fill=X, side=TOP)

		b = Button(f, text="update",
				   command=self.eyeset)
		b.pack(expand=0, fill=Y, side=LEFT, pady=0)
		self.balloon.bind(b, "apply all values in this notebook")

		b = Button(f, text='zero (F8)',
				   command=lambda s=self: s.eyeshift(zero=1))
		b.pack(expand=0, fill=Y, side=LEFT)
		self.balloon.bind(b, "subject is looking at (fx,fy) NOW")

		b = Button(f, text='reset',
				   command=lambda s=self: s.eyeshift(reset=1))
		b.pack(expand=0, fill=Y, side=LEFT)
		self.balloon.bind(b, "reset offset's to 0,0 (immediate effect)")
		b = Button(f, image=self.icons['left'],
				   command=lambda s=self: s.eyeshift(x=1, y=0))
		b.pack(expand=0, fill=Y, side=LEFT)
		self.balloon.bind(b, "shift offsets left (immediate effect)")
		b = Button(f, image=self.icons['right'],
				   command=lambda s=self: s.eyeshift(x=-1, y=0))
		b.pack(expand=0, fill=Y, side=LEFT)
		self.balloon.bind(b, "shift offsets right (immediate effect)")
		b = Button(f, image=self.icons['up'],
				   command=lambda s=self: s.eyeshift(x=0, y=-1))
		b.pack(expand=0, fill=Y, side=LEFT)
		self.balloon.bind(b, "shift offsets up (immediate effect)")

		b = Button(f, image=self.icons['down'],
				   command=lambda s=self: s.eyeshift(x=0, y=1))
		b.pack(expand=0, side=LEFT)
		self.balloon.bind(b, "shift offsets down (immediate effect)")

		v = _safeLookup(state, 'eye_tweak', 1)
		self._eye_tweak = Pmw.Counter(setables,
									  orient=HORIZONTAL,
									  label_text='eye tweak',
									  labelpos = 'w',
									  entry_width = 10,
									  entryfield_value=v,
									  increment = 1,
									  datatype = 'integer')
		self._eye_tweak.pack(expand=0, side=TOP, pady=2, anchor=W)
		self.balloon.bind(self._eye_tweak, \
						  "size of adjustment step (arrows and arrow keys")

		v = _safeLookup(state, 'eye_xgain', 1.0)
		self._eye_xgain = Pmw.Counter(setables,
									  orient=HORIZONTAL,
									  label_text='horiz gain',
									  labelpos = 'w',
									  entry_width = 10,
									  entryfield_value=v,
									  increment = 0.1,
									  datatype = 'real')
		self._eye_xgain.pack(expand=0, side=TOP, pady=2, anchor=W)

		v = _safeLookup(state, 'eye_ygain', 1.0)
		self._eye_ygain = Pmw.Counter(setables,
									  orient=HORIZONTAL,
									  label_text='vert gain',
									  labelpos = 'w',
									  entry_width = 10,
									  entryfield_value=v,
									  increment = 0.1,
									  datatype = 'real')
		self._eye_ygain.pack(expand=0, side=TOP, pady=2, anchor=W)

		v = _safeLookup(state, 'eye_xoff', 0)
		self._eye_xoff = Pmw.Counter(setables,
									  orient=HORIZONTAL,
									  label_text='x offset',
									  labelpos = 'w',
									  entry_width = 10,
									  entryfield_value=v,
									  increment = 1)
		self._eye_xoff.pack(expand=0, side=TOP, pady=2, anchor=W)

		v = _safeLookup(state, 'eye_yoff', 0)
		self._eye_yoff = Pmw.Counter(setables,
									  orient=HORIZONTAL,
									  label_text='y offset',
									  labelpos = 'w',
									  entry_width = 10,
									  entryfield_value=v,
									  increment = 1)
		self._eye_yoff.pack(expand=0, side=TOP, pady=2, anchor=W)

		Label(setables,
			  text="Use Shift/Ctrl/Meta-Arrows in UserDisplay\n"+
			       "window to adjust offsets in real-time").pack(\
			expand=0, fill=X, side=TOP, pady=10)

		Pmw.alignlabels([self._eye_tweak,
						 self._eye_xgain, self._eye_ygain,
						 self._eye_xoff, self._eye_yoff])

		# make sure Notebook is big enough for buttons above to show up
		book.setnaturalsize(pageNames=None)

		# extract some startup params.. these are read only ONCE!
		self.pix_per_dva = float(self.rig_common.queryv('mon_ppd'))

		# keyboard/event input que
		self.keyque = EventQueue(self.tk, '<Key>')

		# userdisplay: shadow of framebuffer window
		self.udpy_visible = 1
		self.udpy = userdpy.UserDisplay(None,
										cwidth=self.config.iget('DPYW'),
										cheight=self.config.iget('DPYH'),
										pix_per_dva=self.pix_per_dva,
										app=self, callback=self.marktime)

		if posixpath.exists(subjectrc('last.fid')):
			self.udpy.loadfidmarks(file=subjectrc('last.fid'))
		if posixpath.exists(subjectrc('last.pts')):
			self.udpy.loadpoints(subjectrc('last.pts'))
		self.dpy_w = self.config.iget('DPYW')
		self.dpy_h = self.config.iget('DPYH')

		# history info
		self._hist = Label(f2, text="", anchor=W, borderwidth=1, relief=RIDGE)
		self._hist.grid(row=3, column=0, columnspan=3, sticky=W+E)
		self.balloon.bind(self._hist, "recent trial result codes")
		self.history(init=1)

		# status line
		self._status = Label(f2, text="", anchor=W, fg="red",
							 borderwidth=1, relief=RIDGE)
		self._status.grid(row=1, column=0, columnspan=3, sticky=W+E)
		self.balloon.bind(self._status, 'plain old status line')

		self.led(0)

		# make sure we're root, if possible
		root_take()

		check = self.config.get('ISCAN_DEV')
		if check and len(check) == 0:
			warn('Error', \
				 'ISCAN_DEV in config is obsolete, change to EYETRACKER_DEV')

		# EYELINK_OPTS can be defined in the pyperc config file and should
		# contained a colon-delimited list of commands to be sent to the
		# eyelink. Most users should NEVER use this feature, it's really
		# just for testing and debugging.
		# NOTE: No attempt is made to make sure the built in commands don't
		# conflict with user commands.

		eyelink_opts = self.config.get('EYELINK_OPTS')
		if len(eyelink_opts) > 0:
			eyelink_opts = eyelink_opts + ':'

		eyelink_opts = eyelink_opts + 'pupil_crosstalk_fixup = %s' % \
					   self.config.get('PUPILXTALK')
		eyelink_opts = eyelink_opts + ':active_eye=both'
		eyelink_opts = eyelink_opts + ':link_sample_data = PUPIL,AREA'
		# Mon Jan 16 14:05:46 2006 mazer
		#  was: ':heuristic_filter = OFF'
		#  now: ':heuristic_filter = 0 0'
		# this will turn off the filter for both LINK and FILE data
		# streams (from Sol).
		eyelink_opts = eyelink_opts + ':heuristic_filter = 0 0'
		eyelink_opts = eyelink_opts + ':pup_size_diameter = NO'

		os.environ['XX_EYELINK_OPTS'] = eyelink_opts
		os.environ['XX_EYELINK_CAMERA'] = self.config.get('EYELINK_CAMERA')
		if self.config.iget('SWAP_XY'):
			os.environ['XX_SWAP_XY'] = '1'

		# possibly have the dacq module initialize a usb joystick device
		if len(self.config.get('USB_JS_DEV')) > 0:
			os.environ['XX_USBJS'] = self.config.get('USB_JS_DEV')

		os.environ['XX_ARANGE'] = self.config.get('ARANGE')

		dacq_start(1,
				   self.config.iget('DACQ_TESTMODE'),
				   self.config.get('EYETRACKER'),
				   self.config.get('DACQ_SERVER'),
				   self.config.get('EYETRACKER_DEV'))
		
		self.drawledbar()
		self.dacq_going = 1
		self.eyeset()

		# while we're possibly still running as root, get access
		# to the parallel port, if possible.  PPORT=1 for default
		# otherwise, specify port in hex: 0xNNN
		pport = self.config.get('PPORT')
		if len(pport) == 5 and pport[0:2] == '0x':
			ppbase = eval(pport)
			if pp_init(ppbase):
				Logger('pype: Parallel Port Enabled\n')
				self.pport = 1
		else:
			self.pport = None

		# stash info on port states
		# this is a hack -- some buttons are down/true others are
		# up/true .. lets user sort it all out..
		self.flip_bar = self.config.iget('FLIP_BAR')
		self.flip_sw1 = self.config.iget('FLIP_SW1')
		self.flip_sw2 = self.config.iget('FLIP_SW2')

		# NOTE:
		# Framebuffer initialization will give up root access
		# automatically.. so make sure you start the dacq process
		# first (see above).

		root_drop()
		if self.config.iget('NO_AUDIO'):
			# disable the beep subsystem:
			beep(disable=1)
			Logger('pype: audio disabled by user config\n')
		else:
			if self.config.get('AUDIODRIVER'):
				audiodriver = self.config.get('AUDIODRIVER')
			elif sys.platform == 'darwin':
				audiodriver = 'sndmgr'
			else:
				# default for linux...
				audiodriver = 'alsa'
			beep()
		root_take()

		self.init_framebuffer()

		# this must be defered until sync spot info is computed..
		self.udpy.drawaxis()

		# added automatic detection of framerate (13-jan-2004 JAM):
		fps = self.fb.calcfps(duration=250)
		if self.config.iget('FPS') and self.config.iget('FPS') != fps:
			Logger('pype: error actually FPS does not match requested rate\n' +
				   '      requested=%dhz actual=%dhz\n' % \
				   (self.config.iget('FPS'), fps))
			raise FatalPypeError
		self.rig_common.set('mon_fps', '%g' % fps)
		self.idlefb()
		Logger('pype: estimated fps = %g\n' % fps)

		# drop root access
		# Tue Jul 12 10:01:53 2005 mazer --
		#  dropping root access causes the ALSA libs to bitch. I'm
		#  not sure what the problem is, but we're generally having
		#  also of sound problems recently..
		root_drop()
		Logger('pype: dropped root access\n')


		# Sat Sep  3 16:56:50 2005 mazer
		# as of now, fixation break and bartransitions received via
		# the interupt handler (SIGUSR1) are handled the first time
		# idlefn() gets called after the interupt. The interupt handler
		# just sets these flags and exceptions are raised at the next
		# possible time. Therefore, you must continue to call idlefn
		# (although you can now use fast=1 to minimize CPU usage) if
		# you can FixBreak and BarTransition to work..
		self._post_fixbreak = 0
		self._post_bartransition = 0
		self._post_alarm = 0

		# catch interupts from the das_server process indicating
		# bar state transitions and fixation breaks

		# disable interupts for a second
		self.allow_ints = 0
		# make sure bar touches don't cause interupts
		dacq_bar_genint(0)
		# configure the handlers
		signal.signal(signal.SIGUSR1, self.int_handler)
		signal.signal(signal.SIGUSR2, self.debug_handler)
		# now ready to receive interupts, but they won't come
		# through until you do in your task:
		#   (app/self).allow_ints = 1


		#
		# External DACQ interface --
		#  this is for multichannel recording systems:
		#    - Plexon MAP box (via PlexNet API)
		#	 - Tucker-Davis (via pype's tdt.py client-server module)
		#
		self.xdacq = None
		self.xdacq_data_store = None
		self.plex = None
		self.tdt = None

		plexhost = self.config.get('PLEXHOST')
		tdthost = self.config.get('TDTHOST')

		if self.sub_common.queryv('training'):
			Logger('pype: xdacq disabled in training mode\n')
		elif len(plexhost) > 0 and len(tdthost) > 0:
			Logger('pype: either PLEXHOST *or* TDTHOST (disabled!!)\n', popup=1)
		elif self.xdacq is None and len(plexhost) > 0:
			try:
				self.plex = PlexNet.PlexNet(plexhost,
											self.config.iget('PLEXPORT'))
				Logger('pype: connected to plexnet @ %s.\n' % plexhost)
				self.xdacq = 'plexon'

				mb.addmenu('PlexNet', '', '')
				mb.addmenuitem('PlexNet', 'command',
							   label='query plexnet',
							   command=self.status_plex)
				mb.addmenuitem('PlexNet', 'separator')
			except socket.error:
				Logger('pype: failed connect to plexnet @ %s.\n' % plexhost,
					   popup=1)
		elif self.xdacq is None and len(tdthost) > 0:
			tankdir = self.config.get('TDTTANKDIR')
			if len(tankdir) == 0:
				Logger('pype: no TDTANKDIR set, using C:\\', popup=1)
				tankdir = 'C:\\'
			if not tankdir[-1] == '\\':
				# dir must have trailing \
				tankdir = tankdir + '\\'
			tankname = subject() + \
					   '%04d%02d%02d' % time.localtime(time.time())[0:3]
			try:
				self.tdt = pype2tdt.Controller(self, tdthost)
				Logger('pype: connected to tdt @ %s.\n' % tdthost)
				t = self.tdt.settank(tankdir, tankname)
				if t is None:
					Logger("pype: is TDT running? Can't set tank.\n", popup=1)
					self.tdt = None
				else:
					Logger('pype: tdt tank = "%s"\n' % t)
					self.xdacq = 'tdt'
			except socket.error:
				self.tdt = None
				Logger('pype: no connection to tdt @ %s.\n' % tdthost, popup=1)

			if self.tdt:
				mb.addmenu('TDT', '', '')
				mb.addmenuitem('TDT', 'command',
							   label='save hoops',
							   command=self.tdt.save)
				mb.addmenuitem('TDT', 'command',
							   label='restore hoops',
							   command=self.tdt.restore)

		Logger('pype: build %s by %s on %s\n' % \
			   (pypeversion.PypeBuildDate, pypeversion.PypeBuildBy,
				pypeversion.PypeBuildHost) +
			   'pype: PYPERC=%s\n' % pyperc() +
			   'pype: CWD=%s\n' % os.getcwd())
		
		if debug():
			print_version_info()

		if dacq_jsbut(-1):
			self.console.writenl("warning: joystick replaces bar input",
								 color='blue')

		self.recording = 0
		self.record_state(0)

		if self.psych:
			self.fb.hide()
			self.udpy_showhide()
		

	def tog_training(self, toggle=1):
		"""INTERNAL"""
		if toggle:
			s = not self.sub_common.queryv('training')
			self.sub_common.set('training', '%d' % s)
		else:
			s = self.sub_common.queryv('training')

		if s:
			self.training.configure(text='TRAINING')
		else:
			self.training.configure(text='')

	def udpy_showhide(self):
		"""INTERNAL"""
		self.udpy.showhide()

	def keyboard(self):
		app = self
		sys.stderr.write('Dropping into keyboard shell\n')
		sys.stderr.write('"app" should be defined!\n')
		keyboard()

	def marktime(self, c, ev):
		"""INTERNAL"""
		if self.isrunning():
			t = self.encode(MARK)
			Logger('pype: <MARK at %d>\n' % t)

	def set_state(self, running=-1, paused=-1, led=-1):
		"""
		Safe wrapper for setting state flags instead of
		letting user's set app.running etc by hand

		"""
		if not (running is -1):	self.running = running
		if not (paused is -1):	self.paused = paused
		if not (led is -1):		self.led(led)

	def drawledbar(self):
		x = ("[ ]", "[*]")
		t = x[dacq_bar()] + x[dacq_sw1()] + x[dacq_sw2()]
		if dacq_jsbut(-1):
			t = t + " ("
			for n in range(10):
				if dacq_jsbut(n):
					t = t+('%d'%n)
				else:
					t = t+'.'
			t = t + ")"
		try:
			last = self.__lastledbar
		except AttributeError:
			last = ""
			
		if not last == t:
			self.__ledbar.configure(text=t)
			self.__lastledbar = t
		

	def isrunning(self):
		"""Query to see if a task is running.

		Returns: 0 or 1

		"""
		return self.running

	def ispaused(self):
		"""Query to see if current task is paused.

		Returns: 0 or 1

		"""
		return self.paused

	def set_result(self, type=None):
		"""Save the result of this trial (or clear saved results if called
		with no arguments.

		"""
		# combination of self.tally() and self.history()
		if type is None:
			self._results = []
		else:
			self._results.append(type)
			self.history(type[0])
			self.tally(type=type)
			self.__runstats_update(resultcode=type)

	def get_result(self, nback=1):
		"""Get the nth to last saved trial result code.

		Note that get_result(1) is result from last trial, not get_result(0)

		"""
		if len(self._results):
			return self._results[-nback]
		else:
			return None

	def tally(self, type=None, clear=None, cleartask=None):
		ctask = self.task_name
		if clear:
			# clear everything
			self.tallycount = {}
		elif cleartask:
			# just clear current task data
			for (task,type) in self.tallycount.keys():
				if ctask == task:
					del self.tallycount[(task,type)]
		elif type:
			# add new data to current task stats
			try:
				self.tallycount[ctask,type] = self.tallycount[ctask,type] + 1
			except KeyError:
				self.tallycount[ctask,type] = 1
			try:
				del self.tally_recent[0]; self.tally_recent.append(type)
			except AttributeError:
				self.tally_recent = [''] * 5

		ks = self.tallycount.keys()
		ks.sort()

		(ntot, s) = (0, '')
		keys = self.tallycount.keys()
		keys.sort()
		for (task,type) in keys:
			d = string.split(type)
			if len(d) > 1:
				d = "%s (%s)" % (d[0], string.join(d[1:]))
			else:
				d = d[0]
			s = s + '%s %s: %d\n' % (task, d, self.tallycount[(task,type)])
			ntot = ntot + self.tallycount[(task,type)]
		s = s + '\ntotal: %d trials\n\n' % ntot

		try:
			N = len(self.tally_recent)
			for n in range(N):
				if n == 0:
					s = s + 'History\n'
				s = s + '%d: %s\n' % (-(N-n), self.tally_recent[n])
		except AttributeError:
			pass

		self.tallyw.clear()
		self.tallyw.write(s)

	def getcommon(self):
		"""Get common params, extend with eyecoil settings.."""
		d = self.rig_common.check()
		d = self.sub_common.check(mergewith=d)
		d['@eye_xgain'] = self.eye_xgain
		d['@eye_ygain'] = self.eye_ygain
		d['@eye_xoff'] = self.eye_xoff
		d['@eye_yoff'] = self.eye_yoff
		d['@pwd'] = os.getcwd()
		d['@host'] = self.__gethostname()

		# add flag for current notion of where spikes are really
		# coming from (currently: 'None', 'plexon' or 'tdt')
		if self.xdacq:
			d['datasrc'] = self.xdacq
		else:
			d['datasrc'] = 'None'

		return d

	def make_taskmenu(self, menubar):
		self.add_tasks(menubar, 'system', pypedir('Tasks'))
		self.add_tasks(menubar, '~pyperc', pyperc('Tasks'))
		files = glob.glob(pyperc('Tasks/*'))
		for d in files:
			m = posixpath.basename(d)
			# Tue Jan  4 11:50:19 2005 mazer
			#   skip names starting with an underscores (ie, disabled)
			if os.path.isdir(d) and not (m[0] == '_'):
				self.add_tasks(menubar, "~"+m, d)
		self.add_tasks(menubar, 'cwd', '.')

		pathlist = []
		if self.config.get('TASKPATH', None):
			pathlist.append(self.config.get('TASKPATH', None))
		if os.environ.has_key('TASKPATH'):
			pathlist.append(os.environ['TASKPATH'])

		for p in pathlist:
			for d in p.split(':'):
				try:
					self.add_tasks(menubar, posixpath.basename(d), d)
				except ValueError:
					Logger("pype: %s in $TASKPATH is a duplicate.\n" % d +
						   "      Terminal directory names must be unique;\n" +
						   "      skipped duplicates\n")

	def add_tasks(self, menubar, dropname, dirname):
		if dirname[-1] == '/':
			g = glob.glob(dirname+'*.py')
		else:
			g = glob.glob(dirname+'/*.py')

		tasks = []
		taskdescrs = {}
		for i in range(len(g)):
			# check each "task" to see if it's task or support file
			# based on !TASK! tag in header
			tasktype, taskdescr = self.__pypefile_type(g[i])
			if tasktype is 'task' or tasktype is None:
				x = posixpath.basename(g[i])
				tasks.append(x[:-3])
				if len(taskdescr) > 0:
					taskdescrs[tasks[-1]] = '  <%s>' % taskdescr
				else:
					taskdescrs[tasks[-1]] = ''

		if len(tasks) == 0:
			return
		else:
			_addpath(dirname, atend=1)
			

		dname = dirname
		if dname is '.': dname = 'current dir'
		
		tasks.sort()
		menubar.addmenu(dropname, '', '')
		menubar.addmenuitem(dropname, 'command', label=dname, foreground='blue')
		menubar.addmenuitem(dropname, 'separator')
		for i in range(0, len(tasks)):
			menubar.addmenuitem(dropname, 'command',
								label=tasks[i] + taskdescrs[tasks[i]],
								command=lambda s=self,t=tasks[i],d=dirname: \
								s.newloadtask(t, d))
		menubar.addmenuitem(dropname, 'separator')
		menubar.addmenuitem(dropname, 'command', label='Reload current',
							command=self.newloadtask)
		

	def unloadtask(self):
		if self.taskmod:
			try:
				self.taskmod.cleanup(self)
			except:
				reporterror(gui=1)
			self.taskmod = None

	def newloadtask(self, taskname=None, dir=None, ask=None):
		"""
		Load a task, if taskname==None and dir==None then we reload the current
		task, if possible.  If ask is true, then pop up a dialog box to ask for
		a filename..

		"""
		if ask:
			(f, mode) = filebox.Open(pattern='*.py')
			if f is None:
				return None
			dir = posixpath.dirname(f)
			taskname = posixpath.basename(f)
			if taskname[-3:] == '.py':
				taskname = taskname[:-3]

		if taskname is None:
			if self.task_name is None:
				warn('Error', "Nothing loaded to reload")
				return None
			taskname = self.task_name
			dir = self.task_dir

		try:
			if dir:
				(file, pathname, descr) = imp.find_module(taskname, [dir])
			else:
				dir = posixpath.dirname(taskname)
				if len(dir) == 0:
					dir = None
					(file, pathname, descr) = imp.find_module(taskname)
				else:
					taskname = posixpath.basename(taskname)
					if taskname[-3:] == '.py':
						taskname = taskname[:-3]
					(file, pathname, descr) = imp.find_module(taskname, [dir])
		except ImportError:
			warn('Error',
				 "Can't find task '%s' on search path.\n" % taskname +
				 "Try specifying a full path!")
			return None

		self.unloadtask()				# unload current, if it exists..

		try:
			try:
				Logger("pype: loading '%s' from '%s'\n" % (taskname, pathname))
				task = imp.load_module(taskname, file, pathname, descr)
			except:
				get_traceback(1)
				task = None
				_goto_error('Load Error')
		finally:
			# in case loading throws an exception:
			if file:
				file.close()

		if dir is None:
			dir = string.join(string.split(pathname, '/')[:-1], '/')

		if task:
			try:
				main = task.main
			except AttributeError:
				Logger("pype: warning -- no 'main' in %s\n" % taskname)
				main = None

			try:
				cleanup = task.cleanup
			except AttributeError:
				Logger("pype: warning -- no 'cleanup' in %s\n" % taskname)
				clean = None

			self.taskmod = task
			self.taskname(taskname, dir)

			if main:
				task.main(self)

		return task

	def set_canvashook(self, fn=None, data=None):
		"""
		Set function to call when unbound key is pressed in the
		udy canvas window. Function should take three arguments,
		e.g., **def hookfn(data, key, ev):...**.

		Where data is whatever you want the function to have
		and key is the string containing the key pressed and
		ev is the full event, in case you want (x,y) etc.

		The hook function should return 1 or 0 to indicate if
		the keypress was actually consumed.

		This function returns the old hookfn and hookdata values
		so they can be saved and restored.

		"""
		oldfn = self.udpy.userhook
		olddata = self.udpy.userhook_data
		self.udpy.userhook = fn
		self.udpy.userhook_data = data
		return (oldfn, olddata)

	def udpy_note(self, t=''):
		self.udpy.note(t)

	def eyeset(self, xgain=None, ygain=None, xoff=None, yoff=None):
		"""Update eye coil params from entry boxes"""

		k = self.rig_common.queryv('eye_smooth')
		k = dacq_eye_smooth(k)

		k = self.rig_common.queryv('fixbreak_tau')
		k = dacq_fixbreak_tau(k)

		try:
			self.eye_tweak = self._eye_tweak.component('entry').get()
		except:
			get_traceback(1)
			self.eye_tweak = 1

		if not xgain is None:
			self.eye_xgain = xgain
		else:
			try:
				self.eye_xgain = float(self._eye_xgain.component('entry').get())
			except:
				get_traceback(1)
				self.eye_xgain = 1.0
		self._eye_xgain.setentry(self.eye_xgain)

		if not ygain is None:
			self.eye_ygain = ygain
		else:
			try:
				self.eye_ygain = float(self._eye_ygain.component('entry').get())
			except:
				get_traceback(1)
				self.eye_ygain = 1.0
		self._eye_ygain.setentry(self.eye_ygain)

		if not xoff is None:
			self.eye_xoff = int(round(xoff))
		else:
			try:
				self.eye_xoff = int(self._eye_xoff.component('entry').get())
			except:
				get_traceback(1)
				self.eye_xoff = 0
		self._eye_xoff.setentry(self.eye_xoff)

		if not yoff is None:
			self.eye_yoff = int(round(yoff))
		else:
			try:
				self.eye_yoff = int(self._eye_yoff.component('entry').get())
			except:
				get_traceback(1)
				self.eye_yoff = 0
		self._eye_yoff.setentry(self.eye_yoff)

		# JAM 07-Feb-2003: prior to today monitor dimensions were not
		# taken into account in computing the gain values because we
		# always ran at 1024x768.  By including the ppd values, the
		# gain terms should now automatically adjust to make eye positions
		# come out in PIXELS, regardless of the current monitor resoultion.

		xg = self.eye_xgain * self.rig_common.queryv("mon_h_ppd")
		yg = self.eye_ygain * self.rig_common.queryv("mon_v_ppd")

		# send these along to the DACQ modules for fast calculation..
		dacq_eye_params(xg, yg, self.eye_xoff, self.eye_yoff)

	def init_framebuffer(self):
		sx = self.config.get('SYNCX', None)
		if not sx is None:
			sx = int(sx)
		sy = self.config.get('SYNCY', None)
		if not sy is None:
			sy = int(sy)

		self.fb = FrameBuffer(self.config.get('SDLDPY'),
							  self.config.iget('DPYW'),
							  self.config.iget('DPYH'),
							  self.config.iget('DPYBITS'),
							  self.config.iget('FULLSCREEN'),
							  syncsize=self.config.iget('SYNCSIZE'),
							  syncx=sx, syncy=sy,
							  synclevel=self.config.iget('SYNCLEVEL'),
							  opengl=self.config.iget('OPENGL'))

		self.fb.app = self
		g = self.config.fget('GAMMA')
		if self.fb.set_gamma(g):
			Logger("pype: gamma set to %f\n" % g)
		else:
			Logger("pype: hardware does not support gamma correction\n")

		# turn off the xserver's audible bell and screensaver!
		d = self.config.get('SDLDPY')
		if os.system("xset -display %s b off" % d):
			Logger("Can't run xset to turn off bell!\n")
		if os.system("xset -display %s s off" % d):
			Logger("Can't run xset to turn off screen saver!\n")
		if os.system("xset -display %s -dpms" % d):
			Logger("Can't run xset to turn off DPMS!\n")

	def __get_statefile_name(self, accesscheck=None):
		hostname = self.__gethostname()
		fname = subjectrc('pypestate.%s' % hostname)
		if accesscheck:
			if not posixpath.exists(fname):
				# statefile doesn't exist, make sure we can write it
				# when we exit later, so open for write then delete.
				# This will raise IOError if it's not accessible:
				open(fname, 'w').close()
				os.unlink(fname)
			elif not os.access(fname, os.W_OK):
				raise IOError
		return fname

	def __gethostname(self):
		"""Safe version of socket.gethostname().

		Returns the first part of socket.gethostname(),	if a
		hostname is actually defined, otherwise returns 'NOHOST'.

		"""
		try:
			return string.split(socket.gethostname(), '.')[0]
		except:
			get_traceback(1)
			return 'NOHOST'

	def __pypefile_type(self, fname):
		"""
		Scan a python file looking in the comments for a tag that indicated
		whether this particular file is a "task" or a "module".

		returns: (["task" or "module" or None], comment-string)

		"""
		re_task = re.compile('.*#.*!TASK!.*')
		re_module = re.compile('.*#.*!MODULE!.*')
		comment = None
		try:
			f = open(fname, 'r')
			# read up to about 50 lines from the file
			lines = f.readlines(80*50)
			f.close()
			for l in lines:
				if re_task.search(l):
					comment = re.split('!TASK!', l)[-1].strip()
					return 'task', comment
				if re_module.search(l):
					comment = re.split('!MODULE!', l)[-1].strip()
					return 'module', comment
			return None, ''
		except:
			get_traceback(1)
			return None, ''

	def __savestate(self):
		if self.tk:
			d = {}

			# force updating of local parameters..
			self.eyeset()

			d['eye_xgain'] = self.eye_xgain
			d['eye_ygain'] = self.eye_ygain
			d['eye_xoff'] = self.eye_xoff
			d['eye_yoff'] = self.eye_yoff
			d['eye_tweak'] = self.eye_tweak
			d['tallycount'] = self.tallycount

			file = open(self.__get_statefile_name(), 'w')
			cPickle.dump(d, file)
			file.close()

			# save common params worksheet
			self.rig_common.save()
			self.sub_common.save()

	def __readstate(self):
		try:
			file = open(self.__get_statefile_name(), 'r')
			d = cPickle.load(file)
			file.close()
			try:
				self.tallycount = d['tallycount']
				del d['tallycount']
			except KeyError:
				self.tallycount = {}
			return d
		except IOError:
			return None

	def __runstats_update(self, clear=None, resultcode=None):
		if clear is not None:
			self.__runstats = {}
			self.__runstats['ncorrect'] = 0
			self.__runstats['nerror'] = 0
			# this is really sequential ui's
			self.__runstats['nui'] = 0
		elif resultcode is not None:
			r = resultcode[0]

			if r in 'C':
				self.__runstats['ncorrect'] = self.__runstats['ncorrect'] + 1
				self.__runstats['nui'] = 0
			elif r in 'EM':
				self.__runstats['nerror'] = self.__runstats['nerror'] + 1
				self.__runstats['nui'] = 0
			elif r in 'U':
				self.__runstats['nui'] = self.__runstats['nui'] + 1

			nmax = self.sub_common.queryv('max_trials')
			n = self.__runstats['ncorrect'] + self.__runstats['nerror']
			if (nmax > 0) and n > nmax:
				self.set_state(running=0)
				warn('Warning',
					 '%d total trials reached -- stopping.' % n, wait=0)

			nmax = self.sub_common.queryv('max_correct')
			n = self.__runstats['ncorrect']
			if (nmax > 0) and n > nmax:
				self.set_state(running=0)
				warn('Warning',
					 '%d correct trials reached -- stopping.' % n, wait=0)

			nmax = self.sub_common.queryv('max_ui')
			n = self.__runstats['nui']
			if (nmax > 0) and n > nmax:
				self.set_state(running=0)
				warn('Warning',
					 '%d sequential UI trials -- stopping.' % n, wait=0)

		ne = self.__runstats['nerror']
		nc = self.__runstats['ncorrect']
		nu = self.__runstats['nui']
		nt = nc + ne
		s = string.join((
			' running = %d'    % (self.isrunning(),),
			'----------------------------------',
			'  nerror = %d'      % (ne,),
			'ncorrect = %d [%d]' % (nc, self.sub_common.queryv('max_correct'),),
			'     nui = %d [%d]' % (nu, self.sub_common.queryv('max_ui'),),
			' ntrials = %d [%d]' % (nt, self.sub_common.queryv('max_trials'),),
			'----------------------------------'), '\n')
		self.statsw.configure(text=s)

	def query_ncorrect(self):
		return self.__runstats['ncorrect']
	
	def query_nerror(self):
		return self.__runstats['nerror']
	
	def query_ntrials(self):
		# note: UI's and ABORTs don't count as trials
		return self.__runstats['ncorrect'] + self.__runstats['nerror']

	def OBSOLETE_trial_ui(self, uimax=None):
		"""This trial was un-initiated.."""
		if uimax is None:
			uimax = self.sub_common.queryv('uimax')
			trialstats['uicount'] = self.trialstats['uicount'] + 1
		if uimax and (self.trialstats['uicount']  > uimax):
			warn('Warning',
				 'UI Count exceeded.\nTime: %s\nPlease intervene.\n' %
				 Timestamp(), wait=1)
			self.trialstats['uicount'] = 0

	def OBSOLETE_trial_clear(self):
		# runset stats
		self.trialstats['trialnum'] = 0	# number of total trial
		self.trialstats['ntrials'] = 0	# number of real/iniated trial
		self.trialstats['ncorrect'] = 0	# number correct (out of ntrials)
		self.trialstats['uicount'] = 0	# number UI trials

	def OBSOLETE_trial_new(self):
		"""Starting a new trial..."""
		self.trialstats['trialnum'] = self.trialstats['trialnum'] + 1

	def OBSOLETE_trial_correct(self, correct):
		"""This trial was correct..."""
		if correct:
			self.trialstats['ncorrect'] = self.trialstats['ncorrect'] + 1
		self.trialstats['ntrials'] = self.trialstats['ntrials'] + 1
		self.trialstats['uicount'] = 0

	def new_cell(self):
		try:
			n = int(self.sub_common.queryv('cell'))
			n = n + 1
			self.sub_common.set('cell', "%d" % n)
		except ValueError:
			warn('Warning', "cell field is non-numeric, can't increment.")

	def set_fxfy(self):
		self.sub_common.set('fix_x', "%d" % self.udpy.fix_x)
		self.sub_common.set('fix_y', "%d" % self.udpy.fix_y)

	def set_startfn(self, fn):
		self.startfn = fn
		if self.startfn:
			self._realstart.config(state=DISABLED)
			self._tmpstart.config(state=DISABLED)
			self._stop.config(state=NORMAL)
		else:
			self._realstart.config(state=NORMAL)
			self._tmpstart.config(state=NORMAL)
			self._stop.config(state=DISABLED)

	def __start(self):
		self.__start_helper(temp=None)

	def __starttmp(self):
		self.__start_helper(temp=1)

	def __start_helper(self, temp=None):
		if not self.startfn:
			self.tk.bell()
			return

		self.__savestate()
		if not self.running:
			self._loadmenu.disableall()
			self._button_bounce.config(state=DISABLED)
			self._button_slideshow.config(state=DISABLED)
			self._realstart.config(state=DISABLED)
			self._tmpstart.config(state=DISABLED)
			self._stop.config(state=NORMAL)
			
			if int(self.rig_common.query('testing')):
				if ask("pype", "testing mode ok?", ("yes", "no")) == 1:
					return
			if temp:
				if self.sub_common.queryv('save_tmp'):
					fname = './%s.tmp' % self.uname
					if posixpath.exists(fname):
						posix.unlink(fname)
				else:
					fname = '/dev/null'
				self.record_selectfile(fname)
			else:
				if self.record_selectfile() is None:
					Logger('pype: run aborted\n')
					return

			# If elog is in use, then at the end of each run insert
			# (or update, since force=1) data on this file in the
			# sql database.
			# Do this at the START of the run so it can be seen right
			# away..
			if self.use_elog and not temp:
				import elogapi
				(ok, ecode) = elogapi.AddDatafile(
					self._exper,
					self.sub_common.queryv('full_subject'),
					self.uname,
					self.record_file,
					self.task_name,
					force=1)
				if not ok:
					warn('Warning (elog)', ecode)
				#del self._exper

			if self.xdacq == 'plexon':
				warn('xdacq', "start the plexon now. I'll wait.", wait=1)
			elif self.xdacq == 'tdt':
				# start new block in current tank, this includes resting the
				# trial counter..
				(server, tank, block) = self.tdt.newblock(record=1)
				Logger('pype: tdt data = %s %s\n' % (tank, block))

			self._allowabort = 1

			self.console.clear()

			# clear/reset result stack at the start of the run..
			self.set_result()

			try:
				# make sure graphic display is visible
				if self.psych: self.fb.show()
				# clear block state before starting a run
				self.__runstats_update(clear=1)

				try:
					# call task-specific start function.
					self.startfn(self)
				except:
					get_traceback(1)
					# some error occured within the task code
					_goto_error('Runtime Error')
			finally:
				# either there was an error OR the task
				# completed normally, ensure proper cleanup
				# gets done:
				dacq_set_pri(0)
				dacq_set_mypri(0)
				dacq_set_rt(0)
				self.idlefb()
				self._allowabort = 0
				
				self._realstart.config(state=NORMAL)
				self._tmpstart.config(state=NORMAL)
				self._button_bounce.config(state=NORMAL)
				self._button_slideshow.config(state=NORMAL)
				self._loadmenu.enableall()
				
				if self.psych:
					self.fb.hide()

			if self.xdacq == 'plexon':
				warn('xdacq', 'Stop the plexon NOW', wait=0)
			elif self.xdacq == 'tdt':
				# recording's done -- direct output back to TempBlk
				self.tdt.newblock(record=0)

		else:
			self.running = 0
			self.udpy.eye_clear()

	def shutdown(self):
		"""
		*Internal* (should never be called by user/application directly)
		Sets the terminate flag in this instance of PypeApp. This
		will eventually cause the PypeApp to exit, once the current
		run is stopped.

		"""
		if self.running:
			if self.tk:
				self.tk.bell()
		else:
			self.__savestate()			# Do this NOW!
			Logger('pype: user shutdown/close -- terminating.\n')
			self.terminate = 1

	def ts(self):
		"""
		Returns current 'time', as determined by the DACQ module.
		This is the veridical time in ms...

		"""
		return dacq_ts()

	def status(self, s):
		"""Set the GUI status message (eg, 'running', 'busy', 'idle' etc)."""
		if self.tk:
			self._status.config(text=s)
		else:
			raise GuiOnlyFunction, "status"

	def eye_txy(self):
		"""
		Get last measured eye position and time of measurement.
		Returns: (time_ms, xpos_pix, ypos_pix)

		"""

		ts = dacq_ts()
		if (self._last_eyepos) is None or (ts > self._last_eyepos):
			self._eye_x = dacq_eye_read(0)
			self._eye_y = dacq_eye_read(1)
			self._last_eyepos = ts
		return (self._last_eyepos, self._eye_x, self._eye_y)

	def eyepos(self):
		"""Get last measured eye position, no time info.

		Returns: (xpos_pix, ypos_pix)

		"""
		(t, x, y) = self.eye_txy()
		return (x, y)

	def looking_at(self, x=0, y=0):
		"""Tell pype where the monkey's supposed to be looking.

		This is crucial for the F8 key -- when you hit F8 telling
		pype to rezero the eyeposition, it assumes that the monkey
		is looking at this location (in pixels) when you strike the
		key.

		"""
		self._eyetarg_x = x
		self._eyetarg_y = y

	def eyeshift(self, x=0, y=0, reset=None, zero=None):
		"""Adjust X & Y offsets to set DC-offsets for eye position

		- if (reset) --> set x/y offsets to (0,0)

		- if (zero)  --> set x/y offset to current gaze position

		- otherwise --> shift the offsets by (x*xincr, y*yincr); use a
		  lambda expression if you want to shift in a callback
		  function to set the options.

		"""
		if reset:
			x, y = 0, 0
		elif zero:
			(x, y) = (dacq_eye_read(0), dacq_eye_read(1))
			x = float(self._eye_xoff.component('entry').get()) + x
			y = float(self._eye_yoff.component('entry').get()) + y
			x = x - self._eyetarg_x
			y = y - self._eyetarg_y
			self.status('[EYE_ZERO]')
		else:
			x = x * int(self._eye_tweak.component('entry').get())
			y = y * int(self._eye_tweak.component('entry').get())
			x = float(self._eye_xoff.component('entry').get()) + x
			y = float(self._eye_yoff.component('entry').get()) + y
		self._eye_xoff.setentry('%.0f' % x)
		self._eye_yoff.setentry('%.0f' % y)
		self.eyeset()
		self.encode(EYESHIFT)

	def drain(self):
		if not self.running:
			warn('Warning',
				 "I'm sorry Ben, but I can't do that (drain juice).", wait=0)

	def idlefn(self, ms=None, update=1, toplevel=None, fast=None):
		"""Idle function -- call me to kill time.

		The idle function -- this function should be call periodically
		by everything.  Whenever the program's looping or busy waiting
		for something (bar to go up/down, timer to expire etc), the
		app should just call idlefn().  The optional ms arg will run
		the idle function for the indicated amount of time -- this is
		not accurate; it just uses the tk after() command, so it's
		X11 limited and only approximate.

		This function is also responsible for monitoring the GUI's
		keyboard queue and handling key events.  Right now only some
		basics are implemented -- give a drop of juice, open/close
		solenoid, run/stop etc.. more can be implemented and eventually
		there should be a way to set user/app specific keybindings
		just like the user buttons.

		**NOTE:**
		anywhere this is called you **MUST** catch the *UserAbort* exception!!!

		"""


		if self._post_fixbreak:
			self._post_fixbreak = 0
			raise FixBreak
		if self._post_bartransition:
			self._post_bartransition = 0
			raise BarTransition
		if self._post_alarm:
			self._post_alarm = 0
			raise Alarm

		if fast:
			return

		if (not self.recording) and (self.plex is not None):
			# drawin the plexon buffer to prevent overflow when
			# pype is idle...
			tank, ndropped = self.plex.drain()
			if tank is None:
				Logger('pype: lost plexon signal.. this is bad..')

		if self.plex:
			self.record_led.configure(text=self.plex.status())


		if self.tk is None:
			if not ms is None:
				t = Timer()
				while t.ms() < ms:
					pass
		elif ms is None:
			# If gamepad/joystick attached -- use as follows:
			#  0,1,2,3 --> SIMULATEED DIGITAL I/O LINES (comedi_server handles)
			#  4,5,6,7 --> special functions, see below
			# NOTE: 0,1,2.. refers to "labels" 1,2,3...
			#
			# 0 ("1"): Response Bar
			# 1 ("2"): Juice squirter (aka SW1)
			# 2 ("3"): userdefined switch 2 (aka SW2)
			# 3 ("4"): not used
			# 4 ("5"): alternate stop button
			# 5 ("6"): alternate F8 (zero eye tracker)
			# 6+7 ("7"+"8"): emergency quit hotkey
			if dacq_jsbut(-1):
				if dacq_jsbut(4):
					if self.running:
						self.__start_helper()
				elif dacq_jsbut(5):
					self.eyeshift(zero=1)
				elif dacq_jsbut(6) and dacq_jsbut(7):
					sys.stderr.write('JOYSTICK PARACHUTE DEPLOYED!\n')
					sys.exit(0)

			(c, ev) = self.keyque.pop()
			if 0 and (c is None) and self.fb:
				ks = self.fb.getkey(wait=None, down=1)
				if ks == 0:
					pass
				else:
					print "<pygame key code: %d>" % ks
			if c == 'F1':
				if not self.running:
					self.juice_on()
					w = warn('Warning', "Juicer is OPEN!!!")
					self.juice_off()
			elif c == 'F3' or c == 'Escape':
				if self._allowabort:
					self.status('[UserAbort]')
					raise UserAbort
			elif c == 'F4':
				self.console.writenl("F4", color='red')
				self.reward()
			elif c == 'F5':
				if self.running:
					self.paused = not self.paused
					if self.paused:
						self.status('Will pause at end of trial')
					else:
						self.status('')
			elif c == 'F8':
				self.eyeshift(zero=1)

			if self.pport and pp_sw3():
				self.close()
				Logger('pype: user requested exit.\n')
				sys.exit(0)

			if self.config.iget('ENABLE_SW1'):
				if self.sw1():
					try:
						tt = self.sw1_timer.ms()
					except:
						tt = 1e9
						self.sw1_timer = Timer()
					# enforce 250ms between reward shots..
					if tt > 250:
						self.reward()
						self.sw1_timer.reset()

			x, y = self.eyepos()
			try:
				self.udpy.eye_at(x, y)
			except TclError:
				pass

			if update:
				self.tk.update()

			if self.taskidle:
				self.taskidle(self)

			self.drawledbar()
			
		else:
			t = Timer()
			while t.ms() < ms:
				self.idlefn()

	def history(self, c=None, init=0):
		"""
		Maintains a 'history stack' ala cortex.  Cortex did do somethings
		right.  The size of the history stack is set by LEN below; it's
		defined in the __init__() function above, you can overright it,
		if you like..  Called with no arguments, history stack will be
		cleared.

		"""

		LEN = 40

		if init:
			self._histstr = ''
		else:
			if c is None:
				self._histstr = '.' * LEN
			else:
				if len(self._histstr) > LEN:
					self._histstr = self._histstr[1:] + c
				else:
					self._histstr = self._histstr + c
		if self.tk:
			if len(self._histstr):
				self._hist.config(text='run hist: ' + self._histstr)
			else:
				self._hist.config(text='')

	def alarm(self):
		for i in range(1):
			for f in range(1000, 3000, 1000):
				beep(f, 10)
			for f in range(3000, 1000, -1000):
				beep(f, 10)

	def warningbeep(self, start=1):
		if start:
			for n in range(3):
				beep(1000, 100)
				beep(0, 10)
		else:
			beep(1000, 100)
			beep(0, 10)
			beep(500, 100)
			beep(0, 10)

	def warn_run_start(self):
		self.warningbeep(1)

	def warn_run_stop(self):
		self.warningbeep(0)

	def warn_trial_correct(self):
		"""
		Currently a NOP, but could be used for positive feedback.

		"""
		warble(3*440, 100)
		pass

	def warn_trial_incorrect(self, flash=1000):
		"""
		Beep and possibly flash screen red for a short time.

		"""
		warble(440, 100)
		if flash:
			self.fb.clear((255, 0, 0), flip=1)
			self.idlefn(flash)
			self.fb.clear((1, 1, 1), flip=1)

	def led(self, state):
		if self.tk:
			if state == 0:
				self.userinfo.configure(bg='#ffc0cb')
			elif state == 1:
				self.userinfo.configure(bg='#c0ffcb')
			elif state == 2:
				self.userinfo.configure(bg='#c0cbff')
			else:
				self.userinfo.configure(bg='white')

	def OBSOLETE_nreps(self):
		"""Query the number of repetitions (slider value)"""
		if self.tk:
			return self.sub_common.queryv('nreps')
		else:
			raise GuiOnlyFunction, "nreps"

	def OBSOLETE_notdone(self, repnum):
		"""Continue running or abort/done?"""
		nreps = self.nreps()
		if self.running and (nreps == 0 or repnum < nreps):
			return 1
		else:
			return 0

	def runstate(self, state=1):
		if state:
			self.paused = 0
			self.running = 1
			self.led(1)
			self.warningbeep(1)
		else:
			self.running = 0
			self.warningbeep(0)
			self.record_done()
			self.led(0)
			self.repinfo()				# clear rep num display

	def dropsize(self):
		"""Query the dropsize (in ms; from slider)"""
		if self.tk:
			return self.sub_common.queryv('dropsize')
		else:
			raise GuiOnlyFunction, "dropsize"

	def dropvar(self):
		"""Query the dropsize variance (in ms)"""
		if self.tk:
			return self.sub_common.queryv('dropvar')
		else:
			raise GuiOnlyFunction, "dropvar"

	def reward(self, multiplier=1.0, dobeep=1, ms=None):
		"""
		Deliver a squirt of juice based on the dropsize slider and
		the current state of the reward schedule settings

		Returns the actual size of the reward (ms open) delivered

		"""

		# if var==0, then ms is the exact time of the drop, if var>0
		# then drop time is selected randomly from a normal distribution
		# with mean=ms, std=var

		# becasue the distribution is normal, very small and very
		# large numbers can (rarely) come up, so you MUST clip the
		# distribution to avoid pype locking up in app.__reward2()...

		if ms is None:
			ms = int(round(multiplier * float(self.dropsize())))
			sigma = sqrt(self.dropvar())
		else:
			# user specified ms, no variance
			sigma = 0

		if ms == 0:
			return

		if not self.config.iget('REWARD_BEEP'):
			# Mon Aug  8 09:58:39 2005 mazer
			# NO_REWARD_BEEP overrides everything else
			dobeep = 0

		maxreward = self.sub_common.queryv('maxreward')
		minreward = self.sub_common.queryv('minreward')

		if sigma > 0:
			while 1:
				t = normal(mean=ms, sigma=sigma)
				if (t > minreward) and (t < maxreward):
					break
			if dobeep:
				beep(440, 40)
			if not self.config.iget('DACQ_TESTMODE'):
				thread.start_new_thread(self.__reward2, (t,))
			if self.tk:
				self.console.writenl("[ran-reward=%dms]" % t, color='black')
			actual_reward_size = t
		else:
			if dobeep:
				beep(1000, 100)
			if not self.config.iget('DACQ_TESTMODE'):
				self.juice_drip(ms)
			if self.tk:
				self.console.writenl("[reward=%dms]" % ms, color='black')
			actual_reward_size = ms
		self.dropcount = self.dropcount + 1

		# Fri Dec  8 14:02:49 2006 mazer
		#  automatically encode the actual reward size (ms open) in
		#  the data file
		self.encode('ACT_' + REWARD + '%d' % actual_reward_size)

		return actual_reward_size

	def __reward2(self, t):
		"""
		This is ONLY to be called from inside reward(), not a user-visble
		function. The point is to call juice_drip() in a separate thread
		and to block over rewards from being delivered until this one's
		finished.

		"""
		self._rewardlock.acquire()
		self.juice_drip(t)
		self._rewardlock.release()

	def juice_on(self):
		if self.pport:
			pp_juice(1)
		else:
			dacq_juice(1)

	def juice_off(self):
		if self.pport:
			pp_juice(0)
		else:
			dacq_juice(0)

	def juice_drip(self, ms):
		if self.pport:
			pp_juice_drip(int(0.5+ms))
		else:
			dacq_juice_drip(int(0.5+ms))

	def barchanges(self, reset=None):
		"""
		(NEW: Sun Mar  9 13:38:36 2003 mazer)

		This counts transitions on the bar line -- should be reset
		at once you're sure monkey's grabbed the bar and then monitored
		for any increases..  Increments each time there's a state
		change (0->1 or 1->0).  Sampled at DACQ frequency (~1khz), so
		as to avoid loosing signals during CPU intensive graphics.

		"""
		if reset:
			return dacq_bar_transitions(1)
		else:
			return dacq_bar_transitions(0)

	def bar_genint(self, enable=1):
		"""
		If this is enabled, then the das_server will generate a SIGUSR1
		interupt each time the bar changes state.  This gets caught
		by an internal function and converted into a python
		exception: BarTransition.

		Don't even THINK about calling this outside a try/except
		wrapper or you're asking for trouble...

		"""
		if enable:
			dacq_bar_genint(1)
		else:
			dacq_bar_genint(0)
			# also: clear saved flag -- no more interupts
			# in theory you could loose a pending interupt here, but it
			# should be unlikely.
			self._post_bartransition = 0


	def set_alarm(self, ms=None, clear=None):
		"""
		Set an alarm to go off in "ms" milliseconds. When the
		alarm goes off it will generate an Alarm exception AT THE NEXT
		CALL TO idlefn(). To clear the alarm (before it goes off), call
		with no args. There is only ONE alarm/timer per dacq process!

		**NOTE:**
		This requires app.allow_ints to be true in order to work!

		"""
		if ms:
			dacq_set_alarm(ms_from_now)
		elif clear:
			dacq_set_alarm(0)

	def int_handler(self, signal, frame):
		"""This is for catching SIGUSR1's from the dacq process"""
		if self.allow_ints:
			# disable interupts until explicitly re-enabled..
			# this acts like a latch and prevents re-entry as well..
			self.allow_ints = 0

			# class/arg is:
			#   1: digital input transition (arg is input # that changed)
			#		 bar is input #0
			#   2: fixwin break (arg is meaningless -- always 0)
			iclass = dacq_int_class()
			iarg = dacq_int_arg()

			if iclass == 1:
				if iarg == 0:
					dacq_release()
					# Sat Sep  3 16:41:55 2005 mazer
					# Changed this to set a flag instead of actually
					# raising the exception. Exceptions are now raised
					# within idlefn().
					self._post_bartransition = 1
					#raise BarTransition
				else:
					# not a bar transition, re-enable ints
					self.allow_ints = 1
					return
			elif iclass == 2:
				# for fixwin breaks, arg is empty..
				dacq_release()
				# Sat Sep  3 16:41:55 2005 mazer
				# Changed this to set a flag instead of actually
				# raising the exception. Exceptions are now raised
				# within idlefn().
				self._post_fixbreak = 1
				# raise FixBreak
			elif iclass == 3:
				dacq_release()
				self._post_alarm = 1
			else:
				self.allow_ints = 1
				return
		else:
			pass

	def debug_handler(self, signal, frame):
		"""This is for catching SIGUSR2's for debugging.."""
		sys.stderr.write('\n------------------------------Recieved SIGUSR2:\n')
		traceback.print_stack(frame)
		keyboard()

	def bardown(self):
		if self.pport:
			return pp_bar()
		else:
			if self.flip_bar:
				return not dacq_bar()
			else:
				return dacq_bar()

	def barup(self):
		return not self.bardown()

	def joybut(self, n):
		"""
		Query the nth joystick button (starting with #0)::

		  -1: no such butten
		  0: button up
		  1: button down

		"""
		return dacq_jsbut(n)

	def joyaxis(self):
		"""
		Query the joystick axis state. Returns (x,y)

		"""
		return (dacq_js_x(), dacq_js_y())

	def sw1(self):
		# if FLIP_SW1 < 0, disable switch 1 (for das08 problems)
		if self.flip_sw1 < 0:
			return 0
	
		if self.config.iget('DACQ_TESTMODE'):
			return 0
		elif self.pport:
			return pp_sw1()
		else:
			if self.flip_sw1:
				return not dacq_sw1()
			else:
				return dacq_sw1()

	def sw2(self):
		# if FLIP_SW2 < 0, disable switch 2 (for das08 problems)
		if self.flip_sw1 < 0:
			return 0
		if self.config.iget('DACQ_TESTMODE'):
			return 0
		elif self.pport:
			return pp_sw2()
		else:
			if self.flip_sw2:
				return not dacq_sw2()
			else:
				return dacq_sw2()

	def close(self):
		"""
		Close application -- shutdown the DACQ interface and framebuffer
		and restore the X11 bell.

		"""
		self.unloadtask()

		try:
			del self._testpat
		except:
			pass

		if self.fb:
			self.fb.close()
			self.fb = None
			# turn bell and screensaver back on -- this isn't really
			# quite right -- it always gets turned back on, even if they
			# weren't on to start with..
			d = self.config.get('SDLDPY')
			os.system("xset -display %s b on" % d)
			os.system("xset -display %s s on" % d)
			os.system("xset -display %s +dpms" % d)

		if self.dacq_going:
			dacq_stop()
			dacq_going = 0

		if self.plex is not None:
			self.plex.drain(terminate=1)
			Logger('pype: closed connection to plexon.\n')

		try:
			self.udpy.fidinfo(file=subjectrc('last.fid'))
			self.udpy.savepoints(subjectrc('last.pts'))
		except AttributeError:
			pass

		if self.tk:
			# only do the state thing if in GUI mode
			self.__savestate()
			Logger('pype: saved state.\n')

		Logger('pype: cleaning up sprites.\n')
		# added 28-feb-2004 to make sure that sprites are getting
		# properly del'ed and garbage collected
		n = len(Sprite.__list__)
		if n > 0:
			Logger('pype: warning -- %d sprites left in memory:\n' % n)
			for sname in Sprite.__list__:
				Logger('%s ' % sname)
			Logger('\n')
		Logger('pype: bye bye.\n')


	def repinfo(self, msg=None):
		self.__repinfo.configure(text=msg)

	def taskname(self, taskname=[], dir=[]):
		if taskname == []:
			return self.task_name

		if taskname is None:
			self.task_name = None
			if self.tk:
				self.__taskname.configure(text="task: none")
				self.balloon.bind(self.__taskname, None)
		else:
			self.task_name = taskname
			self.task_dir = dir
			if self.tk:
				self.__taskname.configure(text="task: %s" % self.task_name)
				self.balloon.bind(self.__taskname, self.task_dir)

	def _recfile(self):
		if self.tk:
			if self.record_file is None:
				self.__recfile.config(text="file: none")
				self.balloon.bind(self.__recfile, None)
			else:
				if len(self.record_file) > 40:
					spacer = "..."
				else:
					spacer = ""
				self.__recfile.config(text="file: %s%s"
									  % (spacer, self.record_file[-25:]))
				self.balloon.bind(self.__recfile, self.record_file)

	def set_userbutton(self, n, text=None, check=None, command=None):
		"""Set callback and label for user-defined buttons"""
		if not self.tk:
			raise GuiOnlyFunction, 'set_userbutton'
		if check:
			c = Checkbutton(self._cpane, text=text, relief=RAISED, pady=4)
		else:
			c = Button(self._cpane, text=text, relief=RAISED, command=command)
		c.pack(expand=0, fill=X, side=TOP, pady=2)
		return c

	def taskbutton(self, text=None, check=None, command=None):
		"""Set callback and label for user-defined buttons"""
		if not self.tk:
			raise GuiOnlyFunction, 'set_userbutton'
		if check:
			c = Checkbutton(self._cpane, text=text, relief=RAISED, pady=4)
		else:
			c = Button(self._cpane, text=text, relief=RAISED, command=command)
		c.pack(expand=0, fill=X, pady=4)
		return c

	def record_start(self):
		"""
		Clear the per-trial recording buffer and reset the per-trial
		timer.  This should be called at the start of every trial, always
		at the same point in the trial.  All timestamping will be relative
		to this call.

		"""

		# bump up the data collect process priorities
		dacq_set_pri(self.rig_common.queryv('dacq_pri'))
		dacq_set_mypri(self.rig_common.queryv('fb_pri'))
		if self.rig_common.queryv('rt_sched'):
			# if rt_sched is set in the rig menu, switch scheduler mode
			# to real time for the duration of the trial
			dacq_set_rt(1)

		self.record_buffer = []

		# Thu Oct 23 15:51:34 2008 mazer
		#
		# - The record_state() function can now block for 250ms to
		#   ensure that the plexon has time to register onset of new
		#   trial, therefore, the timestamp should be recorded when
		#   record_state() returns, not before it's called.
		#
		# - So the t=self.encode(START) has been moved from right
		#   before the self.record_state(1) to right after

		# tell plexon trial is BEGINNING
		self.record_state(1)
		t = self.encode(START)

		# Mon Oct 27 12:56:47 2008 mazer
		# - log full 'time of day' for start event
		self.encode('TOD_START %f' % time.time())

		self.recording = 1

		# start with fresh eye trace..
		self.udpy.eye_clear()

		# save recording start time -- this is used to ensure
		# 250ms between start/stop events for proper plexon sync

	def record_stop(self):
		"""
		Possibly clean up after a trial, right now all this does is
		reset the eye trace

		"""

		# Thu Oct 23 15:53:43 2008 mazer
		# see note about re self.encode(START) -- this has been moved
		# to right AFTER the self.record_state(0) call to avoid
		# problems with plexon sync..

		self.udpy.eye_clear()

		# tell plexon trial is OVER
		self.recording = 0
		self.record_state(0)
		t = self.encode(STOP)

		# Mon Oct 27 12:56:47 2008 mazer
		# - log full 'time of day' for start event
		self.encode('TOD_STOP %f' % time.time())

		# bump back down the data collect process priorities
		dacq_set_pri(0)
		dacq_set_mypri(0)
		dacq_set_rt(0)

		if self.plex is not None:
			self.xdacq_data_store = _get_plexon_events(self.plex, fc=40000)

	def status_plex(self):
		if self.plex is not None:
			Logger("pype: plexon units --")
			for (chan, unit) in self.plex.neuronlist():
				Logger(" sig%03d%c" % (chan, chr(ord('a')+unit)))
			Logger("\n")
		else:
			Logger("pype: plexnet not enabled.")

	def record_state(self, state):
		"""Enable or disable plexon recording state"""

		if not self.config.iget('DACQ_TESTMODE'):
			try:
				l = self._last_recstate
			except:
				self._last_recstate = dacq_ts()

			if self.xdacq is 'plexon':
				warn = 1
				while (dacq_ts() - self._last_recstate) < 250:
					if warn:
						sys.stderr.write('warning: short ITI, stalling\n')
						warn = 0
			# this is causing a wedge!!!
			dacq_dig_out(2, state)
			self._last_recstate = dacq_ts()
		if state:
			self.record_led.configure(fg='blue')
		else:
			self.record_led.configure(fg='red')

	def plexon_psth_trigger(self, state):
		"""change state on the plexon PSTH trigger input line"""
		if not self.config.iget('DACQ_TESTMODE'):
			dacq_dig_out(1, state)

	def eyetrace(self, on):
		"""
		Begin recording eye trace data now. Or, stop recording eye
		data now.  Be sure to call this before you save data with
		record_write() below!

		"""
		if on:
			dacq_adbuf_toggle(1)
			self.encode(EYE_START)
			self._eyetrace = 1
		elif self._eyetrace:
			# only allow turn off once..
			self.encode(EYE_STOP)
			if dacq_adbuf_toggle(0):
				self.encode(EYE_OVERFLOW)
				Logger('pype: warning -- eyetrace overflowed\n')
				warn('Warning', 'eye trace overflow')
			self._eyetrace = 0

	def encode(self, code):
		"""
		Insert <code> into the per-trial buffer along with the current
		trial timestamp (relative to the last call to start_trial.

		Thu Nov 10 15:37:09 2005 mazer

		- If code is a tuple, then encode all the items in the tuple
		  with the same timestamp.

		"""

		t = dacq_ts()
		if type(code) is TupleType:
			for c in code:
				self.record_buffer.append((t, c))
		else:
			self.record_buffer.append((t, code))
		return t

	def get_spikes(self):
		"""
		Wrapper for get_spikes_now() method... (just for backwards
		compatibility).

		"""
		return self.get_spikes_now()

	def get_spikes_now(self):
		"""
		This is gets the spike data out from the ad/ad server in
		mid-trial. You can use this to do on-line statistics or
		generate dynamic stimuli etc.  It should not be considered
		the final data, only an approximation, particularly if you're
		still recording data when you call this.

		"""
		n = dacq_adbuf_size()
		t = zeros(n)
		s0 = zeros(n)

		for i in range(0,n):
			t[i] = dacq_adbuf_t(i)
			s0[i] = dacq_adbuf_c3(i)

		spike_thresh = int(self.rig_common.queryv('spike_thresh'))
		spike_polarity = int(self.rig_common.queryv('spike_polarity'))

		spike_times = _find_ttl(t, s0, spike_thresh, spike_polarity)
		return spike_times

	def get_eyepos_now(self):
		"""
		This function extracts the current state of the x/y eye
		position buffers from the dacq_server NOW.  Like get_spikes()
		you can use this in mid-trial or at the end of the trial
		to adapt the task based on his eye movements.  This should
		NOT be considered the final data, particularly if you're
		still in record mode when you call this function

		Returns: Numeric vectors **t**, **x** and **y**  containing x, y
		eye position and time (in ms) data from start of trial up to the
		current time.

		"""
		n = dacq_adbuf_size()
		t = zeros(n)
		x = zeros(n)
		y = zeros(n)

		for i in range(0,n):
			t[i] = dacq_adbuf_t(i)
			x[i] = dacq_adbuf_x(i)
			y[i] = dacq_adbuf_y(i)

		return (t, x, y)

	def get_photo_now(self):
		"""
		This function extracts the current photodiode trace.

		"""
		n = dacq_adbuf_size()
		t = zeros(n)
		p = zeros(n)

		for i in range(0,n):
			t[i] = dacq_adbuf_t(i)
			p[i] = dacq_adbuf_c2(i)

		return (t, p)

	def get_events_now(self):
		"""
		Returns COPY of current recorded event buffer, all the same
		warnings as the other get_XXXXX_now() methods above..

		"""
		return self.record_buffer[::]

	def record_write(self, result=None, rt=None, pdict=None, taskinfo=None):
		"""
		Write the current record to the specified datafile.

		"""

		if (self.record_file == '/dev/null') and \
			   self.sub_common.queryv('fast_tmp'):
			fast_tmp = 1
		else:
			fast_tmp = 0

		# force taskinfo to be a tuple..
		if type(taskinfo) != TupleType:
			taskinfo = (taskinfo,)

		# stop eye recording, just in case user forgot.
		self.eyetrace(0)

		n = dacq_adbuf_size()
		self.eyebuf_t = zeros(n)
		self.eyebuf_x = zeros(n)
		self.eyebuf_y = zeros(n)
		self.eyebuf_pa = zeros(n)
		p0 = zeros(n)
		s0 = zeros(n)

		# be careful here -- if you're trying to look at the photodiode
		# signals, you'd better not set fast_tmp=1...
		if not fast_tmp or self.show_eyetraces.get():
			if self.rig_common.queryv('save_chn_0'):
				c0 = zeros(n, Numeric.Int32)
			else:
				c0 = None
			if self.rig_common.queryv('save_chn_1'):
				c1 = zeros(n, Numeric.Int32)
			else:
				c1 = None
			if self.rig_common.queryv('save_chn_2'):
				c2 = zeros(n, Numeric.Int32)
			else:
				c2 = None
			if self.rig_common.queryv('save_chn_3'):
				c3 = zeros(n, Numeric.Int32)
			else:
				c3 = None
			if self.rig_common.queryv('save_chn_4'):
				c4 = zeros(n, Numeric.Int32)
			else:
				c4 = None

			for i in range(0,n):
				self.eyebuf_t[i] = dacq_adbuf_t(i)
				self.eyebuf_x[i] = dacq_adbuf_x(i)
				self.eyebuf_y[i] = dacq_adbuf_y(i)
				self.eyebuf_pa[i] = dacq_adbuf_pa(i)
				p0[i] = dacq_adbuf_c2(i)
				s0[i] = dacq_adbuf_c3(i)
				if not c0 is None:
					c0[i] = dacq_adbuf_c0(i)
				if not c1 is None:
					c1[i] = dacq_adbuf_c1(i)
				if not c2 is None:
					c2[i] = dacq_adbuf_c2(i)
				if not c3 is None:
					c3[i] = dacq_adbuf_c3(i)
				if not c4 is None:
					c4[i] = dacq_adbuf_c4(i)

		photo_thresh = int(self.rig_common.queryv('photo_thresh'))
		photo_polarity = int(self.rig_common.queryv('photo_polarity'))
		self.photo_times = _find_ttl(self.eyebuf_t, p0,
									  photo_thresh, photo_polarity)

		spike_thresh = int(self.rig_common.queryv('spike_thresh'))
		spike_polarity = int(self.rig_common.queryv('spike_polarity'))
		self.spike_times = _find_ttl(self.eyebuf_t, s0,
									  spike_thresh, spike_polarity)

		if self.show_eyetraces.get():
			norm = 1
			#norm = self.pix_per_dva
			self.plotEyetraces(self.eyebuf_t,
							   x=self.eyebuf_x / norm,
							   y=self.eyebuf_y / norm,
							   others=((p0, 'photos'),
									   (s0, 'spikes')),
							   raster=self.spike_times)

		self.udpy.info("[%dspks %dsyncs]" %
					   (len(self.spike_times), len(self.photo_times)))


		# Completely wipe the buffers -- don't let them accidently
		# get read TWICE!!  They're saved as self/app.eyebuf_[xyt]
		# in case you wawnt them for something..
		dacq_adbuf_clear()

		# insert these into the param dictionary for later retrieval
		pdict['PypeBuildDate']  = pypeversion.PypeBuildDate
		pdict['PypeBuildHost'] = pypeversion.PypeBuildHost
		pdict['PypeSvnInfo'] = pypeversion.PypeSvnInfo
		pdict['PypeSvnRev']  = pypeversion.PypeSvnRev

		if not fast_tmp and self.record_file:
			# dump the event stream
			info = (result, rt, pdict) + taskinfo

			#
			# note: added p0. s0 raw trace saving, 16-mar-2002
			#
			#
			# Wed Sep 11 14:36:42 2002 mazer
			#
			#  rec[0]		record type STRING: ('ENCODE' usually)
			#  rec[1]		info TUPLE: (trialresult, rt, paramdict, taskinfo)
			#						taskinfo can be ANYTHING user wants to
			#						save in the datafile
			#  rec[2]		event LIST: [(time, event), (time, event) ...]
			#  rec[3]		time VECTOR (numeric array)
			#  rec[4]		eye x-pos VECTOR (numeric array)
			#  rec[5]		eye y-pos VECTOR (numeric array)
			#  rec[6]		LIST of photodiode time stamps
			#  rec[7]		LIST of spike time stamps
			#  rec[8]		record_id (SCALAR; auto incr'd after each write)
			#  rec[9]		raw photodiode response VECTOR
			#  rec[10]		raw spike response VECTOR
			#  rec[11]		TUPLE of raw analog channel data
			#				(chns: 0,1,2,3,4,5,6), but 2 & 3 are same as
			#				rec[9] and rec[10], so they're just None's in
			#				this vector to save space. c5 and c6 aren't
			#				currently implemented
			#  rec[12]		pupil area data (if available) in same format
			#				as the eye [xy]-position data above. This is new
			#				as of 08-feb-2003 (JAM)
			#
			#  ** added rec[13] 31-oct-2005 (JAM) **
			#  rec[13]		on-line plexon data via PlexNet. This should be
			#				a list of (timestamp, unit) pairs, with timestamps
			#				in ms and unit's following the standard plexon
			#				naming scheme (01a, 02a, 02b etc..)

			if self.xdacq == 'tdt':
				# insert tdt tank info into the parameter table for this
				# trial so we can recover the data later.
				(server, tank, block, tnum) = self.tdt.getblock()

				# str() here convert UTF8 strings back to plain old ascii,
				# which is the only thing the p2m can currently handle. small
				# risk here -- don't use international chars for datafile names!
				#
				# NOTE: first trial has tdt_tnum == 1, not zero!!!!
				#
				info[2]['tdt_server'] = str(server.encode('ascii'))
				info[2]['tdt_tank'] = str(tank.encode('ascii'))
				info[2]['tdt_block'] = str(block.encode('ascii'))
				info[2]['tdt_tnum'] = tnum

			rec = [ENCODE, info, self.record_buffer,
				   list(self.eyebuf_t),
				   list(self.eyebuf_x), list(self.eyebuf_y),
				   self.photo_times, self.spike_times,
				   self.record_id, list(p0), list(s0),
				   (c0, c1, c2, c3, c4, None, None),
				   list(self.eyebuf_pa),
				   self.xdacq_data_store]

				   # note the None's in the line above are logical
				   # place holders for c2,c3, which are hardcoded
				   # as p0 and s0

			f = open(self.record_file, 'a')
			labeled_dump('encode', rec, f, 1)
			f.close()

		self.record_id = self.record_id + 1

		return (self.eyebuf_t, p0, s0)

	def record_note(self, tag, note):
		"""
		Insert note into current datafile

		"""
		if self.record_file:
			rec = [NOTE, tag, note]
			f = open(self.record_file, 'a')
			labeled_dump('note', rec, f, 1)
			f.close()

	def _guess_fallback(self):
		subject = self.sub_common.queryv('subject')
		train = self.sub_common.queryv('training')

		if train:
			cell = 0
		else:
			cell = self.sub_common.queryv('cell')

		try:
			pat = "%s%04d.*.[0-9][0-9][0-9]" % (subject, int(cell))
		except ValueError:
			pat = "%s%s.*.[0-9][0-9][0-9]" % (subject, cell)
		# generate list of files (including zipped files)
		flist = glob.glob(pat)+glob.glob(pat+'.gz')

		next = 0
		for f in flist:
			try:
				n = int(string.split(f, '.')[2])
				if n >= next:
					next = n + 1
			except ValueError:
				pass

		try:
			return "%s%04d.%s.%03d" % (subject, int(cell),
									   self.task_name, next)
		except ValueError:
			return "%s%s.%s.%03d" % (subject, cell,
									   self.task_name, next)

	def _guess_elog(self):
		import elogapi
		
		animal = self.sub_common.queryv('subject')
		train = self.sub_common.queryv('training')
		full_animal = self.sub_common.queryv('full_subject')

		if len(animal) == 0 or len(full_animal) == 0:
			warn('Warning (elog)',
				 "Set both 'subject' and 'full_subject' first!")
			return None

		# search database based on full_animal (animal=full_subject)
		exper = elogapi.GetExper(full_animal)
		if exper is None:
			# create first experiment based on 'subject', ie, file prefix..
			exper = "%s%04d" % (animal, 1)
		# update cell slot in worksheets with exper
		self.sub_common.set('cell', exper)

		if train:
			exper = exper[:-4] + '0000'
		self._exper = exper

		# now find next avilable number in the sequence
		pat = "%s.*.[0-9][0-9][0-9]" % (exper, )
		# generate list of files (including zipped files)
		flist = glob.glob(pat)+glob.glob(pat+'.gz')

		next = 0
		for f in flist:
			try:
				n = int(string.split(f, '.')[2])
				if n >= next:
					next = n + 1
			except ValueError:
				pass

		return "%s.%s.%03d" % (exper, self.task_name, next)

	def _guess(self):
		if self.use_elog:
			return self._guess_elog()
		else:
			return self._guess_fallback()

	def record_done(self):
		self.record_note('pype', 'run ends')
		self.record_file = None
		self._recfile()

	def record_selectfile(self, fname=None):
		if not fname is None:
			self.record_file = fname
		else:
			self.record_file = None
			while 1:
				g = self._guess()
				if g is None:
					return None
				(file, mode) = filebox.SaveAs(initialdir=os.getcwd(),
											  pattern='*.[0-9][0-9][0-9]',
											  initialfile=g,
											  datafiles=1)
				if file is None:
					return None
				else:
					self.record_file = file

					if posixpath.exists(self.record_file):
						if mode == 'w':
							Logger('pype: unlinking: %s\n' % \
								   self.record_file)
							posix.unlink(self.record_file)
						elif mode == 'a':
							Logger('pype: appending to: %s\n' % \
								   self.record_file)
					break

		self._recfile()
		self.record_note('pype', 'run starts')

		# stash the userparms dict in the file.. this contains
		# the monitor parameters, just in case they get lost
		# or forgotten..
		self.record_note('userparams', self.config.dict)

		return 1

	def idlefb(self):
		if self.fb:
			try:
				testpat = self._testpat
			except AttributeError:
				t = self.config.get('TESTPAT')
				if t and posixpath.exists(t):
					fname = t
				elif posixpath.exists(pyperc('testpat')):
					fname = pyperc('testpat');
				else:
					fname = libdir('testpat.png');
				# load new test pattern and scale to fit frame buffer
				s = Sprite(x=0, y=0,
						   fname=fname, fb=self.fb, depth=99, on=1)
				s.scale(self.fb.w, self.fb.h)
				self._testpat = s
					
			self.fb.clear((1,1,1))
			if self.testpat.get() and self._testpat:
				self._testpat.blit(force=1)
				s = Sprite(x=50, y=50, width=150, height=150,
						   fb=self.fb, on=1)
				s.fill((255,1,1))
				s.alpha[::]=128
				s.blit()
				s = Sprite(x=-50, y=-50,  width=150, height=150,
						   fb=self.fb, on=1)
				s.fill((1,255,1))
				s.alpha[::]=128
				s.blit()

			self.fb.sync(0)
			self.fb.flip()

	def plotEyetracesRange(self, start=None, stop=None):
		self.show_eyetrace_start = start
		self.show_eyetrace_stop = stop

	def plotEyetraces(self, t=None, x=None, y=None, others=None, raster=None):
		import iplot
		
		if len(t) > 0:
			# works even if _eyetrace_window is None
			oldgraph = iplot.attach(self._eyetrace_window)

			skip = int(self.rig_common.queryv('plotskip'))
			if skip < 1:
				skip = 1

			all = int(self.rig_common.queryv('plotall'))
			if not all:
				# we must be in a hurry, so don't plot everything...
				others = ()
				raster = None

			if self.show_eyetrace_start is not None:
				start = self.show_eyetrace_start
			else:
				start = t[0]

			if self.show_eyetrace_stop is not None:
				stop = self.show_eyetrace_stop
			else:
				stop = t[-1]

			t0 = t[0]

			if raster:
				nplots = 1 + len(others) + 1
			else:
				nplots = 1 + len(others) + 0

			pnum = 1
			iplot.subplot(nplots, 1, pnum)
			iplot.plot(t[::skip] - t0, x[::skip], 'r-')
			iplot.hold_on()
			iplot.plot(t[::skip] - t0, y[::skip], 'g-')
			iplot.hold_off()
			iplot.xrange(start - t0, stop - t0)
			iplot.ylabel('red=x grn=y')

			pnum = pnum + 1
			# plot the others
			for (data, name) in others:
				iplot.subplot(nplots, 1, pnum)
				iplot.plot(t[::skip] - t0, data[::skip], 'k-')
				iplot.ylabel(name)
				iplot.xrange(start - t0, stop - t0)
				pnum = pnum + 1

			if raster:
				# stop xmgrace error message for empty rasters..
				if len(raster) > 1:
					raster = array(raster) - t0
					iplot.subplot(nplots, 1, pnum)
					iplot.plot(raster, 0.0 * raster, 'o')
					iplot.yrange(-1,1)
					iplot.ylabel('raster')
					iplot.xrange(start - t0, stop - t0)

			# restore previous graph window (even if it's None)
			# attach() returns the current handle, so save it
			# (might be different if new or reopened window..)
			self._eyetrace_window  = iplot.attach(oldgraph)

	def showsprites(self):
		for n in range(0, len(Sprite.__list__)):
			Logger('%d: "%s"\n' % (n, sprite.Sprite.__list__[n]))

def pype_hostconfigfile():
	"""
	Return Read host-specfic Config file.
	Config file lives in $(PYPERC)/Config.{HOST_NAME}

	"""
	h = string.split(socket.gethostname(), '.')[0]
	return pyperc('Config.%s' % h)

def pype_hostconfig():
	"""
	Read host-specific config file into a Config
	object and return the object (looks like a
	dictionary).

	"""
	cfile = pype_hostconfigfile()
	return configvars.defaults(cfile)

	#return Config(pype_hostconfigfile())


def _CanOnlyBeOne():
	"""Count number of pype programs currently running.

	Try to figure out if there are already pype processes running
	(actually look for any processes attached to the standard shared
	memory segment (id: 0xDA01). This is ugle, slow and a hack. **BUT**
	it does the job and prevents you from killing your own pype
	process by accident when collecting data...

	If npypes() > 0, you really shouldn't start up another pype
	instance!

	"""
	p = os.popen("ipcs -m | grep da01 | awk '{print $6}'", 'r')
	nproc = p.read()
	p.close()
	if len(nproc) > 0:
		nproc = int(string.split(nproc)[0])
	else:
		nproc = 0
	if nproc > 0:
		Logger('Another pype process appears to be running.\n' +
			   'Use `pypekill` to stop it and then rerun pype.\n')
		raise FatalPypeError


def _find_ttl(t, x, thresh=500, polarity=1):
	"""
	Find downward going TTL pulses in x.  Returns list of onset times.

	Sat Mar 27 15:07:07 2004 mazer

	- pol == 1 --> time of first (negative going) above threshold sample

	- pol != 1 --> time of first (positive going) below threshold sample

	This is BACKWARDS .. but we're NOT going to change it..

	"""

	times = []
	inpulse = 0
	if polarity > 0:
		for i in range(0, len(t)):
			if (not inpulse) and (x[i] < thresh):
				times.append(t[i])
				inpulse = 1
			elif inpulse and (x[i] > thresh):
				inpulse = 0
	else:
		for i in range(0, len(t)):
			if (not inpulse) and (x[i] > thresh):
				times.append(t[i])
				inpulse = 1
			elif inpulse and (x[i] < thresh):
				inpulse = 0
	return times

class _EyeGraph:
	def __init__(self, app):
		pass

	def show(self, start=None, stop=None):
		sys.stderr.write('error: app.eyegraph.show() has been deleted.\n')
		sys.stderr.write('       use app.plotEyetracesRange() instead.\n')
		raise FatalPypeError

def _safeLookup(dict, key, default):
	"""Lookup value in dictionary

	If key doesn't exist, return a default value.

	"""
	try:
		return dict[key]
	except (TypeError, KeyError):
		return default

def subject():
	"""Get the current subject id string.

	This is usually supplied by starting pype with the -s argument.

	"""
	try:
		return os.environ['SUBJECT']
	except KeyError:
		return 'none'

def subjectrc(s=""):
	"""Get current subject's private .pyperc directory.

	Each subject has a directory inside ~/.pyperc that's used to
	store subject-specific configuration data and state parameters.

	"""
	return pyperc('_' + subject() + '/' + s)


def pyperc(s=""):
	"""
	If $(PYPERC) is set, then use $(PYPERC) as the base for the
	user's .pyperc directory. Otherwise use "~/.pyperc".

	"""
	if os.environ.has_key('PYPERC'):
		rc = os.environ['PYPERC']
		if rc[-1] != '/':
			rc = rc + '/'
	else:
		# this is more portable than os.environ['HOME']
		rc = os.path.expanduser('~') + '/.pyperc/'

	return rc+s

def pypedir(s=None):
	if s:
		return os.environ['PYPEDIR']+'/'+s
	else:
		return os.environ['PYPEDIR']+'/'

def libdir(s=None):
	if s:
		return os.environ['PYPEDIR']+'/lib/'+s
	else:
		return os.environ['PYPEDIR']+'/lib/'

class FixWin:
	def __init__(self, x=0, y=0, size=10, app=None, vbias=1.0):
		self.app = app
		self.icon = None
		self.text = None
		self.set(x, y, size)

		# Mon Jan 23 09:57:24 2006 mazer
		#  This effectively turns the fixwin from a circle into an
		#  ellipse. If vbias>1, ellipse is elongated in the
		#  vertical direction, <1 the horizontal direction. Corresponding
		#  changes have been made to dacq.c, das_common.c, dacqinfo.h
		#  to make this works
		#
		#  ** It's just a multiplicative scale for the y dimension **
		#
		self.vbias = vbias

	def __del__(self):
		"""Remove icon, if one exists and disable in dacq process.

		"""
		self.genint(0)
		self.clear()
		self.off()

	def genint(self, enable):
		if enable:
			dacq_fixwin_genint(0, 1)
		else:
			dacq_fixwin_genint(0, 0)
			# also: clear saved flag -- no more interupts
			# in theory you could loose a pending interupt here, but it
			# should be unlikely.
			self._post_fixbreak = 0

	def set(self, x=None, y=None, size=None):
		self.x = x
		self.y = y
		self.size = size

	def reset(self):
		dacq_fixwin_reset(0)

	def on(self):
		"""Turn fix window on - increases load in dacq process.

		"""
		dacq_fixwin(0, self.x, self.y, self.size, self.vbias)

	def off(self):
		"""Turn fix window off - decreases load in dacq process.

		"""
		dacq_fixwin(0, 0, 0, -1, 0.0)

	def inside(self):
		"""Check to see if eye is inside fixwin.

		"""
		if self.app and self.app.config.iget('DACQ_TESTMODE'):
			return 1
		return dacq_fixwin_state(0)

	def broke(self):
		"""Check to see if eye moved out of window, since acquired.

		"""
		if self.app and self.app.config.iget('DACQ_TESTMODE'):
			return 0
		return dacq_fixwin_broke(0)

	def break_time(self):
		"""Get the exact time fixation was broken.

		"""
		return dacq_fixwin_break_time(0)

	def draw(self, color='grey', dash=None, text=None):
		"""Draw fixation window on user display.

		"""
		self.clear()
		self.icon = self.app.udpy.icon(self.x, self.y,
									   2*self.size, 2*self.size*self.vbias,
									   color=color, type=2, dash=dash)
		if text:
			self.text = self.app.udpy.texticon(x=self.x+20, y=self.y+20,
											   text=text)

	def clear(self):
		"""Remove fixation window from user display.

		"""
		if self.icon:
			self.app.udpy.icon(self.icon)
			self.icon = None
		if self.text:
			self.app.udpy.texticon(self.text)
			self.text = None

class LandingZone:
	"""
	Circular Landing zone detector -- this is sort of like a FixWin,
	but all done in pype, without dacq_server intervention. A landing
	zone is circular region located at (x,y) with a radius of size
	pixels.  Once the eyes enter the landing zone, a counter is
	started. If the eyes are still in the landing zone after fixtime,
	then it's considered a landing event the .inside() method returns
	one.

	This depends on the .inside() method being in some sort of
	tight loop and called over and over again until something
	happens, otherwise you might miss exit/entry events..

	Eyes must stay inside the zone for fixtime_ms before it's
	considered a fixation insize the zone. Use fixtime_ms=0 if
	you want to accept pass throughs w/o fixations.

	"""

	def __init__(self, x, y, size, fixtime, app):
		self.app = app
		self.icon = None
		self.x, self.y, self.size = x, y, size
		self.size2 = size**2
		self.fixtime = fixtime
		self.entered_at = None

	def __del__(self):
		self.clear()

	def inside(self, t=None, x=None, y=None):
		"""
		If you have multiple landing zones, you can sit in a loop, use
		app.eye_txy() to query time and eye position ONCE, and then apply
		it to multiple landing zones by passing in (x,y) values

		"""
		if t is None:
			(t, x, y) = self.app.eye_txy()
		if ((self.x-x)**2 + (self.y-y)**2) < self.size2:
			if self.entered_at is None:
				self.entered_at = t
			if (t - self.entered_at) >= self.fixtime:
				return 1
			return 0
		else:
			self.entered_at = None
			return 0

	def draw(self, color='grey', dash=None, text=None):
		self.clear()
		self.icon = self.app.udpy.icon(self.x, self.y,
									   2*self.size, 2*self.size*self.vbias,
									   color=color, type=2, dash=dash)

	def clear(self):
		if self.icon:
			self.app.udpy.icon(self.icon)
			self.icon = None

class SectorLandingZone:
	"""
	Sector-style Landing zone detector -- landing zone is defined
	as an angular sector of an annular zone around a fixation
	spot (xo, yo). Annular sector runs from inner_pix to outer_pix
	and has an angular subtense of angle_deg +- subtense_deg.

	Eyes must stay inside the zone for fixtime_ms before it's
	considered a fixation insize the zone. Use fixtime_ms=0 if
	you want to accept pass throughs w/o fixations.

	See LandingZone for additional details about usage.

	"""

	def __init__(self, xo, yo,
				 inner_pix, outer_pix, angle_deg, subtense_deg,
				 fixtime_ms, app):
		self.app = app
		self.icon = None
		self.xo, self.yo = xo, yo
		self.inner = inner_pix
		self.outer = outer_pix
		self.angle = math.pi * angle_deg / 180.0
		self.subtense = math.pi * subtense_deg / 180.0
		self.fixtime = fixtime_ms
		self.entered_at = None

	def __del__(self):
		self.clear()

	def inside(self, t=None, x=None, y=None):
		"""
		If you have multiple landing zones, you can sit in a loop, use
		app.eye_txy() to query time and eye position ONCE, and then apply
		it to multiple landing zones by passing in (x,y) values

		"""
		if t is None:
			(t, x, y) = self.app.eye_txy()

		x, y = x - self.xo, y - self.yo
		r = (x**2 + y**2)**0.5
		if (r > self.inner) and (r < self.outer):
			d = abs(math.pi * math.atan2(y, x) - self.angle)
			if d > pi:
				d = (2 * math.pi) - d
			if d < self.subtense:
				# inside sector
				if self.entered_at is None:
					self.entered_at = t
				if (t - self.entered_at) >= self.fixtime:
					return 1
			return 0
		else:
			self.entered_at = None
			return 0

	def draw(self, color='grey', dash=None, text=None):
		x = self.xo + (self.inner+self.outer)/2.0 + math.cos(self.angle)
		y = self.xo + (self.inner+self.outer)/2.0 + math.sin(self.angle)
		self.clear()
		self.icon = self.app.udpy.icon(x, y,
									   self.outer-self.inter,
									   self.outer-self.inter,
									   color=color, type=1, dash=dash)

	def clear(self):
		if self.icon:
			self.app.udpy.icon(self.icon)
			self.icon = None

class Timer:
	def __init__(self):
		self.reset()

	def reset(self):
		self._start_at = dacq_ts()

	def ms(self):
		return dacq_ts() - self._start_at

	def us(self):
		Logger("pype: warning -- timer.us method obsolete, faking it\n")
		return 1000 * (dacq_ts() - self._start_at)

class Holder:
	"""Dummy class

	This is just a handle to hold task-related information. You
	can hang things off it and then pickle it or stash it for
	later use.

	"""
	pass

def debug(set=None):
	global __DEBUGFLAG

	if set is not None:
		__DEBUGFLAG = set
	else:
		# if DEBUGFLAG's not set, set it to 0...
		try:
			x = __DEBUGFLAG
		except NameError:
			__DEBUGFLAG = 0
		return __DEBUGFLAG

def loadwarn(fname):
	"""Log load-file working to console

	Prints a warning on stderr to indicate a module has been
	loaded. Typically used by tasks to announce that they've been
	loaded into a running pype instance.

	"""
	if debug():
		Logger("pype: loading '%s'\n" % fname)

def now(military=1):
	"""
	Return a simple timestring of the form HHMM or HHMM[am|pm]
	depending on whether 'military' is true or false.

	"""
	(year, month, day, h, m, s, x1, x2, x3) = time.localtime(time.time())
	if military:
		return "%02d:%02d" % (h, m)
	else:
		if h > 12:
			return "%02d:%02d AM" % (h-12, m)
		else:
			return "%02d:%02d PM" % (h-12, m)

def _get_plexon_events(plex, fc=40000):
	"""
	Drain the Plexon network-based database of timestamp events
	until we hit a StopExtChannel event (this is from the pype-plexon
	TTL sync line). All events left in the tank (post-trial) will
	be discarded.

	"""
	events = None

	hit_stop = 0
	while not hit_stop:
		tank, ndropped = plex.drain()
		if tank is None:
			Logger("pype: oh no.. lost plexon signal during run\n")
			return None

		for e in tank:
			(Type, Channel, Unit, ts, waveform) = e
			if Type == PlexHeaders.Plex.PL_ExtEventType and \
				   Channel == PlexHeaders.Plex.PL_StartExtChannel:
				if events is not None:
					Logger("pype: double trigger\n")
					return None
				events = []
				zero_ts = ts
			elif events is not None:
				if Type == PlexHeaders.Plex.PL_ExtEventType and \
					   Channel == PlexHeaders.Plex.PL_StopExtChannel:
					hit_stop = 1
					# drain rest of tank, then return
				else:
					# use fc (sample freq in hz) to convert timestmaps to ms
					events.append((int(0.5 + float(ts - zero_ts) / fc * 1000.0),
								   Channel, Unit))

	return events

def _goto_error(title):
	"""Open editor window at the last error for debugging"""
	(etype, evalue, tb) = sys.exc_info()
	stack = traceback.extract_tb(tb)
	(fname, line, fn, text) = stack[-1]
	if fn == '<module>':
		fn = 'toplevel'
	msg = 'file:%s line:%d [%s] "%s"' % (fname, line, fn, text)
	Logger('pype: %s -- %s\n' % (title, msg))
	r = ask(title, msg, ['Ignore', '-> editor'])
	if r == 1:
		# try emacs first, then fall back to gedit (should be everywhere)
		os.system("(emacs +%d %s || gedit +%d %s) &" % \
				  (line, fname, line, fname))

def _addpath(d, atend=None):
    """
    Add directory to the HEAD (or TAIL) of the python search path.
	
	**NOTE:**
	This function also lives in pyperun.py.template.
    """
    if atend:
        sys.path = sys.path + [d]
    else:
        sys.path = [d] + sys.path

if __name__ == '__main__':
	sys.stderr.write('%s should never be loaded as main.\n' % __file__)
	sys.exit(1)
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
