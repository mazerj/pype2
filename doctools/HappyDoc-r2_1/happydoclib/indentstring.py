#!/usr/bin/env python
#
# $Id: indentstring.py,v 1.2 2001/11/25 13:05:37 doughellmann Exp $
#
# Copyright 2000 Doug Hellmann
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

"""Function to indent the lines of a string using a standard indent spacing.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: indentstring.py,v $',
    'rcs_id'       : '$Id: indentstring.py,v 1.2 2001/11/25 13:05:37 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'HappyDoc',
    'created'      : 'Sun, 27-Aug-2000 07:49:28 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.2 $',
    'date'         : '$Date: 2001/11/25 13:05:37 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import pprint
import string
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import unittest

#
# Import Local modules
#
from StreamFlushTest import StreamFlushTest

#
# Module
#

def indentString(str, tabWidth=1, tabChar=' '):
    output = StringIO()
    lines = string.split(str, '\n')
    indent_lines = map(lambda x, pre=(tabWidth * tabChar): '%s%s\n' % (pre, x),
                       lines)
    output.writelines(indent_lines)
    return output.getvalue()



class IndentStringTest(StreamFlushTest):

    def testIndentString(self):
        stream = StringIO()
        printer = pprint.PrettyPrinter(indent=2, width=10, stream=stream)

        test_tuple = ( ( ( 1, 'two', (3, 'four') ), ( 1, 'two', (3, 'four') ) ),
                       ( ( 1, 'two', (3, 'four') ), ( 1, 'two', (3, 'four') ) ),
                       ( ( 1, 'two', (3, 'four') ), ( 1, 'two', (3, 'four') ) ),
                       ( ( 1, 'two', (3, 'four') ), ( 1, 'two', (3, 'four') ) ),
                       ( ( 1, 'two', (3, 'four') ), ( 1, 'two', (3, 'four') ) ),
                      )
        printer.pprint(test_tuple)
        indented = indentString(stream.getvalue(), tabWidth=2, tabChar='.')

        expected_value = """..( ( ( 1,
..      'two',
..      ( 3,
..        'four')),
..    ( 1,
..      'two',
..      ( 3,
..        'four'))),
..  ( ( 1,
..      'two',
..      ( 3,
..        'four')),
..    ( 1,
..      'two',
..      ( 3,
..        'four'))),
..  ( ( 1,
..      'two',
..      ( 3,
..        'four')),
..    ( 1,
..      'two',
..      ( 3,
..        'four'))),
..  ( ( 1,
..      'two',
..      ( 3,
..        'four')),
..    ( 1,
..      'two',
..      ( 3,
..        'four'))),
..  ( ( 1,
..      'two',
..      ( 3,
..        'four')),
..    ( 1,
..      'two',
..      ( 3,
..        'four'))))
..
"""
        assert indented == expected_value, \
               'Did not get expected indention "%s"' % indented
        return
    

if __name__ == '__main__':
    unittest.main()
    
