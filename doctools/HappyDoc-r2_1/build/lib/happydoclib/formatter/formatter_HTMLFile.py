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


"""Formatter which produces HTML with tables.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name':'$RCSfile: formatter_HTMLFile.py,v $',
    'creator':'Doug Hellmann <doug@hellfly.net>',
    'project':'HappyDoc',
    'created':'Sat, 03-Jun-2000 17:58:48 EDT',
    #
    #  Current Information
    #
    'author':'$Author: doughellmann $',
    'version':'$Revision: 1.6 $',
    'date':'$Date: 2002/08/24 19:53:31 $',
    }
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import os
import re
import string
import types

#
# Import Local modules
#
import happydoclib
import happydoclib.formatter.fileformatterbase

#
# Module
#

def entryPoint():
    "Return information about this module to the dynamic loader."
    return {
        'name':'HTMLTable',
        'factory':HTMLTableFormatter,
        }



class HTMLTableFormatter(happydoclib.formatter.fileformatterbase.FileBasedFormatter):
    """Formatter which produces HTML with tables.

    The output from this formatter is not generally suitable for
    printing, but works fine for online documentation.  The primary
    concern with printing the output is that the nested tables can
    cause pages to be very wide, especially with a lot of nesting of
    classes.  Printable HTML output should be addressed by another
    formatter.

      Parameters

        compactHTML -- A boolean switch to cause the formatter
                       to generate more compact HTML.  Extra
                       whitespace is removed in order to make the
                       generated files take up less space and
                       download more quickly.  The default is
                       False to cause output to be more readable.
      
        filenamePrefix -- A prefix to preprend to the base names of
                          files and directories being created.  This
                          is useful for situations where the names
                          which would be automatically generated might
                          cause a name clash or conflict.

        pageBackgroundColor -- Background color for HTML pages

        levelOneHeadingBackgroundColor -- Background color for level
                                          one heading sections.

        levelOneHeadingForegroundColor -- Foreground color for level
                                          one heading sections.

        levelTwoHeadingBackgroundColor -- Background color for level
                                          two heading sections

        levelTwoHeadingForegroundColor -- Foreground color for level
                                          two heading sections.

        codeForegroundColor -- Foreground color for code blocks.

        dateStampFiles -- Boolean indicating whether or not to include
                          a date/time stamp in files.

        htmlQuoteText -- Boolean indicating whether or not to assume
                         that docstrings need to be quoted because
                         they might have special HTML characters in
                         them.  Defaults to true so that text is
                         quoted.

        debug -- Enable debugging comments in output.
      
    """

    def __init__(self,
                 docSet,
                 pageBackgroundColor='#ffffff',
                 levelOneHeadingBackgroundColor='#88bbee',
                 levelOneHeadingForegroundColor='#000000',
                 levelTwoHeadingBackgroundColor='#99ccff',
                 levelTwoHeadingForegroundColor='#000000',
                 codeForegroundColor='#000088',
                 docsetTitle=None,
                 dateStampFiles=1,
                 htmlQuoteText=1,
                 compactHTML=0,
                 debug=0,
                 **configuration):
        """Initialize the HTMLTableFormatter.

        Parameters

            'docSet' -- the DocSet instance containing global cross-reference
                      information
            
            '**configuration' -- additional, optional, configuration values

        """
        #
        # Preserve configuration parameters
        #
        self._page_bgcolor = pageBackgroundColor
        self._l1_bgcolor = levelOneHeadingBackgroundColor
        self._l1_fgcolor = levelOneHeadingForegroundColor
        self._l2_bgcolor = levelTwoHeadingBackgroundColor
        self._l2_fgcolor = levelTwoHeadingForegroundColor
        self._code_fgcolor = codeForegroundColor
        

        self._date_stamp_files = happydoclib.optiontools.getBooleanArgumentValue(
            dateStampFiles)
        self._html_quote_text = happydoclib.optiontools.getBooleanArgumentValue(
            htmlQuoteText)
        self._compact_html = happydoclib.optiontools.getBooleanArgumentValue(
            compactHTML)

        self.debug = debug

        #
        # Some stack counters for debugging
        #
        self._section_header_counters = {}
        self._section_header_counter = 0
        self._section_level_counter = 1
        
        #
        # Initialize the base class
        #
        apply( happydoclib.formatter.fileformatterbase.FileBasedFormatter.__init__,
               (self, docSet),
               configuration)
        return

    ##
    ## FileBasedFormatter implementation
    ##

    def _fixReference(self, reference, sep=os.sep):
        """All HTML links use the '/' separator, so here the current
        platform separator needs to be replaced with the '/'.
        """
        happydoclib.TRACE.into('HTMLTableFormatter', '_fixReference',
                               reference=reference)
        new_ref = reference.replace(sep, '/')
        if sep == ':':
            if new_ref[:4] == 'http':
                new_ref = 'http://%s' % new_ref[5:]
        return happydoclib.TRACE.outof(new_ref)
    
        
    def getReference(self, infoSource, relativeSource, name=None):
        """Returns a reference to the 'infoSource' from 'relativeSource'.
        """
        #
        # Figure out the name of the infoSource
        #
        happydoclib.TRACE.into('HTMLTableFormatter', 'getReference',
                               infoSource=infoSource,
                               name=name,
                               relativeSource=relativeSource,
                               )
        
        if hasattr(infoSource, 'getPath'):
            path = infoSource.getPath()
            happydoclib.TRACE.writeVar(path=path)
        if not name:
            name = self.getNameForInfoSource( infoSource )
            happydoclib.TRACE.writeVar(name=name)
            
        info_source_path = self.getFullOutputNameForObject( infoSource )
        happydoclib.TRACE.writeVar(info_source_path=info_source_path)

        link = happydoclib.path.computeRelativeHTMLLink(
            relativeSource,
            info_source_path,
            self._docset.getOutputBaseDirectory()
            )
        happydoclib.TRACE.write('Name is "%s"' % name)
        happydoclib.TRACE.writeVar(link=link)
        if link[0] == '/':
            happydoclib.TRACE.write('starts at root')

        link = self._fixReference(link)
            
        info = {
            'name':name,
            'link':link,
            }
        ref = '<a href="%(link)s">%(name)s</a>' % info
        #if link=='formatterloader.html':
        #    raise 'DEBUG HERE'
        #print 'REFERENCE:', ref
        
        return happydoclib.TRACE.outof(ref)
        

    
    def getNamedReference(self, infoSource, name, relativeSource):
        """Returns a reference to 'name' within the documentation for
        'infoSource' from 'relativeSource'.
        """
        happydoclib.TRACE.into('HTMLTableFormatter', 'getNamedReference',
                               infoSource=infoSource.getName(),
                               name=name,
                               relativeSource=relativeSource,
                               )
        happydoclib.TRACE.writeVar(output_name=self.getOutputNameForObject(infoSource))

        link = happydoclib.path.computeRelativeHTMLLink(
            relativeSource,
            self.getOutputNameForObject(infoSource),
            self._docset.getOutputBaseDirectory()
            )
        
        happydoclib.TRACE.writeVar(link=link)
        
        link = self._fixReference(link)
        
        info = {
            'name':infoSource.getName(),
            'link':link,
            'target':name,
            }
        ref = '<a href="%(link)s#%(target)s">%(target)s</a>' % info
        
        return happydoclib.TRACE.outof(ref)
    

    def getInternalReference(self, infoSource):
        """Returns a reference to 'infoSource' within the current document.
        """
        info = {
            'name':infoSource.getName(),
            }
        ref = '<a href="#%(name)s">%(name)s</a>' % info
        return ref
    
    def getPythonReference(self, moduleName):
        """Returns a reference to 'moduleName' documentation on the
        "Python.org":http://www.python.org documentation site.
        """
        libdoc = self._python_lib_doc
        if moduleName in self.sys_modules:
            return '<a href="%(libdoc)s/module-%(moduleName)s.html">%(moduleName)s</a>' % locals()
        else:
            return moduleName
    
    def getFilenameExtension(self):
        "Returns the extension for creating output files."
        return 'html'

    def openOutput(self, name, title1, title2='&nbsp;'):
        """Open output destination using 'name' with the title from 'title1'.
        Write 'title2' as a secondary title to the new output.
        """
        #print 'OPEN OUTPUT: ', name
        f = happydoclib.formatter.fileformatterbase.FileBasedFormatter.openOutput(
            self,
            name,
            title1,
            )
        self.fileHeader( title1, title2, f )
        return f

    def fileHeader(self, title1, title2='&nbsp;', output=None):
        """Write the formatting for a file header to the open file."""
        self.htmlHeader( title1, title2,
                         self._l1_bgcolor,
                         self._l1_fgcolor,
                         output) 
        return

    def closeOutput(self, output):
        "Close the 'output' handle."
        self.fileFooter(output)
        output.close()
        return

    def fileFooter(self, output):
        """Write the formatting for a file footer to the open file."""
        self.htmlFooter(output)
        return
    
    def pushSectionLevel(self, output):
        "Push a section level on the 'output' stack."
        self._section_level_counter = self._section_level_counter + 1
        self._section_header_counter = self._section_header_counters.get(
            self._section_level_counter, 0)
        self.comment('section %d:%d (push level)' % (self._section_level_counter,
                                                     self._section_header_counter),
                     output)
        self.writeHTML(
            '<table border="0" cellpadding="5" cellspacing="0" width="100%">\n',
            output)
        self.comment('push level', output)
        return

    def popSectionLevel(self, output):
        "Pop a section level from the 'output' stack."
        self.comment('section %d:%d (pop level)' % (self._section_level_counter,
                                                    self._section_header_counter),
                     output)
        #self.writeHTML('</td></tr></table>\n', output)
        self.writeHTML('</table>\n', output)
        self.comment('pop level', output)
        #
        # Depending on the pop level code to
        # close the headers for the level we just left,
        # too.
        #
        self._section_header_counters[self._section_level_counter] = 0
        #
        # Switch levels
        #
        self._section_level_counter = self._section_level_counter - 1
        #
        # Close the headers on the current level
        #
        #self._section_header_counters[self._section_level_counter] = 0
        self._section_header_counter = self._section_header_counters.get(
            self._section_level_counter, 0)
        return


    def getRootLocation(self, output):
        "Return the root documentation node location relative to this 'output' location."
        first_file_opened = self.open_root_file.name
        current_output_name = output.name
        root_node_name = happydoclib.path.join( self._docset.getOutputBaseDirectory(),
                                               self.getRootNodeName())
        if first_file_opened == current_output_name:
            root_location = self.getRootNodeName()
            #print '**SAME'
        else:
            root_location = happydoclib.path.computeRelativeHTMLLink(
                current_output_name,
                root_node_name,
                self._docset.getOutputBaseDirectory()
                )
        return root_location


    def htmlHeader(self, title, subtitle, titleBg, titleFg, output):
        """Output a standard HTML header used by all output files.

        Parameters

            'title' -- title of the document

            'output' -- destination for written output

            'titleBg' -- background color for the title bar

            'titleFg' -- foreground color for text in the title bar

        """
        if not subtitle:
            subtitle = '&nbsp;'
        #
        # Determine where the root node is relative to the last
        # file opened.
        #
        root_location = self.getRootLocation(output)
            #print '**DIFFERENT'
        #
        # Put together parts of the header
        #
        info = {
            'bgcolor':self._page_bgcolor,
            'title':title,
            'subtitle':subtitle,
            'title_bg':titleBg,
            'title_fg':titleFg,
            'root':root_location,
            }
        
        self.writeHTML('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
          "http://www.w3.org/TR/html40/loose.dtd">

<html>
         
  <head>
    <title>%(title)s</title>
  </head>

  <body bgcolor="%(bgcolor)s">

        <p><i><a href="%(root)s">Table of Contents</a></i></p>
        
        <table border="0" cellpadding="5" cellspacing="0" width="100%%">
        <tr>
            <th rowspan="2"
                valign="top"
                align="left"
                width="10%%"
                bgcolor="%(title_bg)s"><font color="%(title_fg)s">%(title)s</font>
            </th>
            <th bgcolor="%(title_bg)s"
                width="90%%"
                align="right"><font color="%(title_fg)s">%(subtitle)s</font>
            </th>
        </tr>
        <tr>
        <td>
        ''' % info, output)
        self.comment('html header', output)
        return
        

    def htmlFooter(self, output):
        "Output a standard HTML footer used by all 'output' files."
        if self._date_stamp_files:
            date_str = 'on %s' % self._update_time
        else:
            date_str = ''
        info = {
            'app_version':happydoclib.cvsProductVersion(),
            'date_str':date_str,
            'root':self.getRootLocation(output),
            }
        
        self.comment('html footer', output)
        self.comment('section header %s' % str(self._section_header_counter), output)
        self.comment('section level %s' % str(self._section_level_counter), output)
        
        self.writeHTML('''
        </td>
        </tr>
        </table>

        <hr>

        <p><i><a href="%(root)s">Table of Contents</a></i></p>

        <font size="-2"><i>This document was automatically generated
        %(date_str)s by
        <a href="http://happydoc.sourceforge.net">HappyDoc</a> version
        %(app_version)s</i></font>
        
        </body>
        </html>
        ''' % info, output)
        return

    def getRootNodeName(self):
        "Returns the name of the root node for documentation of this type."
        happydoclib.TRACE.into('HTMLFileFormatter', 'getRootNodeName')
        if self.getFilenamePrefix():
            root_node_name = '%sindex.html' % self.getFilenamePrefix()
        else:
            root_node_name = 'index.html'
        return happydoclib.TRACE.outof(root_node_name)

    ##
    ## HappyFormatterBase implementation
    ##

    def indent(self, output):
        "Begin an indented section."
        self.writeHTML('<ul>\n', output)
        return

    def dedent(self, output):
        "End an indented section."
        self.writeHTML('</ul>\n', output)
        return

    def writeText(self, text, output, textFormat, quote=1):
        """Format and write the 'text' to the 'output'.

        Arguments:

          'text' -- String to be written.

          'output' -- Stream to which 'text' should be written.

          'textFormat' -- String identifying the format of 'text' so
          the formatter can use a docstring converter to convert the
          body of 'text' to the appropriate output format.

          'quote=1' -- Boolean option to control whether the text
          should be quoted to escape special characters.

        """
        if not text:
            return
        text = self._unquoteString(text)
        #
        # Get a text converter
        #
        converter_factory = happydoclib.docstring.getConverterFactory(textFormat)
        converter = converter_factory()
        #
        # Do we need to quote the text?
        #
        if self._html_quote_text and quote:
            text = converter.quote(text, 'html')
        #
        # Convert and write the text.
        #
        html = converter.convert(text, 'html', level=3)
        self.writeHTML(html, output)
        return

    def writeHTML(self, text, output):
        "Remove extra white space in HTML before outputting."
        if self._compact_html:
            compact_text = string.join( filter( None,
                                                map( string.strip,
                                                     string.split( text,
                                                                   '\n'
                                                                   )
                                                     )
                                                ),
                                        '\n'
                                        )
            self.writeRaw(compact_text, output)
        else:
            self.writeRaw(text, output)
        return

    def formatCode(self, text, textFormat):
        "Format 'text' as source code and return the new string."
        converter_factory = happydoclib.docstring.getConverterFactory(textFormat)
        converter = converter_factory()
        formatted_text = '<font color="%s"><pre>\n%s\n</pre></font>\n' % \
                         (self._code_fgcolor,
                          converter.quote(text, 'html')
                          )
        return formatted_text

    def formatKeyword(self, text):
        "Format 'text' as a keyword and return the new string."
        formatted_text = '<b>%s</b>' % text
        return formatted_text

    def writeCode(self, text, textFormat, output):
        "Format and write the 'text' to 'output' as source code."
        if not text:
            return
        self.writeRaw(self.formatCode(text, textFormat), output)
        return

    def listHeader(self, output, title=None, allowMultiColumn=1):
        """Output 'title' as a heading for a list.  If 'allowMultiColumn' is
        true, set up the list to have more than one column.
        """
        if title:
            self.writeHTML('<h4>%s</h4>\n' % title, output)
        self.writeHTML('\n', output)
        self._pushListContext(allowMultiColumn)
        return

    def listItem(self, output, text):
        "Format and output the 'text' as a list element."
        if self.current_list_context is not None:
            self.current_list_context.append(text)
        else:
            self.writeHTML('%s<br>\n' % text, output)
        return

    def _writeListItems(self, items, output):
        "Format and output the 'items' as list elements."
        #
        # Determine the geometry of the list
        # (number of columns and rows)
        #
        num_items = len(items)
        if num_items < 10:
            num_cols = 1
            num_rows = num_items
        else:
            if num_items < 20:
                num_cols = 2
            else:
                num_cols = 3
            num_rows = (num_items / num_cols) + (num_items % num_cols)
            
        #
        # Output the list
        #
        if num_cols == 1:
            for item in self.current_list_context:
                self.writeHTML('%s<br>\n' % item, output)
        else:
            self.comment('start list', output)
            self.writeHTML('''
            <table border="0" cellspacing="2" cellpadding="2" width="100%">
              <tr>
            ''', output)
            
            for col in range(num_cols):
                self.writeHTML('<td align="LEFT" valign="TOP">\n', output)
                base_item = col * num_rows
                for item_no in range(base_item, base_item + num_rows):
                    try:
                        self.writeHTML('%s<br>\n' % items[item_no], output)
                    except IndexError:
                        break
                self.writeHTML('</td>\n', output)

            self.writeHTML('</tr>', output)
            self.writeHTML('''
            </table>
            ''', output)
            self.comment('list end', output)
        return
    
    def listFooter(self, output):
        "Write the closing footer for a list to the 'output'."
        if self.current_list_context:
            self._writeListItems(self.current_list_context, output)
        self.writeHTML('\n', output)
        self._popListContext()
        return

    def descriptiveListHeader(self, output, title):
        "Write the 'title' as the heading for a descriptive list to the 'output'."
        self.writeRaw('\n', output)
        self.comment('descriptive list header', output)
        if title:
            self.writeHTML('<h4>%s</h4>\n' % title, output)
        self.writeHTML('<table border="0" cellpadding="3" cellspacing="0">\n', output)
        return

    def descriptiveListItem(self, output, item, description, descriptionFormat):
        "Format and write the 'item' and 'description' for a descriptive list to the 'output'."
        self.writeHTML('<tr><td valign="top" align="left"><p>%s</p></td>' % item,
                      output)
        self.writeHTML('<td valign="top" align="left">', output)
        self.writeText(description, output, descriptionFormat)
        self.writeHTML('</td></tr>\n', output)
        return

    def descriptiveListFooter(self, output):
        "Write the closing footer for a descriptive list to the 'output'."
        self.writeHTML('</table>\n', output)
        self.comment('descriptive list footer', output)
        return

    def genericSectionHeader(self, output, title1, title2, anchor=None):
        """Output a standard nested table chunk which represents a section header.

        The output looks something like this::

            |--------|---------------------------|
            | title1 | title2                    |
            |        |---------------------------|
            |        | section text goes here
            |--------|

        Parameters

            'output' -- destination for written output

            'title1' -- title to be placed in left column

            'title2' -- title to be placed on top of right column

            'anchor' -- optional, anchor to which a reference can point
            to find this section

        """
        if title1 is None:
            title1 = ''
        if title2 is None:
            title2 = ''
        bgcolor = '#cccccc'
        fgcolor = '#000000'
        self._section_header_counter = self._section_header_counter + 1
        self._section_header_counters[self._section_level_counter] = self._section_header_counter
        info = {
            'bgcolor':self._l2_bgcolor,
            'fgcolor':self._l2_fgcolor,
            'title1':title1,
            'title2':title2,
            'anchor':anchor,
            }
        self.comment('section %d:%d (header)' % (self._section_level_counter,
                                                 self._section_header_counter),
                     output)
        self.writeHTML('''
        <tr>
            <th bgcolor="%(bgcolor)s"
                rowspan="2"
                valign="top"
                align="left"
                width="20%%"
                >
                <font color="%(fgcolor)s">
                  <a name="%(anchor)s">%(title1)s</a>&nbsp;
                </font>
            </th>
            <th bgcolor="%(bgcolor)s"
                valign="top"
                align="left"
                width="80%%"
                >
                <font color="%(fgcolor)s">%(title2)s&nbsp;</font>
            </th>
        </tr>
        <tr>
        <td>
        ''' % info, output)
        self.comment('section header', output)
        return

    def genericSectionFooter(self, output):
        "Write a general purpose section closing footer to the 'output'."
        self.comment('section %d:%d (footer)' % (self._section_level_counter,
                                                 self._section_header_counter),
                     output)
        self.writeHTML('</td></tr>\n', output)
        self.comment('section footer', output)
        self._section_header_counter = self._section_header_counter - 1
        self._section_header_counters[self._section_level_counter] = self._section_header_counter
        return

    def sectionHeader(self, output, title):
        "Write a general purpose section openning title to the 'output'."
        self.genericSectionHeader( output, title, None, title )
        return
        
    def sectionFooter(self, output):
        "Write a general purpose section closing footer to the 'output'."
        self.genericSectionFooter( output )
        return

    def itemHeader(self, output, infoObject):
        "Write a section openning header for an 'infoObject' to the 'output'."
        name = infoObject.getName()
        self.genericSectionHeader( output, None, name, name )
        return

    def itemFooter(self, output):
        "Write a section closing footer to the 'output'."
        self.genericSectionFooter( output )
        return
        
    def dividingLine(self, output, fill='-'):
        "Write a sectional dividing line made up of repeated 'fill' characters to the 'output'."
        output.write('<hr>\n')
        return

    def comment(self, text, output):
        """Output text as a comment."""
        if self.debug: self.writeHTML('<!-- %s -->\n' % text, output)
        return


class HTMLTableFormatterUT(happydoclib.StreamFlushTest.StreamFlushTest):


    def testReferences(self):
        filenames = [ os.path.join(os.curdir, 'happydoclib', 'CommandLineApp.py') ]
        import happydoclib.parseinfo
        import happydoclib.happydocset
        docset = happydoclib.happydocset.DocSet(
            formatterFactory=HTMLTableFormatter,
            parserFunc=happydoclib.parseinfo.getDocs,
            defaultParserConfigValues={'docStringFormat':'StructuredText'},
            inputModuleNames=filenames,
            outputBaseDirectory=self.output_dir,
            )
        cla = docset[0]
        formatter = docset._formatter
        reference = formatter.getNamedReference( cla, 'CommandLineApp', 'index.html' )
        expected_reference = '<a href="CommandLineApp.html#CommandLineApp">CommandLineApp</a>'
        assert reference == expected_reference, 'Got reference "%s" instead of "%s"' % \
               (reference, expected_reference)
        return

    def testFixReferencesWindows(self):
        filenames = [ os.path.join(os.curdir, 'happydoclib', 'CommandLineApp.py') ]
        import happydoclib.parseinfo
        import happydoclib.happydocset
        docset = happydoclib.happydocset.DocSet(
            formatterFactory=HTMLTableFormatter,
            parserFunc=happydoclib.parseinfo.getDocs,
            defaultParserConfigValues={'docStringFormat':'StructuredText'},
            inputModuleNames=filenames,
            outputBaseDirectory=self.output_dir,
            )
        cla = docset[0]
        formatter = docset._formatter

        input = 'http:\\\\full\\url\\path\\index.html'
        expected = 'http://full/url/path/index.html'
        actual = formatter._fixReference(input, sep='\\')
        assert expected == actual, \
               'Fixing Windows URL failed (%s, %s)' % (expected, actual)
        return

    def testFixReferencesMacOS(self):
        filenames = [ os.path.join(os.curdir, 'happydoclib', 'CommandLineApp.py') ]
        import happydoclib.parseinfo
        import happydoclib.happydocset
        docset = happydoclib.happydocset.DocSet(
            formatterFactory=HTMLTableFormatter,
            parserFunc=happydoclib.parseinfo.getDocs,
            defaultParserConfigValues={'docStringFormat':'StructuredText'},
            inputModuleNames=filenames,
            outputBaseDirectory=self.output_dir,
            )
        cla = docset[0]
        formatter = docset._formatter

        input = 'http:full:url:path:index.html'
        expected = 'http://full/url/path/index.html'
        actual = formatter._fixReference(input, sep=':')
        assert expected == actual, \
               'Fixing MacOS URL failed (%s, %s)' % (expected, actual)
        return
    
if __name__ == '__main__':
    for fro, to in (
        ('index.html', 'index.html'),
        ('HappyDoc/CommandLineApp.py.html', 'index.html'),
        ('HappyDoc/CommandLineApp.py_CommandLineApp.html', 'index.html'),
        ('HappyDoc/CommandLineApp.py_CommandLineApp.html',
         'HappyDoc/CommandLineApp.py.html'),
        ('/home/hellmann/devel/HappyDoc/doc/HappyDoc/ts_regex.py_compile.html',
         '/home/hellmann/devel/HappyDoc/doc/index.html'),
        
        ):
        #print 'FROM: ', fro
        #print 'TO  : ', to
        #print 'LINK: ', path.computeRelativeHTMLLink(fro, to)
        happydoclib.path.computeRelativeHTMLLink(fro, to)
        #print
