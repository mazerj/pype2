#!/usr/bin/env python
#
# $Id: happydocstring.py,v 1.3 2002/08/04 10:47:30 doughellmann Exp $
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

"""Base class for docstring converters.

    A docstring converter is responsible for translating the docstring
    markup syntax to the output formatter syntax.  Docstring
    converters should be as generic as possible, but by their nature
    will have a close relationship with a happyformatter type.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: happydocstring.py,v $',
    'rcs_id'       : '$Id: happydocstring.py,v 1.3 2002/08/04 10:47:30 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <DougHellmann@bigfoot.com>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Wed, 26-Sep-2001 09:41:36 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.3 $',
    'date'         : '$Date: 2002/08/04 10:47:30 $',
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
from StreamFlushTest import StreamFlushTest

#
# Module
#

class ExternalDocumentationFileBase:
    "Formatted documentation in an outside file."

    _input_type = None

    def __init__(self, filename, body=None):
        self.filename = filename

        self._oneliner = ''
        if body:
            self._file_contents = body
        else:
            self._file_contents = open(filename, 'rt').read()
        return

    def oneLiner(self):
        "Returns the one line description from the file."
        return self._oneliner

    def __str__(self):
        "String representation of file."
        return str(self._file_contents)

    def getInputType(self):
        "Input type of file contents."
        return self._input_type

        

class HappyDocStringConverterBase:
    "Base class for docstring converters."

    externalDocumentFactory = ExternalDocumentationFileBase

    def __init__(self, **extraNamedParameters):
        """Initialize the docstring converter.

        Parameters:

          'extraNamedParameters' -- Parameters specified by name which
          were not interpreted by a subclass initialization.

        """
        #
        # Warn about extra named parameters
        #
        for extra_param, extra_value in extraNamedParameters.items():
            print 'WARNING: Parameter "%s" (%s) unrecognized by docstring converter %s.' % \
                  (extra_param, extra_value, self.__class__.__name__)
        return

    
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

          '*args' -- Additional, converter-specific, positional arguments.

          '**namedArgs' -- Additional, converter-specific, named arguments.
        """
        raise ValueError('%s does not implement convert' % self.__class__.__name__)

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
        raise ValueError('%s does not implement quote' % self.__class__.__name__)
        
    def getExternalDocumentationFile(self, filename, *args, **namedArgs):
        """Returns the 'inputText' quoted in a way that special characters are escaped.

        Parameters:

          'filename' -- Name of the file to retrieve.
          
          '*args' -- Additional, converter-specific, positional arguments.

          '**namedArgs' -- Additional, converter-specific, named arguments.
        """
        try:
            file = self.externalDocumentFactory(filename)
        except IOError:
            file = None
        return file



class DocStringConverterTest(StreamFlushTest):

    def __init__(self, methodName, outputDir=''):
        StreamFlushTest.__init__(self, methodName, outputDir)
        
        import happydoclib.docstring
        self._hddocstring = happydoclib.docstring
        return

    def _testConversion(self, inputText, inputFormat, outputFormat, expectedText,
                       errorMessage,
                       debug=0):
        converter_factory = self._hddocstring.getConverterFactory(inputFormat)
        converter = converter_factory()
        converted_text = converter.convert( inputText, outputFormat )
        if debug:
            print '\n[[%s]]' % converted_text
        if converted_text != expectedText:
            print '[INPUT[%s]INPUT]' % inputText
            print '[EXPECTED[%s]EXPECTED]' % expectedText
            print '[CONVERTED[%s]CONVERTED]' % converted_text
        assert (converted_text == expectedText), '%s ("%s", "%s") ' % (errorMessage,
                                                                   expectedText,
                                                                   converted_text)
        return

    def _testQuote(self, inputText, inputFormat, outputFormat, expectedText,
                  errorMessage):
        converter_factory = self._hddocstring.getConverterFactory(inputFormat)
        converter = converter_factory()
        quoted_text = converter.quote(inputText, 'html' )
        assert (quoted_text == expectedText), errorMessage
        return

