#!/usr/bin/env python
#
# COPYRIGHT
#
#   Permission to use, copy, modify, and distribute this software and
#   its documentation for any purpose and without fee is hereby
#   granted, provided that the above copyright notice appear in all
#   copies and that both that copyright notice and this permission
#   notice appear in supporting documentation, and that the name of Doug
#   Hellmann not be used in advertising or publicity pertaining to
#   distribution of the software without specific, written prior
#   permission.
# 
# DISCLAIMER
#
#   DOUG HELLMANN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
#   INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
#   NO EVENT SHALL DOUG HELLMANN BE LIABLE FOR ANY SPECIAL, INDIRECT OR
#   CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
#   OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
#   NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
#   CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# 


"""Define a class to handle pluggable module loading.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name':'$RCSfile: pluginloader.py,v $',
    'creator':'Doug Hellmann <doug@hellfly.net>',
    'project':'HappyDoc',
    'created':'Sat, 03-Jun-2000 19:23:48 EDT',
    #
    #  Current Information
    #
    'author':'$Author: doughellmann $',
    'version':'$Revision: 1.4 $',
    'date':'$Date: 2002/03/31 22:15:35 $',
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
import sys
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import traceback
import UserDict

#
# Import Local modules
#
import happydoclib.path
from happydoclib.trace import trace as TRACE

#
# Module
#

class PluginException(Exception):

    def __init__(self, wrappedException, pluginName):
        self._plugin_name = pluginName
        self._wrapped_exception = wrappedException
        return

    def __str__(self):
        return 'Problem with %s\n%s' % (self._plugin_name,
                                        self._wrapped_exception)

#
# Where is the application installed?
#
APP_HOME_DIR=happydoclib.path.dirname( sys.argv[0] )
sys.path.append(APP_HOME_DIR)

class PluginLoader(UserDict.UserDict):
    """A class to handle pluggable module loading."""
    
    def __init__(self, moduleName, modulePath, parentModulePrefix):
        """Create a PluginLoader.

        Parameters

          moduleName -- The imported module, from which we get name, path,
          etc. to find the sub-modules.

          modulePath -- The path to the module, and therefore the
          parent directory of the plugins.

          parentModulePrefix -- The prefix of parent names to be added
          to moduleName.  For example 'happydoclib'.
          
        """
        TRACE.into('PluginLoader', '__init__',
                   moduleName=moduleName,
                   modulePath=modulePath,
                   parentModulePrefix=parentModulePrefix)
        #
        # Initialize the base class
        #
        UserDict.UserDict.__init__(self)
        #
        # Name for these plugins
        #
        module_name_parts = moduleName.split('.')
        if len(module_name_parts) > 1:
            moduleName = '.'.join( module_name_parts[1:] )
        self.plugin_set_name = moduleName
        #print '\n*** Initializing plugin set %s' % self.plugin_set_name
        #
        # Where the plugins will be
        #
        self.plugin_dir = modulePath
        #print '  From %s' % self.plugin_dir
        #
        # Name to add before importing
        #
        self.parent_module_prefix = parentModulePrefix
        #
        # List of plugins
        #
        _module_list = self.getModuleList()
        _module_list.sort()
        #
        # Load the modules
        #
        for _module_name in _module_list:
            TRACE.into('PluginLoader', '__init__:Loop',
                                   _module_name=_module_name,
                                   )
            module_name_parts = _module_name.split(os.sep)
            module_base_name = module_name_parts[-1]
            plugin_set_name = module_name_parts[-2]
            if plugin_set_name != self.plugin_set_name:
                print 'EEEE Got local plugin set name "%s" instead of "%s"' % \
                      (plugin_set_name, self.plugin_set_name)
            parent_package_name = module_name_parts[-3]
            TRACE.writeVar(parent_package_name=parent_package_name)

            _module_name = happydoclib.path.basename(_module_name)
            if self.parent_module_prefix:
                _import_name = '%s.%s.%s' % (self.parent_module_prefix,
                                             plugin_set_name,
                                             module_base_name)
            else:
                _import_name = '%s.%s' % (plugin_set_name, module_base_name)
            TRACE.writeVar(_import_name=_import_name)
            
            try:
                TRACE.write('Importing %s' % _import_name)
                _module = __import__( _import_name )
            except Exception, msg:
                if int(os.environ.get('PLUGIN_DEBUG', '0')):
                    buffer = StringIO()
                    buffer.write('\n--- Plugin Module Error ---\n')
                    traceback.print_exc(file=buffer)
                    TRACE.into('PluginLoader' 'Plugin module error',
                               _import_name=_import_name)
                    TRACE.write(buffer.getvalue())
                    TRACE.outof()
                    buffer.write('---------------------------\n\n')
                    TRACE.outof()
                    raise PluginException( buffer.getvalue(), _import_name )
                elif int(os.environ.get('PLUGIN_SILENT_ERRORS', '0')):
                    TRACE.outof()
                    continue
                else:
                    sys.stderr.write('\n--- Plugin Module Error ---\n')
                    traceback.print_exc()
                    sys.stderr.write('---------------------------\n\n')
                    TRACE.outof()
                    continue

            import_name_parts = _import_name.split('.')
            for sub_module in import_name_parts[1:]:
                try:
                    _module = getattr(_module, sub_module)
                except AttributeError:
                    sys.stderr.write('ERROR: Could not retrieve %s from %s\n' % \
                                     (sub_module, _module.__name__))
                    raise
                
            try:
                info = _module.entryPoint()
            except AttributeError:
                sys.stderr.write('ERROR: Could not call entryPoint() from %s\n' % _import_name)
                sys.stderr.write('%s\n' % dir(_module))
                raise
            else:
                self.addEntryPoint(info)

            TRACE.outof()

        TRACE.outof()
        return

    def getModuleList(self):
        "Return a list of module names to be used as plugins."
        glob_pattern = happydoclib.path.join( self.plugin_dir,
                                              '%s_*' % self.plugin_set_name,
                                              )
        all_files = glob.glob(glob_pattern)
        all_basenames = [ os.path.splitext(x)[0] for x in all_files]
        unique_modules = []
        for module in all_basenames:
            if module not in unique_modules:
                unique_modules.append(module)
        return unique_modules
    
    def addEntryPoint(self, infoDict):
        """Add an entry point into a module to our lookup tables.

        This method must be implemented by the subclass.
        """
        raise 'Not implemented for %s' % self.__class__.__name__

    
if __name__ == '__main__':
    import os
    os.chdir('TestCases/test_plugin_loader')
    import sys
    sys.path.append( os.getcwd() )
    import runtest
