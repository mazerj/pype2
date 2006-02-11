#
# Structured docset and formatters for HappyDoc.
# 
# Copyright (C) 2001 by wrobell <wrobell@ite.pl>.
# 
# This software comes with ABSOLUTELY NO WARRANTY.
# This is free software, and you are welcome to redistribute it
# under certain conditions. For details see COPYING file.
#

"""Contains abstract class for formatters which can output XML.

It is created for structured docsets.

"""

import string

import happydoclib.formatter.fileformatterbase

__rcs_info__={
    # creation information
    'module_name': '$RCSfile: xmlformatterbase.py,v $',
    'creator':     'wrobell <wrobell@ite.pl>',
    'project':     'HappyDoc',
    'created':     '24-08-2001',

    # current information
    'author':      '$Author: wrobell $',
    'version':     '$Revision: 1.3 $',
    'date':        '$Date: 2002/02/07 01:19:11 $',
}


class XMLFormatter(happydoclib.formatter.fileformatterbase.FileBasedFormatter):
    """Base abstract class for formatters which can output XML.
    """

    def __init__(self, docset, encoding='iso-8859-1', index_file_name='index', \
        file_name_ext='xml', **conf):

        """Initialize the XMLStructFormatter.

        Arguments

            'docset' -- the DocSet instance containing global cross-reference
                      information

             'encoding' -- documentation file encoding (default 'iso-8859-1')

             'index_file_name' -- package index filename (default 'index')

             'file_name_ext' -- documentation filename extension (default 'xml')
            
            '**conf' -- additional, optional configuration values

        """

        self.debug=1
        self.indent_level=0
        self.indent_str='  '

        self.file_name_ext=file_name_ext
        self.index_file_name=index_file_name
        self.encoding=encoding

        self.getRootNodeName=self.getIndexFileName
        self.getFilenameExtension=self.getFileNameExtension
        
        # initialize the base class
        apply(happydoclib.formatter.fileformatterbase.FileBasedFormatter.__init__,
              (self, docset),
              conf)


    def getEncoding(self):
        """Returns XML file encoding. File encoding can be specified with
        'encoding' formatter parameter.
        """
        return self.encoding


    def getIndexFileName(self):
        """Returns package index file name. This file should contain
        all documentation files in current directory. Default filename
        extension is appended to the end of the name. The base name
        can be specified with 'index_name' formatter parameter.
        """
        return self.index_file_name+'.'+self.getFileNameExtension()


    def getFileNameExtension(self):
        """Returns filename extension. It can be specified with 'file_name_ext'
        formatter parameter.
        """
        return self.file_name_ext


    def comment(self, text, output):
        """Outputs comment to the output file.
        
        Arguments
        
            'text' -- comment text

            'output' -- output file object    
        """
        if self.debug: self.writeRaw('<!-- %s -->\n' % text, output)


    def tag(self, name, output, attrs={}):
        """This method outputs opening tag with attributes. Method 'endTag' should
        be used to close the tag.

        Arguments

            'name' -- tag name

            'output' -- output file object
            
            'attrs' -- tag attributes; every item { key: 'value' } is rendered as 'key="value"'
        """
        attr_str=self.getAttrs(attrs)
        if attr_str:
            self.writeRaw('%s<%s %s>\n' % (self.getIndent(), name, self.getAttrs(attrs)), output)
        else:
            self.writeRaw('%s<%s>\n' % (self.getIndent(), name), output)
        self.incIndent()


    def emptyTag(self, name, output, attrs={}):
        """Outputs empty tag.

        Arguments

            'name' -- tag name

            'output' -- output file object
            
            'attrs' -- tag attributes; every item { key: 'value' } is rendered as 'key="value"'
        """
        attr_str=self.getAttrs(attrs)
        if attr_str:
            self.writeRaw('%s<%s %s/>\n' % (self.getIndent(), name, attr_str), output)
        else:
            self.writeRaw('%s<%s/>\n' % (self.getIndent(), name), output)


    def endTag(self, name, output):
        """Outputs closing tag. Method 'tag' should be used to open the tag.

        Arguments

            'name' -- tag name

            'output' -- output file object
        """
        self.decIndent()
        self.writeRaw('%s</%s>\n' % (self.getIndent(), name), output)


    def writeTaggedText(self, tag, text, output):
        """Outputs text between opening and closing XML tags. For example

            self.writeTaggedText('tag', 'text', output)

        outputs

            <tag>text</tag>

        Arguments

            'tag' -- tag name
            
            'text' -- tagged text

            'output' -- output file object
        """
        self.tag(tag, output)
        self.writeText(text, output)
        self.endTag(tag, output)


    def getAttrs(self, attrs):
        """Converts Python dictionary into XML attributes string.
        For example

            {
                'attr1': 'val1',
                'attr2': 'val2',
                'attr3': 'val3',
            }

        is converted to the following string

            attr1="val1" attr2="val2" attr3="val3"

        Arguments
            
            'attrs' -- dictionary with XML attributes

        Returns attributes string.
        """
        return string.join(map(lambda attr_item: '%s="%s"' % attr_item, attrs.items()))


    def writeText(self, text, output, textFormat=None, quote=1):
        """Outputs text to XML file.

        Arguments

            'text' -- text to output

            'output' -- output file object

            'textFormat' -- String identifying the format of 'text' so
            the formatter can use a docstring converter to convert the
            body of 'text' to the appropriate output format.

            'quote=1' -- Boolean option to control whether the text
            should be quoted to escape special characters.
            
        """
        self.writeRaw(self.getIndent()+text+'\n', output)


    # abstract methods

    def processRoot(self, output, stage, rtype):
        """Method invoked by docset, when new file is opened. This method
        can be used to output XML declaration, DTD, etc.

        Arguments

            'output' -- output file object

            'stage' -- processing stage (one of: PRE, START, END, POST values)

            'rtype' -- file type (index, module or class file)
        """
    	self._requiredOfSubclass('processRoot')


    def processPackage(self, info, output, stage):
        """Method invoked by docset, when package is being processed.

        Arguments

            'info' -- package info object

            'output' -- output file object

            'stage' -- processing stage (one of: PRE, START, END, POST values)
        """
        self._requiredOfSubclass('processPackage')


    def processModule(self, info, output, stage):
        """Method invoked by docset, when module is being processed.

        Arguments

            'info' -- module info object

            'output' -- output file object

            'stage' -- processing stage (one of: PRE, START, END, POST values)
        """
    	self._requiredOfSubclass('processModule')


    def processDocString(self, info, output, stage):
        """Method invoked by docset, when docstring is being processed.

        Arguments

            'info' -- docstring owner (module, class, function, etc.) info object

            'output' -- output file object

            'stage' -- processing stage (one of: PRE, START, END, POST values)
        """
    	self._requiredOfSubclass('processDocString')


    def processImport(self, iinfo, minfo, output, stage):
        """Method invoked by docset, when import statement is being processed.

        Arguments

            'iinfo' -- imported module info object

            'minfo' -- info object of module, where import statement is declared

            'output' -- output file object

            'stage' -- processing stage (one of: PRE, START, END, POST values)
        """
    	self._requiredOfSubclass('processImport')


    def processImportSymbol(self, info, output, stage):
        """Method invoked by docset, when import symbol is being processed.

            'info' -- info object of imported symbol or string with symbol name

            'output' -- output file object

            'stage' -- processing stage (one of: PRE, START, END, POST values)
        """
    	self._requiredOfSubclass('processImportSymbol')


    def processClass(self, info, output, stage):
        """Method invoked by docset, when class is being processed.

            'info' -- class info object

            'output' -- output file object

            'stage' -- processing stage (one of: PRE, START, END, POST values)
        """
    	self._requiredOfSubclass('processClass')


    def processException(self, info, output, stage):
        """Method invoked by docset, when exception is being processed.

            'info' -- exception info object or string with exception name

            'output' -- output file object

            'stage' -- processing stage (one of: PRE, START, END, POST values)
        """
    	self._requiredOfSubclass('processException')


    def processFunction(self, info, output, stage):
        """Method invoked by docset, when function or class method is being processed.

            'info' -- function or class method info object

            'output' -- output file object

            'stage' -- processing stage (one of: PRE, START, END, POST values)
        """
    	self._requiredOfSubclass('processFunction')


    def processClassBase(self, info, cinfo, output, stage):
        """Method invoked by docset, when inherited class info of derived class is being processed.

            'info' -- base class info object

            'cinfo' -- derived class

            'output' -- output file object

            'stage' -- processing stage (one of: PRE, START, END, POST values)
        """
    	self._requiredOfSubclass('processClassBase')


    def processParam(self, info, output, stage):
        """Method invoked by docset, when function or class method parameter is being processed.

        Arguments

            'info' -- function or class method parameter info object

            'output' -- output file object

            'stage' -- processing stage (one of: PRE, START, END, POST values)
        """
    	self._requiredOfSubclass('processParam')


    def classIndex(self, info, output):
        """Method invoked by docset to process class index item.

        Arguments

            'info' -- class info object

            'output' -- output file object
        """
    	self._requiredOfSubclass('classIndex')


    def moduleIndex(self, info, output):
        """Method invoked by docset to process module index item.

        Arguments

            'info' -- module info object

            'output' -- output file object
        """
    	self._requiredOfSubclass('moduleIndex')


    def packageIndex(self, info, output):
        """Method invoked by docset to process package index item.

        Arguments

            'info' -- package info object

            'output' -- output file object
        """
    	self._requiredOfSubclass('packageIndex')




    # indentation is not supported yet...


    def incIndent(self):
        assert(self.indent_level>=0)
        self.indent_level+=1


    def decIndent(self):
        self.indent_level-=1
        assert(self.indent_level>=0)


    def getIndent(self):
        assert(self.indent_level>=0)
        assert(self.indent_str)
        #return self.indent_str*self.indent_level
        return ""
