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

import __builtin__
import imp, sys
from guitools import Logger


def __new_import__(*args):
    if not __data__.has_key(args[0]):
        fp, pathname, description = imp.find_module(args[0])
        if fp is not None:
            fp.close()
            # only report non-python imports
            if not pathname.startswith('/usr/lib/python'):
                Logger("{import '%s' <- '%s'}\n" % \
                       (args[0], pathname))
        __data__[args[0]] = 1
    return apply(__original_import__, args)


__data__ = {}
__original_import__ = __builtin__.__import__

def importer(on=1):
    if __builtin__.__import__ == __new_import__:
        was = 1
    else:
        was = 0
        
    if on:
        __builtin__.__import__ = __new_import__
    else:
        __builtin__.__import__ = __original_import__

    return was
