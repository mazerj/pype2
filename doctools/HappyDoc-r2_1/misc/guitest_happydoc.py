#!/usr/bin/env python
#
# $Id: guitest_happydoc.py,v 1.2 2002/06/08 17:00:08 doughellmann Exp $
#
# Time-stamp: <02/06/08 12:59:49 dhellmann>
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

"""GUI App for testing HappyDoc.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: guitest_happydoc.py,v $',
    'rcs_id'       : '$Id: guitest_happydoc.py,v 1.2 2002/06/08 17:00:08 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'HappyDoc',
    'created'      : 'Sun, 25-Feb-2001 18:01:35 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.2 $',
    'date'         : '$Date: 2002/06/08 17:00:08 $',
}

#
# Import system modules
#
import Pmw
from Tkinter import *
import sys
import unittest

#
# Import Local modules
#
from PmwContribD.GuiAppD import GuiAppD
from PipeOutputWindow import PipeOutputWindow
sys.path.append('.')
import test_happydoc

#
# Module
#

class HappyDocTestGUI(GuiAppD):

    appversion='0.1'
    appname='HappyDocTestRunner'

    usebuttonbox=1

    user_preferences = {}

    def appInit(self):
        pass

    def createButtons(self):
        self.buttonAdd('Update',
                       helpMessage='Update list of tests',
                       statusMessage='Update list of tests',
                       command=self.updateTestList,
                       )
        self.buttonAdd('Clear',
                       helpMessage='Clear results window',
                       statusMessage='Clear results window',
                       command=self.clearResultsWindow,
                       )
        self.buttonAdd('Run',
                       helpMessage='Run selected test',
                       statusMessage='Run selected test',
                       command=self.runTest,
                       )
        return

    def runTest(self, *ignore):
        self.busyStart()
        command = './test_happydoc.py %s 2>&1' % self.selected_test.get()
        self.component('output').startBackgroundPipe(command,
                                                     self.testDone)
        return

    def clearResultsWindow(self):
        self.component('output').settext('')
        return

    def testDone(self):
        self.busyEnd()
        return

    def getTestNames(self, nameList, testSuite):
        for test in testSuite._tests:
            try:
                nameList.append(test.id())
            except AttributeError:
                self.getTestNames(nameList, test)
        return
        
    def updateTestList(self):
        testchooser = self.component('testchooser')
        reload(test_happydoc)
        test_suite = test_happydoc.getTestSuite()
        test_names = []
        self.getTestNames(test_names, test_suite)
        test_names.insert(0, 'all')
        testchooser.setlist(test_names)
        default_test = 'all'
        self.selected_test.set(default_test)
        return

    def createMenuBar(self):
        GuiAppD.createMenuBar(self)
        self.menuBar.addmenu('Tests', 'Control the execution of tests')
        self.addMenuItem('Tests', 'command', 'Run the selected test',
                         label='Run',
                         command=self.runTest,
                         acceleratorKey='r',
                         )
        return

    def createInterface(self):
        GuiAppD.createInterface(self)
        self.createButtons()
        self.selected_test = StringVar()
        testchooser = self.createcomponent('testchooser', (), None,
                                           Pmw.ComboBox,
                                           (self.interior(),),
                                           labelpos='w',
                                           label_text='Select a test',
                                           entryfield_entry_textvariable=self.selected_test,
                                           )
        self.busyWidgets.append(testchooser.component('entry'))
        testchooser.pack(side=TOP,
                         expand=NO,
                         fill=X,
                         )
        self.updateTestList()
        output = self.createcomponent( 'output', (), None,
                                       PipeOutputWindow,
                                       (self.interior(), self),
                                       logfile='./trace.txt',
                                       hscrollmode='static',
                                       vscrollmode='static',
                                       text_wrap='none',
                                       #text_background='white',
                                       labelpos='nw',
                                       label_text='Test Log',
                                       errorhandler=self.showError,
                                       )
        self.busyWidgets.append( output.component('text') )

        #
        # Basic config of the output window
        #
        output.tag_configure('commandline',
                             { 'font':Pmw.logicalfont('Courier',
                                                      -2,
                                                      weight='bold',
                                                      ),
                               'background':'#0000ff',
                               'foreground':'#ffffff',
                               }
                             )
        output.tag_configure('default',
                             { 'font':Pmw.logicalfont('Helvetica', -2)}
                             )
        output.addTagStyle('default', '^\w*$')

        #
        # Window dressing from the test case framework
        #
        output.tag_configure('visiblesep', { 'font':Pmw.logicalfont('Helvetica', -1),
                                             'foreground':'grey',
                                             'relief':RAISED,
                                             'borderwidth':1} )
        output.addTagStyle( 'visiblesep', '==+' )
        output.tag_configure('invisiblesep', { 'font':Pmw.logicalfont('Helvetica', -1),
                                               'foreground':'grey',
                                               } )
        output.addTagStyle( 'invisiblesep', '--+' )

        output.tag_configure('arguments', { 'font':Pmw.logicalfont('Courier',
                                                                   -2,
                                                                   #weight='bold',
                                                                   ),
                                            'foreground':'#0000ff',
                                            }
                             )
        output.addTagStyle('arguments', '^Arguments:')
        output.addTagStyle('arguments', "^\W+'")

        #
        # HappyDoc output
        #
        output.tag_configure('documenting', { 'font':Pmw.logicalfont('Helvetica',
                                                                     -2,
                                                                     weight='bold'),
                                              }
                             )
        output.addTagStyle( 'documenting', '\w*Documenting' )
        output.addTagStyle( 'documenting', '\w*Adding' )

        output.tag_configure('warning', {'font':Pmw.logicalfont('Helvetica',
                                                                -2,
                                                                weight='bold'),
                                         'foreground':'#ff00ff',
                                         })
        output.addTagStyle('warning', 'Could not')
        output.addTagStyle('warning', '^IMPLEMENT')

        output.tag_configure('teststats', {'font':Pmw.logicalfont('Helvetica',
                                                                  weight='bold',
                                                                  ),
                                           'foreground':'#00ff00',
                                           'background':'#000000',
                                           })
        output.addTagStyle('teststats', 'Ran')

        output.tag_configure('path', {'font':Pmw.logicalfont('Courier',
                                                             -2,
                                                             ),
                                           })
        output.addTagStyle('path', '/')

        #
        # Last resort
        #
        output.addTagStyle( 'continue', '^\W+')
        
        output.pack(
            side=TOP,
            expand=YES,
            fill=BOTH,
            )
        return

    # updateProgress
    # busyStart
    # busyEnd
    # interior
    # 

if __name__ == '__main__':
    HappyDocTestGUI().run()
    
