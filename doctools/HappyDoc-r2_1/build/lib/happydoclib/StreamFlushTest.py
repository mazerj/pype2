#!/usr/bin/env python
#
# $Id: StreamFlushTest.py,v 1.5 2002/08/04 10:47:06 doughellmann Exp $
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

"""Wrapper to control stdout and stderr for a TestCase.

    The streams for sys.stdout and sys.stderr are written to files in
    the output directory specified for the test instance.  The real
    stdout and stderr streams are saved and restored after each test
    execution, so that the TestRunner can show progress information as
    usual.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: StreamFlushTest.py,v $',
    'rcs_id'       : '$Id: StreamFlushTest.py,v 1.5 2002/08/04 10:47:06 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Sun, 14-Oct-2001 09:28:19 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.5 $',
    'date'         : '$Date: 2002/08/04 10:47:06 $',
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
import unittest

#
# Import Local modules
#

#
# Module
#

class _VerboseFlag:
    def __init__(self, initialValue=0):
        "Initialize a verbose flag"
        self.value = initialValue
        return
    
    def set(self, newValue=1):
        "Set the value to newValue"
        self.value = newValue
        return
    
    def unset(self, newValue=0):
        "Unset the value"
        self.set(newValue)
        return
    
    def get(self):
        "Retrieve the value"
        return self.value

    def __len__(self):
        return self.get()

    def __cmp__(self, other):
        return cmp(self.value, other)

verboseLevel = _VerboseFlag(1)

DEFAULT_OUTPUT_DIR='../HappyDocRegressionTest/SimpleTestOutput'

class StreamFlushTest(unittest.TestCase):
    """Wrapper to control stdout and stderr for a TestCase.

    The streams for sys.stdout and sys.stderr are written to files in
    the output directory specified for the test instance.  The real
    stdout and stderr streams are saved and restored after each test
    execution, so that the TestRunner can show progress information as
    usual.
    
    """

    verboseLevel = verboseLevel

    def __init__(self, methodName, outputDir=DEFAULT_OUTPUT_DIR,
                 statusMessageFunc=None):
        "Initialize"
        self.name = methodName
        self.output_dir = outputDir
        self.status_message_func = statusMessageFunc
        unittest.TestCase.__init__(self, methodName)
        import happydoclib.path
        self.path_module = happydoclib.path
        return

    def statusMessage(self, message, level=1):
        if self.status_message_func:
            self.status_message_func(message, level)
        return

    def __call__(self, result=None):
        "Execute the test"
        self.pushStreams()
        try:
            unittest.TestCase.__call__(self, result)
        finally:
            self.popStreams()
            sys.stdout.flush()
            sys.stderr.flush()
        return

    def pushStreams(self):
        "Substitute files for the sys streams"
        if verboseLevel < 2 and self.output_dir:
            output_dir = os.path.join(self.output_dir, self.name)
            self.saved_sys_stdout = sys.stdout
            self.saved_sys_stderr = sys.stderr
            self.path_module.rmkdir(output_dir)
            self.stdout_filename = os.path.join(output_dir, 'stdout.txt')
            self.stderr_filename = os.path.join(output_dir, 'stderr.txt')
            sys.stdout = open( self.stdout_filename, 'w' )
            sys.stderr = open( self.stderr_filename, 'w' )
        return

    def popStreams(self):
        "Replace the real sys streams"
        if verboseLevel < 2 and self.output_dir:
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout = self.saved_sys_stdout
            sys.stderr = self.saved_sys_stderr
        return
