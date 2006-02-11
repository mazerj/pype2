#
# Structured docset and formatters for HappyDoc.
# 
# This code is based on Doug Hellmann's docset from HappyDoc
# project.
#
# Copyright (C) 2001 by wrobell <wrobell@ite.pl>.
# 
# This software comes with ABSOLUTELY NO WARRANTY.
# This is free software, and you are welcome to redistribute it
# under certain conditions. For details see COPYING file.
#

"""Documentation set which writes output to multiple structured files.

This docset creates file for every module and defined class.

Documentation structure is rendered with formatter's *process* methods
(processClass, processModule, processImport, etc.).  There is special
method -- processRoot. It is invoked when new output is opened
or closed.

These all methods can be called in four different stages (element -- i.e.
class or module):
1. PRE -- before any of elements processing
2. START -- before an element processing
3. END -- after an element processing
4. POST -- after all element processing

Formatters can produce index of created by this docset files with packageIndex,
moduleIndex and classIndex methods.
"""

__rcs_info__ = {
    # creation information
    'module_name':'$RCSfile: docset_mstruct.py,v $',
    'creator':'wrobell <wrobell@ite.pl>',
    'project':'shd',
    'created':'24.08.2001',

    # current information
    'author':'$Author: doughellmann $',
    'version':'$Revision: 1.4 $',
    'date':'$Date: 2002/08/04 12:05:20 $',
    'locker':'$Locker:  $',
}


import happydoclib.happydocset
from happydoclib.docset.mstruct_const import *


def entryPoint():
    "Return info about this module to the HappyDoc dynamic loader."
    return { 
        'name':    'mstruct',
        'factory': MStructDocSet,
     }

#
# Do not use multiple lines in the class docstring, since it shows up as
# part of the generated help message for the app and multiple lines throws
# off the formatting.
#
class MStructDocSet(happydoclib.happydocset.DocSet):
    """Documentation set written to multiple structured files.

    Parameters

      *Adds no additional parameters not understood by DocSet.*
    
    """

    def __init__(self, **args):
        happydoclib.happydocset.DocSet.__init__(self, **args)


    def openOutput(self, name, title, subtitle, rtype=INDEX_FILE):
        """Opens output, where documentation will be written.

        Arguments

            'name' -- output file name

            'title' --  title of documentation file

            'subtitle' -- subtitle of documentation file

            'rtype' -- gives info whether index, module or class file will be opened

        Returns file object of opened documentation file.
        """
        output=happydoclib.happydocset.DocSet.openOutput(self, name, title, subtitle)
        self._formatter.processRoot(output, START, rtype)
        return output


    def closeOutput(self, output, rtype=INDEX_FILE):
        """Closes output, where documentation has been written.

        Arguments

            'output' -- file object of opened documentation file

            'rtype' -- gives info whether index, module or class file will be closed
        """
        self._formatter.processRoot(output, END, rtype)
        happydoclib.happydocset.DocSet.closeOutput(self, output)


    def write(self):
        "Write the documentation set to the output."
        self.statusMessage('Beginning to write...')

        # get the name of and open the docset index file
        self._index_file_name=self.getFullOutputNameForObject(None)
        self._index_file=self.openOutput(self._index_file_name, self._title, '', INDEX_FILE)

        # write the output
        self._writeModules()
        self._writePackages()

        # close things up
        self.closeOutput(self._index_file, INDEX_FILE)
        self.close()
        return


    def _writePackages(self):
        "Output documentation for all packages."

        self.statusMessage()
        self.statusMessage('Writing package documentation...')
        package_items=self._all_packages.items()
        package_items.sort()

        formatter=self._formatter
        output=self._index_file

        formatter.processPackage(None, output, PRE)
        for package_name, package in package_items:
            formatter.processPackage(package, output, START)
            formatter.packageIndex(package, output)
            package.write()
            formatter.processPackage(package, output, END)
        formatter.processPackage(None, output, POST)

    
    def _writeModules(self):
        "Output documentation for all modules."
        self.statusMessage()
        self.statusMessage('Writing module documentation...')
        module_names=self._all_modules.keys()
        module_names.sort()

        self._formatter.processModule(None, self._index_file, PRE)
        for module_name in module_names:
            self._writeModule(module_name)
        self._formatter.processModule(None, self._index_file, POST)

    
    def _writeModule(self, module_name):
        """Output the documentation for the named module.

        Arguments

            'module_name' -- name of the module
        """
        formatter=self._formatter
        module=self._all_modules[module_name]

        formatter.moduleIndex(module, self._index_file)
        
        output_name=self.getFullOutputNameForObject(module)
        output=self.openOutput(output_name, 'Module: %s' % module_name, module.getFilename(), MODULE_FILE)

        # start the module tag
        formatter.processModule(module, output, START)

        imported_modules=module.getImportData()
        if imported_modules:
            formatter.processImport(None, module, output, PRE)
            for name, symbols in imported_modules:
                formatter.processImport(name, module, output, START)
                if symbols:
                    formatter.processImportSymbol(symbols, output, START)
                    formatter.processImportSymbol(symbols, output, END)
                formatter.processImport(name, module, output, END)
            formatter.processImport(None, module, output, POST)

        # write the doc string
        formatter.processDocString(module, output, START)
        formatter.writeText(module.getDocString(), output)
        formatter.processDocString(module, output, END)

        # write the info for the classes in this module
        class_names=self._filterNames(module.getClassNames())

        if class_names:
            class_names.sort()

            formatter.processClass(None, output, PRE)
            for class_name in class_names:
                c=module.getClassInfo(class_name)
                formatter.classIndex(c, output)
                class_output_name=self.getFullOutputNameForObject(c)
                class_output=self.openOutput(class_output_name, 'Class: %s' % class_name, \
                    module.getFilename(), CLASS_FILE)
                self._writeClass(module, class_name, class_output)
                self.closeOutput(class_output, CLASS_FILE)
            formatter.processClass(None, output, POST)
            formatter.comment('END: Classes of module %s' % module_name, output)

        # finish module section
        formatter.processModule(module, output, END)
        self.closeOutput(output, MODULE_FILE)

    
    def _writeBaseClassNames(self, parent, cinfo, output, indent=0):
        """Output the base class hierarchy for the given class.

        Arguments
            
            'parent' -- info about class parent (module, class)

            'cinfo' -- class info

            'output' -- current output file object
        """
        base_classes=cinfo.getBaseClassNames()
        formatter=self._formatter
        if base_classes:
            formatter.processClassBase(cinfo, None, output, PRE)
            for name in base_classes:
                formatter.processClassBase(cinfo, name, output, START)
                formatter.processClassBase(cinfo, name, output, END)
            formatter.processClassBase(cinfo, None, output, POST)


    def _writeClass(self, parent, class_name, output):
        """Output the documentation for the class in the parent object.

        Arguments

            'parent' -- info about class parent (module, class)

            'class_name' -- name of the class

            'output' -- current output file object
        """
        class_info=parent.getClassInfo(class_name)
        formatter=self._formatter

        formatter.processClass(class_info, output, START)
        formatter.processDocString(class_info, output, START)
        formatter.writeText(class_info.getDocString(), output)
        formatter.processDocString(class_info, output, END)

        # base class hierarchy
        base_classes=class_info.getBaseClassNames()
        if base_classes:
            self._writeBaseClassNames(parent, class_info, output)

        # write the info for the methods of this class
        method_names=self._filterNames(class_info.getMethodNames())
        if method_names:
            method_names.sort()
            for method_name in method_names:
                self._writeFunction(method_name, class_info.getMethodInfo, output)

        formatter.processClass(class_info, output, END)


    def _writeFunction(self, function_name, getInfo, output):
        """Output the documentation for the function in the parent object.

        Arguments

            'function_name' -- the function name

            'getInfo' -- reference to method, which will return function info

            'output' -- current output file object
        """
        function=getInfo(function_name)
        formatter=self._formatter
        formatter.processFunction(function, output, START)

        # function signature
        self._formatter.processParam(None, output, PRE)
        for param in function.getParameterNames():
            info=(param, function)+function.getParameterInfo(param)
            self._formatter.processParam(info, output, START)
            self._formatter.processParam(info, output, END)
        self._formatter.processParam(None, output, POST)

        # exceptions
        exception_names=function.getExceptionNames()
        if len(exception_names)>0:
            exception_names.sort()
            formatter=self._formatter

            formatter.processException(None, output, PRE)
            for name in exception_names:
                #name=re.compile('([A-Za-z]+),').search(name).group(1)
                einfo=function.getExceptionInfo(name)

                # if there is no exception info, then name of
                # the exception becomes the info
                if not einfo:
                    einfo=name
                formatter.processException(einfo, output, START)
                formatter.processException(einfo, output, END)

            formatter.processException(None, output, POST)

        # output docstring
        formatter.processDocString(function, output, START)
        self._formatter.writeText(function.getDocString(), output)
        formatter.processDocString(function, output, END)

        formatter.processFunction(function, output, END)
