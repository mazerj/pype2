# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

##########################################################################
# old clunky support functions below.. try not to use if you can help
# it..
##########################################################################

def Make_2D_Sine(freq, phase, rot, rc, gc, bc, im):
	"""OBSOLETE -- DO NOT USE
	
	freq		cycles/image
	
	phase		phase (0=cos; deg)
	
	rot			rotation angle (deg)
	
	rc,gc,bc	red, green, blue contrast (float)
	
	im			target image (typically sprite.im)
	
	"""
	
	Logger("Warning: use singrat instead of Make_2D_Sine!\n")
	
	w, h = im.get_size()
	x, y = sprite.genaxes(w, h, Float)
	x = x / w
	y = y / h

	r = (x**2 + y**2)**0.5
	t = arctan2(y, x) - (math.pi * (rot-90) / 180.0)
	x = r * cos(t)
	y = r * sin(t)

	# convert sin->cos phase:
	phase = phase - 90
		
	g = 127.0 * sin((2.0 * math.pi * freq * x) -
					(math.pi * phase / 180.0))
	gg = transpose(array((rc*g,gc*g,bc*g)).astype(Int),
				   axes=[1,2,0])
	pygame.surfarray.blit_array(im, gg+127)
	pygame.surfarray.pixels_alpha(im)[:] = 255

def Make_2D_Cnc_Rdl(Cord, Rord, Phase, Polarity,
					Logflag, rc, gc, bc, im):
	"""OBSOLETE -- DO NOT USE
	
	Cord: Concentric frequency
	
	Rord: Radial frequendcy (NOTE: spirals have both Cord != & Rord != 0)
	
	Phase: in degrees
	
	Logflag:
	
	Polarity: -1 or +1.	 This really only applies to spirals, +1
				is CCW out from center.
				
	im: target image (typically sprite.im)
	
	"""

	Logger("Warning: use polargrat instead of Make_2D_Cnc_Rdl!\n")
	
	w, h = im.get_size()
	x, y = sprite.genaxes(w, h, Float)

	x = x * Polarity
	
	x = x / w
	y = y / h

	try:
		if Logflag:
			x = (log(hypot(x,y)) * Cord) + \
				(arctan2 (y,x) * Rord / (2.0 * math.pi))
		else:
			x = (hypot (x,y) * Cord) + \
				(arctan2 (y,x) * Rord / (2.0 * math.pi))
	except:
		print "*** PYPE ERROR ***"
		return
	
	# convert sin->cos phase:
	Phase = Phase - 90

	g = 127.0 * sin((2.0 * math.pi * x) - (math.pi * Phase / 180.0))
	
	gg = transpose(array((rc*g,gc*g,bc*g)).astype(Int),
				   axes=[1,2,0])
	pygame.surfarray.blit_array(im, gg+127)
	pygame.surfarray.pixels_alpha(im)[:] = 255

def Make_2D_Hyperbolic(Pf, Phase, Rot, rc, gc, bc, im):
	"""OBSOLETE -- DO NOT USE
	
	"""
	
	Logger("Warning: use hypergrat instead of Make_2D_Hyperbolic!\n")
	
	w, h = im.get_size()
	x, y = sprite.genaxes(w, h, Float)
	x = x / w
	y = y / h

	r = (x**2 + y**2)**0.5
	t = arctan2(y, x) - (math.pi * (Rot-90) / 180.0)
	x = r * cos(t)
	y = r * sin(t)

	x = sqrt(fabs((x * Pf) ** 2 - (y * Pf) ** 2))
	
	# convert sin->cos phase:
	Phase = Phase - 90

	g = 127.0 * sin((2.0 * math.pi * x) - (math.pi * Phase / 180.0))

	gg = transpose(array((rc*g,gc*g,bc*g)).astype(Int),
				   axes=[1,2,0])
	pygame.surfarray.blit_array(im, gg+127)
	pygame.surfarray.pixels_alpha(im)[:] = 255
