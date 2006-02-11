#!/usr/bin/env python
#
# $Id: parsecomments.py,v 1.2 2001/11/25 13:35:51 doughellmann Exp $
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

"""Parse comment information from a module.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: parsecomments.py,v $',
    'rcs_id'       : '$Id: parsecomments.py,v 1.2 2001/11/25 13:35:51 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Sat, 27-Oct-2001 17:49:02 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.2 $',
    'date'         : '$Date: 2001/11/25 13:35:51 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import re
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO


#
# Import Local modules
#
from StreamFlushTest import StreamFlushTest

#
# Module
#

class ParseStack:
    "Helper class for 'extractComments' function in this module."

    def __init__(self):
        "Create a ParseStack."
        self.data = []
        return

    def push(self, name, indent):
        """Push a new 'name' onto the stack.

        Smartly determine, based on 'indent', whether to 'pop' other
        'names' before pushing this one.
        """
        while self.data and (indent <= self.data[-1][1]):
            self.pop()
        self.data.append( (name, indent) )
        return

    def pop(self):
        "Remove the top of the stack and return it."
        item, indent = self.data[-1]
        self.data = self.data[:-1]
        return item

    def __names(self):
        "Return a list of the names as they appear on the stack, bottom first."
        return map(lambda x: x[0], self.data)

    def __str__(self):
        "Create a string representation."
        return string.join(self.__names(), ':')

    def key(self):
        "Return a value to be used as a dictionary key."
        return tuple(self.__names())
    

def extractComments(
    text,
    extractRe=re.compile('^((?P<blankline>\s*$)|(?P<namedobj>(?P<indent>\s*)(?P<nametype>(class|def))\s+(?P<name>[0-9A-Za-z_]+))|(?P<commentline>\s*#+(?P<comment>.*)))').search,
    ignoreRe=re.compile('\s*[+-=#][ +-=#]*\s*$').match,
    ):
    """Given a block of Python source, extract the comments.

    The comment text is associated with nearby named objects
    (functions, methods, classes, etc.).  This function returns
    a dictionary of names and the associated comment text.

    Arguments

      text -- The Python source to be scanned.

    """
    dbg=None

    comment_info = {}

    comment_text = ''
    parse_stack = ParseStack()
    current_name = None

    f = StringIO(text)
    line = f.readline()
    while line:
        #if dbg and (dbg >= 2): print '=>%s' % string.rstrip(line)
        match_obj = extractRe(line)
        if match_obj:
            #
            # Documentation before named object
            #
            match_dict = match_obj.groupdict()
            comment = match_dict['comment']
            name = match_dict['name']
            nametype = match_dict['nametype']
            blankline = match_dict['blankline']
            indent = ((match_dict['indent'] and len(match_dict['indent'])) or 0)

            if match_dict['commentline'] and not comment:
                comment = ' '

            if comment:
                # Append new text to running buffer.
                if ignoreRe and not ignoreRe(comment):
                    #if dbg: print 'PARSEINFO: Adding comment text.'
                    comment_text = '%s%s\n' % (comment_text, comment,)

            elif name and comment_text:
                    
                if current_name:
                    # Hit a new name, store the comment_text buffer
                    # for the current_name
                    #if dbg:
                    #    print 'PARSEINFO: 1 Storing comment for %s' % parse_stack
                    #    print 'PARSEINFO: ', comment_text
                    comment_info[parse_stack.key()] = comment_text
                    # Update the parse stack
                    parse_stack.push(name, indent)
                    #if dbg:
                    #    print 'PARSEINFO: switching to %s' % parse_stack 
                    comment_text = ''
                else:
                    # Hit a new name with existing comment_text,
                    # store the comment along with that name.
                    parse_stack.push(name, indent)
                    #if dbg:
                    #    print 'PARSEINFO: 2 Storing comment for %s' % parse_stack
                    #    print 'PARSEINFO: ', comment_text
                    comment_info[parse_stack.key()] = comment_text
                    comment_text = ''
                    current_name = None

            elif name:
                # Recognized new name definition.
                #if dbg:
                #    print 'PARSEINFO: New name %d:%s:%s' % (indent,
                #                                            nametype,
                #                                            name,
                #                                            )
                current_name = name
                parse_stack.push(name, indent)

            elif blankline:
                # Reset when a blank line separates comment from
                # named stuff.
                #if dbg:
                #    print 'PARSEINFO: blank line'
                if comment_text and current_name:
                    if not comment_info.get(parse_stack, None):
                        #if dbg:
                        #    print 'PARSEINFO: Storing comment after name %s:%s' \
                        #          % parse_stack
                        comment_info[parse_stack.key()] = comment_text
                #else:
                #    if dbg:
                #        if comment_text:
                #            print 'PARSEINFO: Discarding comment "%s"' % comment_text
                current_name = None
                comment_text = ''

            elif current_name and comment_text:
                # Store all comment text for the current_name.
                #if dbg:
                #    print 'PARSEINFO: 3 Storing comment for %s' % current_name
                #    print 'PARSEINFO: ', comment_text
                comment_info[parse_stack.key()] = comment_text
                comment_text = ''
                current_name = None

        else:
            #if dbg:
            #    print 'PARSEINFO: Not matched (%s)' % string.strip(line)
            current_name = None
            comment_text = ''

        line = f.readline()

    f.close()

    if current_name and comment_text:
        # Final storage to make sure we have everything.
        #if dbg:
        #    print 'PARSEINFO: Final storage of comment for %s' % current_name
        comment_info[parse_stack.key()] = comment_text

    #if dbg:
    #    pprint.pprint(comment_info)
    return comment_info


class ParseCommentsTest(StreamFlushTest):

    def testComments(self):
        body = open('TestCases/test_ignore_comments.py', 'rt').read()
        actual = extractComments(body)
        expected = {
            ('WithComments',): ' \n This class is documented only with comments.\n \n Any documentation which appears for this class with the\n comment flag set to ignore comments indicates a bug.\n \n',
            ('WithComments', '__init__'): ' \n WithComments init method.\n \n   You should not see this!\n \n',
            }
        assert actual == expected, \
               'Did not get expected comment values.  Got %s' % str(actual)
        
    
    def testDecoratedComments(self):
        body = open('TestCases/test_decorated_comments.py', 'rt').read()
        actual = extractComments(body)
        expected = {
            ('Dashes',): ' \n Func with dash lines\n \n',
            ('Equals',): ' \n Func with equal lines\n \n',
            ('Hashes',): ' \n \n Func with hash lines\n \n \n',
            ('StructuredTextTable',): " \n This function has, in the comments about it, a table.  That table\n should be rendered via STNG to an HTML table in the test output.\n \n  |-------------------------------------------------|\n  | Function  | Documentation                       |\n  |=================================================|\n  | '__str__' | This method converts the            |\n  |           |  the object to a string.            |\n  |           |                                     |\n  |           | - Blah                              |\n  |           |                                     |\n  |           | - Blaf                              |\n  |           |                                     |\n  |           |       |--------------------------|  |\n  |           |       |  Name   | Favorite       |  |\n  |           |       |         | Color          |  |\n  |           |       |==========================|  |\n  |           |       | Jim     |  Red           |  |\n  |           |       |--------------------------|  |\n  |           |       | John    |  Blue          |  |\n  |           |       |--------------------------|  |\n  |-------------------------------------------------|\n \n", ('Mixed',): ' \n Func with mixed dashes and equals\n \n',
            }
        assert actual == expected, \
               'Did not get expected comment values.  Got %s' % str(actual)
        
