#!/usr/bin/env python
#
# $Id: trace.py,v 1.6 2002/08/04 12:04:16 doughellmann Exp $
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

"""A debugging trace module.

  This debugging trace module makes it easier to follow nested calls
  in output by varying the indention level for log messages.  The
  caller can simply trace 'into()' a new level when control passes
  into a function call, 'write()' debug messages at appropriate spots
  in the function, then call 'outof()' when returning from the
  function.

  The debug level is set via the environment variable 'HAPPYDOC_TRACE'.
  Level '0' or no value specified results in no output.  Positive
  integer values are used to control the verbosity of the output with
  higher numbers resulting in more output messages.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: trace.py,v $',
    'rcs_id'       : '$Id: trace.py,v 1.6 2002/08/04 12:04:16 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Mon, 29-Oct-2001 09:29:22 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.6 $',
    'date'         : '$Date: 2002/08/04 12:04:16 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import os
import sys

#
# Import Local modules
#
from happydoclib.StreamFlushTest import StreamFlushTest

#
# Module
#


class DebugTracer:

    NO_RETURN_VALUE_SPECIFIED='No return value specified.'

    def __init__(self,
                 outputStream=sys.stdout,
                 indentBy='  ',
                 maxOutputLevel=1,
                 startLevel=0):
        self.output = outputStream
        self.level = startLevel
        self.stack = ()
        self.indent_by = indentBy
        self.max_output_level = maxOutputLevel
        return

    def setVerbosity(self, level):
        self.max_output_level = level
        return

    def getIndent(self):
        return self.indent_by * self.level

    def pushLevel(self, newStackTop):
        self.level = self.level + 1
        self.stack = ( newStackTop, self.stack )
        return

    def popLevel(self):
        self.level = self.level - 1
        if self.stack:
            popped, self.stack = self.stack
        else:
            popped = ()
        return popped

    def checkOutputLevel(self, outputLevel):
        return self.max_output_level >= outputLevel

    ###

    def into(self, className, functionName, outputLevel=1, **params):
        """Enter a new debug trace level.
        
        Parameters

            'className' -- Name of the class.

            'functionName' -- The name of the function/method.

            'outputLevel=1' -- The debug level where this message should be printed.

            '**params' -- Parameters sent to the function.
        
        """
        if self.checkOutputLevel(outputLevel):
            self.output.write(self.getIndent())
            self.output.write('%s::%s (' % (className, functionName))
            params = params.items()
            params.sort()
            for name, value in params:
                self.output.write('\n%s\t%s=%s, ' % (self.getIndent(), name, repr(value)))
            self.output.write(') {\n')
            self.pushLevel((className, functionName))
        return

    def callerParent(self, outputLevel=1):
        if self.checkOutputLevel(outputLevel):
            self.output.write(self.getIndent())
            if not self.stack:
                self.output.write('ERROR: trace.callerParent called when no stack present\n')
            if len(self.stack) < 2:
                parent = 'None'
            else:
                try:
                    parent = '%s::%s' % self.stack[1][0]
                except:
                    parent = str(self.stack[1])

            #self.output.write('Called by: %s\n' % parent)
            self.output.write('Called by: %s\n' % str(self.stack))
        return

    def write(self, message, indent=1, outputLevel=1, **vars):
        if self.checkOutputLevel(outputLevel):
            if indent:
                self.output.write(self.getIndent())
            self.output.write(message)
            if vars.items():
                vars = vars.items()
                vars.sort()
                for name, value in vars:
                    self.output.write('\n%s\t%s=%s' % (self.getIndent(), name, repr(value)))
                self.output.write('\n')
            else:
                self.output.write('\n')
                
        return

    def writeVar(self, outputLevel=1, **variables):
        if self.checkOutputLevel(outputLevel):
            variables = variables.items()
            variables.sort()
            for name, value in variables:
                self.write('%s=%s' % (name, repr(value)))
        return

    def outof(self, returnValue=None, outputLevel=1):
        """Exit the current debug trace level.
        
            Parameters

              'returnValue' -- Optional argument indicating
                               the value returned from the function.
        """
        if self.checkOutputLevel(outputLevel):
            self.popLevel()
            self.output.write(self.getIndent())
            self.output.write('} %s\n' % repr(returnValue))
        return returnValue


trace=DebugTracer(maxOutputLevel=int(os.environ.get('HAPPYDOC_TRACE', 0)))
into=trace.into
outof=trace.outof
write=trace.outof


####################################################################################


class TraceUnitTest(StreamFlushTest):

    def testTrace(self):
        from cStringIO import StringIO
        buffer = StringIO()
        trace = DebugTracer(outputStream=buffer)
        trace.callerParent()
        trace.into('__main__', 'topLevel', a='a', b='b')
        trace.callerParent()
        trace.write('hi there')
        trace.into('secondary', 'secondLevel', c='C', d='D')
        trace.write('inside second level')
        trace.callerParent()
        trace.outof()
        trace.outof('string returned')
        expected_value = """ERROR: trace.callerParent called when no stack present
Called by: ()
__main__::topLevel (
	a='a', 
	b='b', ) {
  Called by: (('__main__', 'topLevel'), ())
  hi there
  secondary::secondLevel (
  	c='C', 
  	d='D', ) {
    inside second level
    Called by: (('secondary', 'secondLevel'), (('__main__', 'topLevel'), ()))
  } None
} 'string returned'
"""
        actual_output = buffer.getvalue()
        assert actual_output == expected_value, \
               'Trace generated unexpected output [%s].' % actual_output
        return

    
