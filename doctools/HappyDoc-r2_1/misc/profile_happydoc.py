#!/usr/bin/env python
#
# $Id: profile_happydoc.py,v 1.1 2001/10/24 21:27:36 doughellmann Exp $
#
# Time-stamp: <01/10/01 16:58:23 dhellmann>
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

"""Run the Python profiler against HappyDoc.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: profile_happydoc.py,v $',
    'rcs_id'       : '$Id: profile_happydoc.py,v 1.1 2001/10/24 21:27:36 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <DougHellmann@bigfoot.com>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Sat, 17-Feb-2001 10:18:56 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.1 $',
    'date'         : '$Date: 2001/10/24 21:27:36 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import profile
import pstats
import os
import time

#
# Import Local modules
#
import test_happydoc
from CommandLineApp import CommandLineApp
from happydoc_class import HappyDoc
import hdpath

#
# Module
#

class ProfileHappyDoc(CommandLineApp):

    _num_stats = 10
    _stats = None

    _show_caller = None
    _show_callee = None
    _show_normal = 1

    _hd_args = (
        '-F', 'null',
        '-v',
        '-t', 'Profiling Run',
        '-d', '../HappyDocRegressionTest/ProfilingOutput',
        #'../HappyDoc/TestCases/test_import_packages/lib/python/Products/PythonScripts'
        #'../HappyDoc'
        '../Zope-2-CVS-src'
        )

    def statusMessage(self, message, verboseLevel=1):
        time_str = time.asctime(time.localtime(time.time()))
        CommandLineApp.statusMessage(self, '%s: %s' % (time_str, message), verboseLevel)
        return
    
    def runProfile(self):
        self.statusMessage('Running profile of HappyDoc...')
        profile.run('HappyDoc(%s).run()' % str(self._hd_args), 'happydoc.prof')
        return

    def readProfileResultsData(self, filename):
        self.statusMessage('Reading profile data from %s' % filename)
        if not self._stats:
            self._stats = pstats.Stats(filename)
        else:
            self._stats.add(filename)
        self.optionHandler_t()
        return
    
    def appInit(self):
        if not hdpath.exists('happydoc.prof'):
            self.runProfile()
        self.readProfileResultsData('happydoc.prof')
        return

    def optionHandler_u(self):
        "Update the stats."
        self.runProfile()
        return

    def optionHandler_i(self, inputFile):
        "Include a specific prof data file in outputs."
        self.readProfileResultsData(inputFile)
        return

    def optionHandler_n(self, numStats):
        "Set number of stats to print."
        self._num_stats = int(numStats)
        return

    def optionHandler_cumulative(self):
        "Sort stats by cumulative time."
        self._stats.sort_stats('cumulative')
        return

    def optionHandler_c(self):
        "Print callee stats."
        self._show_callee = 1
        return

    def optionHandler_C(self):
        "Print caller stats."
        self._show_caller = 1
        return

    def optionHandler_t(self):
        "Sort stats by time."
        self._stats.sort_stats('time')
        return

    def optionHandler_nfl(self):
        "Sort stats by nfl (name, file, line)."
        self._stats.sort_stats('nfl')
        return

    def main(self, *args):
        "Print results."
        if self._show_normal:
            self._stats.print_stats(self._num_stats)
        if self._show_caller:
            self._stats.print_callers(self._num_stats)
        if self._show_callee:
            self._stats.print_callees(self._num_stats)
        self.statusMessage('Done')
        return
    

if __name__ == '__main__':
    try:
        ProfileHappyDoc().run()
    except ProfileHappyDoc.HelpRequested:
        pass
    
