#!/usr/bin/env python
#
# $Id: debug_happydoc.py,v 1.1 2001/10/24 21:27:36 doughellmann Exp $
#
# Time-stamp: <01/10/01 16:55:56 dhellmann>
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

"""Run HappyDoc in the debugger.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: debug_happydoc.py,v $',
    'rcs_id'       : '$Id: debug_happydoc.py,v 1.1 2001/10/24 21:27:36 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <DougHellmann@bigfoot.com>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Thu, 08-Mar-2001 17:00:43 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.1 $',
    'date'         : '$Date: 2001/10/24 21:27:36 $',
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


#
# Module
#

import pdb
import test_happydoc

#pdb.run('test_happydoc.debug()')
debugger = pdb.Pdb()
debugger.do_break('test_happydoc.py:712')
#debugger.do_break('test_happydoc.TestCaseDriver.main')
debugger.run('test_happydoc.debug()')

