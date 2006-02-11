# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""matlab like interface to biggle plotting library

This provides a matlab compatible interface to biggles. Biggles is
only suitable for static, non-interactive graphs. If you want
proper interactive graphs, try the **iplot** modules, which
rovides an interface to grace/xmgr.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Tue Apr  3 12:44:04 2001 mazer  ::

  matlab-like quick plot tools.
    plot(x,y,style),
    hist(n, nbins)
    errorbar(x,y,e,style)
    errorbar2(x,y,xe,ye,style)
    hold_on()
    hold_off()
    clf()
    drawnow() **required**
    subplot(nr,nc,n) or subplot(nr,nc,r,c) (note: r & c zerobased)
    psprint()

  NOTE: PLOTS ARE NOT DRAWN UNTIL YOU CALL DRAWNOW()!!
"""

import Numeric
from biggles import *

configure('default', 'fontface', 'Helvetica')
configure('persistent', 'yes')

from math import fmod

LINES = ("solid", "longdashed", "dotted")

SYMBOLS = ("filled circle", "plus", "asterisk", "circle", "cross", "square",
           "triangle", "diamond", "star", "inverted triangle", "octagon",
           "filled square", "filled triangle", "filled diamond",
           "filled inverted triangle" )

COLORS = ("black", "red", "green", "blue", "magenta", "cyan")

LAST = None
HOLD = None
TABLE = None
NROWS = 1
NCOLS = 1
R = 0
C = 0

def parsestyle(s):
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

    if 'y' in s: c='yellow'
    elif 'm' in s: c='magenta'
    elif 'c' in s: c='cyan'
    elif 'r' in s: c='red'
    elif 'g' in s: c='green'
    elif 'b' in s: c='blue'
    elif 'k' in s: c='black'
    elif 'w' in s: c='white'

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

def gettable():
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    if TABLE is None:
        TABLE = Table(NROWS, NCOLS)
    return TABLE

def subplot(nr, nc, r, c=None):
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    if NROWS != nr or NCOLS != nc:
        TABLE = None
    NROWS = nr
    NCOLS = nc
    if c is None:
        R = int(float(r-1)/float(NCOLS))
        C = int(0.5+fmod(float(r)-1.0, float(NCOLS)))
    else:
        R = r
        C = c

def hold_on():
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    HOLD = LAST

def hold_off():
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C

    HOLD = None

def clf():
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    LAST, HOLD, TABLE = None, None, None
    NROWS, NCOLS = 1, 1
    R, C = 0, 0

def drawnow(width=None, height=None):
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    if TABLE:
        try:
            TABLE.show(width=width, height=height)
        except:
            return None

def xlabel(s):
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    if LAST:
        LAST.xlabel = s
        
def ylabel(s):
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    if LAST:
        LAST.ylabel = s

def xrange(a, b):
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    if LAST:
        LAST.xrange = a, b

def yrange(a, b):
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    if LAST:
        LAST.yrange = a, b

def title(s):
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    if LAST:
        LAST.title = s


def plot(x=None, y=None, style=None, show=None, p=None, label=None):
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    if p is None:
        if HOLD:
            p = HOLD
        else:
            t = gettable()
            p = FramedPlot()
            t[R,C] = p

    try:
        nth = p.mplotnum + 1
    except KeyError:
        nth = 0
    p.mplotnum = nth

    if style:
        lstyle, color, mstyle = parsestyle(style)
    else:
        color=COLORS[nth]
        mstyle=SYMBOLS[nth]
        lstyle=LINES[nth]

    if y is None:
        y = x
        x = range(len(y))
        
    if mstyle:
        c = Points(x, y, color=color, symboltype=mstyle)
        if label:
            c.label = label
        p.add(c)
    if lstyle:
        c = Curve(x, y, color=color, linetype=lstyle)
        if label:
            c.label = label
        p.add(c)
    if show:
        p.show()
    LAST = p
    return c

def imagesc(z, x=None, y=None, show=None, p=None, scale=1):
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    if p is None:
        if HOLD:
            p = HOLD
        else:
            t = gettable()
            p = FramedPlot()
            t[R,C] = p

    try:
        nth = p.mplotnum + 1
    except KeyError:
        nth = 0
    p.mplotnum = nth

    if x is None:
        x = Numeric.arange(0, z.shape[0])
    if y is None:
        y = Numeric.arange(0, z.shape[1])

    if scale:
        z = (0.5 + 255.0 * \
             (z - min(Numeric.ravel(z))) \
             / (max(Numeric.ravel(z)) - \
                min(Numeric.ravel(z)))).astype(Numeric.Int32)
    else:
        z = z.astype(Numeric.Int32)

    # convert RGB/Greyscale to 24bit integer array
    if len(z.shape) == 2:
        z = (z << 16) | (z << 8) | z
    else:
        z = (z[:,:,0] << 16) | (z[:,:,1] << 8) | z[:,:,2]

    i, j = 0, 0
    for ii in range(z.shape[0]):
        i = x[ii]
        for jj in range(z.shape[1]):
            j = z.shape[1] - y[jj]
            c = FillBetween([i,i+1], [j,j], [i,i+1], [j+1,j+1],color=z[ii,jj])
            p.add(c)
    if show:
        p.show()
    LAST = p
    return p
    
def legend(x, y, items):
    if LAST:
        LAST.add(PlotKey(x, y, items))
    

def errorbar(x, y, e, style='ko-', show=None, p=None):
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    if p is None:
        if HOLD:
            p = HOLD
        else:
            t = gettable()
            p = FramedPlot()
            t[R,C] = p

    try:
        nth = p.mplotnum + 1
    except KeyError:
        nth = 0
    p.mplotnum = nth

    if style:
        lstyle, color, mstyle = parsestyle(style)
    else:
        color=COLORS[nth]
        mstyle=SYMBOLS[nth]
        lstyle=LINES[nth]

    if mstyle:
        p.add(Points(x, y, color=color, symboltype=mstyle))
    if lstyle:
        p.add(Curve(x, y, color=color, linetype=lstyle))
    p.add(SymmetricErrorBarsY(x, y, e, color=color))
    
    if show:
        p.show()
    LAST = p
    return p

def errorbar2(x, y, xe, ye, style='ko-', show=None, p=None):
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    if p is None:
        if HOLD:
            p = HOLD
        else:
            t = gettable()
            p = FramedPlot()
            t[R,C] = p

    try:
        nth = p.mplotnum + 1
    except KeyError:
        nth = 0
    p.mplotnum = nth

    if style:
        lstyle, color, mstyle = parsestyle(style)
    else:
        color=COLORS[nth]
        mstyle=SYMBOLS[nth]
        lstyle=LINES[nth]

    if mstyle:
        p.add(Points(x, y, color=color, symboltype=mstyle))
    if lstyle:
        p.add(Curve(x, y, color=color, linetype=lstyle))
    p.add(SymmetricErrorBarsX(x, y, xe, color=color))
    p.add(SymmetricErrorBarsY(x, y, ye, color=color))
    
    if show:
        p.show()
    LAST = p
    return p

def hist(v, nbins=10, vmin=None, vmax=None, show=None, p=None):
    global HOLD, LAST, TABLE, NROWS, NCOLS, R, C
    if p is None:
        if HOLD:
            p = HOLD
        else:
            t = gettable()
            p = FramedPlot()
            t[R,C] = p

    try:
        nth = p.mplotnum + 1
    except KeyError:
        nth = 0
    p.mplotnum = nth
        
    if vmin is None:
        vmin = float(min(v))
    if vmax is None:
        vmax = float(max(v))
    binwidth = (vmax - vmin) / float(nbins-1)
    x = Numeric.arrayrange(vmin, vmax+binwidth, binwidth)
    y = Numeric.zeros(x.shape, 'i')
    for i in range(len(v)):
        n = int(round((float(v[i]) - vmin) / binwidth, 0))
        try:
            y[n] = y[n] + 1
        except IndexError:
            pass
    xx = Numeric.zeros(len(x) * 2 + 3, 'f')
    yy = Numeric.zeros(len(y) * 2 + 3)
    xx[0] = x[0]
    yy[0] = 0
    for i in range(0, len(x)):
        xx[1+2*i],xx[1+2*i+1] = x[i],x[i]+binwidth
        yy[1+2*i],yy[1+2*i+1] = y[i],y[i]
    xx[1+2*i+2] = x[i]+binwidth
    yy[1+2*i+2] = 0;
    xx[1+2*i+3] = x[0];
    yy[1+2*i+3] = 0;

    p.add(FillBelow(xx, yy), Curve(xx, yy))
    p.yrange = 0, max(y)

    if show:
        p.show()
    LAST = p
    return p

def psprint(dest="-"):
    if TABLE:
        TABLE.write_eps(dest)

if __name__=='__main__' :
    import sys, Numeric, RandomArray
    x = Numeric.arrayrange(-10,10);
    y = x**2;
    e = y/4

    a = RandomArray.random([20,20,3])
    imagesc(a, x=range(-10,10), y=range(-10,10))
    drawnow()
    sys.stdin.readline()
    

    a = Numeric.array([[[1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
                [0, 0, 0]],
               [[0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]],
               [[0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]],
               [[0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]]])
    imagesc(a)
    drawnow()
    sys.stdin.readline()

    #plot(list(x), list(y), 'ko-')
    errorbar2(list(x), list(y), e, e, 'ko-')

    subplot(2,3,2)
    plot(x, y, 'ro')

    subplot(2,3,3)
    plot(x, y, 'go')

    subplot(2,3,4)
    plot(x, y, 'b-')

    subplot(2,3,5)
    plot([0, 1], [0, 1], 'o')

    drawnow(width=500, height=200)
    sys.stdin.readline()

    drawnow()
    sys.stdin.readline()
    clf()

    

    plot(x, y, '.')
    drawnow()
    sys.stdin.readline()

    clf()
    plot(x, y, 'r*-')
    hold_on()
    plot(x, -y, 'bv-')
    errorbar(x, y/2, e, 'ko-')
    title('foo')
    xlabel('xbar')
    ylabel('ybar')
    hold_off()
    drawnow()
    
    sys.stdin.readline()
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
		

