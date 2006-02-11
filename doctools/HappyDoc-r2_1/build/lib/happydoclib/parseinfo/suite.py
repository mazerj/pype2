#!/usr/bin/env python
#
# $Id: suite.py,v 1.2 2002/08/24 19:55:40 doughellmann Exp $
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

"""Base class for information gathering classes.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: suite.py,v $',
    'rcs_id'       : '$Id: suite.py,v 1.2 2002/08/24 19:55:40 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Sun, 11-Nov-2001 10:45:58 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.2 $',
    'date'         : '$Date: 2002/08/24 19:55:40 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import re

#
# Import Local modules
#
import happydoclib
from happydoclib.happydom import HappyDOM

from happydoclib.parseinfo.utils import *

#
# Module
#

class SuiteInfoBase(HappyDOM):
    """Base class for information gathering classes.

    Default implementation assumes that the user is interested
    in learning about functions and classes defined within the
    parse tree used for initialization.  This makes implementation
    of MethodInfo easy.  Other derived classes add behavior to
    find other information.
    """
    
    #_docstring = ''
    _docstring_summary = None

    def __init__(self, name, parent, filename, tree,
                 commentInfo={},
                 defaultConfigValues={},
                 ):
        """Initialize the info extractor.

        Parameters:

            name -- name of this object
        
            parent -- parent object (e.g. Module for Class)

            filename -- file which contains the tree
            
            tree -- parse tree from which to extract information

            commentInfo -- comments extracted from source file where
            this object was found
            
        """
        self._class_info = {}
        self._function_info = {}
        namespaces = ( self._class_info, self._function_info )
        HappyDOM.__init__(self, name, parent, filename, namespaces)
        
        self._comment_info = commentInfo
        self._configuration_values = {}
        self._configuration_values.update(defaultConfigValues)
        self._extractConfigurationValues()

        comment_key = self.getCommentKey()
        #print 'PARSEINFO: Looking for comments for %s in %s' % (name, comment_key)
        self._comments = commentInfo.get(comment_key, '')
        if tree:
            self._extractInfo(tree)
        return

    def getCommentKey(self):
        if self._parent:
            return self._parent.getCommentKey() + (self._name,)
        else:
            return (self._name,)

    ##
    ## Internal Data Extraction
    ##

    def getConfigurationValues(self):
        "Return any HappyDoc configuration values related to this object."
        values = None
        if self._parent:
            try:
                values = self._parent.getConfigurationValues()
            except:
                values = None
        if values is None:
            values = self._configuration_values
        return values

    def _extractInfo(self, tree):
        "Pull information out of the parse tree."
        from happydoclib.parseinfo.classinfo import ClassInfo
        from happydoclib.parseinfo.functioninfo import FunctionInfo
        
        # extract docstring
        if len(tree) == 2:
            found, vars = match(DOCSTRING_STMT_PATTERN[1], tree[1])
        else:
            found, vars = match(DOCSTRING_STMT_PATTERN, tree[3])
        if found:
            self._docstring = eval(vars['docstring'])
        else:
            self._docstring = ''
        # discover inner definitions
        for node in tree[1:]:
            found, vars = match(COMPOUND_STMT_PATTERN, node)
            if found:
                cstmt = vars['compound']
                if cstmt[0] == symbol.funcdef:
                    name = cstmt[2][1]
                    self._function_info[name] = FunctionInfo(
                        tree=cstmt,
                        parent=self,
                        commentInfo=self._comment_info,
                        )
                    #pprint.pprint(cstmt)
                elif cstmt[0] == symbol.classdef:
                    name = cstmt[2][1]
                    self._class_info[name] = ClassInfo(
                        tree=cstmt,
                        parent=self,
                        commentInfo=self._comment_info
                        )
        return
    
    def _extractConfigurationValues(self):
        "Default implementation does nothing."
        return

    _summary_pattern = re.compile(r'^\s*([^\n]+)\n')
    def _extractSummary(self, text):
        "Extract a summary text from a larger body."
        text = text.strip()
        #
        # Remove surrounding quotes, if present.
        #
        while text and (text[0] in ('"', "'")):
            text = text[1:]
        while text and (text[-1] in ('"', "'")):
            text = text[:-1]
        #
        # Pull out the first line, and return it if
        # we can find it.  Otherwise, return the whole
        # string since that means that the whole thing
        # is just one line.
        #
        matchObj = self._summary_pattern.search(text)
        if matchObj:
            return matchObj.group(0).strip()
        else:
            return text

    ##
    ## DocStrings
    ##
    
    def getDocString(self):
        "Return any __doc__ string value found for the object."
        dstring = '%s\n\n%s' % (self._docstring, self._comments)
        #print 'DOC STRING for %s is ' % self._name, dstring
        return dstring

    def getDocStringFormat(self):
        "Returns the docstring converter format name for the docstring for this object."
        config_values = self.getConfigurationValues()
        return config_values['docStringFormat']
 
    def getSummaryAndFormat(self):
        "Return a summary of the __doc__ string for this object and the docstring converter name for the format of the text."
        if self._docstring_summary is None:
            self._docstring_summary = \
                                    self._extractSummary(self.getDocString())
        return self._docstring_summary, self.getDocStringFormat()
