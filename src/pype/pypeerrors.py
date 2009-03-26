# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**Exception classes for errors**

These are are the standard errors that pype and the pype libraries
functions might throw during task execution.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

class FatalPypeError(Exception): pass
class MonkError(Exception): pass
class MonkNoStart(Exception): pass
class TimeoutError(Exception): 	pass
class NoProblem(Exception): pass
class UserAbort(Exception): pass
class UserExit(Exception): pass
class TaskAbort(Exception): pass
class GuiOnlyFunction(Exception): pass

class BarTransition(Exception): pass
class FixBreak(Exception): pass
class Alarm(Exception): pass
