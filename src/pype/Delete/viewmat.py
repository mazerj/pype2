# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""
Glue functions for displaying **Numeric** data using PIL.

Functions for viewing Numeric matrix data using PIL and PPM
images. Derrived from the Python Numeric Tutorial example
code.

PILImage() and PPMImage() are Tkinter widgets derrived from
the label widget that can be used to display Numeric arrays.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

- Sat Jul 27 23:21:18 2002 mazer

 - from Numeric/Demo/NumTut/view.py

 - Modified to remove conditionals and now hard coded to use
   Tkinter+PIL for display.

"""

_DEFAULT_HEIGHT = 255
_MINSIZE = 150
import os, time

from Numeric import *
import Tkinter
import Image
from threading import *

def save_ppm(ppm, fname=None):
    """
    Write PPM file from string data. ppm should be a string generated
    by array2ppm.
    
    returns filename written
    """
    if fname == None:
        fname = tempfile.mktemp('.ppm')
    f = open(fname, 'wb')
    f.write(ppm)
    f.close()
    return fname


def array2ppm(image):
    """
    Convert a Numeric matrix to a PPM string.

    returns string containing image in PPM/PGM format
    Image should be either a 2d matrix (b/w image) or a 3d matrix
    with third dimension of 3 (rgb image)
    """
    # scaling
    if len(image.shape) == 2:
        # B&W: write an 8bit binary PGM file
        image = transpose(image)
        return "P5\n#PPM version of array\n%d %d\n255\n%s" % \
               (image.shape[1], image.shape[0], ravel(image).tostring())
    else:
        # color: write an 8bit binary PPM file
        image = transpose(image, (1, 0, 2))
        return "P6\n%d %d\n255\n%s" % \
               (image.shape[1], image.shape[0], ravel(image).tostring())

def _preprocess(image, (scalex,scaley)):
    assert len(image.shape) in (1, 2) or \
           len(image.shape) == 3 and image.shape[2] == 3, \
           "image not correct format"
    themin = float(minimum.reduce(ravel(image)))
    themax = float(maximum.reduce(ravel(image)))
    if len(image.shape) == 1:
        len_x = image.shape[0]
        ys = ((image - themin)/(themax-themin)*(_DEFAULT_HEIGHT-1)).astype('b')
        image = (zeros((_DEFAULT_HEIGHT, len_x))+255).astype('b')
        for x in range(len_x):
            image[_DEFAULT_HEIGHT-1-ys[x],len_x-x-1] = 0
        image = transpose(image)
    elif image.typecode() != 'b':
        image = (image - themin) / (themax-themin) * 255
        image = image.astype('b')

    len_x, len_y = image.shape[:2]
    if scalex is None:
        if len_x < _MINSIZE:
            scalex = int(float(_MINSIZE) / len_x) + 1
        else:
            scalex = 1
    if scaley is None:
        if len_y < _MINSIZE:
            scaley = int(float(_MINSIZE) / len_y) + 1
        else:
            scaley = 1
    return image, (scalex, scaley)

#----
# threaded stuff starts here
#----

import sys

def tk_root():
    if Tkinter._default_root is None:
        root = Tkinter.Tk()
        Tkinter._default_root.withdraw()
    else:
        root = Tkinter._default_root
    return root

_root = tk_root()

class PILImage(Tkinter.Label):
    def __init__(self, master, data, (scalex, scaley)):
        width, height = data.shape[:2]
        if len(data.shape) == 3:
            mode = rawmode = 'RGB'
            bits = transpose(data, (1,0,2)).tostring()
        else:
            mode = rawmode = 'L'
            bits = transpose(data, (1,0)).tostring()
        self.image2 = Image.fromstring(mode, (width, height),
                                      bits, "raw", rawmode)
        import ImageTk
        self.image = ImageTk.PhotoImage(self.image2)
        Tkinter.Label.__init__(self, master, image=self.image,
                               bg='black', bd=0)

class PPMImage(Tkinter.Label):
    def __init__(self, master, ppm, (scalex, scaley)):
        self.image = Tkinter.PhotoImage(file=save_ppm(ppm))
        w, h = self.image.width(), self.image.height()
        self.image = self.image.zoom(scalex, scaley)
        self.image.configure(width=w*scalex, height=h*scaley)
        Tkinter.Label.__init__(self, master, image=self.image,
                               bg="black", bd=0)

        self.pack()

class _ThreadedTk(Thread):
    def __init__(self, *args, **kw):
        self._done = 0
        apply(Thread.__init__, (self,)+args, kw)

    def done(self):
        self._done = 1

    def run(self):
        while not self._done:
            _pendinglock.acquire()
            if len(_pendingarrays):       # there are files to process
                for image, scales in _pendingarrays:
                    tl = Tkinter.Toplevel(background='black')
                    u = PILImage(tl, image, scales)
                    u.pack(fill='both', expand=1)
                    u.tkraise()
                del _pendingarrays[:]   # we're done
            _pendinglock.release()
            _root.update()  # do your thing
            time.sleep(0.01)   # go to sleep little baby

def view(image, scale=(None,None)):
    """
    Display image using tkinter widget.  Image can be scaled to
    the range specified by scale.
    """
    
    image, scales = _preprocess(image, scale)
    _pendinglock.acquire()
    _pendingarrays.append((image, scales))
    _pendinglock.release()
    while len(_pendingarrays):
        time.sleep(0.01)


_pendingarrays = []
_pendinglock = Lock()
_t = _ThreadedTk() # this starts a Tk interpreter in a separate thread
_t.start()
done = _t.done

# this little bit cleans up
import sys
if hasattr(sys, 'exitfunc'):
    oldexitfunc = sys.exitfunc
else:
    oldexitfunc = None
def cleanup():
    done()
    if oldexitfunc is not None:
        oldexitfunc()
sys.exitfunc = cleanup

if __name__ == '__main__':
    phase = 0.0
    while 1:
        x = sin(arange(0+phase, 6+phase, .1))
        view(x)
        y = cos(2*arange(0+phase, 6+phase, .1))
        z = x[:,NewAxis] + y[NewAxis,:]
        z2 = x[::-1,NewAxis] + y[NewAxis,:]
        z3 = x[:,NewAxis] + y[NewAxis,::-1]
        view(z)
        z = transpose(array((z,z2,z3)), (2,1,0))
        view(z)
        try:
            phase = input("phase (return to quit) = ")
        except:
            break
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass

