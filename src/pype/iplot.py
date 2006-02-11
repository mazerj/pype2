# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""Interactive plot utilities

Front end for gracePlot/grace_np. These functions provide a
matlab-like interface to the grace/xmgr plotting program for
generating real-time interactive plot windows

**NOTE** --
This module makes use of a hidden global to preserve state
cross calls giving the user/programmer a matlab-like feel.

*This is the preferred interface for interactive plots in pype*

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

"""

import sys
from gracePlot import *
from grace_np import Disconnected
from Numeric import *


_plothandle = None

def graceplot():
    """Get handle to current plot

    matlab equiv: CGF
    """
    global _plothandle

    if _plothandle is None:
        _plothandle = gracePlot()
    else:
        try:
            # Mon Jul 11 17:04:23 2005 mazer 
            # write a NOP to the grace command pipe to see
            # if the window's still alive
            _plothandle.grace.command('1')
            _plothandle.grace.flush()
            # was: (too slow with big datasets!)
            #_plothandle.redraw()
        except Disconnected:
            _plothandle = gracePlot()
        except ValueError:
            _plothandle = gracePlot()
    return _plothandle

def detach():
    """Detach from the current plot window

    **returns** -- handle to hold on to for future use.
    """
    global _plothandle
    
    p = _plothandle
    _plothandle = None
    return p

def attach(handle):
    """attach to existing plot window

    **returns** -- last handle, so you can restore it
    when you're done...
    """
    global _plothandle

    old = _plothandle
    _plothandle = handle

    # plot will take care of this, don't do it now
    # just in case handle is None..
    #_plothandle = graceplot()
    return old
    

def close():
    """Close current figure window.

    If leaveVisible is true, then the window is just disconnected
    from the current plot handle, but left active (basically so the
    next plot/figure command will open a new window.

    matlab equiv: close    
    """
    global _plothandle
    if _plothandle and not leaveVisible:
        _plothandle.exit()
    _plothandle = None

def figure(handle=None):
    """Create new figure

    This version doesn't take an argument like the matlab version!
    Instead of a figure #, this *can* take a 
    You can only have one like/active grace window open at a time
    using this module.

    matlab equiv: FIGURE
    """
    global _plothandle

    if handle is not None:
        _plothandle = handle
    else:
        if _plothandle:
            _plothandle = None
        _plothandle = graceplot()
    return _plothandle

def grid(on=1):
    """turn grid on/off on current plot
    
    matlab equiv: GRID
    """
    if on:
        s = "on"
    else:
        s = "off"
        
    graceplot()._send('xaxis tick major grid %s' % s)
    graceplot()._send('yaxis tick major grid %s' % s)
    graceplot()._send('xaxis tick minor grid %s' % s)
    graceplot()._send('yaxis tick minor grid %s' % s)

    if on:
        graceplot()._send('xaxis tick major linestyle 2')
        graceplot()._send('yaxis tick major linestyle 2')
        graceplot()._send('xaxis tick minor linestyle 2')
        graceplot()._send('yaxis tick minor linestyle 2')
        
    

def _fixup():
    graceplot()._send('xaxis label char size 0.8')
    graceplot()._send('yaxis label char size 0.8')
    graceplot()._send('xaxis ticklabel char size 0.7')
    graceplot()._send('yaxis ticklabel char size 0.7')

    graceplot()._flush()


def plot(x, y=None, style='k-', err=None, xlog=0, ylog=0):
    """plot dataset
    Simple version of the matlab plot command.
    
    **x,y** -- numeric data vectors; if only one is provided, then
    we assume it's y-values and just generate a 1:N vector for x.

    **style** -- line style in matlab-like format

    **err** -- optional error bars (same length as y!)
    
    matlab equiv: PLOT
    """

    if y is None:
        y = x
        x = range(len(y))

    linestyle, color, symbol = _parsestyle(style)

    if not (symbol is None):
        symbol = 1
    graceplot().plot(x, y, dy=err, symbols=symbol, styles=1, color=color)

    if xlog:
        graceplot()._send('xaxes scale logarithmic')
    else:
        graceplot()._send('xaxes scale normal')
    if ylog:
        graceplot()._send('yaxes scale logarithmic')
    else:
        graceplot()._send('yaxes scale normal')

    _fixup()

def polar(r, theta, style='k-', err=None, degrees=1):
    """polar plot dataset
    Simple version of the matlab plot command.
    
    **r,theta** -- numeric data vectors

    **style** -- line style in matlab-like format

    **err** -- optional error bars (same length as y!)
    
    **degrees** -- theta is in deg (default is degrees; use 0 for radians)
    
    matlab equiv: POLAR
    """

    h = graceplot().hold(1)

    r = array(r)
    theta = array(theta)

    if degrees:
        theta = pi * (array(theta) / 180.0)
    r = resize(r, (shape(r)[0]+1,))
    theta = resize(theta, (shape(theta)[0]+1,))
    if err:
        err = resize(err, (shape(err)[0]+1,))
        
    x = r * cos(theta)
    y = r * sin(theta)

    linestyle, color, symbol = _parsestyle(style)

    if not (symbol is None):
        symbol = 1
    graceplot().plot(x, y, symbols=symbol, color=color)
    if err:
        err = array(err)
        a = r - err
        b = r + err
        for n in range(len(r)-1):
            x = [a[n] * cos(theta[n]), b[n] * cos(theta[n])]
            y = [a[n] * sin(theta[n]), b[n] * sin(theta[n])]
            graceplot().plot(x, y, color=color)
    if err:
        m = max(r+err)
    else:
        m = max(r)
    graceplot().plot([-m, m], [0, 0], color=1)
    graceplot().plot([0, 0], [-m, m], color=1)

    #graceplot().xlimit(-m, m)
    #graceplot().ylimit(-m, m)

    _fixup()
    
    graceplot().hold(h)

def hist(x, nbins=15):
    """Simple histogram function.

    **x** -- data set as numeric vector
    
    **nbins** -- number of histogram bins

    matlab equiv: HIST
    """
    import stats
    counts, smallest, binsize, extras = stats.histogram(x, nbins)
    graceplot().histoPlot(counts,
                          x_min=smallest,
                          x_max=smallest+len(counts)*binsize,
                          fillcolor=2, edgecolor=1, labeled=0)

def title(s):
    """Add title string at top of plot.

    **s** -- string

    matlab equiv: TITLE
    """
    graceplot().subtitle(s)

def subtitle(s):
    """Add 'subtitle' string at top of plot

    **s** -- string

    matlab equiv: none
    """
    graceplot().subtitle(s)

def xlabel(s):
    """Add x-axis title.
    
    **s** -- string

    matlab equiv: xlabel
    """
    graceplot().xlabel(s)

def ylabel(s):
    """Add y-axis title.

    **s** -- string

    matlab equiv: xlabel
    """
    graceplot().ylabel(s)

def xrange(lower, upper):
    """Set range on x-axis.

    matlab equiv: none
    """
    graceplot().xlimit(lower, upper)

def yrange(lower, upper):
    """Set range on y-axis.

    matlab equiv: none
    """
    graceplot().ylimit(lower, upper)

def clf():
    """Clear current plot window.

    matlab equiv: CLF
    """
    graceplot().clear()

def hold_on():
    """Lock or hold current plot.

    matlab equiv: HOLD ON
    """
    graceplot().hold(1)

def hold_off():
    """Unlock current plot.
    
    matlab equiv: HOLD OFF
    """
    graceplot().hold(0)

def drawnow():
    """This is a no-op; grace *always* draws now...

    matlab equiv: DRAWNOW
    """
    pass

def subplot(rows, cols, n):
    """Break plot window up into sub-plots.

    Same awkward syntax as the matlab subplot function uses

    **rows,cols** -- number of rows and columns in plot
    
    **n** -- activate n-th subplot in array -- NOTE first plot is ONE!!!!
    
    matlab equiv: SUBPLOT
    """
    p = graceplot()
    p.multi(rows, cols, vgap=0.35, hgap=0.35)
    n = n - 1
    row_num = int(round((n+0.5)/p.cols))
    col_num = n - (row_num * p.cols)
    p.focus(row_num, col_num)

def rawplot(x, y, symbols=None, new=1):
    """DO NOT USE

    Raw access to the underlying graceplot module.
    """
    if new:
        graceplot().hold(0)
    else:
        p.hold(1)
    graceplot().plot(x, y, symbols=symbols)

def _parsestyle(s):
    """INTERNAL

    **s** -- matlab-like description of linetype

    **returns** -- grace-compatible version of the same thing

    **NOTE** -- this won't handle _EVERYTHING_, just the common stuff!
    """
    import string
    l,c,d = None, 'black', None
    
    if string.find(s, '--') >= 0:
        l = 'longdashed'
        s = string.replace(s, '--', '')
    elif string.find(s, '-') >= 0:
        l = 'solid'
        s = string.replace(s, '-', '')
    elif string.find(s, ':') >= 0:
        l = 'dotted'
        s = string.replace(s, ':', '')
    elif string.find(s, '.') >= 0:
        l = None

    #if 'y' in s: c='yellow'
    #elif 'm' in s: c='magenta'
    #elif 'c' in s: c='cyan'
    #elif 'r' in s: c='red'
    #elif 'g' in s: c='green'
    #elif 'b' in s: c='blue'
    #elif 'k' in s: c='black'
    #elif 'w' in s: c='white'

    if 'y' in s: c=5
    elif 'm' in s: c=10
    elif 'c' in s: c=12
    elif 'r' in s: c=2
    elif 'g' in s: c=3
    elif 'b' in s: c=4
    elif 'k' in s: c=1
    elif 'w' in s: c=0
    else: c=11

    if '.' in s: d = 'dot'
    elif 'o' in s: d = 'filled circle'
    elif 'O' in s: d = 'circle'
    elif 'x' in s: d = 'cross'
    elif '+' in s: d = 'plus'
    elif '*' in s: d = 'asterisk'
    elif 'S' in s: d = 'square'
    elif 's' in s: d = 'filled square'
    elif 'D' in s: d = 'diamond'
    elif 'd' in s: d = 'filled diamond'
    elif '^' in s: d = 'triangle'
    elif 'v' in s: d = 'inverted triangle'
    elif '<' in s: d = 'filled triangle'
    elif '>' in s: d = 'filled inverted triangle'
    elif 'P' in s: d = 'octagon'
    elif 'p' in s: d = 'filled octagon'
    elif 'h' in s: d = 'filled octagon'

    return l,c,d


if __name__ == '__main__':
    from Numeric import *

    x = arange(10);
    
    plot(x, x, 'r')
    hold_on()
    plot(x, 1+x, 'k-')
    plot(x, 2+x, 'b-')
    plot(x, 3+x, 'g-')
    plot(x, 4+x, 'y-')
    hold_off()

    title('1')
    sys.stdout.write('>>'); sys.stdin.readline()
    
    saved = detach()

    plot(range(100), range(100), '-')
    title('2')
    sys.stdout.write('>>'); sys.stdin.readline()

    old = attach(saved)
    
    plot(range(10), range(10), '-')
    title('3')
    sys.stdout.write('>>'); sys.stdin.readline()

    plot(range(10), range(10), 'o')
    title('4')
    sys.stdout.write('>>'); sys.stdin.readline()

    plot(range(10), range(10), '-')
    title('5')
    sys.stdout.write('>>'); sys.stdin.readline()

    saved = attach(old)
    title('bye bye')
