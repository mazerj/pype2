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


"""Formatter which produces dia files.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name':'$RCSfile: formatter_Dia.py,v $',
    'creator':'Joerg Henrichs <jhenrichs@gmx.de>',
    'project':'HappyDoc',
    'created':'Sat, 03-Jun-2000 17:58:48 EDT',
    #
    #  Current Information
    #
    'author':'$Author: doughellmann $',
    'version':'$Revision: 1.1 $',
    'date':'$Date: 2001/10/24 21:27:35 $',
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
import happydoclib.indentstring
import happydoclib.formatter.fileformatterbase

#
# Module
#

def entryPoint():
    "Return information about this module to the dynamic loader."
    return {
        'name':'Dia',
        'factory':DiaFormatter,
        }



class DiaFormatter(happydoclib.formatter.fileformatterbase.FileBasedFormatter):
    """Formatter which produces dia files.

      Parameters

        filenamePrefix -- A prefix to preprend to the base names of
                          files and directories being created.  This
                          is useful for situations where the names
                          which would be automatically generated might
                          cause a name clash or conflict.

        dateStampFiles -- Boolean indicating whether or not to include
                          a date/time stamp in files.

        debug -- Enable debugging comments in output.
      
    """

    def __init__(self,
                 docSet,
                 docsetTitle=None,
                 dateStampFiles=1,
                 debug=0,
                 **configuration):
        """Initialize the DiaFormatter.

        Parameters

            'docSet' -- the DocSet instance containing global cross-reference
                      information
            
            '**configuration' -- additional, optional, configuration values

        """
        #
        # Preserve configuration parameters
        #

        self._date_stamp_files = happydoclib.optiontools.getBooleanArgumentValue(
            dateStampFiles)

        self.debug = debug

        #
        # Some attributes to store values needed for the layout
        #
        self._dx         = 0.05        # spacing in the bounding box
        self._dy         = 0.05
        self._xmin       = self._dx    # leftmost point for an object
        self._nextx      = self._xmin  # Position for the next object
        self._nexty      = self._dy
        self._connectlength= 10        # length for connections (general.)
        self._ymax       = -1          # bottom-most Y-position
        self._lastymax   = 0
        # paper width. The (current) algorithms fills one row after each
        # other. As soon as an object would reach the right hand margin,
        # it is placed in the next row - and so on. So the paper heigth
        # is never used.
        self._paperWidth = 200
        
        #
        # Object IDs
        #
        self._objectId       = 0    # counter
        self._ObjName2Id     = {}   # mapping: object name to object id
        self._ObjId2Position = {}   # (x1,y1,x2,y2) position of object
        
        
        #
        # Initialize the base class
        #
        apply( happydoclib.formatter.fileformatterbase.FileBasedFormatter.__init__,
               (self, docSet, docsetTitle),
               configuration)
        return

    ##
    ## FileBasedFormatter implementation
    ##


    # ---------------------------------------------------------------
    def openOutput(self, name, title1, title2='&nbsp;'):
        """Open output destination using 'name' with the title from 'title1'.
        """
        print 'OPEN OUTPUT: ', name
        f = happydoclib.formatter.fileformatterbase.FileBasedFormatter.openOutput(
            self,
            name,
            title1,
            )
        self.fileHeader( title1, title2, f )
        return f

    # ---------------------------------------------------------------
    def fileHeader(self, title1, title2='&nbsp;', output=None):
        """Write the formatting for a file header to the open file."""
        self.writeRaw('''\
<?xml version="1.0"?>
<diagram xmlns:dia="http://www.lysator.liu.se/~alla/dia/">
  <diagramdata>
    <attribute name="background">
      <color val="#ffffff"/>
    </attribute>
    <attribute name="paper">
      <composite type="paper">
        <attribute name="name">
          <string>#A4#</string>
        </attribute>
        <attribute name="tmargin">
          <real val="2.82"/>
        </attribute>
        <attribute name="bmargin">
          <real val="2.82"/>
        </attribute>
        <attribute name="lmargin">
          <real val="2.82"/>
        </attribute>
        <attribute name="rmargin">
          <real val="2.82"/>
        </attribute>
        <attribute name="is_portrait">
          <boolean val="true"/>
        </attribute>
        <attribute name="scaling">
          <real val="1"/>
        </attribute>
        <attribute name="fitto">
          <boolean val="false"/>
        </attribute>
      </composite>
    </attribute>
  </diagramdata>
    ''' % locals(), output)
        return

    # ---------------------------------------------------------------
    def closeOutput(self, output):
        "Close the 'output' handle."
        self.fileFooter(output)
        output.close()
        return

    # ---------------------------------------------------------------
    def fileFooter(self, output):
        """Write the formatting for a file footer to the open file."""
        self.writeRaw('</diagram>', output)
        return

    # ---------------------------------------------------------------
    def BeginObjectSection(self, output):
        """Write the beginning of the object section in the dia file."""
        title = self._docset._title
        self.writeRaw('''<layer name="Background" visible="true">
    <object type="Standard - Text" version="0" id="O11">
        <attribute name="obj_pos">
            <point val="6.0271,-4.71823"/>
        </attribute>
        <attribute name="text">
            <composite type="text">
                <attribute name="string">
                    <string>#%(title)s#</string>
                </attribute>
                <attribute name="font">
                    <font name="Helvetica-Bold"/>
                </attribute>
                <attribute name="height">
                    <real val="1"/>
                </attribute>
                <attribute name="pos">
                    <point val="6.0271,-4.71823"/>
                </attribute>
                <attribute name="color">
                    <color val="#000000"/>
                </attribute>
                <attribute name="alignment">
                    <enum val="1"/>
                </attribute>
            </composite>
        </attribute>
    </object>
''' % locals(), output)

    # ---------------------------------------------------------------
    def EndObjectSection(self, output):
        """Write the end of the object section in the dia file."""
        self.writeRaw('</layer>\n', output)

    # ---------------------------------------------------------------
    def _ComputeSize(self, objectName, methods):
        """Return a tuple consisting of the width and the height of
        an object."""
        if methods:
            num_methods = len(methods)
            maxlen = max(map(lambda x: len(x[0]), methods))
        else:
            print 'WARNING: Using default size values for %s because there are no methods' % objectName
            num_methods = 1
            maxlen = 20
            
        height = num_methods*0.8+2
        width = maxlen*0.4848+2.2544
        return (width, height)
    
    # ---------------------------------------------------------------
    def NewLine(self):
        self._nextx = self._xmin
        self._nexty = self._ymax + self._dy
        
    # ---------------------------------------------------------------
    def WriteObject(self, objectName, methods, output):
        """Writes an object to the dia file.
        Parameters:

        objectName: Name of the class (string)
        methods:    list containing the information about the methods.
                    Each entry in the list is a tuple consisting of
                    (methodName, methodType, methodParameters)
                    """
        width, height = self._ComputeSize(objectName, methods)
        
        # See if this object's width is too big for this row (only
        # if it is not the first object in this row - in that case it
        # has to be placed in this row, as it will fit in no row at all)
        if self._nextx+width>self._paperWidth and self._nextx!=self._xmin:
            self.NewLine()

        objId='O%d'%self._objectId
        self._objectId = self._objectId + 1
        
        para = { 'x'     : self._nextx,
                 'y'     : self._nexty,
                 'width' : width,
                 'height': height,
                 'bb'    : '%f,%f;%f,%f'%(self._nextx-self._dx,
                                          self._nexty-self._dy,
                                          self._nextx+width+self._dx,
                                          self._nexty+height+self._dy),
                 'name'  : objectName,
                 'id'    : objId}
        self._ObjName2Id[objectName]=objId
        self._ObjId2Position[objId]=( self._nextx, self._nexty,
                                      self._nextx+width, self._nexty+height)
        #self._lastymax = self._nexty+height+self._dy
        #self._lastxpos = self._nextx
        # 2*_dx is necessary to allow for the bb border of this and the next
        # object a third _dx is added, to get some space between the objects!
        self._nextx    = self._nextx +width + 3*self._dx 
        if self._nexty+height > self._ymax:
            self._ymax = self._nexty+height+3*self._dy

        self.writeRaw('''<object type="UML - Class" version="0" id="%(id)s">
        <attribute name="obj_pos">
        <point val="%(x)f,%(y)f"/>
        </attribute>
        <attribute name="obj_bb">
        <rectangle val="%(bb)s"/>
        </attribute>
        <attribute name="elem_corner">
        <point val="%(x)f,%(y)f"/>
        </attribute>
        <attribute name="elem_width">
        <real val="%(width)f"/>
        </attribute>
        <attribute name="elem_height">
        <real val="%(height)f"/>
        </attribute>
        <attribute name="name">
        <string>#%(name)s#</string>
        </attribute>
        <attribute name="stereotype">
        <string/>
        </attribute>
        <attribute name="abstract">
        <boolean val="false"/>
        </attribute>
        <attribute name="suppress_attributes">
        <boolean val="false"/>
        </attribute>
        <attribute name="suppress_operations">
        <boolean val="false"/>
        </attribute>
        <attribute name="visible_attributes">
        <boolean val="true"/>
        </attribute>
        <attribute name="visible_operations">
        <boolean val="true"/>
        </attribute>
        <attribute name="attributes"/>
        '''%para, output)
        #
        # Write the methods
        #
        self._writeMethods(methods, output)
        
        self.writeRaw('''<attribute name="template">
        <boolean val="false"/>
      </attribute>
      <attribute name="templates"/>
    </object>'''%para,output)
        
    # ---------------------------------------------------------------
    def _writeMethods(self, methods, output):
        '''Writes the methods of a class.
        Parameter:
        
        methods:    list containing the information about the methods.
                    Each entry in the list is a tuple consisting of
                    (methodName, methodType, methodParameters)'''
        #
        # No methods, write empty method section
        if not methods:
            self.writeRaw('<attribute name="operations"/>\n',output)
            return
        
        #
        # There are methods, write them
        #
        self.writeRaw('<attribute name="operations">\n',output)
        for method,type,parameters in methods:
            if type:
                sType ='<attribute name="type"><string>#%s#</string></attribute>'%\
                        type
            else:
                sType = '<attribute name="type"><string/></attribute>'
            if parameters:
                # not yet implemented
                sParameters = '<attribute name="parameters"/>'
            else:
                sParameters = '<attribute name="parameters"/>'

            para = {'name'      : method,
                    'type'      : sType,
                    'parameters': sParameters}
            
            self.writeRaw('''\
            <composite type="umloperation">
              <attribute name="name"><string>#%(name)s#</string></attribute>
              %(type)s
              <attribute name="visibility"><enum val="0"/></attribute>
              <attribute name="abstract"><boolean val="false"/></attribute>
              <attribute name="class_scope"><boolean val="false"/></attribute>
              %(parameters)s
            </composite>\n'''%para, output)
        #
        # At the end of the loop: write the closing operations section
        self.writeRaw('</attribute>\n',output)
        return

        
    # ---------------------------------------------------------------
    def writeGeneralization(self, class_name, base_class, output):
        '''Write a generalization relation between class_name and
        base_class.'''
        class_name=string.split(class_name,'.')[-1]
        classObjId = self._ObjName2Id.get(class_name, None)
        if not classObjId: 
            print "class_name '%s' not found."%class_name
            self.WriteObject(class_name,[('__init__',None, None)],output)
            classObjId = self._ObjName2Id.get(class_name, None)
            #return
        base_class=string.split(base_class,'.')[-1]
        baseObjId  = self._ObjName2Id.get(base_class, None)
        if not baseObjId:
            print "base_class '%s' not found."%base_class
            self.WriteObject(base_class,[('__init__',None, None)],output)
            baseObjId = self._ObjName2Id.get(base_class, None)
            #return
        classLocation = self._ObjId2Position[classObjId]
        baseLocation  = self._ObjId2Position[baseObjId ]

        # Compute the middle x-position for class and base
        xclass = (classLocation[0]+classLocation[2])/2
        xbase  = (baseLocation[0] +baseLocation[2] )/2
        if (xclass<xbase):
            x1 = xclass
            x2 = xbase
        else:
            x1 = xbase
            x2 = xclass
        if classLocation[3]<baseLocation[3]:
            ymax = baseLocation[3]
            y1 = classLocation[3]
            y2 = baseLocation[3]
        else:
            ymax = classLocation[3]
            y1 = baseLocation[3]
            y2 = classLocation[3]

        ymiddle = (baseLocation[3]+classLocation[1])/2
        objId='O%d'%self._objectId
        self._objectId = self._objectId + 1

        para = {'bb'     : '%f,%f;%f,%f' % (x1-0.85, y1-0.85, x2+0.85,
                                            y2+0.85+self._connectlength),
                'origin' : '%f,%f' % (xbase, baseLocation[3]),
                'p1'     : '%f,%f' % (xbase, baseLocation[3]),
                'p2'     : '%f,%f' % (xbase, ymiddle),
                'p3'     : '%f,%f' % (xclass, ymiddle),
                'p4'     : '%f,%f' % (xclass, classLocation[1]),
                'objId'  : objId,
                'handle0': baseObjId,
                'handle1': classObjId
            }
        self.writeRaw('''\
    <object type="UML - Generalization" version="0" id="$(ObjId)s">
        <attribute name="obj_pos"><point val="%(origin)s"/></attribute>
      <attribute name="obj_bb">
        <rectangle val="%(bb)s"/>
      </attribute>
        <attribute name="orth_points">
        <point val="%(p1)s"/>
        <point val="%(p2)s"/>
        <point val="%(p3)s"/>
        <point val="%(p4)s"/>
      </attribute>
      <attribute name="orth_orient">
        <enum val="1"/>
        <enum val="0"/>
        <enum val="1"/>
      </attribute>
      <attribute name="name"><string/></attribute>
      <attribute name="stereotype"><string/></attribute>
      <connections>
        <connection handle="0" to="%(handle0)s" connection="6"/>
        <connection handle="1" to="%(handle1)s" connection="1"/>
      </connections>
    </object>\n'''%para,output)
        

    # ---------------------------------------------------------------
    def getRootNodeName(self):
        "Returns the name of the root node for documentation of this type."
        return 'dia.dia'

    ##
    ## HappyFormatterBase implementation
    ##


    
if __name__ == '__main__':
    # at the moment: nothing
    pass
