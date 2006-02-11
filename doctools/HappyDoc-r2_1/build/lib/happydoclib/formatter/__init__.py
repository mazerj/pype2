#!/usr/bin/env python
#
# COPYRIGHT
#
#   Permission to use, copy, modify, and distribute this software and
#   its documentation for any purpose and without fee is hereby
#   granted, provided that the above copyright notice appear in all
#   copies and that both that copyright notice and this permission
#   notice appear in supporting documentation, and that the name of Doug
#   Hellmann not be used in advertising or publicity pertaining to
#   distribution of the software without specific, written prior
#   permission.
# 
# DISCLAIMER
#
#   DOUG HELLMANN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
#   INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
#   NO EVENT SHALL DOUG HELLMANN BE LIABLE FOR ANY SPECIAL, INDIRECT OR
#   CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
#   OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
#   NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
#   CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# 


"""Output Formatters

    Formatters are responsible for tranlating the higher level docset
    concepts into specific structures for an output type.  For
    example, the specific way a descriptive list might be rendered in
    HTML could vary between different HTML formatters.  The API for a
    formatter depends on the docset types which is is meant to
    support.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name':'$RCSfile: __init__.py,v $',
    'creator':'Doug Hellmann <doughellmann@home.com>',
    'project':'HappyDoc',
    'created':'Sat, 03-Jun-2000 19:06:39 EDT',
    #
    #  Current Information
    #
    'author':'$Author: doughellmann $',
    'version':'$Revision: 1.4 $',
    'date':'$Date: 2001/12/09 15:35:26 $',
    }
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import os
import sys
import glob


#
# Import Local modules
#
import happydoclib

#
# Module
#

class FormatterLoader(happydoclib.pluginloader.PluginLoader):
    "Load pluggable formatter types."

    def __init__(self):
        happydoclib.pluginloader.PluginLoader.__init__(self, __name__, __path__[0],
                                                       'happydoclib')
        return

    def addEntryPoint(self, infoDict):
        "Add the information about a docset to our lookup table."
        name = infoDict['name']
        factory = infoDict['factory']
        self[name] = factory
        return


