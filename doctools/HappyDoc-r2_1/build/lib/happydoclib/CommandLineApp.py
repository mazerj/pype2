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


"""Base class for building command line applications.

  The CommandLineApp class makes creating command line applications as
  simple as defining callbacks to handle options when they appear in
  'sys.argv'.

  To do

    - enhance intelligence of option handling

        - boolean options should not need to be implemented as functions

        - enable/disable with/without options

        - type checking for option arguments

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name':'$RCSfile: CommandLineApp.py,v $',
    'creator':'Doug Hellmann <doug@hellfly.net>',
    'project':'Open Source',
    'created':'Tue, 23-May-2000 07:11:43 EDT',
    #
    #  Current Information
    #
    'author':'$Author: doughellmann $',
    'version':'$Revision: 1.8 $',
    'date':'$Date: 2002/02/17 12:44:58 $',
    }
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import getopt
import pprint
import sys
import string
import unittest

#
# Import Local modules
#
from StreamFlushTest import StreamFlushTest


#
# Module
#

class CommandLineApp:
    """Base class for building command line applications.
    
    Define a __doc__ string for the class to explain what the
    program does.

    When the argumentsDescription field is not empty,
    it will be printed appropriately in the help message.
    
    When the examplesDescription field is not empty,
    it will be printed last in the help message when
    the user asks for help.
    """

    argumentsDescription = ''

    shortArgumentsDescription = ''
    
    examplesDescription = ''

    #
    # Exception names
    #
    ReservedOptionName = 'Reserved option name'
    HelpRequested='Help requested'
    InvalidOptionValue='Invalid value for option'
    InvalidArgument='Invalid argument to program'

    #
    # Globally useful configuration stuff.
    #
    optionHandlerPrefix = 'optionHandler_'
    optTypeLong = 'optTypeLong'
    optTypeShort = 'optTypeShort'
    optTakesParam = 'optTakesParam'
    optNoParam = 'optNoParam'

    verboseLevel = 1

    _app_version = '0.0' 

    def __init__(self, commandLineOptions=sys.argv[1:]):
        "Initialize CommandLineApp."
        self.commandLineOptions = commandLineOptions
        self.__learnValidOpts__()
        self.__init_getopt__()
        self.appInit()

    def appInit(self):
        """Override this method to perform application initialization.

        This hook may be easier to override than the __init__ method,
        since it takes no parameters.
        """
        pass

    def shortOptionsStringGet(self):
        """Given the information learned through self.__learnValidOpts__,
        construct a string to be passed to getopt to set the valid
        single character option syntax.
        """
        sas = ''
        for (optName, optTakesValue,
             optLongOrShort, ignore, ignore) in self.shortOptions:
            sas = sas + optName
            if optTakesValue == self.optTakesParam:
                sas = sas + ':'
        return sas

    def longOptionsListGet(self):
        """Given the information learned through self.__learnValidOpts__,
        construct a list to be passed to getopt to set the valid
        long form option syntax.
        """
        lal = []
        for (optName, optTakesValue,
             optLongOrShort, ignore, ignore) in self.longOptions:
            if optTakesValue == self.optTakesParam:
                opt = '%s=' % optName
            else:
                opt = optName
            lal.append(opt)
            if opt.find('-') >= 0:
                new_opt = opt.replace('-', '_')
                lal.append(new_opt)
        return lal

    def __init_getopt__(self):
        "Parse the command line options."
        shortOptionsString = self.shortOptionsStringGet() + 'h'
        longOptionList = self.longOptionsListGet()
        longOptionList.append('help')
        try:
            self.parsedOptions, self.remainingOpts = getopt.getopt(
                self.commandLineOptions, 
                shortOptionsString,
                longOptionList)
        except getopt.error, message:
            self.showHelp(message)
            raise getopt.error, message
        return

    def constructOptionInfo(self, methodName, methodRef):
        """Return an info tuple for an option handler method.

        Given a method name, return the information tuple
        for that option to the program.  The tuple contains:

          (option name,
          flag showing whether the option takes a value,
          flag indicating long or short form option,
          help string for option)
        """
        optionName = methodName[len(self.optionHandlerPrefix):]
        if len(methodRef.func_code.co_varnames) > 1:
            optionTakesValue = self.optTakesParam
        else:
            optionTakesValue = self.optNoParam
        if len(optionName) > 1:
            optionLongForm = self.optTypeLong
            optionName = optionName.replace('_', '-')
        else:
            optionLongForm = self.optTypeShort
        return (optionName, optionTakesValue,
                optionLongForm, methodName, methodRef)

    def methodNameFromOption(self, option):
        """Given the name of an option, construct 
        and return the name of the method to handle it.
        """
        methodName = '%s%s' % (self.optionHandlerPrefix, option)
        return methodName
        
    def scanClassForOptions(self, cRef):
        "Scan through the inheritence hierarchy to find option handlers."
        for parentClass in cRef.__bases__:
            self.scanClassForOptions(parentClass)
        for componentName in cRef.__dict__.keys():
            component = cRef.__dict__[componentName]
            if componentName[:len(self.optionHandlerPrefix)] == self.optionHandlerPrefix and \
               type(component).__name__ == 'function':
                optionInfo = self.constructOptionInfo(componentName, component)
                if optionInfo[0] == 'h':
                    raise CommandLineApp.ReservedOptionName, 'h'
                self.allOptions[ optionInfo[0] ] = optionInfo
                self.allMethods[ componentName ] = optionInfo

    def __learnValidOpts__(self):
        """Derive the options which are valid for this application.

        Examine the methods defined for this class to
        learn what options the developer wants to use.  Options
        can be added by defining an optionHandler method with a
        name like optionHandler_<option name>.  If the option
        handler method takes an argument, the option will require
        an argument as well.
        """
        self.shortOptions = []
        self.longOptions = []
        self.allOptions = {}
        self.allMethods = {}
        self.scanClassForOptions(self.__class__)
        for optionName in self.allOptions.keys():
            optionInfo = self.allOptions[optionName]
            if optionInfo[2] == self.optTypeShort:
                self.shortOptions.append( optionInfo )
            else:
                self.longOptions.append( optionInfo )

    def handleHelpOption(self):
        #
        # Look for -h in self.optList.
        # if found, call help function 
        # then raise HelpRequested
        #
        for option in self.parsedOptions:
            if option[0] == '-h':
                self.showHelp()
                raise self.HelpRequested, 'Help message was printed.'
            if option[0] == '--help':
                self.showVerboseHelp()
                raise self.HelpRequested, 'Help message was printed.'
        
    def main(self, *args):
        """Main body of your application.

        This is the main portion of the app, and is run after all of
        the arguments are processed.  Override this method to implment
        the primary processing section of your application.
        """
        pass

    def infoForOption(self, option):
        "Get the stored information about an option."
        optionBase = option
        if optionBase[:2] == '--':
            optionBase = option[2:]
        elif optionBase[0] == '-':
            optionBase = optionBase[1:]

        optionBase = optionBase.replace('_', '-')
        return self.allOptions[ optionBase ]
        
    def methodReferenceFromName(self, methodName):
        "Return a reference to the method with the given name."
        if len(methodName) > 1:
            methodName = methodName.replace('-', '_')
        return self.allMethods[methodName][4]
    
    def run(self):
        """Entry point.

        Process options and execute callback functions as needed.
        This method should not need to be overridden, if the main()
        method is defined.
        """
        try:
            self.handleHelpOption()
            for option, optValue in self.parsedOptions:
                cleanOption = option
                while cleanOption[0] == '-':
                    cleanOption = cleanOption[1:]
                methName = self.methodNameFromOption(cleanOption)
                method = self.methodReferenceFromName(methName)
                optInfo = self.infoForOption(option)
                if optInfo[1] == self.optTakesParam:
                    optArg = string.split(optValue, ',')
                    if len(optArg) <= 1:
                        optArg = optValue
                    method(self, optArg)
                else:
                    method(self)
            exit_code = apply(self.main, tuple(self.remainingOpts))
        except KeyboardInterrupt:
            try:
                self.interruptHandler()
            except AttributeError:
                sys.stderr.write('Cancelled by user.\n')
                pass
            exit_code = 1
        return exit_code
    
    def getSimpleSyntaxHelpString(self):    
        """Return syntax statement.
        
        Return a simplified form of help including only the 
        syntax of the command.
        """
        #
        # Initialize the return value
        #
        helpMsg = ''
        #
        # Initialize some lists of options to organize the
        # printing.
        #
        shortOptionNoArgs = 'h'
        shortOptionArgs = []
        longOptionNoArgs = ['help']
        longOptionArgs = []
        allOptionNames = self.allOptions.keys()
        allOptionNames.sort()
        #
        # Sort out each option into the correct group.
        #
        for option in allOptionNames:
            optName, optTakesValue, optLongOrShort, ignore, ignore = \
                 self.infoForOption(option)
            methodName = self.methodNameFromOption(option)
            method = self.methodReferenceFromName(methodName)
            if optTakesValue == self.optTakesParam:
                if optLongOrShort == self.optTypeLong:
                    longOptionArgs.append(optName)
                else:
                    shortOptionArgs.append(optName)
            else:
                if optLongOrShort == self.optTypeLong:
                    longOptionNoArgs.append(optName)
                else:
                    shortOptionNoArgs = shortOptionNoArgs + optName
        #
        # Print the name of the command, and the short options
        # which take no arguments.
        #
        helpMsg = '%s%s [-%s] ' % (helpMsg, sys.argv[0], shortOptionNoArgs)
        #
        # Print the short options which take arguments.
        #
        for option in shortOptionArgs:
            methodName = self.methodNameFromOption(option)
            method = self.methodReferenceFromName(methodName)
            valueName = method.func_code.co_varnames[1]
            helpMsg = '%s\n\t\t[-%s %s] ' % (helpMsg, option, valueName)
        #
        # Print the long options which take no arguments.
        #
        for option in longOptionNoArgs:
            helpMsg = '%s\n\t\t[--%s] ' % (helpMsg, option)
        #
        # Print the long options which take arguments.
        #
        for option in longOptionArgs:
            methodName = self.methodNameFromOption(option)
            method = self.methodReferenceFromName(methodName)
            valueName = method.func_code.co_varnames[1]
            helpMsg = '%s\n\t\t[--%s=%s] ' % (helpMsg, option, valueName)
        #
        # Print the argument description
        #
        if self.shortArgumentsDescription:
            helpMsg = '%s\n\n\t\t%s' % (helpMsg, self.shortArgumentsDescription)
        #
        helpMsg = '%s\n\n' % helpMsg
        return helpMsg

    def showSimpleSyntaxHelp(self):
        "Show basic syntax message."
        txt = self.getSimpleSyntaxHelpString()
        print txt
        print '\tFor more details, use --help.'
        print
        return

    def getOptionHelpString(self, dashInsert, option, 
                            valueInsert, docString):
        "Build the help string for an option."
        
        indent_size = 15
        
        baseString = '\t%s%s%s' % (dashInsert, 
                                   option, 
                                   valueInsert, 
                                   )
        if len(baseString) > indent_size:
            baseString='%s\n' % baseString
            description_prefix = '\t%s' % (' ' * indent_size)
        else:
            format_str = '%%-%ds' % indent_size
            baseString = format_str % baseString
            description_prefix = ' '
            
        optionString = '%s%s' % (baseString, description_prefix)
        docStringLines = string.split(docString, '\n')
        
        if docStringLines:
            line = docStringLines[0]
            optionString = '%s%s\n' % (optionString, line)

        emit_blank = 1
        for line in docStringLines[1:]:
            line = string.strip(line)
            if not line and emit_blank:
                emit_blank = 0
            elif line:
                emit_blank = 1
            optionString = '%s\t%s%s\n' % (optionString, ' ' * indent_size, line)
            
        optionString = optionString + '\n'
        
        return optionString
        
    def showOptionHelp(self, dashInsert, option, valueInsert, docString):
        'Format and print the help message for a single option.'
        #
        #print '\t%s%s%s' % (dashInsert, option, valueInsert)
        #print ''
        #print '\t\t\t%s' % docString
        #print ''
        print self.getOptionHelpString(dashInsert, option,
                                       valueInsert, docString)

    def showVerboseSyntaxHelp(self):
        "Show a full description of all options and arguments."
        txt = self.getVerboseSyntaxHelpString()
        print txt
        

    def getVerboseSyntaxHelpString(self):
        """Return the full description of the options and arguments.

        Show a full description of the options and arguments to the
        command in something like UNIX man page format. This includes
        
          - a description of each option and argument, taken from the
                __doc__ string for the optionHandler method for
                the option
                
          - a description of what additional arguments will be processed,
                taken from the class member argumentsDescription
                
        """
        #
        # Show them how to use it.
        #
        helpMsg = '\nSYNTAX:\n\n\t'
        #
        # Show the options.
        #
        helpMsg = '%s%sOPTIONS:\n\n' % (helpMsg, 
                                        self.getSimpleSyntaxHelpString())
        helpMsg = string.join( [helpMsg,
        
                    self.getOptionHelpString('-', 'h', '', 
                    'Displays abbreviated help message.'),
                    
                    self.getOptionHelpString('--', 'help', '', 
                    'Displays complete usage information.'),
                    ],
                    ''
                )

        #
        # Get a list of all unique option *names*
        #
        allOptionNames = self.allOptions.keys()
        allOptionNames.sort()
        
        #
        # Figure out which options are aliases
        #
        option_aliases = {}
        reduced_options = []
        for option in allOptionNames:
            optName, optTakesValue, optLongOrShort, ignore, ignore = \
                 self.infoForOption(option)
            methodName = self.methodNameFromOption(option)
            method = self.methodReferenceFromName(methodName)
            existing_aliases = option_aliases.get(method, [])
            if not existing_aliases:
                reduced_options.append(option)
            existing_aliases.append(option)
            option_aliases[method] = existing_aliases

        grouped_options = [ x[1] for x in option_aliases.items() ]
        grouped_options.sort()
            
        #
        # Describe all options, grouping aliases together
        #
        
        for option_set in grouped_options:
            first_option = option_set[0]
            #
            # Build the list of option name/parameter strings
            #
            option_help_strings = []
            for option in option_set:
                optName, optTakesValue, optLongOrShort, ignore, ignore = \
                         self.infoForOption(option)
                methodName = self.methodNameFromOption(option)
                method = self.methodReferenceFromName(methodName)
                if optTakesValue == self.optTakesParam:
                    valueInsert = method.func_code.co_varnames[1]
                else:
                    valueInsert = ''
                if optLongOrShort == self.optTypeLong:
                    dashInsert = '--'
                    if valueInsert:
                        valueInsert = '=%s' % valueInsert
                else:
                    dashInsert = '-'
                    if valueInsert:
                        valueInsert = ' %s' % valueInsert
                option_help_strings.append('%s%s%s' % (dashInsert,
                                                       optName,
                                                       valueInsert,
                                                       )
                                           )
            option_help_string = ', '.join(option_help_strings)

            methodName = self.methodNameFromOption(first_option)
            method = self.methodReferenceFromName(methodName)
            docString = method.__doc__.rstrip()
            helpMsg = string.join( [ helpMsg,
                                     self.getOptionHelpString('',
                                                              option_help_string,
                                                              '',
                                                              docString,
                                                              )
                                     ],
                                   '')
            helpMsg = helpMsg + '\n'
            
        if self.argumentsDescription:
            helpMsg = '%sARGUMENTS:\n\n%s\n\n' % (helpMsg,
                                                  self.argumentsDescription)
            
        return helpMsg

    def showVerboseHelp(self):
        """Show a verbose help message explaining how to use the program.

        This includes:
        
           * a verbose description of the program, taken from the __doc__
             string for the class
             
           * an explanation of each option, produced by
             showVerboseSyntaxHelp()
             
           * examples of how to use the program for specific tasks,
             taken from the class member examplesDescription
             
        """
        #
        # Show the program name and
        # a description of what it is for.
        #
        print ''
        print '%s\n' % sys.argv[0]
        if self.__class__.__doc__:
            print ''
            for line in string.split(self.__class__.__doc__, '\n'):
                line = string.strip(line)
                #if not line: continue
                print '\t%s' % line
            print ''
        self.showVerboseSyntaxHelp()
        if self.examplesDescription:
            print 'EXAMPLES:'
            print ''
            print self.examplesDescription
            print ''
        return

    def showHelp(self, errorMessage=None):
        "Display help message when error occurs."
        print
        if self._app_version:
            print '%s version %s' % (self.__class__.__name__, self._app_version)
        else:
            print self.__class__.__name__
        print
            
        #
        # If they made a syntax mistake, just
        # show them how to use the program.  Otherwise,
        # show the full help message.
        #
        if errorMessage:
            print ''
            print 'ERROR: ', errorMessage
            print ''
            print ''
            print '%s\n' % sys.argv[0]
            print ''
        self.showSimpleSyntaxHelp()
        return

    def statusMessage(self, msg='', verboseLevel=1, error=None):
        """Print a status message to output.
        
        Arguments
        
            msg=''            -- The status message string to be printed.
            
            verboseLevel=1    -- The verbose level to use.  The message
                              will only be printed if the current verbose
                              level is >= this number.
                              
            error=None        -- If true, the message is considered an error and
                              printed as such.
                              
        """
        if self.verboseLevel >= verboseLevel:
            if error:
                output = sys.stderr
            else:
                output = sys.stdout
            output.write('%s\n' % msg)
            output.flush()
        return

    def debugMethodEntry(self, methodName, debugLevel=3, **nargs):
        "Print a method entry debug statement with named arguments."
        arg_str = string.join( map( lambda pair: '%s=%s' % pair, nargs.items() ), ', ')
        return self.statusMessage('%s(%s)' % (methodName, arg_str), debugLevel)
    
    def errorMessage(self, msg=''):
        'Print a message as an error.'
        self.statusMessage('ERROR: %s\n' % msg, 0)
                
    def optionHandler_v(self):
        """Increment the verbose level.
        Higher levels are more verbose.
        The default is 1.
        """
        self.verboseLevel = self.verboseLevel + 1
        self.statusMessage('New verbose level is %d' % self.verboseLevel,
                           3)
        return

    def optionHandler_q(self):
        'Turn on quiet mode.'
        self.verboseLevel = 0

        
class TestApp(CommandLineApp):
    """    This is a simple test application.

    It defines several optionHandler methods to handle
    some example options.  One option of each type is
    handled by an example.

    The __doc__ string for the class should contain
    the info about how to use the application. """

    examplesDescription = \
"""    a description of how to use the program 
    in various ways goes here.
"""                

    argumentsDescription = \
"""    a description of other arguments goes here
"""

    defaultLongFormOption='<default value>'

    def optionHandler_a(self, optValue):
        'get a value for a'
        print '%s: handling a: %s' % (self.__class__.__name__, optValue)

    def optionHandler_b(self):
        'toggle the value of b'
        print '%s: handling b' % (self.__class__.__name__,)

    def optionHandler_long_form_option(self):
        'boolean option'
        print '%s: handling long-form-option' % (self.__class__.__name__,)

    def optionHandler_long_form_with_value(self, optValue):
        """First line of help.
            get a value for long form option

            Default:<manually inserted>"""
        print '%s: handling long-form-with-value: %s' % (self.__class__.__name__,
                                 optValue)

    def main(self, *args):
        'main loop'
        print '%s: LEFT OVERS: ' % (self.__class__.__name__,), self.remainingOpts

        
class SubClassTestApp(TestApp):
    'new doc string'
    
    def optionHandler_a(self, newA):
        'Doc string for SubClassTestApp'
        print 'New A:', newA
        TestApp.optionHandler_a(self, newA)
    
    def optionHandler_z(self):
        'Doc string for SubClassTestApp'
        print '%s -z' % self.__class__.__name__
        
    def optionHandler_option_list(self, optionList):
        'Doc string for SubClassTestApp'
        if type(optionList) == type([]):
            print '%s -z list: ' % self.__class__.__name__, optionList
        else:
            print '%s -z string: %s' % (self.__class__.__name__, optionList)
        
    def main(self, *args):
        apply(TestApp.main, (self,) + args)
        raise 'not an error'


class CLATestCase(StreamFlushTest):

    def runAndCatchOutput(self, args):
        output_text = ''
        
        try:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            from cStringIO import StringIO
            sys.stdout = sys.stderr = StringIO()
            SubClassTestApp( args ).run()
            
        except SubClassTestApp.HelpRequested:
            output_text = sys.stdout.getvalue()
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
        else:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.fail('Help was not requested.')
            
        return output_text
    
    def testShortHelpGeneration(self):
        help_text = self.runAndCatchOutput(['-h'])

        expected_help_text = """
SubClassTestApp version 0.0

%s [-hbqvz] 
		[-a newA] 
		[--help] 
		[--long-form-option] 
		[--long-form-with-value=optValue] 
		[--option-list=optionList] 


	For more details, use --help.

""" % sys.argv[0]
        assert help_text == expected_help_text, \
               'Unexpected help text "%s" does not match "%s"' % (help_text, expected_help_text)
        return

    def testLongHelpGeneratoion(self):
        help_text = self.runAndCatchOutput(['--help'])

        app = sys.argv[0]
        expected_help_text = """
%(app)s


	new doc string


SYNTAX:

	%(app)s [-hbqvz] 
		[-a newA] 
		[--help] 
		[--long-form-option] 
		[--long-form-with-value=optValue] 
		[--option-list=optionList] 

OPTIONS:

	-h             Displays abbreviated help message.

	--help         Displays complete usage information.

	-a newA        Doc string for SubClassTestApp


	-b             toggle the value of b


	--long-form-option
	               boolean option


	--long-form-with-value=optValue
	               First line of help.
	               get a value for long form option
	               
	               Default:<manually inserted>


	--option-list=optionList
	               Doc string for SubClassTestApp


	-q             Turn on quiet mode.


	-v             Increment the verbose level.
	               Higher levels are more verbose.
	               The default is 1.


	-z             Doc string for SubClassTestApp


ARGUMENTS:

    a description of other arguments goes here



EXAMPLES:

    a description of how to use the program 
    in various ways goes here.


""" % locals()
        assert help_text == expected_help_text, 'Unexpected help text "%s" does not match "%s"' % (help_text, expected_help_text)
        return

    def testOptionList(self):

        class CLAOptionListTest(CommandLineApp):
            expected_options = ['a', 'b', 'c']
            def optionHandler_t(self, options):
                "Expects multiple arguments."
                assert options == self.expected_options, \
                       "Option value does not match expected (%s)" % str(options)
            optionHandler_option_list = optionHandler_t

        CLAOptionListTest( [ '-t', 'a,b,c' ] ).run()
        CLAOptionListTest( [ '--option-list', 'a,b,c' ] ).run()
        CLAOptionListTest( [ '--option-list=a,b,c' ] ).run()
        return

    def testLongOptions(self):
        class CLALongOptionTest(CommandLineApp):
            def optionHandler_test(self):
                "Expects no arguments."
                return
            def optionHandler_test_args(self, args):
                "Expects some arguments"
                return

        CLALongOptionTest( [ '--test' ] ).run()
        CLALongOptionTest( [ '--test-args', 'foo' ] ).run()
        CLALongOptionTest( [ '--test-args=foo' ] ).run()

        CLALongOptionTest( [ '--test_args', 'foo' ] ).run()
        CLALongOptionTest( [ '--test_args=foo' ] ).run()
        
        return

    def testArgsToMain(self):
        class CLALongOptionTest(CommandLineApp):
            expected_args = ( 'a', 'b', 'c' )
            def optionHandler_t(self):
                pass
            def main(self, *args):
                assert args == self.expected_args, \
                       'Got %s instead of expected values.' % str(args)

        CLALongOptionTest( [ 'a', 'b', 'c' ] ).run()
        CLALongOptionTest( [ '-t', 'a', 'b', 'c' ] ).run()
        CLALongOptionTest( [ '-t', '--', 'a', 'b', 'c' ] ).run()
        CLALongOptionTest( [ '--', 'a', 'b', 'c' ] ).run()
        new_test = CLALongOptionTest( [ '--', '-t', 'a', 'b', 'c' ] )
        new_test.expected_args = ('-t',) + new_test.expected_args
        new_test.run()
        return
    

if __name__ == '__main__':
    unittest.main()
