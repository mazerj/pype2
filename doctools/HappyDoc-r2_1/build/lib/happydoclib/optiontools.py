#!/usr/bin/env python
#
# $Id: optiontools.py,v 1.2 2001/11/25 13:24:20 doughellmann Exp $
#
# Time-stamp: <01/11/25 08:19:50 dhellmann>
#
# Copyright 2001 Doug Hellmann
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

"""Functions for handling options and arguments.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile: optiontools.py,v $',
    'rcs_id'       : '$Id: optiontools.py,v 1.2 2001/11/25 13:24:20 doughellmann Exp $',
    'creator'      : 'Doug Hellmann <DougHellmann@bigfoot.com>',
    'project'      : 'HappyDoc',
    'created'      : 'Sat, 03-Feb-2001 09:55:18 EST',

    #
    #  Current Information
    #
    'author'       : '$Author: doughellmann $',
    'version'      : '$Revision: 1.2 $',
    'date'         : '$Date: 2001/11/25 13:24:20 $',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import string
import types

#
# Import Local modules
#
from StreamFlushTest import StreamFlushTest

#
# Module
#

def getParameters(prefix, args, prefixSeparator='_'):
    """Find parameter settings in an argument sequence.

    Arguments

      prefix -- Parameter names must begin with this string followed
                by 'prefixSeparator'.

      args -- Sequence containing arguments to scan.

      prefixSeparator -- String separating 'prefix' from actual
                         parameter names.
      
    """
    #
    # What we're going to return
    #
    parameter_set = {}
    ignored_values = []
    #
    # Local variables are faster to access
    #
    ignore = ignored_values.append
    find = string.find
    split = string.split
    prefix_len = len(prefix)
    full_prefix_len = prefix_len + len(prefixSeparator)
    #
    # Process candidates
    #
    for candidate in args:
        #
        # Check that this *is* a parameter
        #
        if find(candidate, '=') < 0:
            ignore(candidate)
            continue
        #
        # Check that this is our parameter
        #
        if candidate[:prefix_len] != prefix:
            ignore(candidate)
            continue
        #
        # Handle the parameter, it's ours.
        #
        param_with_prefix, val = split(candidate, '=')
        param = param_with_prefix[full_prefix_len:]
        parameter_set[param] = val
    return ignored_values, parameter_set



def getBooleanArgumentValue(inputValue):
    """Convert value for a boolean argument into a boolean representation.

    When presented with a representation of a boolean value, convert that
    represetntation to a 1 or 0 and return it.  Currently accepts:

      - integer or floating point values

      - strings (with mixed case) with words 'true', 'false', 'yes',
        'no', 'on', 'off', 'None'

    """
    t = type(inputValue)
    
    if t in ( types.IntType, types.FloatType ):
        #
        # Convert floats to ints
        #
        bool_val = int(inputValue)
        
    elif t == types.StringType:
        #
        # Convert strings with mixed case versions
        # of words that mean true and false.
        #
        lower_input = string.lower(inputValue)
        if lower_input in ('y', 'true', 'yes', 'on'):
            bool_val = 1
        elif lower_input in ('n', 'false', 'no', 'off', 'None'):
            bool_val = 0
        else:
            #
            # Try to interpret the value as 
            try:
                bool_val = int(inputValue)
            except ValueError:
                pass
            
    elif not inputValue:
        #
        # Recognize other types which might indicate false.
        #
        # We do not have a similar test for true because false
        # positives are easier to have happen.
        #
        bool_val = 0
        
    try:
        return bool_val
    except NameError:
        #
        # Wasn't able to get a bool_val, so the name does
        # not resolve.
        #
        raise ValueError('Unrecognized boolean value', inputValue)


class OptionToolTest(StreamFlushTest):

    def testBooleanConversion(self):
        for true_val in ( 1, -1, '1', '-1', 'y', 'Y', 'yes', 'Yes', 'YES',
                          'on', 'On', 'ON', ):
            assert getBooleanArgumentValue(true_val), \
                   'Failed to convert %s to a true value.' % str(true_val)
        for false_val in ( 0, '0', 'n', 'N', 'no', 'No', 'NO',
                           'off', 'Off', 'OFF', ):
            assert not getBooleanArgumentValue(false_val), \
                   'Failed to convert %s to a false value.' % str(false_val)
        

    def testParameterExtraction(self):
        expected_vals = {
            'a':'A',
            'b':'B',
            'longName':'longValue',
            }
        expected_left_overs = [ 'foo', 'blah' ]
        
        left_overs, actual_vals = getParameters( 'foo',
                                                [ 'foo_a=A',
                                                  'foo_b=B',
                                                  'foo_longName=longValue',
                                                  'foo',
                                                  'blah',
                                                  ]
                                                )
        assert actual_vals == expected_vals, \
               'Did not find expected parameters.  Got %s' % str(actual_vals)
        assert left_overs == expected_left_overs, \
               'Did not preserve expected left overs.  Got %s' % str(left_overs)
        return
    
