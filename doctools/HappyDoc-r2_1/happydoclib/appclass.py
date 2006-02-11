#!/usr/bin/env python
#
# $Id: appclass.py,v 1.9 2002/05/12 20:17:56 doughellmann Exp $
#
# Copyright Doug Hellmann 2000
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

"""Command line application class for HappyDoc.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: appclass.py,v $',
    'rcs_id'       : '$Id: appclass.py,v 1.9 2002/05/12 20:17:56 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'HappyDoc',
    'created'      : 'Sun, 13-Aug-2000 11:27:00 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.9 $',
    'date'         : '$Date: 2002/05/12 20:17:56 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import os
import glob
import sys
import types
import string
import re
import parser
import traceback

#
# Import Local modules
#
import happydoclib

#
# Module
#

True = 1
False = None
    
class HappyDoc(happydoclib.CommandLineApp.CommandLineApp):
    """
    HappyDoc is a documentation generation/extraction tool which does
    not depend on being able to import modules.

    The data extraction library used by this app is based on the
    Demos/parser/example.py module distributed with the Python source
    distribution.

    """

    shortArgumentsDescription = 'file...'

    include_private_names = True
    include_comments = True
    output_directory = './doc'
    output = None
    author_name = 'Doug Hellmann <doug@hellfly.net>'
    app_home = 'http://HappyDoc.sourceforge.net/'
    package_description_file = 'README.txt'
    recurse_into_subdirs=True

    docset_type = None
    docset_title = 'HappyDoc Generated Documentation'

    #
    # Define the docstring syntaxes supported
    #
    docstring_syntaxes = happydoclib.docstring.DocStringLoader()
    
    #
    # Define the output formats supported
    #
    supported_formats = happydoclib.formatter.FormatterLoader()

    #
    # Define the documentation set types supported
    #
    supported_docset_types = happydoclib.docset.DocSetLoader()

    ##
    ## Local methods
    ##
    
    def appInit(self):
        self._app_name = self.__class__.__name__
        self._app_version = happydoclib.cvsProductVersion()
        
        self.set_docset_type('MultiFile')
        self.set_format('HTMLTable')
        
        self._ignore_dir_patterns = []
        self.addIgnoreDirectoryPattern('CVS', 'dist', 'build', 'doc', 'docs')

        self.parser_function = happydoclib.parseinfo.getDocs
        return

    def addIgnoreDirectoryPattern(self, *dirNamePatterns):
        "Add one or more directory name patterns to the list which should be ignored."
        for dir_name_pattern in dirNamePatterns:
            if dir_name_pattern not in self._ignore_dir_patterns:
                self._ignore_dir_patterns.append(dir_name_pattern)
                self.statusMessage('Ignoring %s' % dir_name_pattern, 2)
        return

    def ignoreDirectoryTest(self, dirName):
        """Determines whether 'dirName' matches pattern to be ignored.

        Arguments

          'dirName' -- Full path of the directory to be tested.

        Returns true value if 'dirName' should be ignored, false value
        otherwise.

        """
        dir_base = happydoclib.path.basename(dirName) 
        if dir_base in self._ignore_dir_patterns:
            return 1
        else:
            return 0
    
    def set_format(self, format):
        "Set the formatter to be used."
        self.format = format
        try:
            self.formatter_factory = self.supported_formats[format]
        except KeyError:
            raise ValueError('format must be one of %s' \
                             % self.supported_formats.keys(),
                             format)
        return

    def set_docset_type(self, docset_type):
        "Set the docset to be used."
        self.docset_type = docset_type
        try:
            self.docset_factory = self.supported_docset_types[docset_type]
        except KeyError:
            raise ValueError('docset_type must be one of %s' % \
                             self.supported_docset_types.keys(),
                             docset_type)
        return

    ##
    ## Override CommandLineApp methods
    ##

    def _showOptionItemsDescription(self, title, items):
        items.sort()
        for name, obj in items:
            if obj.__doc__:
                description = str(obj.__doc__).strip()
            else:
                description = ''
            print '  %s %s: %s\n' % (title, name, description)
        return

    def showVerboseSyntaxHelp(self):
        "Overloaded to show supported docset and format types."
        happydoclib.CommandLineApp.CommandLineApp.showVerboseSyntaxHelp(self)

        print 'SUPPORTED DOCSTRING SYNTAXES:\n'
        self._showOptionItemsDescription('SYNTAX TYPE', self.docstring_syntaxes.items())

        print
        print 'SUPPORTED FORMATS for -F Option:\n'
        self._showOptionItemsDescription(
            'FORMATTER TYPE', self.supported_formats.items())

        print 'SUPPORTED DOCSET TYPES for -T Option:'
        print
        print '  %s' % happydoclib.happydocset.DocSet.__doc__
        print
        self._showOptionItemsDescription(
            'DOCSET TYPE', self.supported_docset_types.items())

        print
        print 'PARSER ARGUMENTS:'
        print

        print '  Parser arguments control the default behavior of the'
        print '  documentation extraction parser.  Pass the argument'
        print '  as an argument on the command line using the syntax:'
        print
        print '    parser_<argument>=value'
        print
        print '  Arguments:'
        print
        print '    docStringFormat -- Name of the docstring converter'
        print '                       format used in the inline documentation.'
        print '                       Defaults to "StructuredText".'

        print
        return

    ##
    ## Argument handlers
    ##

    def optionHandler_author(self, authorNameAndEmail):
        """Specify the author identification to be inserted for
        references.
        """
        self.author_name = authorNameAndEmail
        return
    
    def optionHandler_d(self, outputDirectory):
        """Specify an outputDirectory.

        Defaults to './doc'."""
        self.output_directory = os.path.normcase(outputDirectory)
        return

    def optionHandler_dia(self):
        """Generate UML diagram in Gnome dia format.
        """
        self.set_docset_type("Dia")
        self.set_format("Dia")
        return

    def optionHandler_F(self, format):
        """Specify the output format.

        Defaults to 'HTMLTable'."""
        self.set_format(format)
        return

    def optionHandler_i(self, ignoreDirectory):
        """Specify a directory basename to be ignored.

        Use just the base name of the directory.
        For instance, to ignore all directories
        with the name CVS, specify: -i CVS.

        Defaults to ignore::
        
          CVS, dist, build, doc, docs.
          
        """
        ignoreDirectory=string.strip(ignoreDirectory)
        self.statusMessage('Adding ignore directive for %s' % ignoreDirectory)
        self.addIgnoreDirectoryPattern(ignoreDirectory)
        return

    def optionHandler_no_comments(self):
        """Do not include comment text as though it was
           a __doc__ string.
        """
        self.include_comments = False
        return

    def optionHandler_no_private_names(self):
        "Do not include names beginning with _."
        self.include_private_names = False
        return

    def optionHandler_o(self):
        "Specify that output should go to stdout."
        self.set_docset_type('StdOut')
        return

    def optionHandler_p(self, packageDescriptionFile):
        """Specify a file with a description of the package.

        The default packageDescriptionFile is README.txt.
        """
        self.package_description_file = packageDescriptionFile
        return
    
    def optionHandler_r(self):
        "Disable recursion into subdirectories."
        self.recurse_into_subdirs = False
        return

    def optionHandler_t(self, title):
        "Specify a title for the documentation set."
        self.docset_title = title
        return

    def optionHandler_T(self, docset_type):
        """Specify the documentation set type.

        Defaults to 'multifile_docset'."""
        self.set_docset_type(docset_type)
        return

    ##
    ## Main
    ##
    
    def main(self, *args):
        
        self.statusMessage('%s version %s' % (self._app_name,
                                              self._app_version))
        
        #
        # Debug info about where the docsets and formatters come from
        #
        self.statusMessage('Docstring converters from %s' % \
                           happydoclib.docstring.__path__[0], 1)
        self.statusMessage('Docsets list from %s' % \
                           happydoclib.docset.__path__[0], 1)
        self.statusMessage('Formatters from %s' % \
                           happydoclib.formatter.__path__[0], 1)

        #
        # Set default parser params
        #
        parser_params = {
            'docStringFormat':'StructuredText',
            }
        #
        # Find parser arguments
        #
        self.statusMessage('Looking for parser parameters', 2)
        args, user_supplied_parser_params = happydoclib.optiontools.getParameters(
            'parser', args)
        parser_params.update(user_supplied_parser_params)
        self.statusMessage('DEBUG: Parser parameters:', 4)
        for p, v in parser_params.items():
            self.statusMessage('DEBUG: \t%s:%s' % (p,v), 4)
                      
        #
        # Find DocSet arguments
        #
        self.statusMessage('Looking for docset parameters', 2)
        args, docset_params = happydoclib.optiontools.getParameters('docset', args)
        self.statusMessage('DEBUG: Docset parameters:', 4)
        for p, v in docset_params.items():
            self.statusMessage('DEBUG: \t%s:%s' % (p,v), 4)
            
        #
        # Find Formatter parameters
        #
        self.statusMessage('Looking for formatter parameters', 2)
        args, formatter_params = happydoclib.optiontools.getParameters('formatter', args)
        self.statusMessage('DEBUG: Formatter parameters:', 4)
        for p, v in formatter_params.items():
            self.statusMessage('DEBUG: \t%s:%s' % (p,v), 4)
            
        #
        # Get the list of modules to input
        #
        if not args:
            #
            # No files specified, print a help message and exit.
            #
            self.showHelp('Specify input file(s) to be processed.')
            raise self.HelpRequested, 'No input file(s) specified.'
        else:
            input_modules = []
            for input_module_name in args:
                input_modules.append(os.path.normcase(input_module_name))
        
        #
        # Create output directory
        #
        if not self.output:
            od = self.output_directory
            self.statusMessage('Output directory is %s' % self.output_directory, 2)
            if (od[0] != '/'):
                od = happydoclib.path.join( happydoclib.path.cwd(), od )
                self.statusMessage('Setting output directory to %s' % od, 2)
            od = happydoclib.path.normpath(od)
            self.statusMessage('Creating output directory %s' % od, 2)
            happydoclib.path.rmkdir(od)
            self.output_directory = od
            
        #
        # Create the docset
        #
        docset_init_params = {

            'formatterFactory':self.formatter_factory,
            'parserFunc':self.parser_function,
            'defaultParserConfigValues':parser_params,
            'inputModuleNames':input_modules,
            
            'author':self.author_name,
            'outputBaseDirectory':self.output_directory,
            'descriptionFilename':self.package_description_file,
            'formatterParameters':formatter_params,
            'ignoreDirFunc':self.ignoreDirectoryTest,
            'includeComments':self.include_comments,
            'includePrivateNames':self.include_private_names,
            'statusMessageFunc':self.statusMessage,
            'title':self.docset_title,
            'useRecursion':self.recurse_into_subdirs,

            }
        docset_init_params.update(docset_params)
        parsed_modules = apply( self.docset_factory, (), docset_init_params)
        #
        # Tell the docset to output its results
        #
        parsed_modules.write()
        #
        # Clean up
        #
        parsed_modules = None
        return

