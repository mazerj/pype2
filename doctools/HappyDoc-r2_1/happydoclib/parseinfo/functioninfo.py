#!/usr/bin/env python
#
# $Id: functioninfo.py,v 1.2 2002/08/04 12:06:49 doughellmann Exp $
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

"""Gather information about a function or method definition.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: functioninfo.py,v $',
    'rcs_id'       : '$Id: functioninfo.py,v 1.2 2002/08/04 12:06:49 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Sun, 11-Nov-2001 10:54:53 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.2 $',
    'date'         : '$Date: 2002/08/04 12:06:49 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import symbol
import token

#
# Import Local modules
#
import happydoclib
from happydoclib.parseinfo.suite import SuiteInfoBase
from happydoclib.parseinfo.utils import *

#
# Module
#


class SuiteFuncInfo:
    #  Mixin class providing access to function names and info.

    def getFunctionNames(self):
        return self._function_info.keys()

    def getFunctionInfo(self, name):
        return self._function_info[name]

    
class FunctionInfo(SuiteInfoBase, SuiteFuncInfo):
    "Gather information about a function or method definition."
    
    def __init__(self, parent=None, tree = None, commentInfo={}):
        """Initialize the info extractor.

        Parameters:

            parent -- parent object for this object (e.g. Module or Function)

            tree -- parse tree from which to extract information

            commentInfo -- comments extracted from the source file holding
            this module

        """
        happydoclib.TRACE.into('FunctionInfo', '__init__',
                               parent=parent,
                               tree=tree,
                               commentInfo=commentInfo,
                               )
        SuiteInfoBase.__init__(self, tree[2][1], parent, parent.getFilename(),
                               (tree and tree[-1] or None),
                               commentInfo=commentInfo)
        parameter_data = self._extractFunctionParameters(tree)
        self._constructParameterInfo(parameter_data)
        self._exception_info = self._extractThrownExceptions(tree)
        #if self._exception_info:
        #    print 'EXCEPTIONS: ',
        #    pprint.pprint(self._exception_info)
        happydoclib.TRACE.outof()
        return


    def getReference(self, formatter, sourceNode):
        "Return a reference to this function from sourceNode."
        ref = formatter.getNamedReference( self, self.getName(), sourceNode.name )
        return ref
    
    def getFullyQualifiedName(self):
        "Return a complete, unique, name representing this object."
        return self.getParent().getFullyQualifiedName()
    
    ##
    ## EXCEPTIONS
    ##
    
    EXCEPTION_BY_NAME_PATTERN = (
        (symbol.factor, ['exception'])
        )
    
    EXCEPTION_STRING_PATTERN = (
        (symbol.factor,
         (symbol.power,
          (symbol.atom,
           (token.STRING, ['exception'])
           )))
        )
        
    def getExceptionNames(self):
        "Return a list of the names of any exceptions raised by the function."
        return self._exception_info.keys()

    def getExceptionInfo(self, exceptionName):
        """Returns a type value for an exception.

        The return value will be one of (token.NAME, token.STRING)
        indicating whether the exception was thrown as a string
        or a named object.
        """
        return self._exception_info[exceptionName]

    def _extractThrownExceptions(self, tree):
        "Return a dictionary of exception->exception_type values."
        #dbg = 0
        thrown_exceptions = {}
        
        if not tree:
            return thrown_exceptions
        
        if type(tree) in (types.ListType, types.TupleType):

            raise_tree_list = findNode(tree, symbol.raise_stmt)
            
            for tree in raise_tree_list:
                
                try:
                    subtree = drill(tree[2], 10)
                except IndexError:
                    subtree = tree
                    
                #if dbg: print 'subtree: ', parseTreeToString(subtree)
                #if dbg: print 'found raise: ', parseTreeToString(tree)
                #if dbg: print 'parsing...'

                #
                # Initialize
                #
                exception_name = None
                exception_type = None
                
                if not exception_name:
                    found, vars = lenientMatch(
                        self.EXCEPTION_STRING_PATTERN,
                        tree,
                        #dbg=1
                        )
                    if found and vars.has_key('exception'):
                        #if dbg: print 'FOUND STRING EXCEPTION: ', vars
                        exception_name = vars['exception']
                        exception_type = token.STRING
                        #if dbg: print 'GOT EXCEPTION: ', exception_name

                if not exception_name:
                    found, vars = lenientMatch(
                        self.EXCEPTION_BY_NAME_PATTERN,
                        tree,
                        #dbg=1
                        )
                    if found and vars.has_key('exception'):
                        #if dbg: print 'FOUND NAMED EXCEPTION: ', vars
                        # Threw a named thing, record the name.
                        exception_name = parseTreeToString(vars['exception'])
                        exception_type = token.NAME
                        #if dbg: print 'GOT EXCEPTION: ', exception_name
                        
                if not exception_name:
                    #if dbg: print 'NO NAME,',
                    if len(tree) >= 3:
                        slice=tree[2:]
                        if slice:
                            #if dbg: print 'using slice of 2:1=', slice
                            exception_name = parseTreeToString(slice)
                        else:
                            #if dbg: print 'using whole tree=', tree
                            execption_name = parseTreeToString(tree)

                if exception_name:
                    #if dbg: print 'STORING REFERENCE'
                    thrown_exceptions[exception_name] = exception_type
                    
        #if dbg and thrown_exceptions: print 'EXCEPTIONS: ', thrown_exceptions.keys()
        return thrown_exceptions

    ##
    ## PARAMETERS
    ##
    
    # This pattern matches the name of an item which appears in a
    # testlist sequence.  This can be used for finding the
    # base classes of a class, or the parameters to a function or
    # method.
    #
    PARAMETER_DEFAULT_PATTERN = (
        symbol.test,
        (symbol.and_test,
         (symbol.not_test,
          (symbol.comparison,
           (symbol.expr,
            (symbol.xor_expr,
             (symbol.and_expr,
              (symbol.shift_expr,
               (symbol.arith_expr, ['term'], ['trailer'], ['trailer_bits'])
               ))))))))
    
    oldPARAMETER_DEFAULT_PATTERN = (
        symbol.test,
        (symbol.and_test,
         (symbol.not_test,
          (symbol.comparison,
           (symbol.expr,
            (symbol.xor_expr,
             (symbol.and_expr,
              (symbol.shift_expr,
               (symbol.arith_expr,
                (symbol.term,
                 (symbol.factor,
                  (symbol.power, ['atom'])
                    )))))))))))
    PARAMETER_DEFAULT_WITH_TRAILER_PATTERN = (
        symbol.test,
        (symbol.and_test,
         (symbol.not_test,
          (symbol.comparison,
           (symbol.expr,
            (symbol.xor_expr,
             (symbol.and_expr,
              (symbol.shift_expr,
               (symbol.arith_expr,
                (symbol.term,
                 (symbol.factor,
                  (symbol.power, ['atom'], ['trailer'], ['trailer_bits'])
                  ))))))))))
        )
    PARAMETER_ARITH_DEFAULT_WITH_TRAILER_PATTERN = (
        symbol.test,
        (symbol.and_test,
         (symbol.not_test,
          (symbol.comparison,
           (symbol.expr,
            (symbol.xor_expr,
             (symbol.and_expr,
              (symbol.shift_expr,
               (symbol.arith_expr,
                #(symbol.term,
                # (symbol.factor,
                #  (symbol.power, ['atom'], ['trailer'], ['trailer_bits'])
                #  ))
                ['expression'], ['trailer'], ['trailer_bits']
                ))))))))
        )

    def _constructParameterInfo(self, parameterData):
        """Construct storable parameter data from a parameter list.
        
        Given the sequence of tuples extracted as a parameter list,
        store the names (in order) in self._parameter_names and the
        information about the parameter in self._parameter_info where
        the keys are the parameter name and the info is a tuple containing:

        (default_specified, default_value, default_value_type)

        Where:

            default_specified -- boolean indicating whether a default value
                                 was specified

            default_value -- the default value given, if any

            default_value_type -- the type of the default value (token.STRING,
                                  token.NAME, None). A type of None means
                                  unknown.
            
        """
        parameter_info = {}
        parameter_names = []
        for (param, default_specified,
             default_value, default_value_type) in parameterData:
            parameter_names.append(param)
            parameter_info[param] = ( default_specified,
                                      default_value,
                                      default_value_type,
                                      )
        self._parameter_names = tuple(parameter_names)
        self._parameter_info = parameter_info
        return

    def getParameterNames(self):
        """Returns a list of the names of all
        parameters to the function, in order."""
        return self._parameter_names

    def getParameterInfo(self, paramName):
        """Returns the info record for a parameter.

        The returned tuple consists of:

        (default_specified, default_value, default_value_type)

        Where:

            default_specified -- boolean indicating whether a default value
                                 was specified

            default_value -- the default value given, if any

            default_value_type -- the type of the default value (token.STRING,
                                  token.NAME, None). A type of None means
                                  unknown.
                                  
        """
        return self._parameter_info[paramName]
    
    def _extractFunctionParameters(self, tree):
        "Extract information about a function's parameters."
        dbg=0
        #if dbg: print
        #if dbg: print self._name
        function_parameters = []
        parameters = tree[3]
        #if dbg: pprint.pprint(parameters)
        if parameters[1][0] != token.LPAR:
            raise 'Unrecognized parse result %s in %s' % (parameters[1],
                                                          parameters)
        if parameters[2][0] == token.RPAR:
            # No parameters: def func()
            return function_parameters
        if parameters[2][0] != symbol.varargslist:
            raise 'Unrecognized parse result %s in %s' % (parameters[2],
                                                          parameters)
        #
        # Move down the parse tree and process the argument list
        #
        parameters = parameters[2]
        #if dbg: pprint.pprint(parameters)
        found_varargs = 0 # are we looking at a variable argument parameter?
        found_kwargs = 0  # are we looking at keyword argument parameter?
        name = None # what is the name of the parameter?
        found_default_value = None # did we see a default value for the param?
        default_value = None # what is the default value?
        default_value_type = None # what is the type of the default value?
        
        for parameter in parameters[1:]:

            # Shortcut cases
            if parameter[0] == token.COMMA:
                continue
            
            if parameter[0] == token.STAR:
                # Start variable argument definition
                found_varargs = 1

            if parameter[0] == token.DOUBLESTAR:
                # Start keyword argument definition
                found_kwargs = 1

            if (parameter[0] in (token.NAME, symbol.fpdef)) and name:
                # We've already found a name,
                # handle adding the previous
                # def to a list.
                function_parameters.append( (name,
                                             found_default_value,
                                             default_value,
                                             default_value_type) )
                name = found_default_value = None
                default_value = None
                default_value_type = None

            if parameter[0] == token.NAME:
                #
                # (Possibly fix and)
                # remember the new name
                #
                name = parameter[1]
                if found_varargs:
                    name = '*%s' % name
                elif found_kwargs:
                    name = '**%s' % name
                continue
                    
            if parameter[0] == symbol.fpdef:
                # Here we've made the concious decision
                # to include 'self' in the parameter list,
                # even if this is a method.  Renderers
                # will know (by context) whether we are
                # a method, and at that point can decide to
                # leave out the first parameter in the
                # paramter list.  This safeguards us from
                # [a] having to know whether we are a method
                # and [b] having to know whether the author
                # of the code used 'self' as the name of
                # 'self'.
                #
                name = parameter[1][1]
                continue

            if parameter[0] == token.EQUAL:
                #
                # Default value for the current parameter
                # coming up...
                #
                found_default_value = 1
                continue
            
            if parameter[0] == symbol.test:
                #
                # This is a parameter definition.
                #

                # Look for ARITH_EXPR parameter
                found, vars = lenientMatch(
                    #self.PARAMETER_DEFAULT_WITH_TRAILER_PATTERN,
                    self.PARAMETER_DEFAULT_PATTERN,
                    parameter,
                    #dbg=1
                    )
                
                if found:

                    #if dbg: print 'FOUND: %s:' % name,
                    #if dbg: pprint.pprint(vars)

                    if vars.has_key('term'):
                        default_value, default_value_type = \
                                       self._reconstructValueFromAtom(
                            vars['term'],
                            [
                            vars['trailer'],
                            vars['trailer_bits'],
                            ]
                            )

                else:
                    print 'UNRECOGNIZED:',
                    pprint.pprint(parameter)
                        
        ##
        ## <end> for parameter in parameters[1:]:
        ##
            
        if name:
            # Handle the last parameter
            #
            function_parameters.append( (name,
                                         found_default_value,
                                         default_value,
                                         default_value_type) )
        #if dbg: print 'FOUND PARAMETERS: ',
        #if dbg: pprint.pprint(function_parameters)
        return function_parameters

    
    def _reconstructValueFromAtom(self, atom, trailer=[]):
        """Convert an atom portion of a parse tree into the value.

        If the atom represents a string, number or name
        """
        dbg=0
        #if dbg: print '\nRECONSTRUCTING VALUE FROM ATOM:',
        #if dbg: pprint.pprint(atom)
        #if trailer and dbg:
        #    print 'AND TRAILER:',
        #    pprint.pprint(trailer)
        if len(atom) == 2:
            if atom[1][0] == token.STRING:
                #if dbg: print '\tSTRING'
                value = atom[1][1]
                value = value[1:-1]
                value_type = token.STRING
            elif atom[1][0] == token.NUMBER:
                #if dbg: print '\tNUMBER'
                value = atom[1][1]
                value = eval(value)
                value_type = token.NUMBER
            elif atom[1][0] == token.NAME:
                #if dbg: print '\tNAME'
                value = atom[1][1]
                value_type = token.NAME
                if value == 'None':
                    value = eval(value)
                else:
                    if trailer and filter(lambda x: x, trailer):
                        #if dbg: print '\t\tVALUE: ', value
                        #if dbg: print '\t\tTRAILER: ',
                        #if dbg: pprint.pprint(trailer)
                        #if dbg: print '\t\tSTRING TRAILER: "%s"' % parseTreeToString(trailer)
                        trailer_string = ''
                        for trailer_part in trailer:
                            if not trailer_part: continue
                            part_string = parseTreeToString(trailer_part)
                            trailer_string = joinCodeSnippets(trailer_string,
                                                              part_string,
                                                              ' ')
                        value = joinCodeSnippets(value, trailer_string, ' ')
                        value_type = None
            elif atom[1][0] == symbol.factor:
                #if dbg: print '\tFACTOR'
                value = parseTreeToString(atom)
                value_type = None
                if trailer and filter(lambda x: x, trailer):
                    #if dbg: print '\t\tVALUE: ', value
                    #if dbg: print '\t\tTRAILER: ',
                    #if dbg: pprint.pprint(trailer)
                    #if dbg: print '\t\tSTRING TRAILER: "%s"' % parseTreeToString(trailer)
                    trailer_string = ''
                    for trailer_part in trailer:
                        if not trailer_part: continue
                        part_string = parseTreeToString(trailer_part)
                        trailer_string = joinCodeSnippets(trailer_string,
                                                          part_string,
                                                          ' ')
                    value = joinCodeSnippets(value, trailer_string, ' ')
                    value_type = None
            else:
                #if dbg: print 'UNHANDLED SINGLETON: ', atom[1][0], ':',
                #if dbg: pprint.pprint(atom)
                value = parseTreeToString(atom)
                value_type = None
        elif atom[1][0] in (token.LPAR, token.LSQB, token.LBRACE):
            # Convert the sequence back into a string
            # since that's good enough for representing
            # it in documentation.
            #
            #if dbg: print '\tPARSE TREE TO STRING'
            value = parseTreeToString(atom)
            #if dbg: print '\t', value
            value_type = None
        else:
            #if dbg: print 'UNHANDLED MULTIPLE: ',
            #if dbg: pprint.pprint(atom)
            value = parseTreeToString(atom)
            value_type = None
        #if dbg: print '\tRETURNING: (%s, %s)' % (value, value_type)
        return value, value_type
