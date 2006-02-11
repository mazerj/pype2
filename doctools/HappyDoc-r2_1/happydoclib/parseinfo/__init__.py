#!/usr/bin/env python
#
# $Id: __init__.py,v 1.8 2002/08/24 19:53:54 doughellmann Exp $
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

"""Extract information from a Python code parse tree.

    This module is based on the Demos/parser/example.py module
    distributed with the Python source distribution.


  File-specific Parser Configuration Values

    Parameters to the HappyDoc Parser can also be embedded within the
    first comment block of the module.  The parameter values
    recognized and their meanings are listed below.

    To provide file-specific parser configuration settings, any Python
    code can be embedded in the comments of the file.  For example::

      #!/usr/bin/env python
      #
      # HappyDoc:# These variables should be discovered.
      # HappyDoc:TestInt=1
      # HappyDoc:TestString="String"
      # HappyDoc:TestStringModule=string.strip(' this has spaces in front and back ')
      # HappyDoc:url=urlencode({'a':'A', 'b':'B'})
      # HappyDoc:docStringFormat='StructuredText'

    All lines beginning with the pattern "'# HappyDoc:'" will be
    concatenated (separated by newlines) and 'execed'.  The local
    namespace resulting from the execution of the code will be
    examined for variables of interest to the parser.  The incoming
    global namespace for the configuration code will have a few
    pre-populated names for convenience.

    Pre-defined Globals

      |------------------------------------------------------------------|
      | Name             | Description                                   |
      |==================================================================|
      | string           | The 'string' module.                          |
      |------------------------------------------------------------------|
      | urlquote         | Same as 'urllib.quote' function.              |
      |------------------------------------------------------------------|
      | urlencode        | Same as 'urllib.urlencode' function.          |
      |------------------------------------------------------------------|
    
    Recognized Parser Configuration Variables

      |------------------------------------------------------------------|
      | Parameter        | Description                                   |
      |==================================================================|
      | docStringFormat  | The name of the format for the '__doc__'      |
      |                  | strings in the module.  This value is used    |
      |                  | to determine the docstring converter which    |
      |                  | will know how to translate the docstrings in  |
      |                  | the module.                                   |
      |------------------------------------------------------------------|

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: __init__.py,v $',
    'rcs_id'       : '$Id: __init__.py,v 1.8 2002/08/24 19:53:54 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Sun, 11-Nov-2001 10:44:25 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.8 $',
    'date'         : '$Date: 2002/08/24 19:53:54 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import parser
import types

#
# Import Local modules
#
import happydoclib
import happydoclib.parsecomments
import happydoclib.path

from happydoclib.parseinfo.moduleinfo import ModuleInfo

from happydoclib.StreamFlushTest import StreamFlushTest

#
# Module
#

def getDocs(parent, fileName, includeComments=1, defaultConfigValues={}):
    """Retrieve information from the parse tree of a source file.

    Parameters
    
      fileName --
        Name of the file to read Python source code from.

      includeComments=1 --
        Flag to indicate whether comments should be parsed for
        cases where __doc__ strings are not available.
        
    """
    happydoclib.TRACE.into('parseinfo', 'getDocs',
                           parent=parent,
                           fileName=fileName,
                           includeComments=includeComments,
                           defaultConfigValues=defaultConfigValues,
                           )
    f = open(fileName)
    #
    # Read file and add an extra newline to fix problem
    # reported with files containing only a single docstring
    # line.
    #
    source = f.read()
    source = '\n'.join(source.split('\r\n')) + '\n'
    f.close()
    base_filename = happydoclib.path.basename(happydoclib.path.splitext(fileName)[0])
    try:
        ast = parser.suite(source)
    except parser.ParserError, msg:
        #
        # Catch parse exception and retry with the
        # compile function which produces better user
        # error messages.
        #
        code = compile(source, fileName, 'exec')
        #
        # In case the compile module can do something,
        # just re-raise the exception we got from the
        # parser.
        #
        raise
    except TypeError, msg:
        raise TypeError(msg, source)
        
    tup = parser.ast2tuple(ast)
    if includeComments:
        comment_info = happydoclib.parsecomments.extractComments(source)
    else:
        comment_info = {}
    happydoclib.TRACE.write('Creating ModuleInfo')
    mod_info = ModuleInfo(parent=parent,
                          tree=tup,
                          name=base_filename,
                          fileName=fileName,
                          commentInfo=comment_info,
                          defaultConfigValues=defaultConfigValues)
    happydoclib.TRACE.outof(mod_info)
    return mod_info




################################################################################


class ParserUnitTest(StreamFlushTest):

    default_filename = './TestCases/test.py'
    filename_map = {
        'testExtractVariablesFromModule':'./TestCases/test_variable_extraction.py',
        'testExtractVariablesFromModuleWithException':'./TestCases/test_variable_extraction_with_exception.py',
        'testVariousImportStatements':'./TestCases/test_import_statements.py',
        'testIgnoreComments':'TestCases/test_ignore_comments.py',
        'testDecoratedComments':'TestCases/test_decorated_comments.py',
        'testDOSFiles':'TestCases/test_bug434946.py',
        'testEmptyModule':'TestCases/emptytest.py',
        'testFunctionParameters':'TestCases/test_function_params.py',
        'testNestedClasses':'TestCases/test_nested_structures.py',
        'testNestedFunctions':'TestCases/test_nested_structures.py',
        }
    include_comments = {
        'testIgnoreComments':0,
        }

    def setUp(self):
        name = self.name
        filename = self.filename_map.get(name, self.default_filename)
        comments_flag = self.include_comments.get(name, 1)
        self.filename = filename
        self.parsed_module = getDocs(None, filename, includeComments=comments_flag)
        return

    def _docStringsAreEqual(self, ds1, ds2):
        if not ds1 and not ds2:
            return 1
        if cmp(ds1, ds2):
            return 0
        else:
            return 1

    def _testComparison(self, full_name, name, importedInfo, parsedInfo, allowedFailures=[]):
        if name[:2] == '__':
            # Ignore private names
            return

        #
        # Get the thing from the imported module
        #
        obj = getattr(importedInfo, name)
        
        if type(obj) == types.IntType:
            return
        
        elif type(obj) == types.ClassType:
            if name not in parsedInfo._class_info.keys():
                if name in allowedFailures:
                    return
            assert name in parsedInfo._class_info.keys(), \
                   'Did not find class docs for %s' % full_name
            try:
                aClass = parsedInfo[name]
            except KeyError:
                self.fail('Did not find class info for %s' % full_name)
            #
            # Verify the class info docstring matches the parser results
            #
            assert self._docStringsAreEqual(aClass._docstring, obj.__doc__), \
                   'Docs for class %s do not match (imported "%s", parsed "%s")' % \
                   (full_name, obj.__doc__, aClass._docstring)
            #
            # Recurse to look at methods
            #
            # Importing results in more names than
            # parsing, so this does not work.
            #
            #for attr_name in dir(obj):
            #    self._testComparison('%s.%s' % (full_name, attr_name),
            #                         attr_name,
            #                         obj,
            #                         aClass,
            #                         allowedFailures
            #                         )
                    
        elif type(obj) == types.MethodType:
            assert name in parsedInfo._function_info.keys(), \
                   'Did not find method info for %s' % full_name
            aMethod = parsedInfo[name]
            assert self._docStringsAreEqual(aMethod._docstring, obj.__doc__), \
                   'Docs for method %s do not match (imported "%s", parsed "%s")' % \
                   (full_name, obj.__doc__, aMethod._docstring)

        elif type(obj) == types.FunctionType:
            if name not in parsedInfo._function_info.keys():
                if name in allowedFailures:
                    return
            assert name in parsedInfo._function_info.keys(), \
                   'Did not find func info for %s' % full_name
            aFunc = parsedInfo[name]
            assert self._docStringsAreEqual(aFunc._docstring, obj.__doc__), \
                   'Docs for func %s do not match (imported "%s", parsed "%s")' % \
                   (full_name, obj.__doc__, aFunc._docstring)
            
            
        else:
            assert obj, 'Got %s for %s' % (obj, full_name)
        return

    def testBasicParser(self):
        package_name = 'TestCases.test'
        temp_locals = {}
        imported_module = __import__(package_name, globals(), temp_locals)
        assert imported_module, 'Could not import %s' % filename
        test_module = imported_module.test

        for name in dir(test_module):
            full_name = '%s.%s' % (package_name, name)
            self._testComparison(full_name, name, test_module, self.parsed_module,
                                 ['OuterClass', 'OuterFunction', 'TestApp',
                                  'ISTERMINAL', 'ISNONTERMINAL', 'ISEOF', 'main',
                                  'appInit'
                                  ])
        return
    
#     def testExtractVariablesFromModule(self):
#         expected_values = {
#             'TestInt':1,
#             'TestString':"String",
#             'TestStringModule':"this has spaces in front and back",
#             'url': 'b=B&a=A',
#             }
#         module_values = self.parsed_module.getConfigurationValues()

#         if self.verboseLevel.get() > 1:
#             print 'Module variables for %s' % self.filename
#             import pprint
#             pprint.pprint(module_values)

#         assert (module_values == expected_values), 'Did not find expected variables'
#         return

    def testExtractVariablesFromModuleWithException(self):
        module_values = self.parsed_module.getConfigurationValues()
        assert not module_values, 'Did not find expected exception'
        return

    def testVariousImportStatements(self):
        expected_import_data =  [
            ('CommandLineApp', None),
            ('CommandLineApp', ['TestApp', 'SubClassTestApp']),
            ('Module1', None),
            ('Module2', ['Symbol1']),
            ('Package1.SubModule1', None),
            ('Package2.SubModule2', ['Symbol2']),
            ('Package3.SubModule3', ['Symbol3']),
            ('a.b', ['c', 'd']),
            ('cgi', None),
            ('one.two', None),
            ('os', None),
            ('prettyast', ['astListFixNames']),
            ('string', None),
            ('string', ['strip']),
            ('sys', ['path']),
            ('token', ['*']),
            ('types', None),
            ('webbrowser', None),
            ]
        import_data = self.parsed_module.getImportData()
        import_data.sort()
        assert import_data, 'No imports were found.'
        for expected, actual in map(None, expected_import_data, import_data):
            if not expected or not actual:
                break
            assert expected == actual, 'Import values do not match %s vs. %s' % \
                   (expected, actual)
        assert import_data == expected_import_data, 'Did not find expected values, got %s instead' % str(import_data)
        return
    
    def testIgnoreComments(self):
        assert not self.parsed_module._comments, \
               'Did not ignore module comments %s' % self.filename
        assert self.parsed_module._docstring, \
               'Did not find docstring for module %s' % self.filename
        
        c = self.parsed_module['WithComments']
        assert not c._comments, \
               'Did not ignore comments in class WithComments'
        assert not c._docstring, \
               'Found unexepcted docstring for class WithComments'

        method = c['__init__']
        assert not method._comments, \
               'Did not ignore comments in method WithComments.__init__'
        assert not method._docstring, \
               'Found unexpected docstring for method WithComments.__init__'
 
        c = self.parsed_module['WithoutComments']
        assert not c._comments, \
               'Found unexepected comments for class WithoutComments'
        assert c._docstring, \
               'Did not find docstring for class WithoutComments'

        method = c['__init__']
        assert not method._comments, \
               'Found unexpected comments for method WithoutComments.__init__'
        assert method._docstring, \
               'Did not find docstring for method WithoutComments.__init__'
        
        return

    def testDecoratedComments(self):
        module = self.parsed_module
        assert module['Hashes']._comments == ' \n \n Func with hash lines\n \n \n', \
               'Did not find expected comment for Hashes'
        
        assert module['Dashes']._comments == ' \n Func with dash lines\n \n', \
               'Did not find expected comment for Dashes'
        
        assert module['Equals']._comments == ' \n Func with equal lines\n \n', \
               'Did not find expected comment for Equals'
        
        assert module['Mixed']._comments == ' \n Func with mixed dashes and equals\n \n', \
               'Did not find expected comment for Mixed'

        expected_for_stt = """ 
 This function has, in the comments about it, a table.  That table
 should be rendered via STNG to an HTML table in the test output.
 
  |-------------------------------------------------|
  | Function  | Documentation                       |
  |=================================================|
  | '__str__' | This method converts the            |
  |           |  the object to a string.            |
  |           |                                     |
  |           | - Blah                              |
  |           |                                     |
  |           | - Blaf                              |
  |           |                                     |
  |           |       |--------------------------|  |
  |           |       |  Name   | Favorite       |  |
  |           |       |         | Color          |  |
  |           |       |==========================|  |
  |           |       | Jim     |  Red           |  |
  |           |       |--------------------------|  |
  |           |       | John    |  Blue          |  |
  |           |       |--------------------------|  |
  |-------------------------------------------------|
 
"""
        
        assert module['StructuredTextTable']._comments == expected_for_stt, \
               'Did not find expected comment for StructuredTextTable'
 
        return
        
    def testDOSFiles(self):
        assert self.parsed_module, 'Did not retrieve any data from %s' % self.filename
        assert self.parsed_module['DefaultClassInst']._docstring, \
               'Did not get docstring from DefaultClassInst'
        assert self.parsed_module['DefaultClassInst']._docstring.find('\r') < 0, \
               'Did not strip carriage returns from docstring for DefaultClassInst'
        return
    
    def testEmptyModule(self):
        assert not self.parsed_module._class_info.items(), 'Found unexpected classes'
        assert not self.parsed_module._function_info.items(), 'Found unexpected functions'
        return

    def testFunctionParameters(self):
        m = self.parsed_module
        f = m['example_function_with_args']
        assert f, 'Did not get function information for example_function_with_args'
        expected_parameter_names = ( 'arg1',
                                     'arg2',
                                     'arg3withDefault',
                                     'arg3aWithDefault',
                                     'arg3bWithDefault',
                                     'arg4DefaultInt',
                                     'arg5DefaultTuple',
                                     'arg6DefaultList',
                                     'arg7DefaultNone',
                                     'arg8DefaultName',
                                     'arg9DefaultInstance',
                                     'arg10DefaultInstanceWithParams',
                                     'negativeIntArg',
                                     'floatArg',
                                     'negativeFloatArg',
                                     'mathArg',
                                     'stringArgWithHTML',
                                     )
        expected_parameter_info = {
            'arg1': (None, None, None),
            'arg2': (None, None, None),
            'arg3withDefault': (1, "'hi there'", None),
            'arg3aWithDefault': (1, '"\'hi again\'"', None),
            'arg3bWithDefault': (1, '\'"hi there again"\'', None),
            'arg4DefaultInt': (1, '101', None),
            'arg5DefaultTuple': (1, '( 1, 2 )', None),
            'arg6DefaultList': (1, '[ 3, 4 ]', None),
            'arg7DefaultNone': (1, 'None', None),
            'arg8DefaultName': (1, 'foo', None),
            'arg9DefaultInstance': (1, 'DefaultClassInst()', None),
            'arg10DefaultInstanceWithParams': (
            1, "DefaultClassInstWithParams(1, 2, ( 'tuple', 'param' ), [ 'list', 'param' ] )", None),
            'negativeIntArg': (1, '-1', None),
            'floatArg': (1, '1.2', None),
            'negativeFloatArg': (1, '-3.4', None),
            'mathArg': (1, '1 + 2', None),
            'stringArgWithHTML': (1, "'<h1>Hi, Dick & Jane!</h1>'", None),
            }
        actual_parameter_names = f.getParameterNames()
        assert actual_parameter_names, 'Did not get any parameter names.'
        assert actual_parameter_names == expected_parameter_names, \
               'Actual parameter names (%s) do not match expected (%s)' % \
               (actual_parameter_names, expected_parameter_names)

        for n in actual_parameter_names:
            parameter_info = f.getParameterInfo(n)
            assert parameter_info, 'Got no parameter info for %s' % n
            try:
                expected_info = expected_parameter_info[n]
            except KeyError:
                self.fail('Unexpected parameter %s found' % n)
            assert parameter_info == expected_info, \
                   'Parameter info for %s does not match expected. %s vs %s' % (
                str(parameter_info),
                str(expected_info),
                )
        return

    def testNestedClasses(self):
        m = self.parsed_module
        try:
            c = m['OuterClass']
        except KeyError:
            self.fail('Could not retrieve class "OuterClass"')
        assert c.getName() == 'OuterClass', \
               'Name of class does not match expected value.'
        
        try:
            ic1 = c['InnerClass']
        except KeyError:
            self.fail('Could not retrieve class "InnerClass" from OuterClass')
        else:
            assert ic1._docstring == """This class is inside of OuterClass.

        This class is nested one level deep.
        """, \
            'Docstring for InnerClass does not match'

            
        try:
            ic2 = ic1['InnerClass2']
        except KeyError:
            self.fail('Could not retrieve class "InnerClass2" from InnerClass')
        else:
            assert ic2._docstring == """This class is inside of InnerClass.

            This class is nested two levels deep.
            """, \
            'Docstring for InnerClass2 does not match'
            
        return

    def testNestedFunctions(self):
        m = self.parsed_module
        try:
            f = m['OuterFunction']
        except KeyError:
            self.fail('Could not retrieve function "OuterFunction"')

        try:
            if1 = f['InnerFunction']
        except KeyError:
            self.fail('Could not retrieve inner function "InnerFunction"')
        else:
            assert if1._docstring == "This function is inside of OuterFunction.", \
                   'Docstring for InnerFunction does not match.'

        try:
            if2 = if1['InnerFunction2']
        except KeyError:
            self.fail('Could not retrieve inner function "InnerFunction2"')
        else:
            assert if2._docstring == "This function is inside of InnerFunction.", \
                   'Docstring for InnerFunction2 does not match.'

        return
