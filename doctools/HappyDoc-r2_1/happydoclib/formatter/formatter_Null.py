#!/usr/bin/env python
#
# $Id: formatter_Null.py,v 1.1 2001/10/24 21:27:35 doughellmann Exp $
#
# Time-stamp: <01/10/23 10:24:00 dhellmann>
#
# Copyright 2001 Doug Hellmann.
#
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of Doug
# Hellmann not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# DOUG HELLMANN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT SHALL DOUG HELLMANN BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

"""Null output formatter used for profiling and testing.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: formatter_Null.py,v $',
    'rcs_id'       : '$Id: formatter_Null.py,v 1.1 2001/10/24 21:27:35 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <DougHellmann@bigfoot.com>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Sat, 17-Feb-2001 12:15:35 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.1 $',
    'date'         : '$Date: 2001/10/24 21:27:35 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#


#
# Import Local modules
#
import happydoclib.formatter.formatter_HTMLFile

#
# Module
#


def entryPoint():
    "Return information about this module to the dynamic loader."
    return {
        'name':'Null',
        'factory':NullFormatter,
        }

class NullFile:
    """Null output file used for profiling and testing.

    *No writes are actually performed with this output file type.
    
    """

    def __init__(self, name):
        self.name = name
        return

    def write(self, *ignored, **ignoredToo):
        return

    def close(self, *ignored, **ignoredToo):
        return
    

class NullFormatter(happydoclib.formatter.formatter_HTMLFile.HTMLTableFormatter):
    """Null output formatter used for profiling and testing.

    This formatter is not useful for much other than testing and
    performance monitoring.
    
    """

    def openOutput(self, name, title1, title2=None):
        self.open_root_file = NullFile(name)
        return self.open_root_file

