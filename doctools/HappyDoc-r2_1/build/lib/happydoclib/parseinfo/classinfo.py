#!/usr/bin/env python
#
# $Id: classinfo.py,v 1.2 2002/08/04 12:06:49 doughellmann Exp $
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

"""Gather information about a Python class from its parse tree.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: classinfo.py,v $',
    'rcs_id'       : '$Id: classinfo.py,v 1.2 2002/08/04 12:06:49 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Sun, 11-Nov-2001 10:54:26 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.2 $',
    'date'         : '$Date: 2002/08/04 12:06:49 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import symbol
import token

#
# Import Local modules
#
import happydoclib
from happydoclib.parseinfo.suite import SuiteInfoBase
from happydoclib.parseinfo.utils import *

#
# Module
#

    
class ClassInfo(SuiteInfoBase):
    "Gather information about a Python class from its parse tree."
    
    def __init__(self, parent = None, tree = None, commentInfo = {}):
        """Initialize the info extractor.

        Parameters:

            parent -- parent object for this class (e.g. Module)

            tree -- parse tree from which to extract information

            commentInfo -- comments extracted from the source file
            for this class

        """
        happydoclib.TRACE.into('ClassInfo', '__init__',
                               parent=parent,
                               tree=tree,
                               commentInfo=commentInfo,
                               )
        SuiteInfoBase.__init__(self, tree[2][1], parent, parent.getFilename(),
                               tree=(tree and tree[-1] or None),
                               commentInfo=commentInfo)
        self._base_class_info = self._extractBaseClasses(tree)
        #print self._base_class_info
        self._class_member_info = self._extractClassMembers(tree)
        #print self._class_member_info
        happydoclib.TRACE.outof()
        return

    def _extractBaseClasses(self, tree):
        "Returns a list of all base classes from which this class is derived."
        #print
        #pprint.pprint(tree)
        base_class_names = []
        for subtree in tree[1:]:
            #pprint.pprint(subtree)
            if subtree[0] == symbol.testlist:
                for test in subtree[1:]:
                    found, vars = lenientMatch(BASE_CLASS_NAME_PATTERN, test)
                    #pprint.pprint(vars)
                    if found and vars.has_key('power'):
                        #base_class_names.append(vars['name'])
                        name = parseTreeToString(vars['power'])
                        base_class_names.append(name)
        return base_class_names

    def _extractClassMembers(self, tree):
        """Returns a list of all variable assignments
        in the class member context."""
        CLASS_MEMBER_STMT_PATTERN = (
            symbol.stmt,
            (symbol.simple_stmt,
             (symbol.small_stmt,
              (symbol.expr_stmt,
               (symbol.testlist,
                (symbol.test,
                 (symbol.and_test,
                  (symbol.not_test,
                   (symbol.comparison,
                    (symbol.expr,
                     (symbol.xor_expr,
                      (symbol.and_expr,
                       (symbol.shift_expr,
                        (symbol.arith_expr,
                         (symbol.term,
                          (symbol.factor,
                           (symbol.power,
                            (symbol.atom,
                             (token.NAME, ['member_name']),
                             ))))))))))))))))))
        #
        # Find the suite defining the class
        #
        for subtree in tree[1:]:
            if subtree[0] == symbol.suite:
                search_in = subtree
                break

        class_members = []
        
        for subtree in search_in[1:]:
            found, vars = lenientMatch(CLASS_MEMBER_STMT_PATTERN,
                                       subtree,
                                       dbg=0)
            if found and vars:
                class_members.append(vars['member_name'])

        return class_members

    def getMethodNames(self):
        "Returns a list of the names of methods defined for this class."
        return self._function_info.keys()

    def getMethodInfo(self, name):
        "Returns a FunctionInfo object for the method 'name', if it exists."
        return self._function_info[name]

    def getBaseClassNames(self):
        "Returns a list of the names of the base classes for this class."
        return self._base_class_info

    def getExceptionNames(self):
        "Returns a list of the names of all exceptions raised by this class."
        exception_names = []
        return exception_names

#     def getReference(self, formatter, sourceNode):
#         "Return a reference to this module from sourceNode."
#         ref = formatter.getReference(self, sourceNode.name)
#         return ref
