#!/usr/bin/env python
#
# $Id: docstring_StructuredText.py,v 1.5 2002/05/12 21:22:29 doughellmann Exp $
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

"""Docstring converter for StructuredText format.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: docstring_StructuredText.py,v $',
    'rcs_id'       : '$Id: docstring_StructuredText.py,v 1.5 2002/05/12 21:22:29 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <DougHellmann@bigfoot.com>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Wed, 26-Sep-2001 09:52:01 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.5 $',
    'date'         : '$Date: 2002/05/12 21:22:29 $',
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
import happydoclib.docstring.StructuredText
import happydoclib

#
# Module
#

def entryPoint():
    "Return information about this module to the dynamic loader."
    return {
        'name':'StructuredText',
        'factory':StructuredTextConverter,
        'filenamePatternList':[ '^.*\.stx$',
                                '^.*\.txt$',
                                '(README|LICENSE|ANNOUNCE|CHANGES)$',
                                ],
        }

class StructuredTextFile(happydoclib.happydocstring.ExternalDocumentationFileBase):
    """External documentation in StructuredText format.
    """
    _input_type = 'StructuredText'
    
    def __init__(self, filename, body=None):
        happydoclib.happydocstring.ExternalDocumentationFileBase.__init__(
            self,
            filename,
            body)
        converted_body = happydoclib.docstring.StructuredText.Basic(self._file_contents)
        one_liner_para = converted_body
        while 1:
            try:
                if one_liner_para.getChildren():
                    one_liner_para = one_liner_para.getChildren()[0]
                else:
                    break
            except AttributeError:
                break
        self._oneliner = str(one_liner_para)
        return


class StructuredTextConverter(happydoclib.happydocstring.HappyDocStringConverterBase):
    """StructuredText format converter.

    This converter supports translating StructuredText (see
    the StructuredText package) input to HTML output.
    
    """

    externalDocumentFactory = StructuredTextFile
    
    RECOGNIZED_OUTPUT_FORMATS = [ 'html' ]

    def _testOutputFormat(self, outputFormat):
        if outputFormat not in self.RECOGNIZED_OUTPUT_FORMATS:
            raise ValueError('Unrecognized output format "%s" for %s.' % (
                outputFormat,
                self.__class__.__name__,
                )
                             )

    def _cleanup(self,
                 inputText,
                 extractBody=re.compile('<body>(.*)</body>', re.MULTILINE | re.DOTALL),
                 ):
        "Clean converted text and return new value."
        match = extractBody.search(inputText)
        if not match:
            clean_text = inputText
        else:
            clean_text = match.group(1)
        return clean_text

    def _unquoteHTML( self,
                      text,
                      character_entities=( (re.compile('&amp;'), '&'),
                                           (re.compile("&lt;"), '<' ),
                                           (re.compile("&gt;"), '>' ),
                                           (re.compile('&quot;'), '"')
                                           ),
                      ):
        "Reverse the quoting process for character entities."
        for regex, replacement in character_entities:
            text = regex.sub(replacement, text)
        return text

    def _unquoteExamplesInST(self, st):
        "Unquote the characters in all example paragraphs in the ST tree."
        try:
            tag_name = st.getTagName()
        except AttributeError:
            return
        else:
            if tag_name in ('StructuredTextExample',):
                actual_para = st.aq_self
                text = self._unquoteHTML(actual_para._src)
                actual_para._src = text
            elif tag_name in ( 'StructuredTextLiteral',):
                actual_para = st.aq_self
                text = self._unquoteHTML(actual_para._value)
                actual_para._value = text
            else:
                for child in st.getChildNodes():
                    self._unquoteExamplesInST(child)
        return

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
        text = inputText
        self._testOutputFormat(outputFormat)
        if outputFormat == 'html':
            applyNamedArgs = {}
            applyNamedArgs.update(namedArgs)
            applyNamedArgs['level'] = level

            # Translate embedded references
            text = re.sub(
                r'[\000\n]\.\. \[([0-9_%s-]+)\]' % \
                happydoclib.docstring.StructuredText.STletters.letters,
                r'\n  <a name="\1">[\1]</a>',
                text)

            text = re.sub(
                r'([\000- ,])\[(?P<ref>[0-9_%s-]+)\]([\000- ,.:])' % \
                happydoclib.docstring.StructuredText.STletters.letters,
                r'\1<a href="#\2">[\2]</a>\3',
                text)

            text = re.sub(
                r'([\000- ,])\[([^]]+)\.html\]([\000- ,.:])',
                r'\1<a href="\2.html">[\2]</a>\3',
                text)
            
            try:
                # Get the ST Document
                st = happydoclib.docstring.StructuredText.Document(text)
            except TypeError, msg:
                # This usually means we're really looking at a
                # Classic StructuredText document, so try
                # falling back there.
                converter_factory = happydoclib.docstring.getConverterFactory('ClassicStructuredText')
                converter = converter_factory()
                html_representation = converter.convert(inputText, outputFormat)
            else:
                # New StructuredText worked, so convert the document
                # to HTML.
                
                # First, unquote example paragraphs so they are not quoted
                # twice by the HTML converter.
                self._unquoteExamplesInST(st)

                # Get the HTML representation
                htmlng = happydoclib.docstring.StructuredText.HTMLClass.HTMLClass()

                html_representation = apply( htmlng,
                                             (st,)+args,
                                             applyNamedArgs,
                                             )
                html_representation = str(html_representation)
                html_representation = self._cleanup(html_representation)
                
            return html_representation
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
        happydoclib.TRACE.into('StructuredTextConverter',
                               'quote',
                               inputText=inputText,
                               outputFormat=outputFormat,
                               args=args,
                               namedArgs=namedArgs,
                               )
        self._testOutputFormat(outputFormat)
        if outputFormat == 'html':
            html_quoted = apply( happydoclib.docstring.StructuredText.html_quote,
                                 (inputText,)+args,
                                 namedArgs,
                                 )
            happydoclib.TRACE.write('AFTER QUOTING="%s"' % html_quoted)
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
            happydoclib.TRACE.write('AFTER FIXUP="%s"' % html_quoted)
            happydoclib.TRACE.outof()
            return html_quoted

        happydoclib.TRACE.outof()
        return inputText


class StructuredTextUnitTest(happydoclib.happydocstring.DocStringConverterTest):
        
    html_quote_text =  '<>&"\'[]{};'
    html_quote_expected_text = "&lt;&gt;&amp;&quot;'[]{};"
    
    st_test_text_with_links = '''
        Structured Text With Links

          This "link":link.html points to link.html.

          This [1] reference points to an internal reference.

.. [1] This is the internal reference.
'''

    st_expected_text_with_links = '''
<h3>        Structured Text With Links</h3>
<p>          This <a href="link.html">link</a> points to link.html.</p>
<p>          This <a href="#1"><a href="#ref1">[1]</a></a> reference points to an internal reference.</p>
<p>  <a name="1"><a href="#ref1">[1]</a></a> This is the internal reference.</p>
'''

    st_test_text = '''Structured Text Manipulation

Parse a structured text string into a form that can be used with 
structured formats, like html.

Structured text is text that uses indentation and simple
symbology to indicate the structure of a document.  

A structured string consists of a sequence of paragraphs separated by
one or more blank lines.  Each paragraph has a level which is defined
as the minimum indentation of the paragraph.  A paragraph is a
sub-paragraph of another paragraph if the other paragraph is the last
preceding paragraph that has a lower level.

Special symbology is used to indicate special constructs:

- A single-line paragraph whose immediately succeeding paragraphs are lower
  level is treated as a header.

- A paragraph that begins with a '-', '*', or 'o' is treated as an
  unordered list (bullet) element.

- A paragraph that begins with a sequence of digits followed by a
  white-space character is treated as an ordered list element.

- A paragraph that begins with a sequence of sequences, where each
  sequence is a sequence of digits or a sequence of letters followed
  by a period, is treated as an ordered list element.

- A paragraph with a first line that contains some text, followed by
  some white-space and '--' is treated as
  a descriptive list element. The leading text is treated as the
  element title.

- Sub-paragraphs of a paragraph that ends in the word 'example' or the
  word 'examples', or '::' is treated as example code and is output as is.

- Text enclosed single quotes (with white-space to the left of the
  first quote and whitespace or puctuation to the right of the second quote)
  is treated as example code.

- Text surrounded by '*' characters (with white-space to the left of the
  first '*' and whitespace or puctuation to the right of the second '*')
  is emphasized.

- Text surrounded by '**' characters (with white-space to the left of the
  first '**' and whitespace or puctuation to the right of the second '**')
  is made strong.

- Text surrounded by '_' underscore characters (with whitespace to the left 
  and whitespace or punctuation to the right) is made underlined.

- Text encloded by double quotes followed by a colon, a URL, and concluded
  by punctuation plus white space, *or* just white space, is treated as a
  hyper link. For example:

    "Zope":http://www.zope.org/ is ...

  Is interpreted as '<a href="http://www.zope.org/">Zope</a> is ....'
  Note: This works for relative as well as absolute URLs.

- Text enclosed by double quotes followed by a comma, one or more spaces,
  an absolute URL and concluded by punctuation plus white space, or just
  white space, is treated as a hyper link. For example: 

    "mail me", mailto:amos@digicool.com.

  Is interpreted as '<a href="mailto:amos@digicool.com">mail me</a>.' 

- Text enclosed in brackets which consists only of letters, digits,
  underscores and dashes is treated as hyper links within the document.
  For example:
    
    As demonstrated by Smith [12] this technique is quite effective.

  Is interpreted as '... by Smith <a href="#12">[12]</a> this ...'. Together
  with the next rule this allows easy coding of references or end notes.

- Text enclosed in brackets which is preceded by the start of a line, two
  periods and a space is treated as a named link. For example:

    .. [12] "Effective Techniques" Smith, Joe ... 

  Is interpreted as '<a name="12">[12]</a> "Effective Techniques" ...'.
  Together with the previous rule this allows easy coding of references or
  end notes. 


- A paragraph that has blocks of text enclosed in '||' is treated as a
  table. The text blocks correspond to table cells and table rows are
  denoted by newlines. By default the cells are center aligned. A cell
  can span more than one column by preceding a block of text with an
  equivalent number of cell separators '||'. Newlines and '|' cannot
  be a part of the cell text. For example:

      |||| **Ingredients** ||
      || *Name* || *Amount* ||
      ||Spam||10||
      ||Eggs||3||

  is interpreted as::

    <TABLE BORDER=1 CELLPADDING=2>
     <TR>
      <TD ALIGN=CENTER COLSPAN=2> <strong>Ingredients</strong> </TD>
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
    </TABLE>'''

    st_expected_text = '''
<p>Structured Text Manipulation</p>
<p>Parse a structured text string into a form that can be used with 
structured formats, like html.</p>
<p>Structured text is text that uses indentation and simple
symbology to indicate the structure of a document.  </p>
<p>A structured string consists of a sequence of paragraphs separated by
one or more blank lines.  Each paragraph has a level which is defined
as the minimum indentation of the paragraph.  A paragraph is a
sub-paragraph of another paragraph if the other paragraph is the last
preceding paragraph that has a lower level.</p>
<p>Special symbology is used to indicate special constructs:</p>

<ul>
<li><p>A single-line paragraph whose immediately succeeding paragraphs are lower
  level is treated as a header.</p></li>
<li><p>A paragraph that begins with a '-', <code>*</code>, or <code>o</code> is treated as an
  unordered list (bullet) element.</p></li>
<li><p>A paragraph that begins with a sequence of digits followed by a
  white-space character is treated as an ordered list element.</p></li>
<li><p>A paragraph that begins with a sequence of sequences, where each
  sequence is a sequence of digits or a sequence of letters followed
  by a period, is treated as an ordered list element.</p></li>
<li><p>A paragraph with a first line that contains some text, followed by
  some white-space and <code>--</code> is treated as
  a descriptive list element. The leading text is treated as the
  element title.</p></li>
<li><p>Sub-paragraphs of a paragraph that ends in the word <code>example</code> or the
  word <code>examples</code>, or <code>::</code> is treated as example code and is output as is.</p></li>
<li><p>Text enclosed single quotes (with white-space to the left of the
  first quote and whitespace or puctuation to the right of the second quote)
  is treated as example code.</p></li>
<li><p>Text surrounded by '<em><code> characters (with white-space to the left of the
  first </code></em>' and whitespace or puctuation to the right of the second <code>*</code>)
  is emphasized.</p></li>
<li><p>Text surrounded by '<strong><code> characters (with white-space to the left of the
  first </code></strong>' and whitespace or puctuation to the right of the second <code>**</code>)
  is made strong.</p></li>
<li><p>Text surrounded by <code>_</code> underscore characters (with whitespace to the left 
  and whitespace or punctuation to the right) is made underlined.</p></li>
<li><p>Text encloded by double quotes followed by a colon, a URL, and concluded
  by punctuation plus white space, <em>or</em> just white space, is treated as a
  hyper link. For example:<p>    <a href="http://www.zope.org/">Zope</a> is ...</p>
<p>  Is interpreted as '<a href="http://www.zope.org/">Zope</a> is ....'
  Note: This works for relative as well as absolute URLs.</p>
</p></li>
<li><p>Text enclosed by double quotes followed by a comma, one or more spaces,
  an absolute URL and concluded by punctuation plus white space, or just
  white space, is treated as a hyper link. For example: <p>    <a href="mailto:amos@digicool.com">mail me</a>.</p>
<p>  Is interpreted as '<a href="mailto:amos@digicool.com">mail me</a>.' </p>
</p></li>
<li><p>Text enclosed in brackets which consists only of letters, digits,
  underscores and dashes is treated as hyper links within the document.
  For example:<p>    As demonstrated by Smith <a href="#12"><a href="#ref12">[12]</a></a> this technique is quite effective.</p>
<p>  Is interpreted as '... by Smith <a href="#12"><a href="#ref12">[12]</a></a> this ...'. Together
  with the next rule this allows easy coding of references or end notes.</p>
</p></li>
<li><p>Text enclosed in brackets which is preceded by the start of a line, two
  periods and a space is treated as a named link. For example:<p>    .. <a href="#12"><a href="#ref12">[12]</a></a> "Effective Techniques" Smith, Joe ... </p>
<p>  Is interpreted as '<a name="12"><a href="#ref12">[12]</a></a> "Effective Techniques" ...'.
  Together with the previous rule this allows easy coding of references or
  end notes. </p>
</p></li>
<li><p>A paragraph that has blocks of text enclosed in <code>||</code> is treated as a
  table. The text blocks correspond to table cells and table rows are
  denoted by newlines. By default the cells are center aligned. A cell
  can span more than one column by preceding a block of text with an
  equivalent number of cell separators <code>||</code>. Newlines and <code>|</code> cannot
  be a part of the cell text. For example:<p>      |||| <strong>Ingredients</strong> ||
      || <em>Name</em> || <em>Amount</em> ||
      ||Spam||10||
      ||Eggs||3||</p>
<p>  is interpreted as:
<pre>
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
</pre>
</p>
</p></li>

</ul>
'''
    

    def testConvertStructuredTextToHTML(self):
        self._testConversion( self.st_test_text, 'StructuredText',
                             'html', self.st_expected_text,
                             'StructuredText-to-HTML conversion failed.'
                             )
        return

    def testConvertStructuredTextToHTMLWithLinks(self):
        self._testConversion( self.st_test_text_with_links, 'StructuredText',
                             'html', self.st_expected_text_with_links,
                             'StructuredText-to-HTML-with-links conversion failed.',
                             )
        return

    def testQuoteStructuredTextToHTML(self):
        self._testQuote(self.html_quote_text, 'StructuredText', 'html',
                       self.html_quote_expected_text,
                       'ST-to-HTML quote failed.',
                       )
        return
    
    def testStructuredTextOneLiner(self):
        stf = StructuredTextFile(filename='internal', body=self.st_test_text)
        assert stf, 'Unable to create valid StructuredTextFile'
        expected_oneliner = 'Structured Text Manipulation'
        assert stf.oneLiner() == expected_oneliner, 'Got different one-liner "%s"' % stf.oneLiner()
        return

    def testBug471981(self):
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
        expected_text1 = '''
<h3> any text</h3>
<p>    first
    section</p>
<h3>first heading</h3>
<p>    second
    section</p>
<h3>second heading</h3>
<p>    third
    section</p>
<p>third heading</p>
'''
        
        self._testConversion(
            input_text1,
            'StructuredText',
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
        expected_text2 = '''
<h3>first heading</h3>
<p>    first
    section</p>
<h3>second heading</h3>
<p>    second
    section</p>
<h3>third heading</h3>
<p>    third
    section</p>
'''
        
        self._testConversion(
            input_text2,
            'StructuredText',
            'html',
            expected_text2,
            'Converting Classic ST to HTML did not produce expected results.',
            )
        return
    
    
    def testWithQuotableCharacters(self):
        input_text = "Here are some quotable characters. & < > < >."
        expected_text = '\n<p>Here are some quotable characters. & < > < >.</p>\n'

        self._testConversion(
            input_text,
            'StructuredText',
            'html',
            expected_text,
            'Converting ST to HTML with quotable characters did not produce expected results.',
            )
        
    
    def testWithQuotableCharactersInExample(self):
        input_text = """Here are some quotable characters in example paragraphs

        First, a true example::

          Begin & < >

        Finally, embedded in a code segment '& < >'.
        """
        expected_text = """
<h3>Here are some quotable characters in example paragraphs</h3>
<p>        First, a true example:
<pre>
          Begin &amp; &lt; &gt;
</pre>
</p>
<p>        Finally, embedded in a code segment '& < >'.</p>
"""

        self._testConversion(
            input_text,
            'StructuredText',
            'html',
            expected_text,
            'Converting ST to HTML with quotable characters did not produce expected results.',
            )
        
