#!/usr/bin/env python
#
# $Id: formatter_DocBook.py,v 1.1 2001/10/24 21:27:35 doughellmann Exp $
#
# Copyright 2001 Balazs Scheidler
#
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of Balazs
# Scheidler not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# BALAZS SCHEIDLER DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT SHALL BALAZS SCHEIDLER BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

"""Formatter which produces simple DocBook SGML.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: formatter_DocBook.py,v $',
    'rcs_id'       : '$Id: formatter_DocBook.py,v 1.1 2001/10/24 21:27:35 doughellmann Exp $',
    'creator'      : 'Balazs Scheidler <bazsi@balabit.hu>',
    'project'      : 'HappyDoc',
    'created'      : 'Sat, 03-Feb-2001 12:53:37 EST',

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
        'name':'SGMLDocBook',
        'factory':DocBookFormatter,
        }


class DocBookFormatter(happydoclib.formatter.fileformatterbase.FileBasedFormatter):
    '''Formatter which produces simple DocBook SGML.'''

    def __init__(self, docSet, **configuration):
        self._section_level_counter = 1
        self.debug = 0
        apply(happydoclib.formatter.fileformatterbase.FileBasedFormatter.__init__,
              (self, docSet),
              configuration)
        return
    
    def openOutput(self, name, title1, title2=""):
        """Write the formatting for a file header to the open file."""
        f = happydoclib.formatter.fileformatterbase.FileBasedFormatter.openOutput(
            self,
            name,
            title1)
        self.fileHeader(title1, title2, f)
        return f

    def closeOutput(self, output):
        "Close the 'output' handle."
        self.fileFooter(output)
        output.close()
        return

    def fileHeader(self, title1, title2, output):
        self.comment('file_header', output)
        return

    def fileFooter(self, output):
        self.comment('file_footer', output)
        return

    # string handling

    def writeText(self, text, output, textFormat, quote=0):
        """Format and write the 'text' to the 'output'.

        Arguments:

          'text' -- String to be written.

          'output' -- Stream to which 'text' should be written.

          'textFormat' -- Ignored.

          'quote=1' -- Boolean option to control whether the text
          should be quoted to escape special characters.

        """
        text = self._unquoteString(text)
        self.writeRaw(text, output)
        return

    def formatCode(self, text, textFormat):
        "Format 'text' as source code and return the new string."
        if textFormat in ('HTML', 'StructuredText', 'PlainText'):
            formatted_text = '<programlisting>\n%s\n</programlisting>\n' % text
        else:
            raise ValueError('DocBook formatter cannot handle sourcde code as %s' % textFormat)
        return formatted_text

    def formatKeyword(self, text):
        "Format 'text' as a keyword and return the new string."
        formatted_text = '<literal>%s</literal>' % text
        return formatted_text

    # structure handling


    # simple lists
    def listHeader(self, output, title=None, allowMultiColumn=1):
        """Output 'title' as a heading for a list.  If 'allowMultiColumn' is
        true, set up the list to have more than one column.
        """
        self.writeRaw('<formalpara>\n<title>%s</title>\n<para><itemizedlist>\n' % title, output)
        return

    def listItem(self, output, text):
        "Format and output the 'text' as a list element."
        self.writeRaw('<listitem><para>%s</para></listitem>\n' % text, output)
        return

    def listFooter(self, output):
        "Write the closing footer for a list to the 'output'."
        self.writeRaw('\n</itemizedlist></para></formalpara>', output)
        return

    # descriptive lists
    def descriptiveListHeader(self, output, title):
        "Write the 'title' as the heading for a descriptive list to the 'output'."
        self.writeRaw('<formalpara><title>%s</title>\n<para><variablelist>\n' \
                      % title, output)
        self.comment('descriptive list header', output)
        return

    def descriptiveListItem(self, output, item, description, descriptionFormat):
        "Format and write the 'item' and 'description' for a descriptive list to the 'output'."
        self.writeRaw('<varlistitem><term>%s</term><listitem><para>' % item,
                      output)
        self.writeText(description, output, descriptionFormat)
        self.writeRaw('</para></listitem></varlistitem>\n', output)
        return

    def descriptiveListFooter(self, output):
        "Write the closing footer for a descriptive list to the 'output'."
        self.writeRaw('</variablelist></para></formalpara>\n', output)
        return

    # headers

    def sectionHeader(self, output, title):
        "Write a general purpose section openning title to the 'output'."
        self.writeRaw('<sect%d>\n<title>%s</title>' \
                      % (self._section_level_counter, title),
                      output)
        return
       
    def sectionFooter(self, output):
        "Write a general purpose section closing footer to the 'output'."
        self.writeRaw('</sect%d>' % self._section_level_counter, output)
        return

    def itemHeader(self, output, infoObject):
        "Write a section openning header for an 'infoObject' to the 'output'."
        name = infoObject.getName()
        self.sectionHeader(output, name)
        return

    def itemFooter(self, output):
        "Write a section closing footer to the 'output'."
        self.sectionFooter(output)
        return

    def pushSectionLevel(self, output):
        self._section_level_counter = self._section_level_counter + 1
        return

    def popSectionLevel(self, output):
        self._section_level_counter = self._section_level_counter - 1
        return

    # misc

    def dividingLine(self, output, fill='-'):
        "Write a sectional dividing line made up of repeated 'fill' characters to the 'output'."
        #output.write('<hr>\n')
        return

    def comment(self, text, output):
        """Output text as a comment."""
        if self.debug: self.writeRaw('<!-- %s -->\n' % text, output)
        return

    def indent(self, output):
        self.comment('indent', output)
        return

    def dedent(self, output):
        self.comment('dedent', output)
        return


    # refererences

    def getReference(self, infoSource, relativeSource, name=None):
        """Returns a reference to the 'infoSource' from 'relativeSource'.
        """
        #print '\ngetReference(', infoSource, ',', relativeSource, ')'
        #link = computeRelativeLink(relativeSource,
        #                           self.getOutputNameForObject(infoSource)
        #                           )
        if not name:
            name = self.getNameForInfoSource( infoSource )
        info = {
            'name':name,
            }
        ref = '<xref linkend="%(name)s">' % info
        return ref

    def getNamedReference(self, infoSource, name, relativeSource):
        info = {
            'name':infoSource.getName(),
            }
        ref = '<xref linkend="%(name)s">' % info
        return ref

    def getInternalReference(self, infoSource):
        """Returns a reference to 'infoSource' within the current document.
        """
        info = {
            'name':infoSource.getName(),
            }
        ref = '<xref linkend="%(name)s">' % info
        return ref
   
    def getPythonReference(self, moduleName):
        """Returns a reference to 'moduleName' documentation on the
       
        "Python.org":http://www.python.org documentation site.
        """
        if moduleName in self.sys_modules:
            return '<ulink url="http://www.python.org/doc/current/lib/module-%(moduleName)s.html">%(moduleName)s</ulink>' % locals()
        else:
            return moduleName

    def getFilenameExtension(self):
        "Returns the extension for creating output files."
        return 'sgml'

    def getRootNodeName(self):
        return 'book.sgml'
