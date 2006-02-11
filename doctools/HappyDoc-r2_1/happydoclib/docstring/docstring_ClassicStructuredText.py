#!/usr/bin/env python
#
# $Id: docstring_ClassicStructuredText.py,v 1.3 2002/08/24 19:57:22 doughellmann Exp $
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

"""Docstring converter for original StructuredText format.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: docstring_ClassicStructuredText.py,v $',
    'rcs_id'       : '$Id: docstring_ClassicStructuredText.py,v 1.3 2002/08/24 19:57:22 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <DougHellmann@bigfoot.com>',
    'project'      : 'HappyDoc',
    'created'      : 'Wed, 26-Sep-2001 09:52:01 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.3 $',
    'date'         : '$Date: 2002/08/24 19:57:22 $',
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

#
# Module
#

def entryPoint():
    "Return information about this module to the dynamic loader."
    return {
        'name':'ClassicStructuredText',
        'factory':ClassicStructuredTextConverter,
        'filenamePatternList':[ ],
        }

class ClassicStructuredTextFile(happydoclib.happydocstring.ExternalDocumentationFileBase):
    """External documentation in StructuredText format.
    """
    _input_type = 'ClassicStructuredText'
    
    def __init__(self, filename, body=None):
        import happydoclib.docstring.StructuredText.ClassicStructuredText
        StructuredText = happydoclib.docstring.StructuredText.ClassicStructuredText
        happydoclib.happydocstring.ExternalDocumentationFileBase.__init__(
            self,
            filename,
            body)
        converted_body = StructuredText.StructuredText(self._file_contents)
        self._oneliner = str(converted_body.structure[0][0])
        return


class ClassicStructuredTextConverter(happydoclib.happydocstring.HappyDocStringConverterBase):
    """Classic StructuredText format converter.

    This converter supports translating StructuredText (see
    happydoc/hddocstring/StructuredText/ClassicStructuredText.py)
    input to HTML output.
    
    """

    externalDocumentFactory = ClassicStructuredTextFile
    
    RECOGNIZED_OUTPUT_FORMATS = [ 'html' ]

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
        import happydoclib.docstring.StructuredText.ClassicStructuredText
        StructuredText = happydoclib.docstring.StructuredText.ClassicStructuredText
        if outputFormat == 'html':
            applyNamedArgs = {}
            applyNamedArgs.update(namedArgs)
            applyNamedArgs['level'] = level
            html_representation = apply( StructuredText.html_with_references,
                                         (inputText,)+args,
                                         applyNamedArgs,
                                         )
            return str(html_representation)
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
        import happydoclib.docstring.StructuredText.ClassicStructuredText
        StructuredText = happydoclib.docstring.StructuredText.ClassicStructuredText
        if outputFormat == 'html':
            html_quoted = apply( StructuredText.html_quote,
                                 (inputText,)+args,
                                 namedArgs,
                                 )
            #
            # Replace form: &quot;.*&quot;:
            #         with: ".*"
            #
            # This allows links to work.
            #
            html_quoted = re.sub(
                '&quot;([^&]+)&quot;:',
                '"\\1":',
                html_quoted)
            return html_quoted
            
        return inputText


class ClassicSTUnitTest(happydoclib.happydocstring.DocStringConverterTest):

    expectedOutput = '''<h3>"""Classic Structured Text Manipulation</h3>
<p>  Parse a structured text string into a form that can be used with
  structured formats, like html.</p>

<p>  Structured text is text that uses indentation and simple symbology
  to indicate the structure of a document.</p>

<p>  A structured string consists of a sequence of paragraphs separated
  by one or more blank lines.  Each paragraph has a level which is
  defined as the minimum indentation of the paragraph.  A paragraph is
  a sub-paragraph of another paragraph if the other paragraph is the
  last preceding paragraph that has a lower level.</p>


<p>Special symbology is used to indicate special constructs:</p>

<ul><li><p>A single-line paragraph whose immediately succeeding paragraphs are lower
  level is treated as a header.</p>

</li>
<li><p>A paragraph that begins with a <code>-</code>, <code>*</code>, or <code>o</code> is treated as an
  unordered list (bullet) element.</p>

</li>
<li><p>A paragraph that begins with a sequence of digits followed by a
  white-space character is treated as an ordered list element.</p>

</li>
<li><p>A paragraph that begins with a sequence of sequences, where each
  sequence is a sequence of digits or a sequence of letters followed
  by a period, is treated as an ordered list element.</p>

</li>
<li><p>A paragraph with a first line that contains some text, followed by
  some white-space and <code>--</code> is treated as
  a descriptive list element. The leading text is treated as the
  element title.</p>

</li>
<li><p>Sub-paragraphs of a paragraph that ends in the word <code>example</code> or the
  word <code>examples</code>, or <code>::</code> is treated as example code and is output as is.</p>

</li>
<li><p>Text enclosed single quotes (with white-space to the left of the
  first quote and whitespace or punctuation to the right of the second quote)
  is treated as example code.</p>

</li>
<li><p>Text surrounded by <code>*</code> characters (with white-space to the left of the
  first <code>*</code> and whitespace or punctuation to the right of the second <code>*</code>)
  is emphasized.</p>

</li>
<li><p>Text surrounded by <code>**</code> characters (with white-space to the left of the
  first <code>**</code> and whitespace or punctuation to the right of the second <code>**</code>)
  is made strong.</p>

</li>
<li><p>Text surrounded by <code>_</code> underscore characters (with whitespace to the left 
  and whitespace or punctuation to the right) is made underlined.</p>

</li>
<li><p>Text encloded by double quotes followed by a colon, a URL, and concluded
  by punctuation plus white space, <em>or</em> just white space, is treated as a
  hyper link. For example:</p>
<p>    "Zope":http://www.zope.org/ is ...</p>

<p>  Is interpreted as <code><a href="http://www.zope.org/">Zope</a> is ....</code>
  Note: This works for relative as well as absolute URLs.</p>


</li>
<li><p>Text enclosed by double quotes followed by a comma, one or more spaces,
  an absolute URL and concluded by punctuation plus white space, or just
  white space, is treated as a hyper link. For example:</p>
<p>    "mail me", mailto:amos@digicool.com.</p>

<p>  Is interpreted as <code><a href="mailto:amos@digicool.com">mail me</a>.</code> </p>


</li>
<li><p>Text enclosed in brackets which consists only of letters, digits,
  underscores and dashes is treated as hyper links within the document.
  For example:</p>
<p>    As demonstrated by Smith <a href="#12">[12]</a> this technique is quite effective.</p>

<p>  Is interpreted as <code>... by Smith <a href="#12">[12]</a> this ...</code>. Together
  with the next rule this allows easy coding of references or end notes.</p>


</li>
<li><p>Text enclosed in brackets which is preceded by the start of a line, two
  periods and a space is treated as a named link. For example:</p>
<p>    .. <a href="#12">[12]</a> "Effective Techniques" Smith, Joe ... </p>

<p>  Is interpreted as <code><a name="12">[12]</a> "Effective Techniques" ...</code>.
  Together with the previous rule this allows easy coding of references or
  end notes. </p>


</li>
<li><p>A paragraph that has blocks of text enclosed in <code>||</code> is treated as a
  table. The text blocks correspond to table cells and table rows are
  denoted by newlines. By default the cells are center aligned. A cell
  can span more than one column by preceding a block of text with an
  equivalent number of cell separators <code>||</code>. Newlines and <code>|</code> cannot
  be a part of the cell text.</p>
<p>  For example:</p>
<PRE>
      |||| **Ingredient** ||
      || *Name* || *Amount* ||
      ||Spam||10||
      ||Eggs||3||

</PRE>

<p>  is interpreted as:</p>
<PRE>
    &lt;TABLE BORDER=1 CELLPADDING=2&gt;
     &lt;TR&gt;
      &lt;TD ALIGN=CENTER COLSPAN=2&gt; &lt;strong&gt;Ingredients&lt;/strong&gt; &lt;/TD&gt;
     &lt;/TR&gt;
     &lt;TR&gt;
      &lt;TD ALIGN=CENTER COLSPAN=1&gt; &lt;em&gt;Name&lt;/em&gt; &lt;/TD&gt;
      &lt;TD ALIGN=CENTER COLSPAN=1&gt; &lt;em&gt;Amount&lt;/em&gt; &lt;/TD&gt;
     &lt;/TR&gt;
     &lt;TR&gt;
      &lt;TD ALIGN=CENTER COLSPAN=1&gt;Spam&lt;/TD&gt;
      &lt;TD ALIGN=CENTER COLSPAN=1&gt;10&lt;/TD&gt;
     &lt;/TR&gt;
     &lt;TR&gt;
      &lt;TD ALIGN=CENTER COLSPAN=1&gt;Eggs&lt;/TD&gt;
      &lt;TD ALIGN=CENTER COLSPAN=1&gt;3&lt;/TD&gt;
     &lt;/TR&gt;
    &lt;/TABLE&gt;

</PRE>

<p>  and appear as:</p>
<p>
<TABLE BORDER=1 CELLPADDING=2>
 <TR>
  <TD ALIGN=CENTER COLSPAN=2> <strong>Ingredient</strong> </TD>
 </TR>
 <TR>
  <TD ALIGN=CENTER COLSPAN=1> <em>Name</em> </TD>
  <TD ALIGN=CENTER COLSPAN=1> <em>Amount</em> </TD>
 </TR>
 <TR>
  <TD ALIGN=CENTER COLSPAN=1>Spam</TD>
  <TD ALIGN=CENTER COLSPAN=1>10</TD>
 </TR>
 <TR>
  <TD ALIGN=CENTER COLSPAN=1>Eggs</TD>
  <TD ALIGN=CENTER COLSPAN=1>3</TD>
 </TR>
</TABLE></p>



</li></ul>
<p>"""</p>

'''

    def testClassicStructuredTextConversion(self):
        filename = 'TestCases/test_classic_structuredtext.py'
        import happydoclib.parseinfo
        parsed_module = happydoclib.parseinfo.getDocs(None, filename)
        input_text = parsed_module._docstring
        
        self._testConversion(
            input_text,
            'ClassicStructuredText',
            'html',
            self.expectedOutput,
            'Converting Classic ST to HTML did not produce expected results.',
            )
        return

    def testBug471981Classic(self):
        input_text1 = """ any text

first heading

    first
    section

second heading

    second
    section

third heading

    third
    section
"""
        expected_text1 = '''<p> any text</p>

<h3>first heading</h3>
<p>    first
    section</p>


<h3>second heading</h3>
<p>    second
    section</p>


<h3>third heading</h3>
<p>    third
    section
</p>


'''
        
        self._testConversion(
            input_text1,
            'ClassicStructuredText',
            'html',
            expected_text1,
            'Converting Classic ST to HTML did not produce expected results.',
            )
        
        input_text2 = """

first heading

    first
    section

second heading

    second
    section

third heading

    third
    section
"""
        expected_text2 = '''<p>
<TABLE BORDER=1 CELLPADDING=2>
</TABLE></p>

<h3>first heading</h3>
<p>    first
    section</p>


<h3>second heading</h3>
<p>    second
    section</p>


<h3>third heading</h3>
<p>    third
    section
</p>


'''
        
        self._testConversion(
            input_text2,
            'ClassicStructuredText',
            'html',
            expected_text2,
            'Converting Classic ST to HTML did not produce expected results.',
            )
        return
    
