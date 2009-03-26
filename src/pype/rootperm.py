# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Getting and setting root access.

This stuff's for accessing the hardware from a running
pype process. Not really for general use.

**Revision History**

- Sat Jul  9 12:48:58 2005 mazer 

 - separated from pype.py
"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

import pwd
import os
from dacq import *

def _realuid():
	"""INTERNAL; DO NOT USE
	
	Figure out the real or effective user id based on the
	current (inherited) environment. This is part of the
	whole take/drop root access stuff.
	"""
	try:
		uid = pwd.getpwnam(os.environ['SUDO_USER'])[2]
	except KeyError:
		uid = pwd.getpwnam(os.environ['USER'])[2]
	return uid

def root_take():
	"""Attempt to gain root access.

	If pype is started suid-root, then this can be used to enable
	root access.

	**NOTE** -- this is a dangerous toy; _use with caution!_
	"""
	return (dacq_seteuid(0) == 0)

def root_drop():
	"""Give of root access.

	This is used to give up root access after the framebuffer
	and DACQ code has been initialized (these typically require
	root acces). Root access is given up by setting the effective
	UID back to the user's original UID.
	"""
	return (dacq_seteuid(_realuid()) == 0)
