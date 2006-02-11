#!/usr/bin/env python
#
# $Id: __init__.py,v 1.4 2001/12/09 15:35:26 doughellmann Exp $
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

"""Python docstring converter plugins.

    *How does an author write documentation so that it will be marked
    up and look fancy?* This is a perennial question for
    "Python":http://www.python.org users, and seems to have introduced
    a roadblock into the development of more robust and useful
    documentation tools.  HappyDoc stands firmly on the fence and does
    not attempt to resolve the issue.

    By separating the docstring converter and formatter classes from
    the docset classes, HappyDoc allows a user to create their own
    converter and formatter to interpret comments in any way they see
    fit.

    The docstring converter plugins are responsible for translating
    text from the input markup syntax to the output format.  This
    translation is formatter independent, so that the same HTML
    conversion might be used by mutliple HTML formatters.  It is,
    however, *format* dependent, so that HTML output should not be
    used by a plain text formatter.

    The default for the 'HTMLTableFormatter' (the default formatter
    for HappyDoc) is to treat '__doc__' strings as
    "StructuredTextNG":http://www.zope.org//Members/jim/StructuredTextWiki/StructuredTextNGRules.
    This is the "Next Generation" version of the original
    "StructuredText":http://www.python.org/sigs/doc-sig/stext.html
    markup syntax.  See also the 'StructuredText' package for a
    description of the rules for using StructuredText.

    *Don't like StructuredText?* Write your own docstring converter
    that uses something different and drop it into place.  Refer to
    the 'happydocstring.py' module for the base class and APIs
    required of a docstring converter.  If a defacto (or otherwise)
    standard structured markup for Python '__doc__' strings emerges,
    HappyDoc will be updated to use that format by default.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: __init__.py,v $',
    'rcs_id'       : '$Id: __init__.py,v 1.4 2001/12/09 15:35:26 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <DougHellmann@bigfoot.com>',
    'project'      : 'HappyDoc',
    'created'      : 'Wed, 26-Sep-2001 09:31:19 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.4 $',
    'date'         : '$Date: 2001/12/09 15:35:26 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import sys
import re
import traceback

#
# Import Local modules
#
import happydoclib

#
# Module
#

_plugin_loader=None
def DocStringLoader():
    global _plugin_loader
    if not _plugin_loader:
        _plugin_loader = DocStringLoaderSingleton()
    return _plugin_loader

class DocStringLoaderSingleton(happydoclib.pluginloader.PluginLoader):
    "Load pluggable docstring converters."

    def __init__(self):
        self._filename_patterns = []
        happydoclib.pluginloader.PluginLoader.__init__(self, __name__, __path__[0],
                                                       'happydoclib')
        return

    def addEntryPoint(self, infoDict):
        "Add the information about a converter to our lookup table."
        #
        # Local variables make this method easier to understand
        #
        name = infoDict['name']
        factory = infoDict['factory']
        pattern_list = infoDict['filenamePatternList']
        #
        # Record the filename pattern information
        #
        for pattern in pattern_list:
            try:
                regex = re.compile(pattern)
            except:
                sys.stderr.write('\n--- Plugin Module Error ---\n')
                traceback.print_exc()
                sys.stderr.write('---------------------------\n\n')
                continue
            else:
                self._filename_patterns.append((regex, name))
        #
        # Record the factory for this name
        #
        self[name] = factory
        return

    def getConverterNameForFile(self, filename, default='PlainText'):
        "Return the name of the docstring converter for the file specified."
        #
        # Error cases
        #
        if not filename:
            return default
        #
        # Check patterns
        #
        for regex, plugin_name in self._filename_patterns:
            if regex.search(filename):
                return plugin_name
        #
        # Check file contents?
        #
        #
        # Return the default
        #
        return default

        
def getConverterFactory(formatType):
    """Returns the factory for a docstring converter for 'formatType' text.

    Parameters:

      'formatType' -- A string representing the name of the input text
      type.  If this string does not match a registered docstring
      converter input format, a ValueError exception will be raised.

    """
    plugins = DocStringLoader()
    if formatType not in plugins.keys():
        print 'Wanted: "%s"' % formatType
        print 'Have  : %s' % str(plugins.keys())
        raise ValueError('Unrecognized docstring format type "%s"' % formatType)
    else:
        return plugins[formatType]
    

def getConverterFactoryForFile(filename):
    """Returns the  factory for a docstring converter for an external file.

    Parameters:

      'filename' -- The name of the external file to be examined.
    
    """
    plugins = DocStringLoader()
    converter_name = plugins.getConverterNameForFile(filename)
    #print 'GOT CONVERTER NAME "%s" for %s' % (converter_name, filename)
    return getConverterFactory(converter_name)
