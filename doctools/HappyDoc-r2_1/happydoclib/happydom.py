#!/usr/bin/env python
#
# $Id: happydom.py,v 1.5 2002/08/24 19:47:48 doughellmann Exp $
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

"""Base class for accessing documentation extracted from inputs.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: happydom.py,v $',
    'rcs_id'       : '$Id: happydom.py,v 1.5 2002/08/24 19:47:48 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'HappyDoc',
    'created'      : 'Sat, 27-Oct-2001 17:26:26 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.5 $',
    'date'         : '$Date: 2002/08/24 19:47:48 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import string

#
# Import Local modules
#
import happydoclib

#
# Module
#


class HappyDOM:
    """Base class for accessing documentation extracted from inputs.

    """

    _name = ''
    
    def __init__(self, name, parent, filename, namespaces):
        """Initialize the HappyDOM attributes.

        Arguments

          name -- The name of this node.

          parent -- Reference to parent node.

          filename -- The name of the file represented by this node.

          namespaces -- A sequence of namespaces to be scanned, in
                        order, when looking up a name.

        """
        happydoclib.TRACE.into('HappyDOM', '__init__',
                               name=name,
                               parent=parent,
                               filename=filename,
                               namespaces=namespaces)
        self._name = name
        self._parent = parent
        self._filename = filename
        self._namespaces = namespaces
        happydoclib.TRACE.outof()
        return


    def __str__(self):
        return '<%s at id=%s name=%s>' % ( self.__class__.__name__,
                                           id(self),
                                           self.getName())

    def getName(self):
        "Return the name of the object."
        return self._name

    def getParent(self):
        "Return the parent node."
        return self._parent

    def getPath(self):
        "Returns a sequence of node names leading to this node."
        happydoclib.TRACE.into('HappyDom', 'getPath',
                               object=self)
        parent = self.getParent()
        if parent:
            path = parent.getPath()
        else:
            path = []
        name = self.getName()
        happydoclib.TRACE.writeVar(name=name)
        if name:
            path.append( name )
        else:
            happydoclib.TRACE.write('name was empty, ADDED NOTHING')
        happydoclib.TRACE.outof(path)
        return path
    
    def getFilename(self):
        "Return the filename from which the object came."
        happydoclib.TRACE.into('HappyDOM', 'getFilename')
        happydoclib.TRACE.outof(self._filename)
        return self._filename
    
    def getFullyQualifiedName(self):
        "Return a complete, unique, name representing this object."
        happydoclib.TRACE.into('HappyDOM', 'getFullyQualifiedName')
        happydoclib.TRACE.writeVar(name=self.getName())
        if not self.getParent():
            happydoclib.TRACE.write('no parent')
            name = self.getQualifiedName()
        else:
            happydoclib.TRACE.write('with parent')
            parent_name = self.getParent().getFullyQualifiedName()
            parent_base, parent_ext = happydoclib.path.splitext( parent_name )
            happydoclib.TRACE.writeVar(parent_base=parent_base)
            happydoclib.TRACE.writeVar(parent_ext=parent_ext)
            my_file = self.getFilename()
            name = happydoclib.path.join(parent_base, my_file)
        happydoclib.TRACE.outof(name)
        return name    

    def getQualifiedName(self, transTable=string.maketrans('/', '_')):
        happydoclib.TRACE.into('HappyDOM', 'getQualifiedName',
                               selfClass=self.__class__.__name__,
                               )
        happydoclib.TRACE.writeVar(name=self.getName())
        if not self.getParent():
            #
            # Start with the filename for this object
            #
            name = self.getFilename()
            #
            # Remove preceding slashes to make name relative
            #
            name = happydoclib.path.removeRelativePrefix(name)
        else:
            basename = happydoclib.path.basename
            name = '%s_%s' \
                   % (basename(self.getParent().getQualifiedName()),
                      self.getName())
        happydoclib.TRACE.outof(name)
        return name


    def getSymbolInfo(self, name, tryParent=1):
        """Look up the info record for the name.

        Looks in the namespaces registered for this DOM node.  If no
        value is found, 'None' is returned.
        """
        for ns in self._namespaces:
            info = ns.get(name, None)
            if info:
                return info
        if tryParent and self.getParent():
            return self.getParent().getSymbolInfo(name, tryParent)
        return None

    def __getitem__(self, itemName):
        info = self.getSymbolInfo(itemName)
        if not info:
            raise KeyError('Unrecognized name: "%s"' % itemName, itemName)
        return info

    def getReference(self, formatter, sourceNode):
        "Return a reference to this module from sourceNode."
        ref = formatter.getReference(self, sourceNode.name)
        return ref

    def getReferenceTargetName(self):
        "Return the name to use as a target for a reference such as a hyperlink."
        happydoclib.TRACE.into('HappyDOM', 'getReferenceTargetName')
        reference_target_name = self.getName()
        happydoclib.TRACE.outof(reference_target_name)
        return reference_target_name
