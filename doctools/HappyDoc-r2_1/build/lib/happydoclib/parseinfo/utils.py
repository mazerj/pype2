#!/usr/bin/env python
#
# $Id: utils.py,v 1.2 2001/11/18 22:13:24 doughellmann Exp $
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

"""Utility functions for parseinfo package.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: utils.py,v $',
    'rcs_id'       : '$Id: utils.py,v 1.2 2001/11/18 22:13:24 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Sun, 11-Nov-2001 10:47:39 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.2 $',
    'date'         : '$Date: 2001/11/18 22:13:24 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import pprint
import symbol
import token
import types

#
# Import Local modules
#


#
# Module
#

    
#  This pattern identifies compound statements, allowing them to be readily
#  differentiated from simple statements.
#
COMPOUND_STMT_PATTERN = (
    symbol.stmt,
    (symbol.compound_stmt, ['compound'])
    )



# This pattern matches the name of an item which appears in a
# testlist sequence.  This can be used for finding the
# base classes of a class, or the parameters to a function or
# method.
#
# BASE_CLASS_NAME_PATTERN = (
#     symbol.test,
#     (symbol.and_test,
#      (symbol.not_test,
#       (symbol.comparison,
#        (symbol.expr,
#         (symbol.xor_expr,
#          (symbol.and_expr,
#           (symbol.shift_expr,
#            (symbol.arith_expr,
#             (symbol.term,
#              (symbol.factor,
#               (symbol.power,
#                (symbol.atom, 
#                 (token.NAME, ['name'])
#                 )))))))))))))
BASE_CLASS_NAME_PATTERN = (
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
             (symbol.factor, ['power'])
             ))))))))))



#  This pattern will match a 'stmt' node which *might* represent a docstring;
#  docstrings require that the statement which provides the docstring be the
#  first statement in the class or function, which this pattern does not check.
#
DOCSTRING_STMT_PATTERN = (
    symbol.stmt,
    (symbol.simple_stmt,
     (symbol.small_stmt,
      (symbol.expr_stmt,
       (symbol.testlist,
        (symbol.test,
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
                   (symbol.power,
                    (symbol.atom,
                     (token.STRING, ['docstring'])
                     )))))))))))))))),
     (token.NEWLINE, '')
     ))

def joinCodeSnippets(first, second, separator):
    """Join two code snippets into one string.

    Use some general code content rules to try to make the
    resulting snippet look nice.
    """
    
    if second.strip() in ('.',):
        sep_to_be_used = ''
        
    elif second and ( second[0] in ('.', ',', '(',) ):
        if second[0] == '(' and first and first[-1] == ',':
            sep_to_be_used = separator
        else:
            sep_to_be_used = ''
        
    elif (not first) or (first and first[-1] in ('.',)) or (first in ('-',)):
        sep_to_be_used = ''
        
    elif ( (first and ( first[-1] in ('(', '[', '{') )) and
           (second and ( second[-1] in (')', ']', '}') ))
           ):
        sep_to_be_used = ''
        
    elif first and ( first[-1] in ('(', '[', '{') ):
        sep_to_be_used = separator
        
    else:
        sep_to_be_used = separator
                
    text = '%s%s%s' % (first, sep_to_be_used, second)
    return text



def parseTreeToString(tree, separator=' '):
    """Convert a parse tree to a string which would have parsed in that way.

    Given a parse tree, walk it to determine the original string
    which would have been parsed to produce that tree.
    """
    #pprint 'STRINGING: ',
    #pprint.pprint(tree)
    text = ''
    if tree and type(tree) in (types.TupleType, types.ListType):
        if type(tree[0]) in (types.TupleType, types.ListType):
            tree_parts = tree
        else:
            tree_parts = tree[1:]
        sub_parts = map( lambda x, s=separator: parseTreeToString(x, s),
                         tree_parts)
        for one_part in sub_parts:
            text = joinCodeSnippets(text, one_part, separator)
    else:
        text = str(tree)
    return text




def findNode(tree, node, response=None):
    "Return a sequence of subtrees starting with node value of 'node'."
    if response == None:
        response = []
    if type(tree) not in (types.ListType, types.TupleType):
        return response
    if tree[0] == node:
        response.append(tree)
    else:
        for subtree in tree[1:]:
            findNode(subtree, node, response)
    return response




def drill(tree, depth):
    "Return the section of the parse 'tree' that is 'depth' nodes deep."
    for i in range(depth):
        try:
            tree = tree[1]
        except IndexError:
            return ()
    return tree


    

def match(pattern, data, vars=None, dbg=0):
    """Match `data' to `pattern', with variable extraction.

    pattern --
        Pattern to match against, possibly containing variables.

    data --
        Data to be checked and against which variables are extracted.

    vars --
        Dictionary of variables which have already been found.  If not
        provided, an empty dictionary is created.

    The `pattern' value may contain variables of the form ['varname'] which
    are allowed to match anything.  The value that is matched is returned as
    part of a dictionary which maps 'varname' to the matched value.  'varname'
    is not required to be a string object, but using strings makes patterns
    and the code which uses them more readable.

    This function returns two values: a boolean indicating whether a match
    was found and a dictionary mapping variable names to their associated
    values.
    """
    pattern_type = type(pattern)
    #if dbg:
    #    print 'PATTERN: ',
    #    pprint.pprint(pattern)
    #    print 'DATA:',
    #    pprint.pprint(data)
    if vars is None:
        vars = {}
    if pattern_type is types.ListType:       # 'variables' are ['varname']
        #if dbg:
        #    print 'storing "%s" for variable "%s"' % (data, pattern[0])
        vars[pattern[0]] = data
        return 1, vars
    if pattern_type is not types.TupleType:
        #if dbg:
        #    print 'end recursion'
        #    print 'pattern=', pattern
        #    print 'data', data
        #
        # Ignore comments, since the pattern will include an empty
        # string.
        #
        if (pattern_type == types.StringType) and (data and data[0] == '#'):
            return 1, vars
        return (pattern == data), vars
    if len(data) != len(pattern):
        #if dbg:
        #    print 'shortcut, length does not match'
        return 0, vars
    for pattern, data in map(None, pattern, data):
        #if dbg:
        #    print 'recursing'
        same, vars = match(pattern, data, vars, dbg=dbg)
        if not same:
            break
    return same, vars





def lenientMatch(pattern, data, vars=None, dbg=0):
    """Match `data' to `pattern', with variable extraction.

    pattern --
        Pattern to match against, possibly containing variables.

    data --
        Data to be checked and against which variables are extracted.

    vars --
        Dictionary of variables which have already been found.  If not
        provided, an empty dictionary is created.

    The `pattern' value may contain variables of the form ['varname'] which
    are allowed to match anything.  The value that is matched is returned as
    part of a dictionary which maps 'varname' to the matched value.  'varname'
    is not required to be a string object, but using strings makes patterns
    and the code which uses them more readable.

    This function is based on the match() function, but is more lenient.
    The pattern does not have to completely describe the tree.  Instead,
    it can be the 'top' portion of the tree.  Everything must match down
    to the leaves of the pattern.  At that point, the matching stops.  If
    a match was found at all, the return values indicate a match.
    
    This function returns two values: a boolean indicating whether a match
    was found and a dictionary mapping variable names to their associated
    values.
    """
    #if dbg:
    #    print 'PATTERN : ',
    #    pprint.pprint(pattern)
    #    print 'DATA    :',
    #    #pprint.pprint(data)
    #    print data
    if vars is None:
        vars = {}
    if type(pattern) is types.ListType:       # 'variables' are ['varname']
        #if dbg:
        #    print 'storing "%s" for variable "%s"' % (data, pattern[0])
        vars[pattern[0]] = data
        return 1, vars
    if type(pattern) is not types.TupleType:
        #if dbg:
        #    print 'end recursion'
        return (pattern == data), vars
    found_match = 0
    if pattern and data:
        for pattern, data in map(None, pattern, data):
            #if dbg:
            #    print 'recursing'
            same, vars = lenientMatch(pattern, data, vars, dbg=dbg)
            if not same:
                break
            else:
                found_match = same
    return found_match, vars
