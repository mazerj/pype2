#!/usr/bin/env python
#
# $Id: __init__.py,v 1.4 2001/12/09 15:35:02 doughellmann Exp $
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
"""HappyDoc Components

    The 'happydoclib' library can be used to create a variety of
    programs which can process source files and extract documentation.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: __init__.py,v $',
    'rcs_id'       : '$Id: __init__.py,v 1.4 2001/12/09 15:35:02 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'HappyDoc',
    'created'      : 'Sun, 21-Oct-2001 17:34:58 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.4 $',
    'date'         : '$Date: 2001/12/09 15:35:02 $',
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
import happydoclib.CommandLineApp
from happydoclib.cvsversion import cvsProductVersion
import happydoclib.happydom
import happydoclib.path
import happydoclib.optiontools
import happydoclib.parseinfo
import happydoclib.pluginloader
import happydoclib.prettyast
import happydoclib.trace

#
# Import Plugins
#
import happydoclib.happydocset
import happydoclib.docset

import happydoclib.happydocstring
import happydoclib.docstring

import happydoclib.happyformatter
import happydoclib.formatter


#
# Module
#
import happydoclib.appclass
HappyDoc = happydoclib.appclass.HappyDoc

TRACE=happydoclib.trace.trace


