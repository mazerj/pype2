#!/usr/bin/env python
#
# $Id: cvsversion.py,v 1.1 2001/10/24 21:27:35 doughellmann Exp $
#
# Time-stamp: <01/10/21 17:48:48 dhellmann>
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

"""Get the CVS version information based on the $Name: r2_1 $ token.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: cvsversion.py,v $',
    'rcs_id'       : '$Id: cvsversion.py,v 1.1 2001/10/24 21:27:35 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <DougHellmann@bigfoot.com>',
    'project'      : 'HappyDoc',
    'created'      : 'Sat, 03-Feb-2001 12:48:26 EST',

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
import string

#
# Import Local modules
#


#
# Module
#

def cvsProductVersion(cvsVersionString='$Name: r2_1 $'):
    cvs_version_parts=string.split(cvsVersionString)
    if len(cvs_version_parts) >= 3:
        app_version = string.strip(cvs_version_parts[1]).replace('_', '.')
        if app_version and app_version[0] == 'r':
            app_version = app_version[1:]
    else:
        app_version = 'WORKING'
    return app_version

if __name__ == '__main__':
    print cvs_product_version()
    
