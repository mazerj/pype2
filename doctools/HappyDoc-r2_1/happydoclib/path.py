#!/usr/bin/env python
#
# $Id: path.py,v 1.9 2002/08/24 19:48:25 doughellmann Exp $
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

"""Provide a common set of path management functions.

Many of the os.path functions are fronted by functions here to allow
for tracing and consistent use of those functions.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: path.py,v $',
    'rcs_id'       : '$Id: path.py,v 1.9 2002/08/24 19:48:25 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <DougHellmann@bigfoot.com>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Sat, 03-Feb-2001 12:49:56 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.9 $',
    'date'         : '$Date: 2002/08/24 19:48:25 $',
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
import string
import sys
import unittest

#
# Import Local modules
#
from StreamFlushTest import StreamFlushTest
from trace import trace as TRACE

#TRACE.setVerbosity(3)

#
# Module
#

def isSomethingThatLooksLikeDirectory(path):
    return (os.path.isdir(path)
            or
            os.path.islink(path)
            or
            os.path.ismount(path)
            )

def rmkdir(path):
    "Create a directory and all of its children."
    if not path:
        return
    parts = os.path.split(path)
    if len(parts) > 1:
        parent, child = parts
        if not isSomethingThatLooksLikeDirectory(parent):
            rmkdir(parent)
    if not isSomethingThatLooksLikeDirectory(path):
        os.mkdir(path)
    return


def applyPrefixToPath(path, prefix):
    "Add the prefix value to every part of a given path."
    TRACE.into('PATH', 'applyPrefixToPath', path=path, prefix=prefix)
    drive, path = os.path.splitdrive(path)
    parts = string.split( path, os.sep )
    TRACE.writeVar(parts=parts)
    prefix_len = len(prefix)
    real_parts = []
    for p in parts:
        if not p:
            pass
        elif p not in ( '.', '..' ) and (p[:prefix_len] != prefix):
            TRACE.write('modifying "%s"' % p)
            p = '%s%s' % (prefix, p)
        real_parts.append(p)

    TRACE.writeVar(real_parts=real_parts)
    name = apply(os.path.join, real_parts)
    if drive:
        name = os.sep.join((drive, name))
    elif path and path[0] == os.sep:
        name = os.sep + name
    TRACE.outof(name)
    return name

def removePrefix(path, prefix):
    "Remove prefix from the beginning of path, if present."
    TRACE.into('PATH', 'removePrefix', path=path, prefix=prefix)

    path=os.path.normcase(path)
    prefix=os.path.normcase(prefix)
    TRACE.writeVar(path_after_norm_case=path)
    TRACE.writeVar(prefix_after_norm_case=prefix)

    one_up = os.path.dirname(path)
    TRACE.writeVar(one_up=one_up)
    
    common_prefix = commonPrefix(one_up, prefix)
    TRACE.writeVar(common_prefix=common_prefix)
    
    if common_prefix == prefix:
        path = path[len(common_prefix):]
    else:
        TRACE.write('common prefix (%s)' % common_prefix)
        TRACE.write('does not match specified prefix (%s)' % prefix)
        
    TRACE.writeVar(pathMinusPrefix=path)
    while path and (path[0] == os.sep):
        path = path[1:]
        
    TRACE.outof(path)
    return path

def commonPrefix(path1, path2):
    """Find parts of path1 and path2 at the beginning of each which are the same.

    Arguments

      path1 -- A filesystem path.

      path2 -- A filesystem path.

    Returns a string containing the full path which occurs at the
    beginning of both path1 and path2.

    This function differs from os.path.commonprefix in that a part of
    the path is considered the same only if the *full* directory or
    subdirectory name matches.
    """
    TRACE.into('PATH', 'commonPrefix', path1=path1, path2=path2)
    if not path1 or not path2:
        TRACE.outof('')
        return ''
    
    drive1, path1 = os.path.splitdrive(path1)
    TRACE.writeVar(drive1=drive1)
    drive2, path2 = os.path.splitdrive(path2)
    TRACE.writeVar(drive2=drive2)
    if drive1 != drive2:
        TRACE.outof('')
        return ''
    
    path1_parts = string.split(path1, os.sep)
    TRACE.writeVar(path1_parts=path1_parts)
    path2_parts = string.split(path2, os.sep)
    TRACE.writeVar(path2_parts=path2_parts)
    
    common = []
    for p1, p2 in map(None, path1_parts, path2_parts):
        if p1 and p1 == p2:
            TRACE.write('Found common part "%s"' % p1)
            common.append(p1)
        elif not p1:
            pass
        else:
            break
    common = string.join(common, os.sep)
    if drive1 and common:
        TRACE.write('have a drive spec')
        common = os.path.normcase('%s%s%s' % (drive1, os.sep, common))
    elif path1 and path1[0] == os.sep and common and common[0] != os.sep:
        common = os.sep + common
    TRACE.outof(common)
    return common

def joinWithCommonMiddle(path1prefix, path1, path2):
    """Join path1 and path2.

    Arguments

      path1prefix -- Beginning of path1 which should be ignored for
                     comparisons between path1 and path2.

      path1 -- First path to join.

      path2 -- Second path to join, may have part of path1 after
               path1prefix.

    This function is a bit weird.  The result of::

      joinWithCommonMiddle('/root/one', '/root/one/two', 'two/three/filename.txt')

    is::

      /root/one/two/three/filename.txt
    
    """
    #
    # Find the part of path1 which is *not* part of path1prefix
    #
    TRACE.into('PATH', 'joinWithCommonMiddle', path1prefix=path1prefix,
               path1=path1, path2=path2)
    common_prefix = commonPrefix(path1prefix, path1)
    TRACE.writeVar(common_prefix=common_prefix)
    real_base = removePrefix(path1, common_prefix)
    TRACE.writeVar(real_base=real_base)
    #
    # Remove the prefix common to the docset_real_base and
    # file_name.
    #
    common_prefix = commonPrefix(real_base, path2)
    TRACE.write('common prefix with real base and path2:', common_prefix)
    path2 = removePrefix(path2, common_prefix)
    TRACE.write('fixed path2:', path2)
            
    name = join( path1, path2 )
    TRACE.outof(name)
    return name
    

def computeRelativeHTMLLink(fromName, toName, baseDirectory):
    """Compute the relative link between fromName and toName.

    Parameters

      'fromName' -- Named output node from which to compute the link.

      'toName' -- Named output node to which link should point.

      'baseDirectory' -- Name of the base directory in which both
      fromName and toName will reside.
      
    Both fromName and toName are strings refering to URL targets.
    This method computes the relative positions of the two nodes
    and returns a string which, if used as the HREF in a link in
    fromName will point directly to toName.
    """
    TRACE.into('PATH', 'computeRelativeHTMLLink',
               fromName=fromName,
               toName=toName,
               baseDirectory=baseDirectory,
               )
    #
    # Normalize directory names
    #
    fromName = os.path.normpath(fromName)
    toName = os.path.normpath(toName)
    TRACE.writeVar(fromNameNormalized=fromName)
    TRACE.writeVar(toNameNormalized=toName)
    
    #
    # Remove the base directory prefix from both
    #
    fromName = removePrefix(fromName, baseDirectory)
    toName = removePrefix(toName, baseDirectory)
    TRACE.writeVar(fromNameMinusPrefix=fromName)
    TRACE.writeVar(toNameMinusPrefix=toName)
    
    if fromName == toName:
        TRACE.writeVar(toName=toName)
        relative_link = os.path.basename(toName)
    else:
        common_prefix = commonPrefix(os.path.dirname(fromName), os.path.dirname(toName))
        from_name_no_prefix = fromName[len(common_prefix):]
        while from_name_no_prefix and (from_name_no_prefix[0] == os.sep):
            from_name_no_prefix = from_name_no_prefix[1:]
            TRACE.writeVar(from_name_no_prefix=from_name_no_prefix)
        subdir_path = os.path.dirname(from_name_no_prefix)
        parts = string.split(subdir_path, os.sep)
        TRACE.writeVar(parts=parts)
        if parts and parts[0]:
            levels = len(string.split(subdir_path, os.sep))
        else:
            levels = 0
        up_levels = (os.pardir + os.sep) * levels
        to_name_no_prefix = toName[len(common_prefix):]
        if to_name_no_prefix and (to_name_no_prefix[0] == os.sep):
            to_name_no_prefix = to_name_no_prefix[1:]
        relative_link = "%s%s" % (up_levels, to_name_no_prefix)
    TRACE.outof(relative_link)
    return relative_link


def findFilesInDir(directoryName, filenamePattern='*'):
    """Find all files in the directory which match the glob pattern.

    Parameters

      directoryName -- String containing the name of a directory on
      the file system.

      filenamePattern -- String containing a regular expression to be
      used by the glob module for matching when looking for files in
      'directoryName'.

    """
    search_pat = os.path.join( directoryName, filenamePattern )
    found = glob.glob( search_pat )
    return found
    

def removeRelativePrefix(filename):
    """Remove './', '../', etc. from the front of filename.

    Returns a new string, unless no changes are made.
    """
    chars_to_remove = os.curdir + os.sep
    if filename and filename[0] == os.curdir:
        while filename and (filename[0] in chars_to_remove):
            filename = filename[1:]
    return filename


##
## os.path functions
##
def join( *args ):
    "os.path.join"
    TRACE.into('PATH', 'join', args=args)
    result=apply(os.path.join, args)
    TRACE.outof(result)
    return result

def cwd():
    "os.getcwd"
    return os.getcwd()

def normpath( p ):
    "os.path.normpath"
    return os.path.normpath(p)

def isdir( f ):
    "os.path.isdir"
    return os.path.isdir(f)

def exists( f ):
    "os.path.exists"
    return os.path.exists(f)

def basename( f ):
    "os.path.basename"
    return os.path.basename(f)

def dirname( f ):
    "os.path.dirname"
    return os.path.dirname(f)

def splitext( f ):
    "os.path.splitext"
    return os.path.splitext(f)

def split( f ):
    "os.path.split"
    return os.path.split(f)


class PathTest(StreamFlushTest):

    def testApplyPrefixToPath(self):
        expected = os.path.join('BLAH_tmp', 'BLAH_foo')
        actual = applyPrefixToPath(os.path.join('tmp', 'foo'), 'BLAH_')
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    if os.name == 'nt':
        def testApplyPreifxToPathWin32(self):
            expected = 'c:\\BLAH_tmp\\BLAH_foo'
            actual = applyPrefixToPath('c:\\BLAH_tmp\\BLAH_foo', 'BLAH_')
            assert actual == expected, \
                   'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
                   % (expected, actual)
            return
    
    def testApplyPrefixToPathEmpty(self):
        expected = ''
        actual = applyPrefixToPath('', 'BLAH_')
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    def testApplyPrefixToPathRelative(self):
        expected = os.path.join(os.pardir, 'BLAH_tmp', 'BLAH_foo')
        actual = applyPrefixToPath(os.path.join(os.pardir, 'tmp', 'foo'), 'BLAH_')
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    def testRemovePrefix(self):
        expected = 'foo'
        actual = removePrefix(os.sep + os.path.join('tmp', 'foo'), os.sep + 'tmp')
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    if os.name == 'nt':
        def testRemovePrefixWin32(self):
            expected = 'foo'
            actual = removePrefix('c:\\tmp\\foo', 'c:\\tmp')
            assert actual == expected, \
                   'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
                   % (expected, actual)
            return
    
    def testRemovePrefixNotThere(self):
        expected = os.path.join('tmp', 'foo')
        actual = removePrefix(os.path.join('tmp', 'foo'), os.sep + 'blah')
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    if os.name == 'nt':    
        def testRemovePrefixNotThereWin32(self):
            expected = 'c:\\tmp\\foo'
            actual = removePrefix('c:\\tmp\\foo', 'c:\\blah')
            assert actual == expected, \
                   'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
                   % (expected, actual)
            return
    
    def testRemovePrefixEmptyPath(self):
        expected = ''
        actual = removePrefix('', os.sep + 'blah')
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return
    
    def testRemovePrefixEmptyPrefix(self):
        expected = os.path.join('tmp', 'foo')
        actual = removePrefix(os.path.join('tmp', 'foo'), '')
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    def testCommonPrefix(self):
        expected = os.sep + 'tmp'
        actual = commonPrefix(os.sep + os.path.join('tmp', 'foo'),
                              os.sep + os.path.join('tmp', 'blah'))
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    if os.name == 'nt':
        def testCommonPrefixWin32(self):
            expected = 'c:\\tmp'
            actual = commonPrefix('c:\\tmp\\foo',
                                  'c:\\tmp\\blah')
            assert actual == expected, \
                   'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
                   % (expected, actual)
            return

    def testCommonPrefixNone(self):
        expected = ''
        actual = commonPrefix(os.path.join('var', 'tmp', 'foo'),
                              os.path.join('tmp', 'blah')
                              )
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    if os.name == 'nt':
        def testCommonPrefixNoneWin32(self):
            expected = ''
            actual = commonPrefix('c:\\var\\tmp\\foo',
                                  'c:\\tmp\\blah',
                                  )
            assert actual == expected, \
                   'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
                   % (expected, actual)
            return


    def testCommonPrefixEmptyPaths(self):
        expected = ''
        actual = commonPrefix('', os.path.join('tmp', 'blah'))
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        expected = ''
        actual = commonPrefix(os.path.join('var', 'tmp', 'foo'), '')
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return
        
    def testJoinWithCommonMiddle(self):
        expected = os.path.join('root', 'one', 'two', 'three', 'filename.txt')
        actual = joinWithCommonMiddle(os.path.join('root', 'one'),
                                      os.path.join('root', 'one', 'two'),
                                      os.path.join('two', 'three', 'filename.txt')
                                      )
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    if os.name == 'nt':        
        def testJoinWithCommonMiddleWin32(self):
            expected = 'c:\\root\\one\\two\\three\\filename.txt'
            actual = joinWithCommonMiddle('c:\\root\\one',
                                          'c:\\root\\one\\two',
                                          'two\\three\\filename.txt'
                                          )
            assert actual == expected, \
                   'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
                   % (expected, actual)
            return
    
    def testJoinWithCommonMiddleNotCommon(self):
        expected = os.path.join('root', 'one', 'four', 'two', 'three', 'filename.txt')
        actual = joinWithCommonMiddle(os.path.join('root', 'one', 'five'),
                                      os.path.join('root', 'one', 'four'),
                                      os.path.join('two', 'three', 'filename.txt')
                                      )
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    if os.name == 'nt':    
        def testJoinWithCommonMiddleNotCommonWin32(self):
            expected = 'c:\\%s' % os.path.join('root', 'one', 'four', 'two', 'three', 'filename.txt')
            actual = joinWithCommonMiddle('c:\\%s' % os.path.join('root', 'one', 'five'),
                                          'c:\\%s' % os.path.join('root', 'one', 'four'),
                                          os.path.join('two', 'three', 'filename.txt')
                                          )
            assert actual == expected, \
                   'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
                   % (expected, actual)
            return
    
    def testJoinWithCommonMiddleEmptyPrefix(self):
        expected = os.path.join('root', 'one', 'four', 'two', 'three', 'filename.txt')
        actual = joinWithCommonMiddle('',
                                      os.path.join('root', 'one', 'four'),
                                      os.path.join('two', 'three', 'filename.txt')
                                      )
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    if os.name == 'nt':    
        def testJoinWithCommonMiddleEmptyPrefixWin32(self):
            expected = 'c:\\%s' % os.path.join('root', 'one', 'four', 'two', 'three', 'filename.txt')
            actual = joinWithCommonMiddle('',
                                          'c:\\%s' % os.path.join('root', 'one', 'four'),
                                          os.path.join('two', 'three', 'filename.txt')
                                          )
            assert actual == expected, \
                   'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
                   % (expected, actual)
            return
    
    def testJoinWithCommonMiddleEmptyPath1(self):
        expected = os.path.join('two', 'three', 'filename.txt')
        actual = joinWithCommonMiddle(os.path.join('root', 'one', 'five'),
                                      '',
                                      os.path.join('two', 'three', 'filename.txt')
                                      )
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return
        
        
    def testJoinWithCommonMiddleEmptyPath2(self):
        expected = os.path.join('root', 'one', 'two') + os.sep
        actual = joinWithCommonMiddle(os.path.join('root', 'one'),
                                      os.path.join('root', 'one', 'two'),
                                      '')
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    def testComputeRelativeHTMLLink(self):
        expected = 'my.gif'
        actual = computeRelativeHTMLLink('index.html', 'my.gif', '/tmp/base/dir')
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    def testComputeRelativeHTMLLinkUpOneDirectory(self):
        expected = os.path.join(os.pardir, 'my.gif')
        actual = computeRelativeHTMLLink('index.html',
                                         os.path.join(os.pardir, 'my.gif'),
                                         os.path.join('tmp', 'base', 'dir')
                                         )
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return
        

    def testComputeRelativeHTMLLinkInParentDirectory(self):
        expected = os.path.join(os.pardir, 'my.gif')
        actual = computeRelativeHTMLLink(
            os.path.join('tmp', 'base', 'dir', 'index.html'),
            os.path.join('tmp', 'base', 'my.gif'),
            os.path.join('tmp', 'base')
            )
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    def testRemoveRelativePrefixCurrentDir(self):
        expected = 'foo'
        actual = removeRelativePrefix(os.path.join(os.curdir, 'foo'))
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return

    def testRemoveRelativePrefixParentDir(self):
        expected = 'foo'
        actual = removeRelativePrefix(os.path.join(os.pardir, 'foo'))
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return
        
    def testJoin(self):
        expected = os.path.join('tmp', 'foo')
        actual = join('tmp', 'foo')
        assert actual == expected, \
               'Path modification failed.\n\tExpected "%s",\n\tgot      "%s"' \
               % (expected, actual)
        return
               

if __name__ == '__main__':
            unittest.main()
