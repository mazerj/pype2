#!/usr/bin/env python
#
# $Id: moduleinfo.py,v 1.3 2002/08/04 12:06:50 doughellmann Exp $
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

"""Information gatherer for source code modules.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: moduleinfo.py,v $',
    'rcs_id'       : '$Id: moduleinfo.py,v 1.3 2002/08/04 12:06:50 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Sun, 11-Nov-2001 10:52:52 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.3 $',
    'date'         : '$Date: 2002/08/04 12:06:50 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import pprint
import re
import string
import sys
import traceback
import urllib

#
# Import Local modules
#
import happydoclib
from happydoclib.parseinfo.classinfo import ClassInfo
from happydoclib.parseinfo.functioninfo import SuiteFuncInfo, FunctionInfo
from happydoclib.parseinfo.suite import SuiteInfoBase
from happydoclib.parseinfo.imports import ImportInfo
from happydoclib.parseinfo.utils import *

#
# Module
#

class ModuleInfo(SuiteInfoBase, SuiteFuncInfo):
    """Information gatherer for source code modules.

    Extract information about a source module from
    its parse tree.
    """
    
    def __init__(self,
                 parent,
                 tree,
                 name = "<string>",
                 fileName = None,
                 commentInfo = {},
                 defaultConfigValues={},
                 ):
        """Initialize the info extractor.

        Parameters:

            tree -- parse tree from which to extract information

            name -- name of the module

            fileName -- name of the file containing the module

            commentInfo -- comments extracted from the file

        """
        happydoclib.TRACE.into('ModuleInfo', '__init__',
                               parent=parent,
                               tree=tree,
                               name=name,
                               fileName=fileName,
                               commentInfo=commentInfo,
                               defaultConfigValues=defaultConfigValues,
                               )
        self._filename = fileName
        SuiteInfoBase.__init__(self, name, parent, fileName, tree,
                               commentInfo=commentInfo,
                               defaultConfigValues=defaultConfigValues)
        if tree:
            #
            # Look for doc string
            #
            found, vars = match(DOCSTRING_STMT_PATTERN, tree[1])
            if found:
                self._docstring = vars["docstring"]
            #
            # Look for imported modules
            #
            self._import_info = self._extractImportedModules(tree)

        happydoclib.TRACE.outof()
        return

    ##
    ## Internal data extraction
    ##

    def _extractConfigurationValues(
        self,
        matchConfigValue=re.compile('^#\s*HappyDoc:(.+)$', re.IGNORECASE).match,
        ):
        """Look into the module source file and extract HappyDoc configuration values.

        Variables can be embedded in the first comment block of the module.
        """

        body = open(self._filename, 'rt').read()
        lines = body.split('\n')
        config_statement = ''
        
        for l in lines:
            l = l.strip()
            if not l:
                break
            if l[0] != '#':
                break
            match = matchConfigValue(l)
            if match:
                config_statement = '%s\n%s' % (config_statement, match.group(1))
                
        #
        # Exec puts in values from the builtin modules to set up the
        # namespace.  That means we don't want to use our
        # configuration value table for global and local names, so we
        # create (and use) a dummy table here.  We can pre-populate
        # it with a few modules we think the user should be allowed
        # to call.
        #
        global_namespace = {
            'string':string,
            'urlquote':urllib.quote,
            'urlquote_plus':urllib.quote_plus,
            'urlencode':urllib.urlencode,
            }
        local_namespace = {
            }
        try:
            exec config_statement in global_namespace, local_namespace
        except:
            sys.stderr.write('\n--- Parser Config Value Extraction Error ---\n')
            traceback.print_exc()
            sys.stderr.write('--------------------------------------------\n\n')
        else:
            self._configuration_values.update(local_namespace)
        return

    def _extractImportedModules(self, tree):
        """Returns modules imported by code in tree.
        
        Scan the parse tree for import statements
        and return the names of all modules imported.
        """
        dbg=0
        IMPORT_STMT_WITH_LIST_PATTERN =(
            symbol.stmt,
            (symbol.simple_stmt,
             (symbol.small_stmt,
              ['import_stmt']
              ),
             (token.NEWLINE, '')
             )
            )
        imported_modules = ImportInfo()
        for subtree in tree[1:]:
            #if dbg: print '\nNEW IMPORT SUBTREE'
            found, vars = match(IMPORT_STMT_WITH_LIST_PATTERN, subtree, dbg=dbg)
            #if dbg:
            #    print 'found:', found
            #    if found:
            #        print 'vars: ',
            #        pprint.pprint(vars)
            if found:
                # vars['import_stmt'] should be an import statement
                # in one of several different forms
                import_stmt = vars['import_stmt']
                if import_stmt[0] == symbol.import_stmt:
                    
                    first = import_stmt[1]
                    
                    if (first[0] == token.NAME) and (first[1] == 'import'):
                        
                        for import_module in import_stmt[2:]:

                            try:
                                if import_module[0] == symbol.dotted_as_name:
                                    #if dbg: print 'Collapsing dotted_as_name'
                                    import_module = import_module[1]
                            except AttributeError:
                                #
                                # Must be using python < 2.0
                                #
                                pass
                            
                            if import_module[0] == symbol.dotted_name:
                                # Get the tuples with the name
                                module_name_parts = import_module[1:]
                                # Get the strings in the 2nd part of each tuple
                                module_name_parts = map(lambda x: x[1],
                                                        module_name_parts)
                                # Combine the strings into the name
                                module_name = ''.join(module_name_parts)
                                #if dbg: print 'ADDING module_name=%s' % module_name
                                imported_modules.addImport(module_name)
                                
                    elif (first[0] == token.NAME) and (first[1] == 'from'):

                        #if dbg: print 'FROM ', import_stmt

                        x=import_stmt[2]
                        try:
                            if x[0] == symbol.dotted_name:
                                x = x[1:]
                        except AttributeError:
                            #
                            # Must be using python < 2.0
                            #
                            pass
                            
                        #if dbg: print 'from x import y'
                        module_name = parseTreeToString(x)
                        try:
                            symbol_list = imported_modules.importedSymbols(module_name)
                        except ValueError:
                            symbol_list = []
                        names = import_stmt[4:]
                        #if dbg: print 'NAMES: ', names
                        
                        for n in names:
                            if n[0] == token.NAME:
                                #symbol_list.append(n[1])
                                imported_modules.addImport(module_name, n[1])
                            elif n[0] == token.STAR:
                                #symbol_list.append('*')
                                imported_modules.addImport(module_name, '*')
                            elif n[0] == getattr(symbol, 'import_as_name', 9999):
                                # python 2.x "from X import Y as Z" feature
                                import_name = parseTreeToString(n[1])
                                imported_modules.addImport(module_name, import_name)
                                
                    #if dbg:
                    #    for part in import_stmt[1:]:
                    #        pprint.pprint(part)
            #if dbg: print 'ITERATION IMPORTS: ', imported_modules
        #if dbg: print 'FINAL IMPORTS: ', imported_modules, '\n'
        return imported_modules

    ##
    ##
    ##
                
    def getClassNames(self):
        "Return the names of classes defined within the module."
        return self._class_info.keys()

    def getClassInfo(self, name):
        "Return a ClassInfo object for the class by name."
        return self._class_info[name]

    def getCommentKey(self):
        return ()
    
    def getImportData(self):
        "Returns a list of which symbols are imported."
        return self._import_info.items()

#     def getReference(self, formatter, sourceNode):
#         "Return a reference to this module from sourceNode."
#         ref = formatter.getReference(self, sourceNode.name)
#         return ref

    def getReferenceTargetName(self):
        "Return the name to use as a target for a reference such as a hyperlink."
        #print 'PARSINFO: ModuleInfo::getReferenceTargetName(%s)' % self.getName()
        target_name = self.getName()
        if target_name == '__init__':
            #print 'PARSINFO: \tasking for parent'
            parent = self.getParent()
            if parent:
                #print 'PARSINFO: \tusing parent'
                target_name = parent.getReferenceTargetName()
            else:
                #print 'PARSINFO: \tusing name'
                target_name = self.getName()
        #print 'PARSINFO: \ttarget:%s' % target_name
        return target_name
