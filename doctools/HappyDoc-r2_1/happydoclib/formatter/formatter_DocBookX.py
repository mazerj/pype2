#
# Structured docset and formatters for HappyDoc.
# 
# Copyright (C) 2001 by wrobell <wrobell@ite.pl>.
# 
# This software comes with ABSOLUTELY NO WARRANTY.
# This is free software, and you are welcome to redistribute it
# under certain conditions. For details see COPYING file.
#

"""XML DocBook formatter.

   All files contains XML and doctype declaration, so
   every document is a valid XML file. This way, it is possible
   to use every file separately.

   Every index file indicates a chapter.
   Every module or class document indicates section.

   It was tested with libxml 2.4.10 and libxslt 1.0.6 (http://xmlsoft.org).
   Use your favourite XML and XSLT processors with XInclude support.

   Example:

       happydoc -T mstruct -F docbookx my_module formatter_encoding=utf-8

       xsltproc --xinclude my_custom_docbook_to_html.xsl my_module/index.docb > my_module.html
"""

import os.path
import string

from types import *

import happydoclib.formatter.xmlformatterbase

from happydoclib.docset.mstruct_const import *


__rcs_info__ = {
    # creation Information
    'module_name': '$RCSfile: formatter_DocBookX.py,v $',
    'creator':     'wrobell <wrobell@ite.pl>',
    'project':     'HappyDoc',
    'created':     '24-08-2001',

    # current information
    'author':      '$Author: wrobell $',
    'version':     '$Revision: 1.5 $',
    'date':        '$Date: 2002/02/07 01:21:03 $',
}


def entryPoint():
    "Return information about this module to the dynamic loader."
    return {
        'name':    'docbookx',
        'factory':  XMLDocBookFormatter,
    }


class XMLDocBookFormatter(happydoclib.formatter.xmlformatterbase.XMLFormatter):
    """XML DocBook formatter.
    """

    def __init__(self, docset, title='', encoding='iso-8859-1', index_file_name='index', \
        file_name_ext='xml', **conf):

        """Initialize the XMLDocBookFormatter.

        Parameters

            'docset' -- the DocSet instance containing global cross-reference
                      information

             'title' -- documentation title

             'encoding' -- documentation file encoding (default 'iso-8859-1')

             'index_file_name' -- package index filename (default 'index')

             'file_name_ext' -- documentation filename extension (default 'xml')
            
            '**conf' -- additional, optional, configuration values

        """
        
        apply(happydoclib.formatter.xmlformatterbase.XMLFormatter.__init__, \
            (self, docset, encoding, index_file_name, file_name_ext), conf)
        self.file_name_ext='docb'
        self.title=title

        self.doctypes={
            INDEX_FILE:  'chapter',
            MODULE_FILE: 'section',
            CLASS_FILE:  'section',
        }


    #
    # XMLFormatter class abstract methods implementation.
    #

    def processRoot(self, output, stage, rtype):
        """XMLFormatter class abstract method implementation.
        """
        if stage==START:
            self.writeRaw('<?xml version="1.0" encoding="%s"?>\n' % self.getEncoding(), output)
            self.writeRaw('<!DOCTYPE %s PUBLIC "-//OASIS//DTD DocBook XML V4.1.2//EN" "file:///usr/share/sgml/docbook/xml-dtd-4.1.2/docbookx.dtd">\n' % self.doctypes[rtype], output)

        if rtype==INDEX_FILE:
            if stage==START:
                self.tag('chapter', output, {'xmlns:xi': 'http://www.w3.org/2001/XInclude'})
                if self.title:
                    self.writeTaggedText('title', self.title, output)
            elif stage==END:
                self.endTag('chapter', output)


    def processPackage(self, info, output, stage):
        """XMLFormatter class abstract method implementation.
        """
        pass


    def processModule(self, info, output, stage):
        """XMLFormatter class abstract method implementation.
        """
        if stage==START:
            self.tag('section', output, {'xmlns:xi': 'http://www.w3.org/2001/XInclude'})
            name=info.getFullyQualifiedName()
            name=string.replace(name, '/', '.')[:-3]
            self.writeTaggedText('title', 'Module %s' % name, output)
        elif stage==END:
            self.endTag('section', output)


    def processDocString(self, info, output, stage):
        """XMLFormatter class abstract method implementation.
        """
        pass


    def processImport(self, iinfo, minfo, output, stage):
        """XMLFormatter class abstract method implementation.
        """
        if stage==PRE:
            self.tag('para', output)
            self.writeText('Imported modules and (or) symbols:', output)
            self.tag('itemizedlist', output)
        elif stage==START:
            self.tag('listitem', output)
            self.tag('para', output)
            self.writeText(iinfo, output)
        elif stage==END:
            self.endTag('para', output)
            self.endTag('listitem', output)
        elif stage==POST:
            self.endTag('itemizedlist', output)
            self.endTag('para', output)


    def processImportSymbol(self, info, output, stage):
        """XMLFormatter class abstract method implementation.
        """
        if stage==START:
            if len(info)==1 and info[0]=='*':
                self.writeText('- all symbols', output)
            else:
                self.writeText('- %s' % string.join(info, ','), output)


    def processClass(self, info, output, stage):
        """XMLFormatter class abstract method implementation.
        """
        if stage==START:
            self.tag('section', output)
            self.writeTaggedText('title', 'Class %s' % info.getName(), output)
        elif stage==END:
            self.endTag('section', output)


    def processException(self, einfo, output, stage):
        """XMLFormatter class abstract method implementation.
        """
        if stage==PRE:
            self.tag('para', output)
            self.writeText('Raised exceptions:', output)
            self.tag('itemizedlist', output)

        elif stage==START:
            self.tag('listitem', output)

            if type(einfo)==StringType: name=einfo
            else: name=einfo.getName()
            self.writeTaggedText('para', name, output)

            self.endTag('listitem', output)

        elif stage==POST:
            self.endTag('itemizedlist', output)
            self.endTag('para', output)


    def processFunction(self, info, output, stage):
        """XMLFormatter class abstract method implementation.
        """
        if stage==START:
            self.tag('funcsynopsis', output)
            self.tag('funcprototype', output)
            self.tag('funcdef', output)
            self.writeTaggedText('function', info.getName(), output)
        elif stage==END:
            self.endTag('funcdef', output)
            self.endTag('funcprototype', output)
            self.endTag('funcsynopsis', output)


    def processClassBase(self, info, cinfo, output, stage):
        """XMLFormatter class abstract method implementation.
        """
        if stage==PRE:
            self.tag('para', output)
            self.writeText('Derives from:', output)
            self.tag('itemizedlist', output)
        elif stage==START:
            self.tag('listitem', output)
            self.tag('para', output)
            self.writeText(cinfo, output)
        elif stage==END:
            self.endTag('para', output)
            self.endTag('listitem', output)
        elif stage==POST:
            self.endTag('itemizedlist', output)
            self.endTag('para', output)


    def processParam(self, info, output, stage):
        """XMLFormatter class abstract method implementation.
        """
        if stage==START:
            name, finfo, default_specified, default_value, default_value_type=info
            self.tag('paramdef', output)

            if default_specified:
                self.writeTaggedText('parameter', '%s=%s' % (name, default_value), output)
            else:
                self.writeTaggedText('parameter', name, output)
        elif stage==END:
            self.endTag('paramdef', output)


    def classIndex(self, class_info, output):
        """XMLFormatter class abstract method implementation.
        """
        name=os.path.basename(self.getOutputNameForObject(class_info))
        self.emptyTag('xi:include', output, { 'href': name })


    def moduleIndex(self, module_info, output):
        """XMLFormatter class abstract method implementation.
        """
        name=os.path.basename(self.getOutputNameForObject(module_info))
        self.emptyTag('xi:include', output, { 'href': name })


    def packageIndex(self, package_info, output):
        """XMLFormatter class abstract method implementation.
        """
        if package_info.getName():
            pname=package_info.getName()
        else:
            pname=package_info.getFilename()

        name='%s/%s#%s' \
            % (pname, self.getIndexFileName(), 'xpointer(/chapter/section)')

        self.emptyTag('xi:include', output, { 'href': name })
