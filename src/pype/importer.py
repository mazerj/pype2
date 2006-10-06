#!/usr/bin/python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""
Override standard import function for debugging.

Importing this module wil override the standard definition of __import__
to print debugging information each time a module gets imported.
"""

import __builtin__
import imp, sys


def __new_import__(*args):
    if not __data__.has_key(args[0]):
        fp, pathname, description = imp.find_module(args[0])
        if fp is not None:
            fp.close()
            # only report non-python imports
            if not pathname.startswith('/usr/lib/python'):
                sys.stderr.write("{'%s' from '%s'}\n" % (args[0], pathname))
        __data__[args[0]] = 1
    return apply(__original_import__, args)


__data__ = {}
__original_import__ = __builtin__.__import__
__builtin__.__import__ = __new_import__
