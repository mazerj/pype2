# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
**Clone of the matlab GRIDDATA function**

This basically works by taking a set of (x,y,z) data and using the
existing data to interpolate z-values for a new set of (X,Y)
coordinates using linear interpolation based on the 3 nearest neighbor
points (from the orignal (x,y,z) set).

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

Tue Mar 17 14:41:32 2009 mazer

"""

__author__   = '$Author$'
__date__     = '$Date$'
__revision__ = '$Revision$'
__id__       = '$Id$'

try:
	from Numeric import *
except ImportError:
	raise ImportError, "%s requires Numeric module" % __name__

def _crossproduct(a, b):
	"""Compute cross product of two 3-d vectors (x,y,z)"""
	if len(a) != 3 or len(b) != 3:
		raise TypeError, "Cross product only for vectors of length 3"
	v = [a[1]*b[2] - a[2]*b[1],
		 a[2]*b[0] - a[0]*b[2],
		 a[0]*b[1] - a[1]*b[0]]
	return array(v)

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
	
	nz = zeros((len(nx), len(ny)), 'f')
	for i in range(len(nx)):
		for j in range(len(ny)):
			x, y = nx[i], ny[j]
			d = (((xd - x) ** 2) + ((yd - y) ** 2)) ** 0.5
			ix = argsort(d)
			a = array((xd[ix[0]], yd[ix[0]], zd[ix[0]]), 'f')
			b = array((xd[ix[1]], yd[ix[1]], zd[ix[1]]), 'f')
			for n in range(2, len(ix)):
				c = array((xd[ix[n]], yd[ix[n]], zd[ix[n]]), 'f')
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
	
	new_z = zeros((len(new_xd),), 'f')
	for i in range(len(new_z)):
		x, y = nx[i], ny[j]
		d = (((xd - x) ** 2) + ((yd - y) ** 2)) ** 0.5
		ix = argsort(d)
		a = array((xd[ix[0]], yd[ix[0]], zd[ix[0]]), 'f')
		b = array((xd[ix[1]], yd[ix[1]], zd[ix[1]]), 'f')
		for n in range(2, len(ix)):
			c = array((xd[ix[n]], yd[ix[n]], zd[ix[n]]), 'f')
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
	import mplot

	xd, yd, zd = [], [], []
	xa = arange(-3.0, 3.0, 0.5)
	ya = arange(-3.0, 3.0, 0.5)
	m  = zeros((len(xa), len(ya)), 'f')

	for i in range(len(xa)):
		for j in range(len(ya)):
			z = sin(2*xa[i])
			xd.append(xa[i])
			yd.append(ya[j])
			zd.append(z)
			m[i,j]= z

	mplot.subplot(2,1,1)
	mplot.imagesc(m, x=xa, y=ya)
	mplot.xrange(-5.0, 5.0)
	mplot.title('original')

	
	nx = arange(-4.5, 4.5, 0.1)
	ny = arange(-4.5, 4.5, 0.1)
	nz = griddata(array(xd), array(yd), array(zd), nx, ny)

	mplot.subplot(2,1,2)
	mplot.imagesc(nz, x=nx, y=ny)
	mplot.xrange(-5.0, 5.0)
	mplot.title('interpolated')

	print 'done.'

	mplot.drawnow()
else:
	try:
		from pype import loadwarn
		loadwarn(__name__)
	except ImportError:
		pass
		

