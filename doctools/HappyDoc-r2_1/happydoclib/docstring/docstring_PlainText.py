#!/usr/bin/env python
#
# $Id: docstring_PlainText.py,v 1.1 2001/10/24 21:27:35 doughellmann Exp $
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

"""Plan text format converter.

    This is *not* the same as the RawText converter, which is a
    pass-through converter.  This converter will actually modify some
    output.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: docstring_PlainText.py,v $',
    'rcs_id'       : '$Id: docstring_PlainText.py,v 1.1 2001/10/24 21:27:35 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <DougHellmann@bigfoot.com>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Wed, 26-Sep-2001 09:52:01 EDT',

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
import happydoclib.docstring.StructuredText
import happydoclib

#
# Module
#

def entryPoint():
    "Return information about this module to the dynamic loader."
    return {
        'name':'PlainText',
        'factory':PlainTextConverter,
        'filenamePatternList':[],
        }


class PlainTextFile(happydoclib.happydocstring.ExternalDocumentationFileBase):
    """External documentation in PlainText format.
    """
    _input_type = 'PlainText'
    
    def __init__(self, filename, body=None):
        happydoclib.happydocstring.ExternalDocumentationFileBase.__init__(
            self,
            filename,
            body)
        lines = self._file_contents.split('\n')
        for body_line in lines:
            body_line = body_line.strip()
            if not body_line:
                continue
            self._oneliner = body_line
            break
        return

class PlainTextConverter(happydoclib.happydocstring.HappyDocStringConverterBase):
    """PlainText format converter.

    This is *not* the same as the RawText converter, which is a
    pass-through converter.  This converter will actually modify some
    output.
    
    """

    externalDocumentFactory = PlainTextFile
    
    RECOGNIZED_OUTPUT_FORMATS = [ 'html' ]
    _input_type = 'PlainText'

    def _testOutputFormat(self, outputFormat):
        if outputFormat not in self.RECOGNIZED_OUTPUT_FORMATS:
            raise ValueError('Unrecognized output format "%s" for %s.' % (
                outputFormat,
                self.__class__.__name__,
                )
                             )

    def convert(self, inputText, outputFormat, level=3, *args, **namedArgs):
        """Returns the 'inputText' data translated into the 'outputFormat'.

        Parameters:

          'inputText' -- String or other sequence of characters to be
          converted.  This string should be in the format advertised
          by the docstring converter.

          'outputFormat' -- String defined by the docstring converter
          class to represent a supported output scheme.  This value is
          converter-specific, and not all converters will support the
          same output formats.

          'level=3' -- Beginning indention level for the text.  This
          controls what type of header elements are created among
          other behaviors.
        
        """
        self._testOutputFormat(outputFormat)
        if outputFormat == 'html':
            return '<pre>\n%s\n</pre>' % str(inputText)
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
        self._testOutputFormat(outputFormat)
        if outputFormat == 'html':
            return apply( happydoclib.docstring.StructuredText.html_quote,
                          (inputText,)+args,
                          namedArgs,
                          )
        return inputText


class PlainTextUnitTest(happydoclib.happydocstring.DocStringConverterTest):


    def testPlainTextOneLiner(self):
        body = '''This is the one liner.

        Here is some additional text.
        '''
        ptf = PlainTextFile(filename='internal', body=body)
        assert ptf, 'Unable to create valid PlainTextFile'
        expected_oneliner = 'This is the one liner.'
        assert ptf.oneLiner() == expected_oneliner, \
               'Got different one-liner "%s"' % ptf.oneLiner()
        return
    
