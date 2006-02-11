#!/usr/bin/env python
#
# $Id: docset_MultipleFile.py,v 1.7 2002/08/24 19:50:06 doughellmann Exp $
#
# COPYRIGHT
#
#   Permission to use, copy, modify, and distribute this software and
#   its documentation for any purpose and without fee is hereby
#   granted, provided that the above copyright notice appear in all
#   copies and that both that copyright notice and this permission
#   notice appear in supporting documentation, and that the name of
#   Doug Hellmann not be used in advertising or publicity pertaining
#   to distribution of the software without specific, written prior
#   permission.
#
# DISCLAIMER
#
#   DOUG HELLMANN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
#   SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
#   FITNESS, IN NO EVENT SHALL DOUG HELLMANN BE LIABLE FOR ANY
#   SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#   WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
#   AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
#   ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
#   THIS SOFTWARE.
# 


"""Documentation set which writes output to multiple files.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name':'$RCSfile: docset_MultipleFile.py,v $',
    'creator':'Doug Hellmann <doug@hellfly.net>',
    'project':'HappyDoc',
    'created':'Sun, 26-Mar-2000 11:19:54 EST',
    #
    #  Current Information
    #
    'author':'$Author: doughellmann $',
    'version':'$Revision: 1.7 $',
    'date':'$Date: 2002/08/24 19:50:06 $',
    'locker':'$Locker:  $',
    }
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import glob
import os
import parser
import re
import string
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import symbol
import sys
import token

#
# Import Local modules
#
import happydoclib

#
# Module
#

def entryPoint():
    "Return info about this module to the dynamic loader."
    return { 'name':'MultiFile',
             'factory':MultiFileDocSet,
             }

#
# Do not use multiple lines in the class docstring, since it shows up as
# part of the generated help message for the app and multiple lines throws
# off the formatting.
#
class MultiFileDocSet(happydoclib.happydocset.DocSet):
    """Documentation set written to multiple files.

    Parameters

      *Adds no additional parameters not understood by DocSet.*
    
    """

    def write(self):
        "Write the documentation set to the output."
        happydoclib.TRACE.into('MultiFileDocSet', 'write')
        self.statusMessage('Beginning to write %s...' % self.getName())
        #
        # Get the name of and open the docset root file
        #
        self._root_name = self.getFullOutputNameForObject(None)
        happydoclib.TRACE.writeVar(root_name=self._root_name)
        self._root_node = self.openOutput( self._root_name, self._title, '' )
        happydoclib.TRACE.writeVar(root_node=self._root_node)
        #
        # Get the description for the docset from the
        # file specified.
        #
        self._writeDescription( self._root_node )
        #
        # Write the output
        #
        self._writePackages()
        self._writeModules()
        self._writePrewrittenFiles()
        self._writeTOC()
        self._writeIndex()
        #
        # Close things up
        #
        self.close()
        happydoclib.TRACE.outof()
        return

    def _writeDescription(self, output):
        """Write the contents of the description file in 'directoryName' to 'output'.
        """
        name = self.getName()
        happydoclib.TRACE.into('MultiFileDocSet', '_writeDescription', name=name)
        happydoclib.TRACE.writeVar(description_filename=self._description_filename)

        description, input_type = self.getDescriptionAndFormat()

        #
        # If we have found a description, write it out.
        #
        if description:
            self._formatter.writeText( description, output, input_type, 0 )
            
        happydoclib.TRACE.outof()
        return

    def _organizeSubNodesByDir(self, outputDict, inputDict, removePrefix=0):
        happydoclib.TRACE.into('MultiFileDocSet', '_organizeSubNodesByDir',
                               outputDict=outputDict,
                               inputDict=inputDict,
                               removePrefix=removePrefix)
        items = inputDict.items()
        subnode_ids = []
        #
        # Translate nodes to records showing what directory they are
        # in and what their names are.
        #
        for x in items:
            happydoclib.TRACE.into('inputDict.items()', 'loop', x=x)
            
            node_name = x[0]
            happydoclib.TRACE.writeVar(node_name=node_name)
            
            dir_name = happydoclib.path.dirname(x[1].getFilename())
            happydoclib.TRACE.writeVar(dir_name=dir_name)
            
            if removePrefix:
                happydoclib.TRACE.write('removing prefix')
                dir_name = happydoclib.path.removeRelativePrefix( dir_name )
                happydoclib.TRACE.writeVar(dir_name=dir_name)
                
            file_name = x[1].getFilename()
            happydoclib.TRACE.writeVar(file_name=file_name)
            
            rec = (dir_name, file_name, node_name)
            subnode_ids.append(rec)
            
            happydoclib.TRACE.outof(rec)
        #
        # For each subnode, record the node information in the list associated
        # with the directory where the node is located.
        #
        for dir_name, file_name, subnode_name in subnode_ids:
            happydoclib.TRACE.into('subnode_ids', 'loop',
                                   dir_name=dir_name,
                                   file_name=file_name,
                                   subnode_name=subnode_name)
            l = outputDict.get(dir_name, [])
            l.append( (file_name, subnode_name, inputDict) )
            outputDict[dir_name] = l
            happydoclib.TRACE.outof()
            
        happydoclib.TRACE.outof()
        return
    
    def _writeTOC(self):
        "Output the TOC."
        happydoclib.TRACE.into('MultiFileDocSet', '_writeTOC')
        happydoclib.TRACE.writeVar(docset_name=self.getName())
        self.statusMessage()
        self.statusMessage('Writing table of contents...')
        formatter = self._formatter
        #
        # Open a new section and list
        #
        formatter.comment('BEGIN: TOC', self._root_node)

        #
        # Build directory contents information for modules
        # and packages
        #
        subnodes_by_dir = {}
        self._organizeSubNodesByDir(subnodes_by_dir, self._all_modules, removePrefix=1)
        self._organizeSubNodesByDir(subnodes_by_dir, self._all_packages, removePrefix=0)
        happydoclib.TRACE.writeVar(subnodes_by_dir=subnodes_by_dir)
        
        #
        # Write Module references to TOC
        #
        dirs = subnodes_by_dir.keys()
        dirs.sort()
        if dirs:
            formatter.comment('BEGIN: TOC->Modules', self._root_node)
            formatter.pushSectionLevel(self._root_node)
            formatter.sectionHeader(self._root_node, 'Modules and Packages')

        for dir_name in dirs:
            happydoclib.TRACE.into('dirs', 'loop', directory=dir_name)
            relative_dir_name = happydoclib.path.removeRelativePrefix(dir_name)
            #
            # Open the section for this directory
            #
            subnode_set = subnodes_by_dir[dir_name]
            extra_files = self._directories_with_extra_docs.get(relative_dir_name, [])
            if dir_name and (dir_name[-1] != '/'):
                dir_name = dir_name + '/'
            formatter.descriptiveListHeader( self._root_node,
                                             dir_name)
            #
            # Write the list of extra files
            # which are in the directory being processed
            #
            if extra_files:
                formatter.comment('BEGIN: Extra files', self._root_node)
            for extra, summary, format in extra_files:
                #
                # Get the full name, including any fixup required
                # by the formatter.
                #
                full_extra_name = happydoclib.path.join(dir_name, extra)
                full_extra_name = formatter.fixUpOutputFilename(full_extra_name)
                #
                # Add reference to the TOC list
                #
                ref = formatter.getReference( full_extra_name,
                                              self._root_name,
                                              extra )
                self.statusMessage('\tAdding reference to %s to TOC' % extra, 2)
                self.statusMessage('\tref="%s"' % ref, 3)
                formatter.descriptiveListItem(
                    self._root_node,
                    ref,
                    summary,
                    format,
                    )
            if extra_files:
                formatter.comment('END: Extra files', self._root_node)
            #
            # Write the list of modules
            # which are in the directory being processed
            #
            subnode_set.sort(lambda x, y: cmp(x[1], y[1]))
            for file_name, subnode_name, subnode_dict in subnode_set:
                happydoclib.TRACE.into('subnode_set', 'loop',
                                       file_name=file_name,
                                       subnode_name=subnode_name,
                                       subnode_dict=subnode_dict,
                                       )
                
                subnode = subnode_dict[subnode_name]
                self.statusMessage('\tAdding %s to TOC' % subnode_name, 2)
                
                #
                # Build a reference to the documentation for the subnode
                # based on the type of referencing supported.
                #
                new_ref = subnode.getReference(formatter, self._root_node)
                
                happydoclib.TRACE.writeVar(root_node_name=self._root_node.name)
                happydoclib.TRACE.writeVar(new_ref=new_ref)
                
                if hasattr( subnode, 'getFullOutputNameForObject' ):
                    happydoclib.TRACE.write('using getFullOutputNameForObject')
                    ref = formatter.getReference(
                        subnode.getFullOutputNameForObject(),
                        self._root_name,
                        subnode_name )
                else:
                    happydoclib.TRACE.write('using formatter getReference')
                    ref = formatter.getReference(subnode,
                                                 self._root_name,
                                                 )
                    
                happydoclib.TRACE.writeVar(ref=ref)
                subnode_summary, subnode_format = subnode.getSummaryAndFormat()
                formatter.descriptiveListItem(
                    self._root_node,
                    ref,
                    subnode_summary,
                    subnode_format,
                    )
                
                happydoclib.TRACE.outof()
                
            formatter.descriptiveListFooter(self._root_node)
            happydoclib.TRACE.outof()
            
        #
        # Close the Modules section
        #
        if dirs:
            formatter.sectionFooter(self._root_node)
            formatter.popSectionLevel(self._root_node)
            formatter.comment('END: TOC->Modules', self._root_node)

        #
        # Close TOC section
        #
        formatter.comment('END: TOC', self._root_node)
        return

    def _writeIndex(self):
        "Output the index."
        self.statusMessage()
        self.statusMessage('IMPLEMENT Writing index...')
        return

    def _writePrewrittenFiles(self):
        """Convert the format of the discovered pre-written files.

        Convert the format of the discovered pre-written files.
        and write out new files as part of the docset.
        """
        happydoclib.TRACE.into('MultiFileDocset', '_writePrewrittenFiles')
        directories_with_extra_docs = {}
        formatter = self._formatter
        for filename in self._prewritten_files:
            external_file = self.getExternalDocumentationFile(filename)
            summary = external_file.oneLiner()
            body = str(external_file)
            if not body:
                continue
            
            #
            # Convert the file using the formatter.
            #
            output_filename = formatter.getFullOutputNameForFile(filename)
            short_output_filename = output_filename[len(self.getOutputBaseDirectory())+1:]
            self.statusMessage('\tRewriting %s\n\t       to %s' \
                               % (filename, short_output_filename),
                               2)
            external_file = self.getExternalDocumentationFile(filename)
            if external_file:
                summary = external_file.oneLiner()
                body = str(external_file)
                format = external_file.getInputType()
            else:
                summary = ''
                body = ''
                format = 'RawText'
            self.statusMessage('\t       as %s' % format, 2)
            output = self.openOutput( output_filename, self._title, '' )
            formatter.writeText( body, output, format )
            self.closeOutput( output )
            #
            # Generate a reference to the file in the TOC
            #
            relative_output_name = formatter.getOutputNameForFile( filename )
            dir, base = happydoclib.path.split(relative_output_name)
            file_list = directories_with_extra_docs.get( dir, [] )
            file_list.append( (base, summary, format) )
            directories_with_extra_docs[dir] = file_list
        self._directories_with_extra_docs = directories_with_extra_docs
        happydoclib.TRACE.outof()
        return

    def _writePackages(self):
        "Output documentation for all packages."
        self.statusMessage()
        self.statusMessage('Writing package documentation...')
        package_items = self._all_packages.items()
        package_items.sort()
        for package_name, package in package_items:
            package.write()
        return
    
    def _writeModules(self):
        "Output documentation for all modules."
        self.statusMessage()
        self.statusMessage('Writing module documentation...')
        module_names = self._all_modules.keys()
        module_names.sort()
        for module_name in module_names:
            self._writeModule( module_name )
        return

    def _describeClassInModuleNode(self, output, class_output_file_name, class_info):
        happydoclib.TRACE.into('', '_describeClassInModuleNode',
                               output=output,
                               class_output_file_name=class_output_file_name,
                               class_info=class_info,
                               )
        #ref = self._formatter.getReference(class_info, class_output_file_name)
        ref = self._formatter.getReference(class_info, output.name)
        class_info_summary, class_info_format = class_info.getSummaryAndFormat()
        self._formatter.descriptiveListItem( output,
                                             ref,
                                             class_info_summary,
                                             class_info_format,
                                             )
        happydoclib.TRACE.outof()
        return

    def _writeModuleImportList(self, module_name, module, output_name, output):
        formatter = self._formatter
        #
        # Get some pre-formatted text we're going to reuse a lot
        #
        from_keyword = formatter.formatKeyword('from')
        import_keyword = formatter.formatKeyword('import')
        #
        # List the dependant modules
        #
        formatter.comment('Testing for imports %s' % module_name, output)
        imported_modules = module.getImportData()
        if imported_modules:
            formatter.comment('BEGIN: imports %s' % module_name, output)
            formatter.sectionHeader(output, 'Imported modules')
            formatter.listHeader(output, None, allowMultiColumn=0)
            for name, symbols in imported_modules:
                #print '\n\nDOCSET_MULTIPLEFILE: looking for %s' % name
                i_module = self.getSymbolInfo(name)
                
                if i_module:
                    #print 'DOCSET_MULTIPLEFILE: got %s' % i_module
                    #print 'DOCSET_MULTIPLEFILE:   i_module is a %s' % \
                    #      i_module.__class__.__name__
                    ref = i_module.getReference(formatter, output)
                    #print 'DOCSET_MULTIPLEFILE: MODULE REFERENCE: '
                    #print 'DOCSET_MULTIPLEFILE: FROM:', output.name
                    #print 'DOCSET_MULTIPLEFILE: TO:', ref
                else:
                    ref = formatter.getPythonReference( name )
                    i_module = None
                    
                if symbols:
                    if i_module:
                        #
                        # Process the list of imported names and
                        # generate references to the ones which are
                        # recognized by our parser.
                        #
                        import_list = []
                        for i_name in symbols:
                            i_info = i_module.getSymbolInfo(i_name)
                            if i_info:
                                i_ref = i_info.getReference(formatter, output)
                            else:
                                #print 'DOCSET_MULTIPLEFILE: UNABLE TO FIND %s in %s' % \
                                #      (i_name, name)
                                i_ref = i_name
                            import_list.append(i_ref)
                    else:
                        import_list = symbols
                    #
                    # from X import Y, Z
                    #
                    formatter.listItem( output,
                                        '%s %s %s %s' % \
                                        ( from_keyword,
                                          ref,
                                          import_keyword,
                                          string.join(import_list, ', ')
                                          )
                                        )
                    
                else:
                    #
                    # import X
                    #
                    formatter.listItem( output,
                                        '%s %s' % (import_keyword, ref)
                                        )
                    
            formatter.listFooter(output)
            formatter.sectionFooter(output)
            formatter.comment('END: imports %s' % module_name, output)
        else:
            #
            # No imports
            #
            formatter.comment('No imports %s' % module_name, output)
        return
    
    def _writeModule(self, module_name):
        "Output the documentation for the module named."
        module = self._all_modules[module_name]
        output_name = self.getFullOutputNameForObject(module)
        output = self.openOutput(output_name,
                                 'Module: %s' % module_name,
                                 module.getFilename())
        formatter = self._formatter
        formatter.comment('BEGIN: Module %s' % module_name, output)
        #
        # Write the doc string
        #
        formatter.writeText( module.getDocString(), output, module.getDocStringFormat() )
        #
        # Start the indented section
        #
        formatter.pushSectionLevel(output)
        #
        # Write list of imported symbols
        #
        self._writeModuleImportList(module_name, module, output_name, output)
        #
        # Write the info for the functions in this module
        #
        function_names = self._filterNames(module.getFunctionNames())
        if function_names:
            formatter.comment('BEGIN: Functions of module %s' % module_name, output)
            formatter.sectionHeader( output, 'Functions' )
            function_names.sort()
            #
            # TOC list
            #
            formatter.listHeader( output )
            for function_name in function_names:
                formatter.listItem(
                    output,
                    formatter.getInternalReference(
                    module.getFunctionInfo(function_name)
                    )
                    )
            formatter.listFooter( output )
            #
            # Function descriptions
            #
            for function_name in function_names:
                self._writeFunction(function_name,
                                    module.getFunctionInfo,
                                    output)
            formatter.sectionFooter(output)
            formatter.comment('END: Functions of module %s' % module_name, output)
        #
        # Write the info for the classes in this module
        #
        class_names = self._filterNames(module.getClassNames())
        if class_names:
            formatter.comment('BEGIN: Classes of module %s' % module_name, output)
            formatter.sectionHeader( output, 'Classes' )
            formatter.descriptiveListHeader( output, None )
            class_names.sort()
            for class_name in class_names:
                happydoclib.TRACE.into('class_names', 'loop', class_name=class_name)
                c = module.getClassInfo(class_name)
                class_output_name = self.getFullOutputNameForObject(c)
                happydoclib.TRACE.writeVar(class_output_name=class_output_name)
                self._describeClassInModuleNode(output, class_output_name , c)
                class_output = self.openOutput(class_output_name,
                                               'Class: %s' % class_name,
                                               module.getFilename())
                self._writeClass( module, class_name, class_output )
                self.closeOutput(class_output)
                happydoclib.TRACE.outof()
            formatter.descriptiveListFooter(output)
            formatter.sectionFooter( output )
            formatter.comment('END: Classes of module %s' % module_name, output)
        #
        # Finish that indented level.
        #
        formatter.sectionFooter(output)
        formatter.popSectionLevel(output)
        formatter.comment('END: Module %s' % module_name, output)
        #
        # Close the output file
        #
        self.closeOutput(output)
        return


    
    def _writeBaseclassNames(self, parent, classInfo, output, indent=0):
        "Output the base class hierarchy for the given class."
        base_classes = classInfo.getBaseClassNames()
        formatter = self._formatter
        if base_classes:
            if indent: formatter.indent(output)
            formatter.listHeader(output, None, allowMultiColumn=0) 
            for name in base_classes:
                try:
                    child = parent.getClassInfo(name)
                except KeyError:
                    formatter.listItem( output, name )
                else:
                    formatter.listItem(
                        output,
                        formatter.getReference(child,
                                               output.name,
                                               )
                        )
                    if name != classInfo.getName():
                        self._writeBaseclassNames(parent, child, output, 1)
            formatter.listFooter(output)
            if indent: formatter.dedent(output)
        return

    def _writeClass(self, parent, class_name, output):
        "Output the documentation for the class in the parent object."
        happydoclib.TRACE.into('MultiFileDocSet', '_writeClass',
                               parent=parent,
                               class_name=class_name,
                               output=output,
                               )
        class_info = parent.getClassInfo(class_name)
        formatter = self._formatter
        formatter.comment('BEGIN: Class %s' % class_name, output)
        formatter.writeText( class_info.getDocString(),
                             output,
                             class_info.getDocStringFormat(),
                             )
        #
        # Base class hierarchy
        #
        base_classes = self._filterNames(class_info.getBaseClassNames())
        happydoclib.TRACE.writeVar(base_classes=base_classes)
        if base_classes:
            formatter.pushSectionLevel(output)
            formatter.sectionHeader(output, 'Base Classes')
            self._writeBaseclassNames(parent, class_info, output)
            formatter.sectionFooter(output)
            formatter.popSectionLevel(output)
        #
        # Start the indented section
        #
        formatter.pushSectionLevel(output)
        #
        # Write the info for the methods of this class
        #
        method_names = self._filterNames(class_info.getMethodNames())
        if method_names:
            formatter.sectionHeader( output, 'Methods' )
            method_names.sort()
            #
            # TOC list
            #
            formatter.listHeader( output )
            for method_name in method_names:
                formatter.listItem(
                    output,
                    formatter.getInternalReference(
                    class_info.getMethodInfo(method_name)
                    )
                    )
            formatter.listFooter( output )
            for method_name in method_names:
                self._writeFunction(method_name,
                                    class_info.getMethodInfo,
                                    output)
            formatter.sectionFooter(output)
            
        #
        # Finish that indented level.
        #
        formatter.sectionFooter(output)
        formatter.popSectionLevel(output)
        formatter.comment('END: Class %s' % class_name, output)

        happydoclib.TRACE.outof()        
        return

    def _writeFunctionParameter(self, name, info, output):
        '''Write a function parameter to the output.
         
        No indenting or formatting is performed.  The output
        looks like::

            name

        or
        
            name=default
 
        Parameters:
 
            name -- name of the parameter
 
            info -- tuple of (default_specified, default_value,
                    default_value_type)
                    concerning the default value of the parameter
 
            output -- destination for written output
             
        '''
        formatter = self._formatter
        formatter.writeRaw(name, output)
        default_specified, default_value, default_value_type = info
        if default_specified:
            formatter.writeRaw('=', output)
            if default_value_type == token.STRING:
                formatter.writeRaw(`default_value`, output)
            elif default_value_type == token.NUMBER:
                formatter.writeRaw(str(default_value), output)
            else:
                #print 'FUNCTION DEFAULT VALUE (%s, %s): "%s"' % (
                #    type(default_value),
                #    default_value_type or 'Unknown',
                #    default_value)
                formatter.writeRaw(str(default_value), output)
        return

    def _writeFunctionSignature(self, function, output):
        """Write the function signature for 'function' to 'output'.

        Parameters

          function -- Instance of FunctionInfo from parseinfo module.

          output -- Where to write.
          
        """
        formatter = self._formatter
        function_name = function.getName()
        signature_buffer = StringIO()
        signature_buffer.write('%s (' % function_name)
        parameter_names = function.getParameterNames()
        if parameter_names:
            if len(parameter_names) <= 2:
                for param in parameter_names:
                    param_info = function.getParameterInfo(param)
                    signature_buffer.write(' ')
                    self._writeFunctionParameter(param, param_info,
                                                 signature_buffer)
                    if param != parameter_names[-1]:
                        signature_buffer.write(',')
                    signature_buffer.write(' ')
            else:
                signature_buffer.write('\n')
                indent = 8 #len(name) + 3
                for param in parameter_names:
                    signature_buffer.write(' ' * indent)
                    param_info = function.getParameterInfo(param)
                    self._writeFunctionParameter(param, param_info,
                                                 signature_buffer)
                    signature_buffer.write(',\n')
                signature_buffer.write('%s' % (' ' * indent))
        signature_buffer.write(')\n')
        formatter.writeCode(signature_buffer.getvalue(), 'PlainText', output)
        return


    def _writeExceptionListForFunction(self, output, function, listHeader):
        """Write the list of exceptions raised by a function.

        Parameters

          output -- Where to write.

          function -- FunctionInfo from parseinfo module.

          listHeader -- Header for list being generated.

        """
        formatter = self._formatter
        formatter.pushSectionLevel(output)
        formatter.sectionHeader(output, 'Exceptions')
        formatter.listHeader(output, listHeader)
        exception_names = function.getExceptionNames()
        exception_names.sort()
        #output_reduced_name = output.name[len(self.getDocsetBaseDirectory())+1:]
        output_buffer = StringIO()
        for name in exception_names:
            exception_class = self.getClassInfo(name)
            if exception_class:
                ref = formatter.getReference( exception_class,
                                              #output_reduced_name,
                                              output.name,
                                              )
            else:
                ref = formatter.getPythonReference( name )
            #output_buffer.write('%s\n' % ref)
            formatter.listItem(output, ref)
        #formatter.writeCode(output_buffer.getvalue(), output)
        formatter.listFooter(output)
        formatter.sectionFooter(output)
        formatter.popSectionLevel(output)
        return

    def _writeFunction(self, function_name, getInfo, output):
        "Output the documentation for the function in the parent object."
        function = getInfo(function_name)
        #
        # Header
        #
        self._formatter.itemHeader( output, function )
        #
        # Function signature
        #
        self._writeFunctionSignature( function, output )
        #
        # Docstring
        #
        self._formatter.writeText( function.getDocString(),
                                   output,
                                   function.getDocStringFormat() )
        #
        # Exceptions
        #
        exception_names = function.getExceptionNames()
        if exception_names:
            self._writeExceptionListForFunction(output, function, None)
        return


    
class MultiFileDocsetUnitTest(happydoclib.StreamFlushTest.StreamFlushTest):    
    
    def testIgnorePackageReadme(self):
        filename = os.path.join('TestCases', 'test_package_summaries', 'FromReadmeTxt')
        import happydoclib.formatter.formatter_Null
        import happydoclib.parseinfo
        docset = MultiFileDocSet(
            formatterFactory=happydoclib.formatter.formatter_Null.NullFormatter,
            parserFunc=happydoclib.parseinfo.getDocs,
            defaultParserConfigValues={'docStringFormat':'StructuredText'},
            inputModuleNames=[ filename ],
            outputBaseDirectory=self.output_dir,
            descriptionFilename='-',
            #descriptionFilename='README.txt',
            )
        buffer = StringIO()
        docset._writeDescription( buffer )
        assert not buffer.getvalue(), 'Wrote a description file when should not have.'
        return

    
    def testModuleOutputFileCalculation(self):
        filename = os.path.join('TestCases', 'test.py')
        import happydoclib.formatter.formatter_Null
        import happydoclib.parseinfo
        docset = MultiFileDocSet(
            formatterFactory=happydoclib.formatter.formatter_Null.NullFormatter,
            parserFunc=happydoclib.parseinfo.getDocs,
            defaultParserConfigValues={'docStringFormat':'StructuredText'},
            inputModuleNames=[ filename ],
            outputBaseDirectory=self.output_dir,
            docsetBaseDirectory=os.path.join(self.output_dir, 'TestCases'),
            descriptionFilename='-',
            )
        info_obj = docset[0]
        actual_output_name = docset.getFullOutputNameForObject(info_obj)
        expected_output_name = os.path.join(self.output_dir,
                                            'TestCases',
                                            'test.html')
        self.failUnlessEqual(
            actual_output_name, expected_output_name,
            ('Outputs do not match:\n'
             'Got:      %s\n'
             'Expected: %s' % (actual_output_name,
                               expected_output_name,
                               )
             )
            )
        return
    
    def testPackageOutputFileCalculation(self):
        filename = os.path.join('TestCases', 'test.py')
        import happydoclib.formatter.formatter_Null
        import happydoclib.parseinfo
        docset = MultiFileDocSet(
            formatterFactory=happydoclib.formatter.formatter_Null.NullFormatter,
            parserFunc=happydoclib.parseinfo.getDocs,
            defaultParserConfigValues={'docStringFormat':'StructuredText'},
            inputModuleNames=[ filename ],
            outputBaseDirectory=self.output_dir,
            descriptionFilename='-',
            #descriptionFilename='README.txt',
            )
        info_obj = None
        actual_output_name = docset.getFullOutputNameForObject(info_obj)
        expected_output_name = os.path.join(self.output_dir, 'index.html')
        self.failUnlessEqual(
            actual_output_name, expected_output_name,
            'Outputs do not match:\n  %s\nvs.\n  %s' % (actual_output_name,
                                                        expected_output_name,
                                                        )
            )
        return
    
        
