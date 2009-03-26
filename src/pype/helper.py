# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""
**Helper functions for pype tasks**

If you import helper.py in your task or program then you can
access most of the methods hanging of the standard 'app'
param without having to type 'app.METHOD'. Use with caution.
This is really intended ONLY for people not familiar with
objected oriented programming..

This is for task files only - it should not be used in plain
pypenv programs - there won't be any PypeApp instance to find.

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

import sys
from pype import *

if PypeApp.handle is None:
    sys.stderr.write('error: helper.py imported before pype was initialized!\n')
else:
    set_state               = PypeApp.handle.set_state
    isrunning               = PypeApp.handle.isrunning
    ispaused                = PypeApp.handle.ispaused
    getcommon               = PypeApp.handle.getcommon
    eyeset                  = PypeApp.handle.eyeset
    eyepos                  = PypeApp.handle.eyepos
    looking_at              = PypeApp.handle.looking_at
    idlefn                  = PypeApp.handle.idlefn
    history                 = PypeApp.handle.history
    warn_run_start          = PypeApp.handle.warn_run_start
    warn_run_stop           = PypeApp.handle.warn_run_stop
    warn_trial_start        = PypeApp.handle.warn_trial_start
    warn_trial_correct      = PypeApp.handle.warn_trial_correct
    warn_trial_incorrect    = PypeApp.handle.warn_trial_incorrect
    nreps                   = PypeApp.handle.nreps
    reward                  = PypeApp.handle.reward
    bar_genint              = PypeApp.handle.bar_genint
    int_handler             = PypeApp.handle.int_handler
    bardown                 = PypeApp.handle.bardown
    barup                   = PypeApp.handle.barup
    joybut                  = PypeApp.handle.joybut
    record_start            = PypeApp.handle.record_start
    record_stop             = PypeApp.handle.record_stop
    eyetrace                = PypeApp.handle.eyetrace
    encode                  = PypeApp.handle.encode
    record_write            = PypeApp.handle.record_write
    record_note             = PypeApp.handle.record_note
    record_done             = PypeApp.handle.record_done
    record_selectfile       = PypeApp.handle.record_selectfile
    idlefb                  = PypeApp.handle.idlefb
    framebuffer             = PypeApp.handle.fb
    userdisplay             = PypeApp.handle.udpy


    

