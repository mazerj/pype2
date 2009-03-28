# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**Read tar/tar.gz files through pipes**

This is *not* a very efficient implementation.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

import posix

def tarfile(tarfile, fname=None, asfile=None):
    if tarfile[-1] == 'z':
        compressed = 'z'
    else:
        compressed = ''
        
    if fname is None:
        if compressed:
            cmd = 'gunzip < %s | tar tf - 2>/dev/null' % tarfile
        else:
            cmd = 'tar tf - <%s 2>/dev/null' % tarfile
        fp = posix.popen(cmd, 'r')
        l = []
        for line in fp.readlines():
            if len(line) == 0: break
            l.append(line[0:-1])
        fp.close()
        return l
    else:
        if compressed:
            cmd = 'gunzip < %s | tar xfO - %s 2>/dev/null' % (tarfile, fname)
        else:
            cmd = 'tar xfO - %s <%s 2>/dev/null' % (fname, tarfile)
        fp = posix.popen(cmd, 'r')
        if asfile:
            return fp
        data = fp.read()
        fp.close()
        if len(data) == 0:
            return None
        else:
            return data

if __name__ == '__main__':
    #sys.stderr.write('%s does nothing as main.\n' % __name__)
    print tarfile('foo.tar', 'sprite.py', asfile=1)
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass

