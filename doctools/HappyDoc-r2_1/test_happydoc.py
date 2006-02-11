#!/usr/bin/env python
#
# $Id: test_happydoc.py,v 1.88 2002/08/24 17:54:02 doughellmann Exp $
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

"""Driver for unit tests for HappyDoc.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: test_happydoc.py,v $',
    'rcs_id'       : '$Id: test_happydoc.py,v 1.88 2002/08/24 17:54:02 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'HappyDoc',
    'created'      : 'Sun, 13-Aug-2000 10:16:13 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.88 $',
    'date'         : '$Date: 2002/08/24 17:54:02 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import sys
import os
sys.path.append(os.getcwd())
import tempfile
import string
from glob import glob
import pprint
import unittest
    
#
# Local Modules
#
import happydoclib
from happydoclib.appclass import HappyDoc
from happydoclib.StreamFlushTest import StreamFlushTest, DEFAULT_OUTPUT_DIR
from happydoclib.StreamFlushTest import verboseLevel as globalVerboseLevel

WEB_CHECKER_DIR='../Python-2.2/Tools/webchecker/'

if os.path.exists(WEB_CHECKER_DIR) and (os.name == 'posix'):
    sys.path.append(WEB_CHECKER_DIR)
    import webchecker
    WEBCHECKER_AVAILABLE=1
else:
    WEBCHECKER_AVAILABLE=0

#
# Modules with tests
#
import happydoclib.docset.docset_MultipleFile
import happydoclib.happydocset
import happydoclib.happydocstring
import happydoclib.docstring
import happydoclib.docstring.docstring_ClassicStructuredText
import happydoclib.docstring.docstring_StructuredText
import happydoclib.docstring.docstring_RawText
import happydoclib.docstring.docstring_PlainText
import happydoclib.formatter.openoffice
import happydoclib.parseinfo
import happydoclib.trace

#
# Module
#
    
    
class HappyDocTestBase(StreamFlushTest):
    
    WEB_CHECKER = os.path.join(WEB_CHECKER_DIR, 'webchecker.py')

    def __init__(self, methodName='runTest', outputDir=DEFAULT_OUTPUT_DIR,
                 statusMessageFunc=None):
        StreamFlushTest.__init__(self, methodName, outputDir, statusMessageFunc)
        return

    def setUp(self):
        self.happydoc = os.path.join(os.curdir, 'happydoc')
        return

    def runHappyDoc(self, modules=(), extraArgs=(), useWebChecker=0):
        #
        # Fix up output directory variable
        #
        output_dir = self.output_dir
        happydoc = self.happydoc
        test_name = self.name
        output_dir = os.path.join(output_dir, test_name)
        #
        # Verbose level setting
        #
        if self.verboseLevel.get():
            verboseArgs = '-%s' % ('v' * self.verboseLevel.get())
        else:
            verboseArgs = '-q'
        #
        # Build the argument list for the command.
        #
        # We have to pay some attention to the
        # order in which values are added to the
        # list, to ensure all options are presented
        # before arguments (so getopt will not
        # interpret arguments as filenames)
        #
        argv = [ verboseArgs,
                 '-t', self.name,
                 '-d', output_dir,
                 '-i', 'TestCases',
                 '-i', 'tmp',
                 ] + \
                 \
                 list(extraArgs) + \
                 \
                 [ 'formatter_dateStampFiles=0',  # always different, breaks diff
                   ] + \
                   \
                   list(modules)

        #
        # Set up for the test.
        #
        
        try:
            
            if self.verboseLevel.get():
                print
                print
                print 'Arguments: ',
                pprint.pprint(argv)
                print
                
            exit_code = HappyDoc(argv).run()
            
        except HappyDoc.HelpRequested, msg:
            if msg:
                exit_code = 1

        #
        # Run webchecker to verify the links that were written to the
        # output.
        #
        if useWebChecker and WEBCHECKER_AVAILABLE:

            if self.verboseLevel.get():
                print
                print 'WebChecker:'
                print
            c = webchecker.Checker()
            c.setflags( checkext=0, verbose=2, nonames=1 )

            #
            # Work out the output prefix, if one was specified.  This is
            # used to determine the real root filename, since it will
            # also include the prefix value.
            #
            prefix = ''
            for extra_arg in extraArgs:
                try:
                    name, value = extra_arg.split('=')
                except ValueError:
                    pass
                else:
                    if name == 'formatter_filenamePrefix':
                        prefix = value
                        break
            
            url = os.path.join(output_dir, '%sindex.html' % prefix)
            c.addroot( url )
            c.run()
            c.report()
            assert not c.bad, "Link checker reports errors."
        
        #
        # Flush the output so watchers can keep up
        #
        sys.stdout.flush()
        sys.stderr.flush()
        return exit_code
    
class ExecuteHappyDocTest(HappyDocTestBase):

    """Tests involving external executions of HappyDoc.

    Separated the definitions of the test from the base class because
    unittest appears to duplicate tests if they are inherited.
    """

    #
    # Application tests
    #
    
    def testHelpSyntax(self):
        assert self.runHappyDoc( (),
                                 extraArgs=('-h',)
                                 ), 'Basic help syntax test failed.'
        return
 
    def testHelpManual(self):
        assert self.runHappyDoc( (),
                                 extraArgs=('--help',)
                                 ), 'Help manual generation test failed.'
        return
 
    def testUsageWhenNoArgs(self):
        assert self.runHappyDoc( (),
                                 extraArgs=()
                                 ), 'Usage message test failed.'
        return

    #
    # Formatter and docset tests
    #
    
    
    def testDocBookX(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases', 'test.py'),),
                                      extraArgs=('-F',
                                                 'docbookx')
                                      )
                ), 'Full self documentation in DocBookS format output test failed.'
        return
    
    def testHTMLSimple(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases', 'test.py'),),
                                      extraArgs=('-p', '-',),
                                      useWebChecker=1,
                                      )
                ), 'Basic single-file docset test failed.'
        return
    
    def testHTMLSimpleWithPackageDescriptionFiles(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases',
                                                    'test_package_summaries'),
                                       ),
                                      useWebChecker=1,
                                      )
                ), 'Basic docset test with package description files failed.'
        return
    
    def testSelfHTMLCompact(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases', 'test.py'),),
                                      extraArgs=('formatter_compactHTML=yes',),
                                      useWebChecker=1,
                                      )
                ), 'Full self documentation with compact output test failed.'
        return
    
    def testHTMLSingleFile(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases', 'test.py'),),
                                      extraArgs=('-p', '-', '-T', 'SingleFile'),
                                      useWebChecker=1,
                                      )
                ), 'Basic single-file docset test failed.'
        return
    
    def testHTMLSingleFileCompact(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases', 'test.py'),),
                                      extraArgs=('-p', '-', '-T', 'SingleFile',
                                                 'formatter_compactHTML=yes',
                                                 ),
                                      useWebChecker=1,
                                      )
                ), 'Basic single-file docset test failed.'
        return

    def testHTMLStdout(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases', 'test.py'),),
                                      extraArgs=('-T', 'StdOut'),
                                      )
                ), 'HTML to standard-output docset test failed.'
        return

    def testDashOStdOut(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases', 'test.py'),),
                                      extraArgs=('-o',)
                                      )
                ), 'HTML to standard-output docset test failed.'
        return

    def testText(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases', 'test.py'),),
                                      extraArgs=('-F', 'Text')
                                      )
                ), 'Text formatter test failed.'
        return

    def testTextStdout(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases', 'test.py'),),
                                      extraArgs=('-F', 'Text', '-T', 'StdOut')
                                      )
                ), 'Text to standard-output docset test failed.'
        return

    def testDia(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases', 'test_dia.py'), ),
                                      extraArgs=('--dia',)
                                      )
                ), 'Dia output test failed.'
        return

    def testImportsFromPackages(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases',
                                                    'test_import_packages_basic'),),
                                      useWebChecker=1,
                                      )
                ), 'Import from packages test failed.'
        return

    def testBasicImportsFromPackagesIgnorePackages(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases',
                                                    'test_import_packages'),),
                                      extraArgs=('docset_usePackages=0',), 
                                      useWebChecker=1,
                                      )
                ), 'Import from packages while ignoring package special handling test failed.'
        return

    def testOutputWithPrefix(self):
        assert (not self.runHappyDoc( (os.path.join('TestCases',
                                                    'test_import_packages_basic'),),
                                      extraArgs=('-p',
                                                 '',
                                                 'formatter_filenamePrefix=TESTPREFIX_'),
                                      useWebChecker=1,
                                      )
                ), 'Formatter output prefix test failed.'
        return 

    ##
    ## Full self documentation tests
    ##
    
    def testSelfHTML(self):
        assert (not self.runHappyDoc( (os.path.join(os.pardir, 'HappyDoc'),),
                                      useWebChecker=1,
                                      )
                ), 'Full self documentation test failed.'
        return
    
    def testSelfSGMLDocBookSingleFile(self):
        assert (not self.runHappyDoc( (os.path.join(os.pardir, 'HappyDoc'),),
                                      extraArgs=('-F',
                                                 'SGMLDocBook',
                                                 '-T',
                                                 'SingleFile'),
                                      )
                ), 'Full self documentation in SGMLDocBook format output test failed.'
        return
    
    def testSelfDocBookXSingleFile(self):
        assert (not self.runHappyDoc( (os.path.join(os.pardir, 'HappyDoc'),),
                                      extraArgs=('-F',
                                                 'docbookx',
                                                 '-T',
                                                 'SingleFile'),
                                      )
                ), 'Full self documentation in DocBookS format output test failed.'
        return
        

class OtherWorkingDirTest(HappyDocTestBase):

    def __init__(self,
                 methodName='runTest',
                 workingDir=os.curdir,
                 outputDir='DefaultTestOutputDir',
                 **nargs
                 ):
        #
        # Base class
        #
        output_dir = happydoclib.path.join(os.pardir, 'HappyDoc', outputDir)
        nargs['outputDir'] = output_dir
        nargs['methodName'] = methodName
        apply(HappyDocTestBase.__init__, (self,), nargs)
        #
        # This class
        #
        self.dir_stack = None
        self.working_dir = workingDir
        return

    def setUp(self):
        self.happydoc = os.path.join(os.pardir, 'HappyDoc', 'happydoc')
        return
    
    def runHappyDoc(self, *args, **nargs):
        self.pushDir()
        apply(HappyDocTestBase.runHappyDoc, (self,) + args, nargs)
        self.popDir()
        return

    def pushDir(self):
        self.dir_stack = (os.getcwd(), self.dir_stack)
        os.chdir(self.working_dir)
        return

    def popDir(self):
        if self.dir_stack:
            top, self.dir_stack = self.dir_stack
            os.chdir(top)
        return


    
class ExternalTest(HappyDocTestBase):

    def externalApp(self, command):
        ret = os.system('python %s' % command)
        assert not ret, 'External test command "%s" failed' % command

    def testPluginLoader(self):
        self.externalApp(os.path.join(os.curdir, 'TestCases',
                                      'test_plugin_loader',
                                      'runtest.py'))
        return


    
class ZopeTest(OtherWorkingDirTest):
    
    def testZopeFull(self):
        assert (not self.runHappyDoc( (os.path.join(os.pardir, 'Zope-2-CVS-src'),),
                                      )
                ), 'Zope full documentation test failed.'
        return
    
    def testZopeRoot(self):
        assert (not self.runHappyDoc( (os.path.join(os.pardir, 'Zope-2-CVS-src'),),
                                      extraArgs=('-r',))
                ), 'Zope full documentation test failed.'
        return

    def testGadflyParseError(self):
        assert (not self.runHappyDoc( (os.path.join(os.pardir,
                                                    'Zope-2-CVS-src',
                                                    'lib',
                                                    'python',
                                                    'Products',
                                                    'ZGadflyDA',
                                                    'gadfly',
                                                    'gfdb0.py',
                                                    ),),
                                      extraArgs=('-r',))
                ), 'Gadfly test with parse-error failed.'
        return

    def testZEOParseError(self):
        assert (not self.runHappyDoc( (os.path.join(os.pardir,
                                                    'Zope-2-CVS-src',
                                                    'lib',
                                                    'python',
                                                    'ZEO',
                                                    'zrpc.py',
                                                    ),),
                                      extraArgs=('-r',))
                ), 'ZEO test with parse-error failed.'
        return

    def testZopeWithSafePrefix(self):
        assert (not self.runHappyDoc( (os.path.join(os.pardir, 'Zope-2-CVS-src'),),
                                      extraArgs=('formatter_filenamePrefix=zsd_',))
                ), 'Zope test with output prefix failed.'
        return
        
        
        
def ZopeTestFactory(**nargs):
    nargs['workingDir'] = nargs.get('workingDir', os.path.join(os.pardir,
                                                               'Zope-2-CVS-src'))
    return apply(ZopeTest, (), nargs)



class HappyDocBugRegressionTest(HappyDocTestBase):

    def __init__(self,
                 methodName='',
                 outputDir='DefaultTestOutputDir',
                 ):
        HappyDocTestBase.__init__(self,
                              outputDir=outputDir,
                              methodName='testBugReport%s' % methodName)
        return

    def checkBugReport(self, bugId):
        print '\n%s: %s' % (bugId, os.getcwd())
        assert not self.runHappyDoc( (os.path.join(os.curdir, 'TestCases',
                                                   'test_bug%s.py' % bugId), ),
                                     extraArgs=('-p', '-'),
                                     ), 'Check for bug %s failed.' % bugId

    def __getattr__(self, name):
        prefix = 'testBugReport'
        prefix_len = len(prefix)
        if name[:prefix_len] == prefix:
            id = name[prefix_len:]
            test_func = lambda bug=id, s=self: s.checkBugReport(bug)
            test_func.__doc__ = 'Regression test for bug %s' % id
            return test_func
        raise AttributeError(name)


class HappyDocTestLoader(unittest.TestLoader):
    """Special TestLoader for HappyDoc

    This TestLoader subclass tell the TestCases it loads to write to a
    specific output directory, thereby letting us differentiate
    between standard test output and regression test output.
    """

    def __init__(self, outputDir='', statusMessageFunc=None, knownTestCaseClasses=[]):
        self.output_dir = outputDir
        self.status_message_func = statusMessageFunc
        self.known_classes = knownTestCaseClasses
        return

    def loadTestsFromTestCase(self, testCaseClass):
        """Return a suite of all tests cases contained in testCaseClass"""
        names = self.getTestCaseNames(testCaseClass)
        tests = []
        for n in names:
            try:
                test_case = testCaseClass(n,
                                          outputDir=self.output_dir,
                                          statusMessageFunc=self.status_message_func,
                                          )
            except TypeError:
                test_case = testCaseClass(n, outputDir=self.output_dir)
                
            tests.append(test_case)
        return self.suiteClass(tests)

    def loadTestsFromName(self, name, module=None):
        try:
            test_obj = unittest.TestLoader.loadTestsFromName(self, name, module)
            test_obj.status_message_func = self.status_message_func
            return test_obj
        except ImportError:
            for checking_class in self.known_classes:
                if name in self.getTestCaseNames(checking_class):
                    return self.suiteClass([
                        checking_class(name,
                                       outputDir=self.output_dir,
                                       statusMessageFunc=self.status_message_func)
                        ])
                

def addAllTests(test_loader, actual_test_suite):
    #
    # Load tests from modules we know contain tests
    #
    for m in (
        #
        # Supporting tools
        #
        happydoclib.CommandLineApp,
        happydoclib.indentstring,
        happydoclib.optiontools,
        happydoclib.trace,
        happydoclib.path,

        #
        # Foundation modules
        #
        happydoclib.parsecomments,
        happydoclib.parseinfo,
        happydoclib.happydocstring,
        happydoclib.happydocset,

        #
        # Docstring converters
        #
        happydoclib.docstring,
        happydoclib.docstring.docstring_ClassicStructuredText,
        happydoclib.docstring.docstring_StructuredText,
        happydoclib.docstring.docstring_RawText,
        happydoclib.docstring.docstring_PlainText,

        #
        # Formatters
        #
        happydoclib.formatter.fileformatterbase,
        happydoclib.formatter.openoffice,
        happydoclib.formatter.formatter_HTMLFile,

        #
        # Docsets
        #
        happydoclib.docset.docset_MultipleFile

        ):
        actual_test_suite.addTest(test_loader.loadTestsFromModule(m))
    #
    # Load tests from classes in this module
    #
    for c in ( ExecuteHappyDocTest,
               ExternalTest,
               ):
        actual_test_suite.addTest(test_loader.loadTestsFromTestCase(c))
    return



def getBugTests(actual_test_suite, output_dir):
    bug_ids = map(lambda x:x[18:-3], glob(os.path.join('TestCases', 'test_bug*.py')))
    bug_ids.sort()
    for bug in bug_ids:
        #test_definitions.append( (bug, HappyDocBugRegressionTest) )
        actual_test_suite.addTest(
            HappyDocBugRegressionTest( methodName=bug,
                                       outputDir=output_dir,
                                       )
            )
    return

def getTestSuite(get_all_tests=1, get_bug_tests=1, output_dir='/dev/null',
                 progress_callback=None, args=[]):
    actual_test_suite = unittest.TestSuite()

    test_loader = HappyDocTestLoader(output_dir,
                                     progress_callback,
                                     (ExecuteHappyDocTest,
                                      ZopeTest,
                                      HappyDocBugRegressionTest,
                                      ))

    if get_all_tests:
        addAllTests(test_loader, actual_test_suite)
        getBugTests(actual_test_suite, output_dir)

    elif get_bug_tests:
        getBugTests(actual_test_suite, output_dir)
        
    elif args:
        # Run the tests specified by the user
        for a in args:
            actual_test_suite.addTest( test_loader.loadTestsFromName(a) )
    else:
        # Default to running all tests
        get_all_tests = 0
        actual_test_suite.addTest( test_loader.loadTestsFromName('__main__.ExecuteHappyDocTest.testSelfHTML') )

    return actual_test_suite


class TestCaseDriver(happydoclib.CommandLineApp.CommandLineApp):
    "Drive the test cases for HappyDoc."

    LIST = 'list'
    RUNTEST = 'run'

    _include_zope = 0
    _output_dir = 'DefaultTestOutputDir'
    _operation = RUNTEST

    #
    # Use the verbosity manager from the StreamFlushTest
    # module so that all verbosity is managed the same way.
    #
    verboseLevel = globalVerboseLevel

    ##
    ## OPTION HANDLERS
    ##

    log_file=open('log.txt', 'wt')

    def statusMessage(self, msg='', level=1):
        happydoclib.CommandLineApp.CommandLineApp.statusMessage(
            self, msg, level)
        self.log_file.write('%s\n' % msg)
        self.log_file.flush()
        return

    def optionHandler_d(self, outputDir):
        "Specify the output directory for the tests."
        self.statusMessage('Setting output directory to "%s"' % outputDir, 2)
        self._output_dir = outputDir
        return

    def optionHandler_list(self):
        "List the tests available."
        self._operation = self.LIST
        return
    
    def optionHandler_q(self):
        "Disable visible output."
        self.verboseLevel.unset()
        return

    def optionHandler_v(self):
        "Increase verbose level by one.  Can be repeated."
        self.verboseLevel.set(self.verboseLevel.get() + 1)
        return

    def optionHandler_withzope(self):
        "Add the Zope tests to the set."
        self.statusMessage('Including Zope testes', 2)
        self._include_zope = 1
        return


    ##
    ## APPLICATION
    ##
    
    def appInit(self):
        self._desired_tests = []
        self.optionHandler_d(DEFAULT_OUTPUT_DIR)
        return

    def listTests(self, suite):
        "List the available test cases."
        self.statusMessage('Available tests', 2)
        for test in suite._tests:
            if issubclass(test.__class__, unittest.TestSuite):
                self.listTests(test)
            else:
                try:
                    description = test.shortDescription()
                    if not description:
                        description = test.id()
                    print '%s : %s' % (test.name, description)
                except AttributeError:
                    print dir(test)
                    raise
        return

    def runTests(self, suite):
        "Run the required test cases."
        #
        # Run the test suite
        #

        verbosity = self.verboseLevel.get()

        if verbosity > 1:
            print '=' * 80
            print 'START'
            print '-' * 80
            print
            
        runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=verbosity)
        runner.run(suite)

        if verbosity > 1:
            print
            print '-' * 80
            print 'FINISH'
            print '=' * 80
            
        return
    
    def main(self, *args):
        "Run the requested test suites."

        #
        # Create the output directory
        #
        self.statusMessage('Creating %s' % self._output_dir, 2)
        happydoclib.path.rmkdir(self._output_dir)
        
        #
        # Figure out what tests to process
        #
        get_all_tests = 0
        get_bug_tests = 0
        if 'all' in args:
            # We will define "all" of the tests later
            get_all_tests = 1
        elif 'bugs' in args:
            get_bug_tests = 1
            
        actual_test_suite = getTestSuite(get_all_tests=get_all_tests,
                                         get_bug_tests=get_bug_tests,
                                         output_dir=self._output_dir,
                                         progress_callback=self.statusMessage,
                                         args=args)
        
        #
        # Optionally include the Zope tests
        #
        if self._include_zope:
            actual_test_suite.addTest(test_loader.loadTestsFromTestCase(ZopeTest))
                
        #
        # Figure out what action to take
        #
        if self._operation == self.RUNTEST:
            self.runTests(actual_test_suite)
        elif self._operation == self.LIST:
            self.listTests(actual_test_suite)
        else:
            raise ValueError('Operation (%s) must be one of RUNTEST or LIST.' % \
                             self._operation)
        
        self.log_file.close()
        return
    

def main(argv=()):
    try:
        TestCaseDriver(argv).run()
    except TestCaseDriver.HelpRequested:
        pass


def debug():
    os.chdir('c:\\happydoc\happydoc')
    import happydoclib.trace
    #happydoclib.trace.trace.setVerbosity(3)
    main( ('all',) )
    #main( ('-v',
    #       'happydoclib.formatter.fileformatterbase.FileFormatterBaseTest.testGetFullOutputNameForObjectNone') )
    return
    

if __name__ == '__main__':
    if os.name == 'nt':
        debug()
    else:
        main(sys.argv[1:])
