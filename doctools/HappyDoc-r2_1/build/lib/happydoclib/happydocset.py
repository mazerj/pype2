#!/usr/bin/env python
#
# $Id: happydocset.py,v 1.10 2002/08/24 19:57:07 doughellmann Exp $
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

"""Base for docsets.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: happydocset.py,v $',
    'rcs_id'       : '$Id: happydocset.py,v 1.10 2002/08/24 19:57:07 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <DougHellmann@bigfoot.com>',
    'project'      : 'HappyDoc',
    'created'      : 'Sat, 10-Feb-2001 08:18:58 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.10 $',
    'date'         : '$Date: 2002/08/24 19:57:07 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
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
import UserList


#
# Import Local modules
#
import happydoclib
import parseinfo

#
# Module
#

class DocSet(UserList.UserList, happydoclib.happydom.HappyDOM):
    """Basic DocSet Parameters
    
        Parameters

            includeComments -- Boolean.  False means to skip the
                               comment parsing step in the parser.
                               Default is True.
            
            includePrivateNames -- Boolean.  False means to ignore
                                   names beginning with _.  Default
                                   is True.

            usePackages -- Boolean.  True means to provide special
                           handling for Packages (directories
                           containing __init__.py files) from
                           non-package Modules.

            prewrittenFileBasenames -- Base names (no extensions) of
                                       files which are to be converted
                                       to the output format and
                                       included in the docset.

            statusMessageFunc -- function which will print a status
                                 message for the user

            title -- the title of the documentation set

            useRecursion -- Recurse into subdirectories looking for
                            subdirectories and files within them.

    """

    def __init__(self,
                 
                 formatterFactory,
                 parserFunc,
                 defaultParserConfigValues,
                 inputModuleNames,
                 
                 author='',
                 outputBaseDirectory=None,
                 docsetBaseDirectory=None,
                 descriptionFilename=None,
                 formatterParameters={},
                 ignoreDirFunc=None,
                 includeComments=1,
                 includePrivateNames=1,
                 usePackages=1,
                 prewrittenFileBasenames=( 'ANNOUNCE',
                                           'CHANGES',
                                           'LICENSE',
                                           'README',
                                           'TODO',
                                           ),
                 statusMessageFunc=None,
                 title='HappyDoc Generated Documentation (use -t to specify a new title)',
                 useRecursion=1,

                 #
                 # Special package handling arguments
                 #
                 packageName='',
                 docsetRoot=None,
                 parent=None,

                 #
                 # DON'T FORGET TO UPDATE THE CLONE METHOD!!!
                 #
                 
                 **extraNamedParameters
                 ):
        """Initialize the documentation set.

        Parameters

            formatterFactory -- a callable object which creates the type
                                of formatter class to be used for formatting
                                the documentation set.  The object will be
                                called and passed the DocSet along with other
                                configuration values for the formatter.

            parserFunc -- Parser function which returns the info for a module.

            inputModuleNames -- List of modules or directories to be documented.
            
            outputBaseDirectory -- the name of the root directory for this and any
                                   parent docsets

            docsetBaseDirectory -- the name of the root directory for this docset

            descriptionFilename -- File describing the docset as a whole.

            formatterParameters -- other named configuration values to be passed
                                   to the formatter when it is created through the
                                   factory.  Any unrecognized values will be
                                   quietly ignored.

            ignoreDirFunc -- Function which returns true if the directory should
                             be ignored.

            packageName -- Name of the package being documented by
                           this docset.  This value should only be
                           specified when recursively creating a
                           docset (HappyDoc handles this case
                           automatically).

            docsetRoot=None -- The root DocSet object, when recursing.

            *For others, see class documentation.*
                                   
        """
        happydoclib.TRACE.into('HappyDocset', '__init__',
                               packageName=packageName,
                               parent=parent,
                               docsetBaseDirectory=docsetBaseDirectory,
                               outputBaseDirectory=outputBaseDirectory,
                               )
        happydoclib.TRACE.callerParent()
        #
        # Storage for sub-objects
        #
        self._all_packages = {}
        self._all_modules = {}
        self._all_classes = {}
        namespaces = ( self._all_packages, self._all_modules, self._all_classes )
        #
        # Initialize base classes
        #
        self._status_message_func = statusMessageFunc
        self.statusMessage('Initializing documentation set %s...' % title)
        UserList.UserList.__init__(self)
        happydoclib.happydom.HappyDOM.__init__(self,
                                               packageName,
                                               parent,
                                               docsetBaseDirectory,
                                               namespaces)
        #
        # Store parameters
        #
        self._formatter_factory = formatterFactory
        self._parser_func = parserFunc
        self._default_parser_config_values = defaultParserConfigValues
        self._input_module_names = inputModuleNames
        self._contained_names = [] # list of inputModuleNames actually used
        self._title = title
        self._output_base_directory = outputBaseDirectory
        if docsetBaseDirectory:
            self._docset_base_directory = docsetBaseDirectory
        else:
            self._docset_base_directory = outputBaseDirectory
        self._description_filename = descriptionFilename
        self._formatter_configuration = formatterParameters
        self._include_private_names = happydoclib.optiontools.getBooleanArgumentValue(
            includePrivateNames)
        self._include_comments = happydoclib.optiontools.getBooleanArgumentValue(
            includeComments)
        self._use_packages = happydoclib.optiontools.getBooleanArgumentValue(
            usePackages)
        self._use_recursion = useRecursion
        self._ignore_dir_name = ignoreDirFunc
        self._prewritten_file_basenames = prewrittenFileBasenames
        self._prewritten_files = []
        self._docset_root = docsetRoot
        
        #
        # Initialize this class
        #
        self._open_handles = []
        
        #
        # Handle unrecognized named parameters.
        #
        for extra_param, extra_value in extraNamedParameters.items():
            self.statusMessage(
                'WARNING: Parameter "%s" (%s) unrecognized by docset %s.' % \
                (extra_param, extra_value, self.__class__.__name__)
                )
        #
        # Create the formatter
        #
        self._formatter = apply( self._formatter_factory,
                                 ( self, ),
                                 self._formatter_configuration )
        #
        # Process the modules specified.
        #
        self.processFiles(inputModuleNames)
        happydoclib.TRACE.outof()
        return

    def _requiredOfSubclass(self, name):
        "Convenient way to raise a consistent exception."
        raise AttributeError('%s is not implemented for this class.' % name,
                             self.__class__.__name__)

    def __del__(self):
        #
        # Attempt to reduce cycles, since the
        # formatter generally has a reference
        # to the docset as well.
        #
        self._formatter = None
        return

    def statusMessage(self, message='', verboseLevel=1):
        "Print a status message for the user."
        if self._status_message_func:
            self._status_message_func(message, verboseLevel)
        return

    ##
    ## HappyDOM
    ##

    def getFilename(self):
        "Returns the \"filename\" of the documentation set."
        happydoclib.TRACE.into('HappyDocset', 'getFilename')
        my_path = happydoclib.path.removePrefix( self.getDocsetBaseDirectory(),
                                                 self.getOutputBaseDirectory())
        happydoclib.TRACE.outof(my_path)
        return my_path
    
    def getSymbolInfo(self, name, tryParent=1):
        """Look up the info record for the name.

        Looks in the namespaces registered for this DOM node.  If no
        value is found, 'None' is returned.
        """
        #
        # First try locally
        #
        my_answer = happydoclib.happydom.HappyDOM.getSymbolInfo(self, name, tryParent=0)
        if my_answer:
            return my_answer
        #
        # Next try in our __init__.py module
        #
        init_module = self._all_modules.get('__init__', None)
        if init_module:
            # do not try parent, as that will call *this* method again
            init_answer = init_module.getSymbolInfo(name, tryParent=0)
            if init_answer:
                return init_answer
        #
        # Last, try our parent.  We can just call the base class method
        # again with the appropriate flag set, since we know it will
        # fail normally but then try the parents.  This saves us having
        # to re-implement that feature here.
        #
        if tryParent:
            return happydoclib.happydom.HappyDOM.getSymbolInfo( self,
                                                                name,
                                                                tryParent=tryParent)
        return None

    def getReference(self, formatter, sourceNode):
        "Return a reference to this package from sourceNode."
        happydoclib.TRACE.into( 'DocSet', 'getReference',
                                formatter=formatter, sourceNode=sourceNode)
        init_module = self._all_modules.get('__init__', self)
        fully_qualified_name = formatter.getOutputNameForObject(self)
        happydoclib.TRACE.writeVar(fully_qualified_name=fully_qualified_name)
        
        extension = '.%s' % formatter.getFilenameExtension()
        len_extension = len(extension)
        if fully_qualified_name[-len_extension:] == extension:
            happydoclib.TRACE.write('fully qualified name has extension')
            fully_qualified_name = fully_qualified_name[:-len_extension]
            happydoclib.TRACE.writeVar(fully_qualified_name=fully_qualified_name)
                                
        root_node_name = formatter.getRootNodeName()
        my_root_node = happydoclib.path.join(fully_qualified_name, root_node_name)
        happydoclib.TRACE.writeVar(my_root_node=my_root_node)
        ref = formatter.getReference( my_root_node,
                                      sourceNode.name,
                                      self.getReferenceTargetName() )
        happydoclib.TRACE.outof(ref)
        return ref
        

    def getFullOutputNameForObject(self, infoObject=None):
        "Returns the output destination for documentation about this object."
        happydoclib.TRACE.into('DocSet', 'getFullOutputNameForObject',
                               infoObject=infoObject)
        if infoObject is None:
            output_name = self._formatter.getFullOutputNameForObject(None)
        else:
            output_name = self._formatter.getFullOutputNameForObject(infoObject)
        happydoclib.TRACE.outof(output_name)
        return output_name

    ##
    ## External documents
    ##
    
    def getExternalDocumentationFile(self, filename):
        """Retrieve documentation that is not in a program source file.

        Parameters:

          'filename' -- Name of the file to retrieve.
        """
        converter_factory = happydoclib.docstring.getConverterFactoryForFile(filename)
        converter = converter_factory()
        try:
            file = converter.getExternalDocumentationFile(filename)
        except IOError:
            file = None
        return file
        

    def _foundReadme(self):
        """If a README file was found, return the name of the file.
        """
        for fname in self._prewritten_files:
            if happydoclib.path.basename(fname)[:6] == 'README':
                return fname
        return None

    
    ##
    ## Docstrings
    ##
    
    def getSummaryAndFormat(self):
        """Return one line summary of the documentation set.
        """
        happydoclib.TRACE.into('HappyDocset', 'getSummaryAndFormat',
                               name=self.getName())
        one_liner = ''
        format = 'PlainText'
        #
        # First check for __init__.py description.
        #
        if (not one_liner) and self._all_modules.has_key('__init__'):
            happydoclib.TRACE.write('Trying __init__.py')
            one_liner, format = self._all_modules['__init__'].getSummaryAndFormat()
        #
        # Then check for first line of README file.
        #
        if (not one_liner) and self._foundReadme():
            readme_filename = self._foundReadme()
            external_file = self.getExternalDocumentationFile( readme_filename )
            if external_file:
                happydoclib.TRACE.write('Trying file %s' % readme_filename)
                one_liner = external_file.oneLiner()
                format = external_file.getInputType()
        #
        # Then check for specified title.
        #
        if (not one_liner) and self._title:
            happydoclib.TRACE.write('Trying title')
            one_liner = self._title

        happydoclib.TRACE.outof(one_liner)
        return one_liner, format

    def getDocStringFormat(self):
        "Returns the docstring converter name for the docstring for this object."
        summary, format = self.getSummaryAndFormat()
        return format

    def getDescriptionAndFormat(self):
        "Returns the complete description of the docset and the docstring converter name for the format."
        happydoclib.TRACE.into('HappyDocSet', 'getDescriptionAndFormat')
        description = input_type = ''
        name = self.getName()
        #
        # Look for a description file (e.g. README.txt)
        #
        if self._description_filename and (self._description_filename != '-'):
            description_dir = '.'
            if self._contained_names:
                first_name = self._contained_names[0]
                if happydoclib.path.isdir(first_name):
                    description_dir = first_name
                elif happydoclib.path.exists(first_name):
                    description_dir = happydoclib.path.dirname(first_name)
                
            description_filename = happydoclib.path.join( description_dir,
                                                          self._description_filename )
            self.statusMessage('Looking for docset description in %s' % \
                               description_filename,
                               3)
            description_file = self.getExternalDocumentationFile(description_filename)
            if description_file:
                happydoclib.TRACE.write('file exists')
                #summary = description_file.oneLiner()
                description = str(description_file)
                input_type = description_file.getInputType()

        #
        # Look for a description in the __init__.py module.
        #
        if (not description) and (name not in ('__init__',)):
            init_module = self.getSymbolInfo('__init__', 0)
            if init_module:
                happydoclib.TRACE.write('found __init__')
                description = init_module.getDocString()
                input_type = init_module.getDocStringFormat()

        if description:
            happydoclib.TRACE.outof('found description')
        else:
            happydoclib.TRACE.outof('did not find description')
        return (description, input_type)

    ##
    ## Docset methods
    ##

    def getFormatter(self):
        "Returns the formatter instance being used by this docset."
        return self._formatter

    def getDocsetRoot(self):
        """Return the root node of the documentation set.
        """
        if self._docset_root:
            return self._docset_root
        else:
            return self

    def clone(self, packageName, docsetBaseDirectory, inputModuleNames):
        """Create a new object which is configured the same as the current.

        It is possible, by passing optional arguments, to
        create a clone with a different configuration.  This
        is useful for recursive work.

        Parameters

          packageName -- The name of the package being created.

          docsetBaseDirectory -- The base of output for the new docset.

          inputModuleNames -- Names of files to be included.

        """
        happydoclib.TRACE.into('HappyDocset', 'clone',
                               packageName=packageName,
                               docsetBaseDirectory=docsetBaseDirectory,
                               inputModuleNames=inputModuleNames)
        constructor_args = self.getCloneArguments(packageName,
                                                  docsetBaseDirectory,
                                                  inputModuleNames)
        new_obj = apply(self.__class__, (), constructor_args)
        happydoclib.TRACE.outof()
        return new_obj

    def getCloneArguments(self, packageName, docsetBaseDirectory, inputModuleNames):
        '''Return arguments to create a new docset based on the current one.

        Parameters

          packageName -- The name of the package being created.

          docsetBaseDirectory -- The base of output for the new docset.

          inputModuleNames -- Specify the file names to be included in
          the docset.

        Subclasses should override this method, but should also call
        the parent method using an algorithm such as::

          subclass_args = {}
          subclass_args.update( ParentClass.getCloneArguments(
                                    self,
                                    packageName,
                                    baseDirectory,
                                    inputModuleNames) )
          subclass_args.update( {
              "subClassArgument":self._sub_class_argument,
              })
          return subclass_args

        '''
        current_docset_path = self.getPath()
        happydoclib.TRACE.writeVar(current_docset_path=current_docset_path)

        docset_base_directory_prefix = docsetBaseDirectory[:-len(packageName)]
        while (docset_base_directory_prefix
               and
               (docset_base_directory_prefix[-1] == os.sep)
               ):
            docset_base_directory_prefix = docset_base_directory_prefix[:-1]
        happydoclib.TRACE.writeVar(
            docset_base_directory_prefix=docset_base_directory_prefix,
            )
        
        constructor_args = {
            'formatterFactory':self._formatter_factory,
            'parserFunc':self._parser_func,
            'defaultParserConfigValues':self._default_parser_config_values,
            'inputModuleNames':inputModuleNames,

            'outputBaseDirectory':self._output_base_directory,
            'docsetBaseDirectory':docsetBaseDirectory,
            
            'descriptionFilename':self._description_filename,
            'formatterParameters':self._formatter_configuration,
            'ignoreDirFunc':self._ignore_dir_name,
            'includeComments':self._include_comments,
            'includePrivateNames':self._include_private_names,
            'usePackages':self._use_packages,
            'prewrittenFileBasenames':self._prewritten_file_basenames,

            'statusMessageFunc':self._status_message_func,
            'useRecursion':self._use_recursion,
            'parent':self,
            }
        #
        # Construct a reasonable title
        #
        if self.getName():
            title = '%s.%s' % (self._title, packageName)
        else:
            title = '%s: %s' % (self._title, packageName)
        constructor_args['title'] = title
        #
        # Set up recursion into package with
        # a reference back to the root.
        #
        constructor_args.update( { 'packageName':packageName,
                                   'docsetRoot':self.getDocsetRoot(),
                                   }
                                 )
        return constructor_args
    
    def getFileInfo(self, fileName):
        "Parse the file and return the parseinfo instance for it."
        happydoclib.TRACE.into('DocSet', 'getFileInfo',
                               fileName=fileName,
                               )
        self.statusMessage('Getting info for %s' % fileName)
        module_info = self._parser_func( self,
                                         fileName,
                                         self._include_comments,
                                         self._default_parser_config_values,
                                      )
        happydoclib.TRACE.outof(module_info)
        return module_info

    def lookForPrewrittenFiles(self, dirName):
        """Look for prewritten documentation files in 'dirName'.
        """
        self.statusMessage('Looking for non-source documentation files')
        self.statusMessage('  in %s' % dirName, 4)
        files = []
        for file_basename in self._prewritten_file_basenames:
            pattern = '%s*' % file_basename
            self.statusMessage('  for %s' % pattern, 4)
            found = happydoclib.path.findFilesInDir( dirName, pattern )
            self.statusMessage('    %s' % str(found), 4)
            for f in found:
                #
                # Eliminate any backup files, etc. created by
                # text editors.
                #
                if f[-1] in '*~#':
                    continue
                #
                # Record this name
                #
                self.statusMessage(
                    '  Found external documentation file\n    %s' \
                    % f, 2)
                files.append(f)
        return files
    
    def processFiles(self,
                     fileNames,
                     moduleFileName=re.compile(r'^.*\.(py|cgi)$').match,
                     ):
        """Get information about a list of files.

        Parameters

          fileNames -- Sequence of names of files to be read.

        Each file in fileNames is parsed to extract information
        to be used in documenting the file.

        """
        happydoclib.TRACE.into('HappyDocset', 'processFiles', fileNames=fileNames)
        for file_name in fileNames:

            if ( happydoclib.path.isdir(file_name)
                 and
                 (not self._ignore_dir_name or not self._ignore_dir_name(file_name))
                 and
                 (self._use_recursion >= 0)
                 ):
                #
                # Record that we paid attention to this directory
                #
                self._contained_names.append(file_name)
                #
                # Find modules and directories within to
                # recurse.
                #
                dir_contents = happydoclib.path.findFilesInDir(file_name)
                #
                # Adjust the recursion factor.
                #
                # -1 -- Do not recurse.
                #  0 -- Recurse one level.
                #  1 -- Always recurse.
                #
                if not self._use_recursion:
                    self._use_recursion = -1
                #
                # Check if the current dir is a Package
                #
                init_file = happydoclib.path.join( file_name, '__init__.py' )
                if happydoclib.path.exists( init_file ) and self._use_packages:
                    self.statusMessage('Detected package %s' % file_name, 2 )
                    happydoclib.TRACE.write('Detected package %s' % file_name)
                    #
                    # Special handling for Package directories
                    #
                    orig_file_name = file_name
                    file_name = happydoclib.path.removeRelativePrefix(file_name)
                    package_name = happydoclib.path.basename(file_name)
                    docset_base = self.getDocsetBaseDirectory()
                    output_base = self.getOutputBaseDirectory()
                    new_base = happydoclib.path.joinWithCommonMiddle(
                        output_base,
                        docset_base,
                        file_name)
                    
                    new_docset = self.clone( packageName=package_name,
                                             docsetBaseDirectory=new_base,
                                             inputModuleNames=dir_contents,
                                             )
                    new_docset._prewritten_files = new_docset.lookForPrewrittenFiles(
                        orig_file_name)
                    self.append(new_docset)
                else:
                    self.statusMessage('Recursing into %s' % file_name)
                    #
                    # Find pre-written files within the regular directory
                    #
                    self._prewritten_files = self._prewritten_files + \
                                             self.lookForPrewrittenFiles(file_name)
                    self.processFiles(dir_contents)
                    
            elif ( not happydoclib.path.isdir(file_name)
                   and
                   moduleFileName(file_name)
                   ):
                happydoclib.TRACE.write('regular module file')
                #
                # Record that we paid attention to this file
                #
                self._contained_names.append(file_name)
                #
                # Regular module file
                #
                try:
                    file_info = self.getFileInfo(file_name)
                except SyntaxError, msg:
                    self.statusMessage('\nERROR: SyntaxError: %s[%s] %s' % \
                                       (file_name, msg.lineno, msg.msg)
                                       )
                    self.statusMessage('\n%s' % msg.text)
                    self.statusMessage('Skipping %s' % file_name)
                else:
                    self.append(file_info)
                    
            else:
                #
                # Ignoring
                #
                self.statusMessage('Ignoring %s' % file_name, 4)
                
        happydoclib.TRACE.outof()
        return

    def getDocsetBaseDirectory(self):
        "Returns the base directory for this documentation set."
        happydoclib.TRACE.into('HappyDocset', 'getDocsetBaseDirectory')
        happydoclib.TRACE.outof(self._docset_base_directory)
        return self._docset_base_directory

    def getOutputBaseDirectory(self):
        "Returns the base directory for all documentation sets."
        happydoclib.TRACE.into('HappyDocset', 'getOutputBaseDirectory')
        happydoclib.TRACE.outof(self._output_base_directory)
        return self._output_base_directory

    def getClassInfo(self, className):
        "Returns class info if have it, None otherwise."
        return self._all_classes.get(className, None)
        
    def write(self):
        """Write the documentation set to the output.

        Developers creating their own, new, docset types should
        override this method to cause the docset instance to
        generate its output.

        """
        self._requiredOfSubclass('write')
        return

    def _filterNames(self, nameList):
        """Remove names which should be ignored.

        Parameters

          nameList -- List of strings representing names of methods,
          classes, functions, etc.
        
        This method returns a list based on the contents of nameList.
        If private names are being ignored, they are removed before
        the list is returned.

        """        
        if not self._include_private_names:
            nameList = filter(lambda x: ( (x[0] != '_') or (x[:2] == '__') ),
                              nameList)
        return nameList

    def close(self):
        "Close the open documentation set."
        for f in self._open_handles:
            try:
                self.closeOutput(f)
            except:
                pass
        return

    def append(self, infoObject):
        """Add a module to the docset.
        """
        if infoObject.__class__ == self.__class__:
            #
            # Recursive package definition
            #
            self._all_packages[ infoObject.getName() ] = infoObject
        else:
            #
            # Contained module definition
            #
            self._all_modules[ infoObject.getName() ] = infoObject
            for c in infoObject.getClassNames():
                self._all_classes[ c ] = infoObject.getClassInfo(c)
        #
        # Add to our list representation.
        #
        UserList.UserList.append(self, infoObject)
        return

    def openOutput(self, name, title, subtitle):
        """Open output for writing.
        
        Using this method to open output destinations
        means they will automatically be closed.

        Parameters

          name -- Name of output destination to open.

          title -- The main title to be given to the output (e.g.,
          HTML page title or other documentation title).

          subtitle -- A subtitle which should be applied to the
          output.

        See also 'closeOutput'.
        """
        self.statusMessage('\tDocumenting : "%s"' % title, 2)
        self.statusMessage('\t              "%s"' % subtitle, 3)
        self.statusMessage('\t         to : "%s"' % name, 3)
        f = self._formatter.openOutput(name, title, subtitle)
        self._open_handles.append(f)
        return f
    
    def closeOutput(self, output):
        """Close the output handle.

        Parameters

          output -- A handle created by 'openOutput'.
        
        """
        self._formatter.closeOutput(output)
        return

    
class DocsetUnitTest(happydoclib.StreamFlushTest.StreamFlushTest):    

    def testOutputDirectory(self):
        filename = 'TestCases/test.py'
        test_output_dir = 'c:\\happydoc\\HappyDocTestOut'
        import happydoclib.formatter.formatter_Null
        docset = DocSet( formatterFactory=happydoclib.formatter.formatter_Null.NullFormatter,
                         parserFunc=happydoclib.parseinfo.getDocs,
                         defaultParserConfigValues={'docStringFormat':'StructuredText'},
                         inputModuleNames=[ filename ],
                         outputBaseDirectory=test_output_dir,
                         statusMessageFunc=self.status_message_func,
                         )
        docset_base_dir = docset.getDocsetBaseDirectory()
        assert docset_base_dir == test_output_dir, 'Docset directory %s does not match %s' % \
            (docset_base_dir, test_output_dir)
        output_base_dir = docset.getOutputBaseDirectory()
        assert docset_base_dir == test_output_dir, 'Output directory %s does not match %s' % \
            (docset_base_dir, test_output_dir)
        docset_file_name = docset.getFilename()
        assert docset_file_name == test_output_dir, 'File name %s does not match expected %s' % \
               (docset_file_name, test_output_dir)
        return

    if os.name != 'nt':    
        def testPackageSummaries(self):
            filename = 'TestCases/test_package_summaries'
        
            basic_expected_package_info = {
                'FromInit':'Summary from __init__.py',
                'FromReadme':'Summary from README',
                'FromReadmeTxt':'Summary from README.txt',
                'FromTitle':'HappyDoc Generated Documentation (use -t to specify a new title): Nested.FromTitle',
                }
            basic_expected_package_names = basic_expected_package_info.keys()
            
            parent_expected_package_info = {}
            parent_expected_package_info.update(basic_expected_package_info)
            parent_expected_package_info['Nested'] = 'Nested Modules'
            parent_expected_package_info['FromTitle'] = 'HappyDoc Generated Documentation (use -t to specify a new title): FromTitle'
            parent_expected_package_names = parent_expected_package_info.keys()
            
            #module = getDocs(None, filename)
            import happydoclib.formatter.formatter_Null
            docset = DocSet( formatterFactory=happydoclib.formatter.formatter_Null.NullFormatter,
                             parserFunc=happydoclib.parseinfo.getDocs,
                             defaultParserConfigValues={'docStringFormat':'StructuredText'},
                             inputModuleNames=[ filename ],
                             outputBaseDirectory=self.output_dir,
                             statusMessageFunc=self.status_message_func,
                             )
            for m in docset.data:
                name = m.getName()
                assert name in parent_expected_package_names, \
                       'Unexpected module %s found in docset.' % name
    
                expected_summary = parent_expected_package_info[name]
    
                actual_summary, format = m.getSummaryAndFormat()
                assert actual_summary == expected_summary, \
                       'Summary values do not match for %s (expected "%s", got "%s")' \
                       % (name, expected_summary, actual_summary)
    
                if name == 'Nested':
                    for cm in m.data:
                        cname = cm.getName()
                        if cname == '__init__':
                            continue
                        assert cname in basic_expected_package_names, \
                               'Unexpected child module %s found in child docset.' % cname
    
                        cexpected_summary = basic_expected_package_info[cname]
    
                        cactual_summary, format = cm.getSummaryAndFormat()
                        assert cactual_summary == cexpected_summary, \
                               'Summary values do not match for child module %s (expected "%s", got "%s")' \
                               % (cname, cexpected_summary, cactual_summary)
            return

    def _privateNameTest(self, includePrivateNames):
        filename = 'TestCases/test_private_names.py'
        import happydoclib.formatter.formatter_Null
        docset = DocSet( formatterFactory=happydoclib.formatter.formatter_Null.NullFormatter,
                         parserFunc=happydoclib.parseinfo.getDocs,
                         defaultParserConfigValues={'docStringFormat':'StructuredText'},
                         inputModuleNames=[ filename ],
                         outputBaseDirectory=self.output_dir,
                         includePrivateNames=includePrivateNames,
                         statusMessageFunc=self.status_message_func,
                         )
        assert len(docset.data) == 1, 'Did not get expected docset.'
        m = docset.data[0]
        assert m, 'Could not retrieve module'
        try:
            c = m['Public']
        except KeyError:
            self.fail('Could not retrieve class "Public"')
        assert c.getName() == 'Public', 'Name of class does not match expected value.'
        
        all_function_names = c.getMethodNames()
        all_function_names.sort()
        expected_all_function_names = [ 'public_method',
                                        '_private_method',
                                        '__getattr__' ]
        expected_all_function_names.sort()
        
        if includePrivateNames:
            assert all_function_names == expected_all_function_names, \
                   'Expected unfiltered names %s, got names %s' % \
                   (expected_all_function_names, all_function_names)
        else:
            expected_filtered_function_names = [ 'public_method', '__getattr__' ]
            expected_filtered_function_names.sort()
            filtered_function_names = docset._filterNames(all_function_names)
            assert filtered_function_names == expected_filtered_function_names, \
                   'Expected filtered names %s, got names %s' % \
                   (expected_filtered_function_names, filtered_function_names)
        return
    
    def testPrivateNamesKeep(self):
        self._privateNameTest(1)
        return

    def testPrivateNamesIgnore(self):
        self._privateNameTest(0)
        return

    def _testIgnoreDirectoriesTestFunc(self, dirName):
        dir_name = happydoclib.path.basename(dirName)
        if dir_name in self.ignore_list:
            return 1
        else:
            return 0

    def testIgnoreDirectories(self):
        "Ignore some subdirectories."
        filename = '../HappyDoc'
        import happydoclib.formatter.formatter_Null
        self.ignore_list = [ 'docset',
                             'formatter',
                             'docstring',
                             'TestCases',
                             'dist',
                             'tmp',
                             ]
        docset = DocSet( formatterFactory=happydoclib.formatter.formatter_Null.NullFormatter,
                         parserFunc=happydoclib.parseinfo.getDocs,
                         defaultParserConfigValues={'docStringFormat':'StructuredText'},
                         inputModuleNames=[ filename ],
                         outputBaseDirectory=self.output_dir,
                         ignoreDirFunc=self._testIgnoreDirectoriesTestFunc,
                         statusMessageFunc=self.status_message_func,
                         )
        for m in docset.data:
            name = m.getName()
            assert name not in self.ignore_list, \
                   'Found %s but it should have been ignored.' % name
        return
