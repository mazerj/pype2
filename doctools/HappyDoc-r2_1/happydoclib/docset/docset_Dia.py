#!/usr/bin/env python
#
# COPYRIGHT
#
#   Permission to use, copy, modify, and distribute this software and
#   its documentation for any purpose and without fee is hereby
#   granted, provided that the above copyright notice appear in all
#   copies and that both that copyright notice and this permission
#   notice appear in supporting documentation, and that the name of
#   Doug Hellmann not be used in advertising or publicity pertaining
#   to distribution of the software without specific, written prior
#   permission.
#
# DISCLAIMER
#
#   DOUG HELLMANN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
#   SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
#   FITNESS, IN NO EVENT SHALL DOUG HELLMANN BE LIABLE FOR ANY
#   SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#   WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
#   AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
#   ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
#   THIS SOFTWARE.
# 


"""Documentation set which writes output in dia format.

  Some known bugs/deficiencies

    - you can NOT specify an output filename yet, it is fixed to
    'dia.dia' (quite easy to solve, I just haven't had the time). The
    dia file is not yet compressed, but it can be used without changes
    in dia. If you save the file from within dia, it will be saved in
    gzipped format (without .gz).
  
    - in some cases, the generalization arrows are not actually
    connected to the class, but sometimes they will 'snap' to the
    right class when you move the class box on the screen. This
    appears only (I think) if the name of the class in the dia class
    font (which is a proportional font) is longer than the longest
    method-name (which is displayed in a non proportional font).  At
    the moment I compute the size of the boxes only by calculating the
    width of the string for the longest method name. I have no idea
    how to get the length of the class name string :( ( I can work
    around this one, if I connected the arrows to the left side of the
    boxes instead of the middle, but I like it better that way.)
  
    - If a base class is not included in the directories the dia file
    is produced from, a message will be issues 'base_class <...> not
    found' and a dummy UML object is created (with just one __init__
    method).
  
    - The Layout is of course not really good (esp. for automatically
    generated base classes, since they will be put in the same 'line'
    as the class where it is needed)
  
    - No package support right now.  Just a matter of time ;-)
  
    - I assume that each class name is unique. If you have several
    classes with the same name, one of the classes will have all the
    generalizations arrows!

  To Do

    - update an existing dia file if you change the python code
    (e.g. just adding the new methods).
  
    - automatically generate python code for an UML diagram?
    
    - add attributes as well (matter of the parser)

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name':'$RCSfile: docset_Dia.py,v $',
    'creator':'Joerg Henrichs <jhenrichs@gmx.de>',
    'project':'HappyDoc',
    'created':'Sun, 26-Mar-2000 11:19:54 EST',
    #
    #  Current Information
    #
    'author':'$Author: doughellmann $',
    'version':'$Revision: 1.2 $',
    'date':'$Date: 2002/08/04 12:04:41 $',
    'locker':'$Locker:  $',
    }
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import copy
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

#
# Import Local modules
#
import happydoclib.happydocset

#
# Module
#

def entryPoint():
    "Return info about this module to the dynamic loader."
    return { 'name':'Dia',
             'factory':DiaDocSet,
             }

#
# Do not use multiple lines in the class docstring, since it shows up as
# part of the generated help message for the app and multiple lines throws
# off the formatting.
#
class DiaDocSet(happydoclib.happydocset.DocSet):
    """Documentation set written in dia format.

    Parameters

      *Adds no additional parameters not understood by DocSet.*
    
    """

    def __init__(self, formatterFactory, parserFunc, inputModuleNames,
                 usePackages=0,
                 defaultParserConfigValues={},
                 **extraNamedParameters):
        extra_args = {}
        extra_args.update(extraNamedParameters)
        extra_args['usePackages'] = usePackages
        apply(happydoclib.happydocset.DocSet.__init__,
              (self, formatterFactory, parserFunc,
               defaultParserConfigValues,
               inputModuleNames),
              extra_args)
        return
    
    def write(self):
        "Write the documentation set to the output."
        self.statusMessage('Beginning to write...')
        #
        # Get the name of and open the docset root file
        #
        self._root_name = self.getFullOutputNameForObject(None)
        self._output = self.openOutput( self._root_name, self._title, '' )

        #
        # Write the output
        #
        self._writePackages()
        self._writeModules()
        #
        # Close things up
        #
        self.close()
        return


    # ---------------------------------------------------------------
    def _writePackages(self):
        "Output documentation for all packages."
        self.statusMessage()
        self.statusMessage('Writing package documentation...')
        package_items = self._all_packages.items()
        package_items.sort()
        for package_name, package in package_items:
            package._write()
        return
    
    # ---------------------------------------------------------------
    def _writeAllClasses(self, classes, class2bases, class2module):
        # classes and class2bases will be modified here. Since the
        # original content is still needed, we have to made a copy
        # and modify this copy only. And in case of class2bases, a
        # deep copy is needed :((
        l = copy.copy(classes)
        c2b = copy.deepcopy(class2bases)
        classes.sort()
        # written must just be an non empty list
        written=[1]
        while l and written:
            # Write all classes which do not have any not yet written
            # base classes
            written=[]
            for c in l:
                if not c2b[c]:
                    self._writeClass(class2module[c], c)
                    written.append(c)
            self._formatter.NewLine()
            # Now remove the written classes from the directory of
            # not yet written base classes
            for c in written:
                for c1 in c2b.keys():
                    try:
                        c2b[c1].remove(c)
                    except ValueError:
                        pass
                #try:
                #    del c2b[c]
                #except KeyError:
                #    # This can happen, if you have a duplicate base name
                #    pass
                l.remove(c)
        # write the remaining classes
        # (e.g.: if a base class is not found, a class will
        # still be in the list)
        for c in l:
            self._writeClass(class2module[c], c)
        
    # ---------------------------------------------------------------
    def _writeModules(self):
        "Output documentation for all modules."
        self.statusMessage()
        self.statusMessage('Writing all classes ...')
        (classes, class2bases,class2module) = self._GetAllClassesInformation()

        self._formatter.BeginObjectSection(self._output)
        
        self._writeAllClasses(classes, class2bases, class2module)
            
        self.statusMessage('Writing Generalization ...')
        for module_name in self._all_modules.keys():
            self._writeModuleConnections( module_name )
        self._formatter.EndObjectSection(self._output)
        return

    # ---------------------------------------------------------------
    def _GetAllClassesInformation(self):
        '''Returns a tuple (classes,class2bases, class2module), where
        classes is a list of all classes to write,
        class2bases is a dictionary containing for each class
        the list of all direct subclasses and
        class2module is a dictionary containing for each class the
        module to which this class belongs'''
        module_names = self._all_modules.keys()
        classes      = []
        class2bases  = {}
        class2module = {}
        for moduleName in module_names:
            module =  self._all_modules[moduleName]
            l = self._filterNames(module.getClassNames())
            if l:
                classes=classes+l
            for c in l:
                class2module[c] = module
                b = module.getClassInfo(c)
                # this directory is modified in
                class2bases[c] = b.getBaseClassNames()

        return (classes, class2bases, class2module)
        
    # ---------------------------------------------------------------
    def _writeClass(self, parent, class_name):
        "Output the documentation for the class in the parent object."
        class_info = parent.getClassInfo(class_name)
        method_names = self._filterNames(class_info.getMethodNames())
        #
        # Get the parameters and type of the methods
        # (at the moment: only the name!)
        methods_types_parameters = map(lambda x: (x,None, None), method_names)
        
        if method_names:
            methods_types_parameters.sort()
        self._formatter.WriteObject(class_name,
                                    methods=methods_types_parameters,
                                    output=self._output)

    # ---------------------------------------------------------------
    def _writeModuleConnections(self, module_name):
        "Output the documentation for the module named."
        module = self._all_modules[module_name]
        formatter = self._formatter

        #
        # Write the info for the classes in this module
        #
        class_names = self._filterNames(module.getClassNames())
        if not class_names:
            return
        for class_name in class_names:
            c = module.getClassInfo(class_name)
            base_classes = c.getBaseClassNames()
            for base_class in base_classes:
                self._formatter.writeGeneralization(class_name,base_class,
                                                    self._output)

