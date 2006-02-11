#!/usr/bin/env python
#
# $Id: imports.py,v 1.1 2001/11/11 18:51:37 doughellmann Exp $
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

"""Collects info about imports for a module.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: imports.py,v $',
    'rcs_id'       : '$Id: imports.py,v 1.1 2001/11/11 18:51:37 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Sun, 11-Nov-2001 10:51:52 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.1 $',
    'date'         : '$Date: 2001/11/11 18:51:37 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#


#
# Import Local modules
#


#
# Module
#

class ImportInfo:
    """Collects info about imports for a module.
    """

    def __init__(self):
        self._straight_imports = []
        self._named_imports = {}
        return

    def addImport(self, moduleName, symbolName=None, asName=None):
        """Add information about an import statement to the saved info.

        Parameters

          moduleName -- The name of the module involved in the import.
          For example, in 'from X import Y', X is the moduleName and
          in 'import A.B', A.B is the moduleName.

          symbolName -- The name of the symbol being imported.  For
          example, in 'from X import Y', Y is the symbolName.

          asName -- The name within the module by which symbolName can
          be referenced.  Usually, this is the same as symbolName, but
          by using the 'import X as Y' syntax, the name can be changed.
          
        """
        dbg=0
        
        if symbolName:
            #if dbg: print '\nIMPORT SYMBOL %s from MODULE %s' % (symbolName, moduleName)
            name_list = self._named_imports.get(moduleName, [])
            if symbolName not in name_list:
                #if dbg: print '\t*** added'
                name_list.append(symbolName)
                self._named_imports[moduleName] = name_list
                
        else:
            #if dbg: print '\nIMPORT MODULE: %s' % moduleName
            if moduleName not in self._straight_imports:
                #if dbg: print '\t*** added'
                self._straight_imports.append(moduleName)
        #if dbg:
        #    print 'STRAIGHT: ',
        #    pprint.pprint(self._straight_imports)
        #    print 'NAMED: ',
        #    pprint.pprint(self._named_imports)
        #    print 'CURRENT IMPORTS: ', self.items()
        return
    
    def importedSymbols(self, moduleName):
        if self._named_imports.has_key(moduleName):
            return self._named_imports[moduleName]
        else:
            raise ValueError('No symbols imported for module', moduleName)
        return

    def __str__(self):
        return '(%s)' % string.join( map(str, self.items()),
                                     '\n'
                                     )
    
    def items(self):
        """Returns a sequence of tuples containing module names and the
        symbols imported from them.
        """
        all_names = self._straight_imports[:]
        for name in self._named_imports.keys():
            if name not in all_names:
                all_names.append(name)
        all_names.sort()
        all_items = []
        for name in all_names:
            if name in self._straight_imports:
                all_items.append( (name, None) )
            if self._named_imports.has_key(name):
                all_items.append( (name, self._named_imports[name]) )
        return all_items

