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


"""A base class for file-based formatters for HappyDoc.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name':'$RCSfile: fileformatterbase.py,v $',
    'creator':'Doug Hellmann <doug@hellfly.net>',
    'project':'HappyDoc',
    'created':'Sat, 03-Jun-2000 17:56:22 EDT',
    #
    #  Current Information
    #
    'author':'$Author: doughellmann $',
    'version':'$Revision: 1.10 $',
    'date':'$Date: 2002/08/24 19:51:02 $',
    }
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import os
import string
import types

#
# Import Local modules
#
import happydoclib
import happydoclib.StreamFlushTest as StreamFlushTest

#
# Module
#

    
class FileBasedFormatter(happydoclib.happyformatter.HappyFormatterBase):
    """A base class for file-based formatters for HappyDoc.
    """

    def __init__(self, docSet, filenamePrefix='', **extraNamedParameters):
        """Initialize a FileBasedFormatter.

        Parameters

          docSet -- The documentation set controlling the formatter.
          
          filenamePrefix -- A prefix to append to the base names of
          files and directories being created.  This is useful for
          situations where the names which would be automatically
          generated might cause a name clash or conflict.

          extraNamedParameters -- Parameters specified by name which
          were not supported by a subclass initialization.
          
        """
        #
        # Store parameters
        #
        self._filename_prefix = filenamePrefix
        #
        # Initialize the base class
        #
        apply(happydoclib.happyformatter.HappyFormatterBase.__init__,
              (self, docSet,),
              extraNamedParameters)
        return

    def openOutput(self, name, title1, title2=None):
        "Open the named output destination and give the title."
        happydoclib.path.rmkdir(happydoclib.path.dirname(name))
        f = open(name, 'wt')
        if not hasattr(self, 'open_root_file'):
            self.open_root_file = f
        return f

    def closeOutput(self, output):
        "Close the output handle."
        output.close()
        return

    def fixUpOutputFilename(self, filename):
        """Tweak the filename to remove relative references
        and add the safe prefix.

        Returns a relative path, but without the ./ or ../ at the
        front.  This path will then, usually, be tacked on the end of
        the output path to create a full path.
        """
        happydoclib.TRACE.into('FileBasedFormatter', 'fixUpOutputFilename',
                               filename=filename)
        #
        # Remove preceding slashes to make name relative
        #
        filename = happydoclib.path.removeRelativePrefix(filename)
        happydoclib.TRACE.writeVar(filename_after_remove_relative_prefix=filename)
        #
        # Apply the path prefix, if required
        #
        if self.getFilenamePrefix():
            filename = happydoclib.path.applyPrefixToPath( filename,
                                                           self.getFilenamePrefix())
            happydoclib.TRACE.writeVar(filename_after_apply_prefix=filename)
        happydoclib.TRACE.outof(filename)
        return filename
    
    def getOutputNameForFile(self, filename):
        """Return the base name of the thing to which output should be
        written for a file.

        This is usually a file name, but could be anything understood
        by the formatter as a name.  If infoObject is None, return the
        name for a root node for this formatter.
        """
        happydoclib.TRACE.into('FileBasedFormatter', 'getOutputNameForFile',
                               filename=filename)
        filename = self.fixUpOutputFilename(filename)
        happydoclib.TRACE.writeVar(filename=filename)
        #
        # Set the correct extension for the output file
        #
        extension = self.getFilenameExtension()
        happydoclib.TRACE.writeVar(extension=extension)
        #
        # Build the name
        #
        name = '%s.%s' % (filename, extension)
        happydoclib.TRACE.outof(name)
        return name
    
    def getOutputNameForObject(self, infoObject):
        """Return the base name of the thing to which output should be written
        for an info source.

        This is usually a file name, but could be anything understood
        by the formatter as a name.  If infoObject is None, return the
        name for a root node for this formatter.
        """
        happydoclib.TRACE.into('FileBasedFormatter', 'getOutputNameForObject',
                               infoObject=infoObject)
        
        if type(infoObject) == types.StringType:
            happydoclib.TRACE.write('object is a string')
            name = infoObject
            
        elif type(infoObject) == types.FileType:
            happydoclib.TRACE.write('object is a file')
            name = infoObject.name
            
        elif infoObject is not None:
            happydoclib.TRACE.write('object is an infoObject')
            #name = self.getOutputNameForFile(infoObject.getFullyQualifiedName())
            name = apply(happydoclib.path.join, infoObject.getPath() )
            name = '%s.%s' % (name,  self.getFilenameExtension())
            happydoclib.TRACE.write('file for %s' % infoObject.getName())
            happydoclib.TRACE.write('is %s' % name)
            
        else:
            happydoclib.TRACE.write('object is a root node')
            docset_path = self._docset.getPath()
            if docset_path:
                name = apply(happydoclib.path.join, docset_path )
                name = happydoclib.path.join(name, self.getRootNodeName())
            else:
                name = self.getRootNodeName()
            
        happydoclib.TRACE.outof(name)
        return name


    def getLocalOutputNameForObject(self, infoObject):
        """Return a local reference to base name of the thing to which
        output should be written for an info source.

        This is usually a file name, but could be anything understood
        by the formatter as a name.  If infoObject is None, return the
        name for a root node for this formatter.
        """
        extension = self.getFilenameExtension()
        if infoObject is not None:
            name = '%s.%s' % ( infoObject.getQualifiedName(self.getFilenamePrefix()),
                               extension )
        else:
            name = self.getRootNodeName()
        return name

    def getFullOutputNameForObject(self, infoObject):
        """Get the full name, including path, to the object being output.

        The prefix of the return value should be the output path for
        all documentation.  The rest of the return value will be based
        on the path to the source for the object.
        """
        happydoclib.TRACE.into('FileBasedFormatter', 'getFullOutputNameForObject',
                               infoObject=infoObject)

        #
        # Get the basic output name for the object
        #
        obj_output_name = self.getOutputNameForObject(infoObject)
        #
        # Get the root output directory
        #
        output_base = self._docset.getOutputBaseDirectory()
        #
        # Get the base input directory for the docset
        #
        docset_base_directory = self._docset.getDocsetBaseDirectory()
        
        happydoclib.TRACE.writeVar(obj_output_name=obj_output_name)
        happydoclib.TRACE.writeVar(docset_base_directory=docset_base_directory)
        happydoclib.TRACE.writeVar(output_base=output_base)
        
        if (not infoObject) and docset_base_directory:
            #
            # For a docset root node, just tack the object
            # output name onto the output base directory.
            #
            happydoclib.TRACE.write('ROOT NODE FOR CURRENT DOCSET')
            
            #
            # Now reduce docset_base_minux_prefix by the
            # path of the docset itself, so we don't end
            # up with duplicate subdirectory names.
            #
            docset_path = self._docset.getPath()
            if docset_path:
                happydoclib.TRACE.write('removing docset_path')
                docset_path = apply(os.path.join, docset_path)
                len_docset_path = len(docset_path)
                docset_base_minus_prefix = docset_base_directory[:-len_docset_path]
                base = docset_base_minus_prefix
            else:
                happydoclib.TRACE.write('do not need to remove prefix')
                #base = os.path.join(output_base, docset_base_minus_prefix)
                base = docset_base_directory

            happydoclib.TRACE.writeVar(
                base=base,
                )
                
            #name = happydoclib.path.join(output_base, obj_output_name)
            name = happydoclib.path.join(base, obj_output_name)
            
        elif docset_base_directory:
            #
            # Here we have a real HappyDOM based object.
            #
            happydoclib.TRACE.write('SUBNODE OF DOCSET')
            #obj_parent_path = infoObject.getParent().getPath()
            #obj_parent_path = infoObject.getPath()
            #obj_parent_file_path = apply(os.path.join, obj_parent_path)
            #output_dir = happydoclib.path.join(output_base, obj_parent_file_path)

            if type(infoObject) == types.StringType:
                #
                # What we have is a name for an external documentation
                # file, and that file name should include the full
                # path from the docset root down to the file, so
                # just stick the output base on the front and we're
                # done.
                #
                happydoclib.TRACE.write('FILENAME')
                name = os.path.join(output_base,
                                    infoObject)
                
            else:
                happydoclib.TRACE.write('OBJECT')

                #
                # Determine if there is any path component between the
                # docset base and the output base.
                #
                prefix = happydoclib.path.commonPrefix(docset_base_directory,
                                                       output_base,
                                                       )
                docset_base_minus_prefix = happydoclib.path.removePrefix(
                    docset_base_directory,
                    prefix,
                    )
                happydoclib.TRACE.writeVar(
                    prefix=prefix,
                    docset_base_minus_prefix=docset_base_minus_prefix,
                    )

                #
                # Now reduce docset_base_minux_prefix by the
                # path of the docset itself, so we don't end
                # up with duplicate subdirectory names.
                #
                docset_path = self._docset.getPath()
                if docset_path:
                    happydoclib.TRACE.write('removing docset_path')
                    docset_path = apply(os.path.join, docset_path)
                    len_docset_path = len(docset_path)
                    docset_base_minus_prefix = docset_base_minus_prefix[:-len_docset_path]

                happydoclib.TRACE.writeVar(
                    prefix=prefix,
                    docset_base_minus_prefix=docset_base_minus_prefix,
                    docset_path=docset_path,
                    )

                name = os.path.join(output_base,
                                    docset_base_minus_prefix,
                                    obj_output_name,
                                    )
                #name = happydoclib.path.join(output_base, obj_output_name)
                #name = happydoclib.path.join(docset_base_directory, obj_output_name)
            
        else:
            happydoclib.TRACE.write('OTHER')
            #
            # How can we get here?
            #
            name = self.getOutputNameForObject(infoObject)

        #name = os.path.normpath(name)

        happydoclib.TRACE.outof(name)
        return name

    def getFullOutputNameForFile(self, filename):
        "Get the full name, including path, to the filename to convert."
        if self._docset.getOutputBaseDirectory():
            name = happydoclib.path.join(
                self._docset.getOutputBaseDirectory(),
                self.getOutputNameForFile(filename),
                )
        else:
            name = self.getOutputNameForFile(filename)

        name = os.path.normpath(name)
        
        return name

    def getRootNodeName(self):
        "Return the name of the root node for the documentation tree."
        self._requiredOfSubclass('getRootNodeName')
        return

    def getFilenamePrefix(self):
        "Return the filename prefix value for this formatter instance."
        return self._filename_prefix


class FileFormatterBaseTest(StreamFlushTest.StreamFlushTest):

    output_base_dir = os.sep + os.path.join('tmp', 'fakedocset', 'output')
    if os.name == 'nt':
        output_base_dir_win32 = 'c:\\%s' % output_base_dir[1:]
    
    def setUp(self):
        
        class FakeDocset:

            def getPath(self):
                return [  ]
            
            def getOutputBaseDirectory(self):
                return FileFormatterBaseTest.output_base_dir

            def getDocsetBaseDirectory(self):
                return os.path.join(self.getOutputBaseDirectory(),
                                    'docset', 'base', 'directory')
            
        class FakeDocsetWin32:
            def getOutputBaseDirectory(self):
                return FileFormatterBaseTest.output_base_dir_win32

            def getDocsetBaseDirectory(self):
                return 'c:\\' + os.path.join('docset', 'base', 'directory')

        class TestFormatter(FileBasedFormatter):
            def getFilenameExtension(self):
                return 'test'
            def getRootNodeName(self):
                return 'index.test'
            
        self.formatter = TestFormatter(FakeDocset())
        self.formatter_win32 = TestFormatter(FakeDocsetWin32())
        return

    def testFixUpOutputFilenameFromRoot(self):
        expected = os.sep + os.path.join('fix', 'up', 'filename')
        actual = self.formatter.fixUpOutputFilename(
            os.sep + os.path.join('fix', 'up', 'filename')
            )
        assert expected == actual, \
               'Fixed filenames do not match ("%s" vs. "%s").' % (expected, actual)
        return

    if os.name == 'nt':
        def testFixUpOutputFilenameFromRootWin32(self):
            expected = 'c:\\' + os.path.join('fix', 'up', 'filename')
            actual = self.formatter.fixUpOutputFilename(
                'c:\\' + os.path.join('fix', 'up', 'filename')
                )
            assert expected == actual, \
                   'Fixed filenames do not match ("%s" vs. "%s").' % (expected, actual)
            return

    def testFixUpOutputFilenameParentDir(self):
        expected = os.path.join('fix', 'up', 'filename')
        actual = self.formatter.fixUpOutputFilename(
            os.path.join(os.pardir, 'fix', 'up', 'filename')
            )
        assert expected == actual, \
               'Fixed filenames do not match ("%s" vs. "%s").' % (expected, actual)
        return

    def testFixUpOutputFilenameCurrentDir(self):
        expected = os.path.join('fix', 'up', 'filename')
        actual = self.formatter.fixUpOutputFilename(
            os.path.join(os.curdir, 'fix', 'up', 'filename')
            )
        assert expected == actual, \
               'Fixed filenames do not match ("%s" vs. "%s").' % (expected, actual)
        return
            
    def testGetOutputNameForFileAtRoot(self):
        filename = 'filename.py'
        expected = '%s.%s' % (filename, 'test')
        actual = self.formatter.getOutputNameForFile(filename)
        assert expected == actual, \
               'Filenames do not match ("%s" vs. "%s").' % (expected, actual)
        return
            
    def testGetOutputNameForFile(self):
        filename = 'TestCases/test_package_summaries/FromReadme/README.txt'
        expected = '%s.%s' % (filename, 'test')
        actual = self.formatter.getOutputNameForFile(filename)
        assert expected == actual, \
               'Filenames do not match ("%s" vs. "%s").' % (expected, actual)
        return
            
    def testGetFullOutputNameForFileName(self):
        filename = 'TestCases/test_package_summaries/FromReadme/README.txt'
        expected = os.path.join(self.output_base_dir, '%s.%s' % (filename, 'test'))
        actual = self.formatter.getFullOutputNameForFile(filename)
        assert expected == actual, \
               'Filenames do not match ("%s" vs. "%s").' % (expected, actual)
        return
            
##    def testGetFullOutputNameForFileObject(self):
##        filename = 'TestCases/test_package_summaries/FromReadme/README.txt'
##        expected = os.path.join(self.output_base_dir, 'docset', 'base', 'directory', filename)
##        actual = self.formatter.getFullOutputNameForObject(filename)
##        assert expected == actual, \
##               ('Filenames do not match\n'
##                'Expected: "%s"\n'
##                'Got:      "%s"' % (expected, actual)
##                )
##        return

    def testGetOutputNameForObjectNone(self):
        info_obj = None
        expected = 'index.test'
        actual = self.formatter.getOutputNameForObject(info_obj)
        assert expected == actual, \
               'Output name for object does not match ("%s" vs "%s")' % \
               (expected, actual)
        return

    def testGetOutputNameForObjectString(self):
        info_obj = 'filename.test'
        expected = 'filename.test'
        actual = self.formatter.getOutputNameForObject(info_obj)
        assert expected == actual, \
               'Output name for object does not match ("%s" vs "%s")' % \
               (expected, actual)
        return

    def testGetOutputNameForObjectFile(self):
        info_obj = open('tmpfile.test', 'wt')
        expected = 'tmpfile.test'
        actual = self.formatter.getOutputNameForObject(info_obj)
        assert expected == actual, \
               'Output name for object does not match ("%s" vs "%s")' % \
               (expected, actual)
        return

    def testGetOutputNameForObjectFullyQualifiedNameRoot(self):
        import happydoclib.happydom
        class FakeInfoObj(happydoclib.happydom.HappyDOM):
            pass
        info_obj = FakeInfoObj('myfake', None, 'filename.py', [])
        expected = 'myfake.test'
        actual = self.formatter.getOutputNameForObject(info_obj)
        assert expected == actual, \
               'Output name for object does not match (\n"%s"\nvs\n"%s")' % \
               (expected, actual)
        return

    def testGetOutputNameForObjectFullyQualifiedNameOneParent(self):
        import happydoclib.happydom
        class FakeInfoObj(happydoclib.happydom.HappyDOM):
            pass
        parent_obj = FakeInfoObj('myfakeparent', None, 'parent', [])
        info_obj = FakeInfoObj('myfake', parent_obj, 'filename.py', [])
        expected = 'myfakeparent/myfake.test'
        actual = self.formatter.getOutputNameForObject(info_obj)
        assert expected == actual, \
               'Output name for object does not match (\n"%s"\nvs\n"%s")' % \
               (expected, actual)
        return

    def testGetOutputNameForObjectFullyQualifiedNameMultipleParents(self):
        import happydoclib.happydom
        class FakeInfoObj(happydoclib.happydom.HappyDOM):
            pass
        one = FakeInfoObj('one', None, 'parent', [])
        two = FakeInfoObj('two', one, 'parent', [])
        three = FakeInfoObj('three', two, 'parent', [])
        info_obj = FakeInfoObj('myfake', three, 'filename.py', [])
        expected = os.path.join('one', 'two', 'three', 'myfake.test')
        actual = self.formatter.getOutputNameForObject(info_obj)
        assert expected == actual, \
               'Output name for object does not match (\n"%s"\nvs\n"%s")' % \
               (expected, actual)
        return

    def testGetFullOutputNameForObjectFullyQualifiedNameMultipleParents(self):
        import happydoclib.happydom
        class FakeInfoObj(happydoclib.happydom.HappyDOM):
            pass
        one = FakeInfoObj('one', None, 'parent', [])
        two = FakeInfoObj('two', one, 'parent', [])
        three = FakeInfoObj('three', two, 'parent', [])
        info_obj = FakeInfoObj('myfake', three, 'filename.py', [])
        expected = os.path.join(self.output_base_dir,
                                'docset', 'base', 'directory', 'one', 'two', 'three', 'myfake.test')
        actual = self.formatter.getFullOutputNameForObject(info_obj)
        assert expected == actual, \
               'Output name for object does not match (\n"%s"\nvs\n"%s")' % \
               (expected, actual)
        return

    def testGetLocalOutputNameForObjectFullyQualifiedNameRoot(self):
        import happydoclib.happydom
        class FakeInfoObj(happydoclib.happydom.HappyDOM):
            pass
        info_obj = FakeInfoObj('myfake', None, 'filename.py', [])
        expected = 'filename.py.test'
        actual = self.formatter.getLocalOutputNameForObject(info_obj)
        assert expected == actual, \
               'Output name for object does not match ("%s" vs "%s")' % \
               (expected, actual)
        return

    def testGetLocalOutputNameForObjectFullyQualifiedNameOneParent(self):
        import happydoclib.happydom
        class FakeInfoObj(happydoclib.happydom.HappyDOM):
            pass
        parent_obj = FakeInfoObj('myfakeparent', None, 'parent', [])
        info_obj = FakeInfoObj('myfake', parent_obj, 'filename.py', [])
        expected = 'parent_myfake.test'
        actual = self.formatter.getLocalOutputNameForObject(info_obj)
        assert expected == actual, \
               'Output name for object does not match ("%s" vs "%s")' % \
               (expected, actual)
        return

    def testGetFullOutputNameForObjectFullyQualifiedNameRoot(self):
        import happydoclib.happydom
        class FakeInfoObj(happydoclib.happydom.HappyDOM):
            pass
        info_obj = FakeInfoObj('filename', None, 'filename.py', [])
        expected = os.sep + os.path.join('tmp', 'fakedocset', 'output',
                                         'docset', 'base', 'directory',
                                         'filename.test'
                                         )
        actual = self.formatter.getFullOutputNameForObject(info_obj)
        assert expected == actual, \
               'Output name for object does not match\n(\n"%s"\nvs\n"%s")' % \
               (expected, actual)
        return

    if os.name == 'nt':    
        def testGetFullOutputNameForObjectFullyQualifiedNameRootWin32(self):
            import happydoclib
            import happydoclib.happydom
            happydoclib.TRACE.verboseLevel = 1
            class FakeInfoObj(happydoclib.happydom.HappyDOM):
                pass
            info_obj = FakeInfoObj('myfake', None, 'filename.py', [])
            expected = happydoclib.path.join(
                'c:\\',
                os.path.join('tmp', 'fakedocset', 'output', 'filename.py.test')
                )
            actual = self.formatter_win32.getFullOutputNameForObject(info_obj)
            assert expected == actual, \
                   'Output name for object does not match (expect "%s", got "%s")' % \
                   (expected, actual)
            return

    def testGetFullOutputNameForObjectNone(self):
        info_obj = None
        expected = os.path.join(
            self.output_base_dir,
            'docset', 'base', 'directory',
            'index.test'
            )
        actual = self.formatter.getFullOutputNameForObject(info_obj)
        assert expected == actual, \
               ('Output name for object does not match\n'
                'Expected: "%s"\n'
                'Actual:   "%s"' % \
                (expected, actual)
                )
        return

    if os.name == 'nt':    
        def testGetFullOutputNameForObjectNoneWin32(self):
            info_obj = None
            expected = os.path.join('c:\\',
                                    'tmp',
                                    'fakedocset',
                                    'output',
                                    'docset',
                                    'base',
                                    'directory',
                                    'index.test'
                                    )
            actual = self.formatter_win32.getFullOutputNameForObject(info_obj)
            assert expected == actual, \
                   'Output name for object does not match (expected "%s", got "%s")' % \
                   (expected, actual)
            return
    
    def testGetFullOutputNameForObjectFullyQualifiedNameOneParent(self):
        import happydoclib.happydom
        class FakeInfoObj(happydoclib.happydom.HappyDOM):
            pass
        parent_obj = FakeInfoObj('myfakeparentname', None, 'myfakeparentfilename', [])
        info_obj = FakeInfoObj('myfake', parent_obj, 'filename.py', [])
        expected = os.sep + os.path.join('tmp', 'fakedocset', 'output',
                                         'docset', 'base', 'directory',
                                         'myfakeparentname', 'myfake.test'
                                         )
        actual = self.formatter.getFullOutputNameForObject(info_obj)
        assert expected == actual, \
               'Output name for object does not match\n(\n"%s"\nvs\n"%s")' % \
               (expected, actual)
        return

    def testGetFullOutputNameForFileFullyQualifiedNameRoot(self):
        filename = 'filename.py'
        expected = os.sep + os.path.join('tmp', 'fakedocset', 'output',
                                         'filename.py.test'
                                         )
        actual = self.formatter.getFullOutputNameForFile(filename)
        assert expected == actual, \
               'Output name for file does not match\n(\n"%s"\nvs\n"%s")' % \
               (expected, actual)
        return

    def testGetFullOutputNameForFileFullyQualifiedNameOneParent(self):
        filename = os.path.join('parentdir', 'filename.py')
        expected = os.sep + os.path.join('tmp', 'fakedocset', 'output',
                                         'parentdir',
                                         'filename.py.test'
                                         )
        actual = self.formatter.getFullOutputNameForFile(filename)
        assert expected == actual, \
               'Output name for file does not match\n(\n"%s"\nvs\n"%s")' % \
               (expected, actual)
        return

    
