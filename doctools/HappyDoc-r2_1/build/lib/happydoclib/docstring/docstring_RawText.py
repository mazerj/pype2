#!/usr/bin/env python
#
# $Id: docstring_RawText.py,v 1.2 2001/10/27 19:59:46 doughellmann Exp $
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

"""Raw (pass-through) docstring converter.

    This converter does not modify its inputs in any way.

    This is most useful for internal calls in a formatter.  For
    instance, if a formatter calls self.writeText() and passes text
    that it has produced, it can use "RawText" as the 'textFormat'
    argument.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: docstring_RawText.py,v $',
    'rcs_id'       : '$Id: docstring_RawText.py,v 1.2 2001/10/27 19:59:46 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <DougHellmann@bigfoot.com>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Wed, 26-Sep-2001 09:52:01 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.2 $',
    'date'         : '$Date: 2001/10/27 19:59:46 $',
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
import happydoclib

#
# Module
#

def entryPoint():
    "Return information about this module to the dynamic loader."
    return {
        'name':'RawText',
        'factory':RawTextConverter,
        'filenamePatternList':[],
        }

class RawTextConverter(happydoclib.happydocstring.HappyDocStringConverterBase):
    """Raw (pass-through) docstring converter.

    This is most useful for internal calls in a formatter.  For
    instance, if a formatter calls self.writeText() and passes text
    that it has produced, it can use "RawText" as the 'textFormat'
    argument.

    This converter is not recommended for most uses.
    
    """
    
    def convert(self, inputText, outputFormat, *args, **namedArgs):
        """Returns the 'inputText' data translated into the 'outputFormat'.

        Parameters:

          'inputText' -- String or other sequence of characters to be
          converted.  This string should be in the format advertised
          by the docstring converter.

          'outputFormat' -- String defined by the docstring converter
          class to represent a supported output scheme.  This value is
          converter-specific, and not all converters will support the
          same output formats.
        
        """
        return inputText

    def quote(self, inputText, outputFormat, *args, **namedArgs):
        """Returns the 'inputText' quoted in a way that special characters are escaped.

        Parameters:

          'inputText' -- String or other sequence of characters to be
          converted.  This string should be in the format advertised
          by the docstring converter.

          'outputFormat' -- String defined by the docstring converter
          class to represent a supported output scheme.  This value is
          converter-specific, and not all converters will support the
          same output formats.

          '*args' -- Additional, converter-specific, positional arguments.

          '**namedArgs' -- Additional, converter-specific, named arguments.
          
        """
        return inputText

class RawTextUnitTest(happydoclib.happydocstring.DocStringConverterTest):

    def testConvertRaw(self):
        conversion_text = '''This is some text.

        It includes several paragraphs.
        '''
        self._testConversion( conversion_text, 'RawText', 'html',
                              conversion_text,
                              'RawText conversion failed.')
        return

    def testQuoteRaw(self):
        quote_text = '<html><head><title>Title</title></head><body>Hi&nbsp;there</body></html>'
        self._testQuote( quote_text, 'RawText', 'html',
                         quote_text,
                         'RawText quote failed.',
                         )
        return
