#
# Structured docset and formatters for HappyDoc.
# 
# Copyright (C) 2001 by wrobell <wrobell@ite.pl>.
# 
# This software comes with ABSOLUTELY NO WARRANTY.
# This is free software, and you are welcome to redistribute it
# under certain conditions. For details see COPYING file.
#

"""Xpydoc formatter.

"""

import happydoclib.formatter.xmlformatterbase

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name': '$RCSfile: formatter_XPyDoc.py,v $',
    'creator':     'wrobell <wrobell@ite.pl>',
    'project':     'HappyDoc',
    'created':     '24-08-2001',
    #
    #  Current Information
    #
    'author':      '$Author: doughellmann $',
    'version':     '$Revision: 1.1 $',
    'date':        '$Date: 2001/10/24 21:27:35 $',
}


def entryPoint():
    "Return information about this module to the dynamic loader."
    return {
        'name':    'xpydoc',
        'factory':  XPyDocFormatter,
    }


class XPyDocFormatter(happydoclib.formatter.xmlformatterbase.XMLFormatter):
    """Xpydoc formatter.

    """

    def __init__(self, docSet, **configuration):
        """Initialize the XMLStructFormatter.

        Parameters

            'docSet' -- the DocSet instance containing global cross-reference
                      information
            
            '**configuration' -- additional, optional, configuration values

        """
        
        apply(hdformatter_xml.XMLFormatter.__init__, (self, docSet), configuration)
        self.filename_ext='xpd'


    def rootTag(self, output, end=0):
        if end:
            self.endTag('xpydoc', output)
        else:
            self.tag('xpydoc', output)


    def moduleTag(self, info, output, end=0):
        if end:
            self.endTag('module', output)
        else:
            self.tag('module', output, { 'name': info.getName() })


    def descriptionTag(self, output, end=0):
        if end:
            self.endTag('description', output)
        else:
            self.tag('description', output)


    def importTag(self, module, output, end=0):
        if end:
            self.endTag('import', output)
        else:
            self.tag('import', output, { 'module': module })


    def symbolTag(self, output, end=0):
        if end:
            self.endTag('symbol', output)
        else:
            self.tag('symbol', output)


    def classTag(self, info, output, end=0):
        if end:
            self.endTag('class', output)
        else:
            self.tag('class', output, { 'name': info.getName() })


    def exceptionTag(self, finfo, name, output, end=0):
        if end:
            self.endTag('exception', output)
        else:
            self.tag('exception', output, { 'name': name })


    def functionTag(self, info, output, end=0):
        if end:
            self.endTag('function', output)
        else:
            self.tag('function', output, { 'name': info.getName() })


    def baseTag(self, info, name, output, end=0):
        if end: return

        self.emptyTag('base', output, { 'class': name })


    def paramTag(self, info, name, output, end=0):
        if end: return

        default_specified, default_value, default_value_type=info
        attr={ 'name': name }

        if default_specified:
            attr['default']=default_value

        self.emptyTag('param', output, attrs=attr)


    def classIndex(self, class_info, output, end=0):
        self.emptyTag('class', output, { 'name': class_info.getName() })


    def moduleIndex(self, module_info, output, end=0):
        self.emptyTag('module', output, { 'name': module_info.getName() })


    def getEncoding(self):
        return self.encoding
