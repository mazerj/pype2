# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**Override standard import function for debugging**

Importing this module wil override the standard definition of __import__
to print debugging information each time a module gets imported.

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

import __builtin__, imp, sys
from guitools import Logger

_native_imp =  __builtin__.__import__

def _verbose_import(*args):
    fp, pathname, description = imp.find_module(args[0])
    if fp is not None:
        fp.close()
        # only report non-python imports
        if not pathname.startswith('/usr/lib/python'):
            Logger("importing '%s' from '%s'\n" % (args[0], pathname))
    return apply(_native_imp, args)

def importer(report=1):
    if report:
        __builtin__.__import__ = _verbose_import
    else:
        __builtin__.__import__ = _native_imp


