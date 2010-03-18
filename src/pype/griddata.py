# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**Clone of the matlab GRIDDATA function**

This basically works by taking a set of (x,y,z) data and using the
existing data to interpolate z-values for a new set of (X,Y)
coordinates using linear interpolation based on the 3 nearest neighbor
points (from the orignal (x,y,z) set).

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Fri Jan 15 09:53:24 2010 mazer

- migrated from Numeric to numpy

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

try:
	import numpy as _N
except ImportError:
	raise ImportError, "%s requires numpy module" % __name__

def _crossproduct(a, b):
	"""Compute cross product of two 3-d vectors (x,y,z)"""
	if len(a) != 3 or len(b) != 3:
		raise TypeError, "Cross product only for vectors of length 3"
	v = [a[1]*b[2] - a[2]*b[1],
		 a[2]*b[0] - a[0]*b[2],
		 a[0]*b[1] - a[1]*b[0]]
	return _N.array(v)

def _project(a, b, c, x, y):
	"""
	Project a line (x,y,0) to the plane defined by abc (perpendicular
	to the XY plane) and return the z value of the intersection point.

		a,b,c: 3-vectors
		x,y: scalars
		returns: scalar z-value
	"""
	nv = -_crossproduct((a-b),(a-c))
	d = nv[0]*a[0] + nv[1]*a[1] + nv[2]*a[2]
	if nv[2] == 0:
		# points are co-linear, normal isn't defined
		return None
	else:
		return (d - nv[0]*x - nv[1]*y) / nv[2]

def griddata(xd, yd, zd, nx, ny):
	"""Clone of matlab GRIDDATA function.

	**xd, yd, zd** -- all vectors of same length describing the
	surface to be interpolated in 3-space

	**nx, ny** -- 2 vectors indicating the *AXIS* points where new
	z-values are to be computed. nx and ny must be same length;
	(len(nx)*len(ny)) points will be computed.

	**return** -- return in a 2d numeric matrix containing intepolated
	z-values at the grid points defined by nx,ny.

	**NOTE:** griddata() should only be used to interpolate onto a
	regular grid.

	Similar to the matlab griddata() function.	Takes a set of
	XYZ triples that define a surface.	The sampling can be
	irregular or gridded, order doesn't matter.	 The surface is
	then resample on the grid defined by nx and ny using nearest
	neighbor linear interpolation.

	"""
	
	if len(xd) != len(yd) or len(xd) != len(zd):
		raise TypeError, "xd,yd,zd must all be same length"
	
	nz = _N.zeros((len(nx), len(ny)), 'f')
	for i in range(len(nx)):
		for j in range(len(ny)):
			x, y = nx[i], ny[j]
			d = (((xd - x) ** 2) + ((yd - y) ** 2)) ** 0.5
			ix = _N.argsort(d)
			a = _N.array((xd[ix[0]], yd[ix[0]], zd[ix[0]]), 'f')
			b = _N.array((xd[ix[1]], yd[ix[1]], zd[ix[1]]), 'f')
			for n in range(2, len(ix)):
				c = _N.array((xd[ix[n]], yd[ix[n]], zd[ix[n]]), 'f')
				z = _project(a, b, c, x, y)
				if not (z is None):
					break
			if not (z is None):
				nz[i,j] = z
			else:
				# all points are colinear!
				return None
	return nz

def surfinterp(xd, yd, zd, new_xd, new_yd):
	"""Interpolate from raw x,y,z data to new space.

	**xd, yd, zd** -- all vectors of same length describing the
	surface to be interpolated in 3-space

	**new_xd, new_yd** -- 2 vectors indicating the *AXIS* points where
	new z-values are to be computed. nx and ny must be same length;
	(len(nx)*len(ny)) points will be computed.

	**return** -- return in a 2d numeric matrix containing intepolated
	z-values at the grid points defined by new_xd, new_yd.

	*NOTE:* Algorithm is identical to griddata(), but doesn't assume
	that the output space is a regular grid.

	"""
	if len(xd) != len(yd) or len(xd) != len(zd):
		raise TypeError, "xd,yd,zd must all be same length"
	if len(new_xd) != len(new_yd):
		raise TypeError, "new_xd and new_yd must be same length"

	new_z = _N.zeros((len(new_xd),), 'f')
	for i in range(len(new_z)):
		x, y = nx[i], ny[j]
		d = (((xd - x) ** 2) + ((yd - y) ** 2)) ** 0.5
		ix = _N.argsort(d)
		a = _N.array((xd[ix[0]], yd[ix[0]], zd[ix[0]]), 'f')
		b = _N.array((xd[ix[1]], yd[ix[1]], zd[ix[1]]), 'f')
		for n in range(2, len(ix)):
			c = _N.array((xd[ix[n]], yd[ix[n]], zd[ix[n]]), 'f')
			z = _project(a, b, c, x, y)
			if not (z is None):
				break
		if not (z is None):
			new_z[i] = z
		else:
			# all points are colinear!
			return None
	return new_z

if __name__ == '__main__':
	import pylab

	xd, yd, zd = [], [], []
	xa = _N.arange(-3.0, 3.0, 0.5)
	ya = _N.arange(-3.0, 3.0, 0.5)
	m  = _N.zeros((len(xa), len(ya)), 'f')

	for i in range(len(xa)):
		for j in range(len(ya)):
			z = _N.sin(2*xa[i])
			xd.append(xa[i])
			yd.append(ya[j])
			zd.append(z)
			m[i,j]= z

	pylab.subplot(2,1,1)
	pylab.imshow(m)
	#pylab.xrange(-5.0, 5.0)
	pylab.title('original')

	nx = _N.arange(-4.5, 4.5, 0.1)
	ny = _N.arange(-4.5, 4.5, 0.1)
	nz = griddata(_N.array(xd), _N.array(yd), _N.array(zd), nx, ny)

	pylab.subplot(2,1,2)
	pylab.imshow(nz)
	#pylab.xrange(-5.0, 5.0)
	pylab.title('interpolated')

	print 'done.'

	pylab.show()
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
