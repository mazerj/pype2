#!/usr/bin/env python
#
# $Id: openoffice.py,v 1.2 2002/08/04 10:47:30 doughellmann Exp $
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

"""Utilities for working with OpenOffice documents.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: openoffice.py,v $',
    'rcs_id'       : '$Id: openoffice.py,v 1.2 2002/08/04 10:47:30 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'HappyDoc',
    'created'      : 'Fri, 12-Oct-2001 09:35:18 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.2 $',
    'date'         : '$Date: 2002/08/04 10:47:30 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import os
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
from UserDict import UserDict
from xml.sax import saxlib, saxexts
import zipfile
    
#
# Import Local modules
#
import happydoclib.path
from happydoclib.StreamFlushTest import StreamFlushTest

#
# Module
#


class Style:
    "A TextFile Style definition"

    def __init__(self, organizationProperties, styleProperties):
        "Initialize the style."
        self.org_properties = organizationProperties
        self.style_properties = styleProperties

        try:
            self.name = organizationProperties['style:name']
        except KeyError:
            self.name = 'default'
        self.family = organizationProperties['style:family']
        return

    def __cmp__(self, other):
        "Compare this Style with another"
        org_compare = cmp( self.org_properties.items(),
                           other.org_properties.items()
                           )
        if org_compare:
            return org_compare
        style_compare = cmp( self.style_properties.items(),
                             other.style_properties.items()
                             )
        return style_compare



    
class StyleCatalog:
    """A collection of Styles in a TextFile.

    The catalog is organized into 'families'.
    """
    
    def __init__(self):
        self._catalogs = {
            'graphics':{},
            'paragraph':{},
            'character':{},
            }
        return

    def getFamilies(self):
        "Return the list of families"
        return self._catalogs.keys()

    def getFamily(self, family):
        "Return the contents of a family"
        return self._catalogs[family]

    def addStyle(self, style):
        "Add a style to the catalog."
        try:
            catalog = self._catalogs[style.family]
        except KeyError:
            self._catalogs[style.family] = {}
            catalog = self._catalogs[style.family]
            
        name = style.name
        catalog[name] = style
        return

    def __cmp__(self, other):
        "Compare this catalog with another."
        return cmp(self._catalogs, other._catalogs)



    

class StyleCatalogHandler(saxlib.HandlerBase):
    "Extract information from StyleCatalog data."

    def __init__(self):
        "Initialize"
        self.style_catalog = StyleCatalog()
        self._current_style = None
        return

    def startElement(self, ele, attr):
        
        if ele in ('style:default-style', 'style:style'):
            if self._current_style:
                raise RuntimeError('Parser has encountered unexecpted start %s' % ele)
            else:
                self._current_style = (ele, attr, {})
                #print '<%s %s>' % (ele, str(attr.items()))
            
        elif ele in ('style:properties',):
            if not self._current_style:
                #raise RuntimeError('Parser has encountered unexecpted start %s' % ele)
                pass
            else:
                for name, val in attr.items():
                    self._current_style[2][name] = val
                #print '\t<%s %s>' % (ele, str(attr.items()))
        #else:
        #    print '#<%s %s>' % (ele, str(attr.items()))
        return

    def endElement(self, ele):
        
        if ele in ('style:style', 'style:default-style'):
            if self._current_style:
                orig_element, org_properties, style_properties = self._current_style
                new_style = Style(org_properties, style_properties)
                self.style_catalog.addStyle(new_style)
                self._current_style = None
                #print '</%s>' % ele
            else:
                raise RuntimeError('Parser has encountered unexpected end %s' % ele)
            
        #print '/Element %s' % ele
        return

    def getStyleCatalog(self):
        "Return the style catalog."
        return self.style_catalog
    



    
class TextFile(zipfile.ZipFile):
    """OpenOffice Text File
    """
    def __init__(self, filename, mode='a', templateFileName=None):
        "Initialize the OpenOffice TextFile"
        zipfile.ZipFile.__init__(self, filename, mode=mode)
        self.template_filename = templateFileName
        return

    #
    # Default contents for required files
    #
    _default_contents = {

        'Pictures/':'',

        'META-INF/manifest.xml':'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE manifest:manifest PUBLIC "-//OpenOffice.org//DTD Manifest 1.0//EN" "Manifest.dtd">
<manifest:manifest xmlns:manifest="http://openoffice.org/2001/manifest">
</manifest:manifest>''',

        'content.xml':'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE office:document-content PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "office.dtd">
<office:document-content xmlns:office="http://openoffice.org/2000/office" xmlns:style="http://openoffice.org/2000/style" xmlns:text="http://openoffice.org/2000/text" xmlns:table="http://openoffice.org/2000/table" xmlns:draw="http://openoffice.org/2000/drawing" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:number="http://openoffice.org/2000/datastyle" xmlns:svg="http://www.w3.org/2000/svg" xmlns:chart="http://openoffice.org/2000/chart" xmlns:dr3d="http://openoffice.org/2000/dr3d" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:form="http://openoffice.org/2000/form" xmlns:script="http://openoffice.org/2000/script" office:class="text" office:version="1.0">
</office:document-content>''',

        'meta.xml':'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE office:document-meta PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "office.dtd">
<office:document-meta xmlns:office="http://openoffice.org/2000/office" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:meta="http://openoffice.org/2000/meta" office:version="1.0">
</office:document-meta>
        ''',

        'settings.xml':'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE office:document-settings PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "office.dtd">
<office:document-settings xmlns:office="http://openoffice.org/2000/office" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:config="http://openoffice.org/2001/config" office:version="1.0">
</office:document-settings>''',

        'styles.xml':'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE office:document-styles PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "office.dtd">
<office:document-styles xmlns:office="http://openoffice.org/2000/office" xmlns:style="http://openoffice.org/2000/style" xmlns:text="http://openoffice.org/2000/text" xmlns:table="http://openoffice.org/2000/table" xmlns:draw="http://openoffice.org/2000/drawing" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:number="http://openoffice.org/2000/datastyle" xmlns:svg="http://www.w3.org/2000/svg" xmlns:chart="http://openoffice.org/2000/chart" xmlns:dr3d="http://openoffice.org/2000/dr3d" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:form="http://openoffice.org/2000/form" xmlns:script="http://openoffice.org/2000/script" office:version="1.0">
</office:document-styles>''',

        }


    def writeDataToNameInFile(self, arcname, data, compress_type=None):
        "Write data buffer to the archive under the name arcname."
        try:
            zinfo = self.NameToInfo[arcname]
        except KeyError:
            tmpnam=os.tmpnam()
            f=open(tmpnam, 'w')
            f.write(data)
            f.close()
            self.write(filename=tmpnam, arcname=arcname, compress_type=compress_type)
            os.unlink(tmpnam)
        else:
            self.writestr(zinfo, data)
        return

    def _initRequiredManifest(self):
        "Intialize the contents of a ZipFile that are required for a TextFile."

        if self.template_filename:
            get_data = TextFileTemplate(self.template_filename).read
        else:
            get_data = self._default_contents.get

        #
        # Get these values from defaults or from template, depending
        # on whether we have a template.
        #
        for name in (
                      'META-INF/manifest.xml',
                      'styles.xml',
                      ):
            if not self.NameToInfo.has_key(name):
                self.writeDataToNameInFile(arcname=name, data=get_data(name))

        #
        # Take these values only from defaults, even if we have
        # a template.
        #
        get_data = self._default_contents.get
        for name in ( 'Pictures/',
                      'content.xml',
                      'meta.xml',
                      'settings.xml',
                      ):
            if not self.NameToInfo.has_key(name):
                self.writeDataToNameInFile(arcname=name, data=get_data(name))
                
        return

    def close(self):
        "Close the archive file and ensure it contains enough pieces to be valid."
        if ('a' in self.mode) or ('w' in self.mode):
            self._initRequiredManifest()
        zipfile.ZipFile.close(self)
        return

    def getStyleCatalog(self):
        "Returns the style definitions for the TextFile."
        
        style_data = self.read('styles.xml')
        style_data_buffer = StringIO(style_data)
        
        parser = saxexts.make_parser()
        handler = StyleCatalogHandler()
        parser.setDocumentHandler(handler)
        
        parser.parseFile(style_data_buffer)

        style_catalog = handler.getStyleCatalog()
        
        return style_catalog


    
class TextFileTemplate(TextFile):
    """OpenOffice Text File Template
    """

    
class OpenOfficeUnitTest(StreamFlushTest):

    def __init__(self, methodName, outputDir=''):
        StreamFlushTest.__init__(self, methodName, outputDir)
        return

    def testCreateNewOOTextFile(self):
        output_dir = os.path.join(self.output_dir, 'createNewOOTextFile')
        happydoclib.path.rmkdir(output_dir)
        filename = os.path.join(output_dir, 'openoffice.sxw')
        new_file = TextFile(filename, 'w')
        assert new_file, 'Could not instantiate OpenOffice TextFile object.'
        new_file.close()
        assert os.path.exists(filename), 'Could not create OpenOffice text file.'

    def _compareManifests(self, file1, file2):
        "Verify that the manifests for the open files are the same."
        file1_names = file1.namelist()
        file2_names = file2.namelist()
        for n in file1_names:
            if n == 'layout-cache':
                continue
            assert (n in file2_names), '%s has item (%s) in manifest not in %s' \
                   % (file1.filename, n, file2.filename)
        for n in file2_names:
            if n == 'layout-cache':
                continue
            assert (n in file1_names), '%s has item (%s) in manifest not in %s' \
                   % (file2.filename, n, file1.filename)
        return

    def _compareStyleCatalog(self, file1, file2):
        "Verify that the style catalogs for both files are the same."
        
        file1_styles = file1.getStyleCatalog()
        assert file1_styles, 'No styles in %s' % file1.filename
        file2_styles = file2.getStyleCatalog()
        assert file2_styles, 'No styles in %s' % file2.filename

        assert file1_styles == file2_styles, 'Style catalogs are different.'
        
        return
    
    def testCreateNewOOTextFileFromTemplate(self):
        output_dir = os.path.join(self.output_dir, 'createNewOOTextFileFromTemplate')
        happydoclib.path.rmkdir(output_dir)

        filename = os.path.join(output_dir, 'openoffice.sxw')
        template_name = './happydoclib/formatter/OpenOffice/default_styles.stw'

        if os.path.exists(filename):
            os.unlink(filename)
        assert not os.path.exists(filename), 'Could not unlink %s' % filename
        
        new_file = TextFile(filename, 'w',
                            templateFileName=template_name)
        assert new_file, 'Could not instantiate OpenOffice TextFile object.'
        new_file.close()
        del new_file
        new_file = TextFile(filename)
        assert new_file, 'Could not re-open %s to read' % filename
        
        template_file = TextFileTemplate(template_name)
        assert template_file, 'Could not instantiate OpenOffice TextFileTemplate object.'

        self._compareManifests(new_file, template_file)
        self._compareStyleCatalog(new_file, template_file)

        #
        # Check contents of new file against defaults
        #
        for name in ( 'Pictures/',
                      'content.xml',
                      'meta.xml',
                      'settings.xml',
                      ):
            expected_value = TextFile._default_contents[name]
            actual_value = new_file.read(name)
            
            assert actual_value == expected_value, '%s does not match default' % name

        #
        # Check contents of new file against template
        #
        for name in ( 'META-INF/manifest.xml',
                      'styles.xml',
                      ):
            expected_value = template_file.read(name)
            actual_value = new_file.read(name)
            assert actual_value == expected_value, '%s does not match template' % name

        return
