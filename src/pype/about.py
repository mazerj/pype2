# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$

"""INTERNAL; DO NOT CALL DIRECTLY

AboutPype class for making the about window and splash box.

Author -- James A. Mazer (james.mazer@yale.edu)

**Revision History**

- Sun Aug 11 18:54:24 2002 mazer

 - created (from pype.py)
"""

from Tkinter import *
from pypeversion import *

class AboutPype:
	
	"""
	Class for the About box.  This is just to make sure
	only one box per run gets built and reused.
	"""
	
	_w = None
	def __init__(self):
		from pype import PyIcon
		from guitools import undermouse
		
		if AboutPype._w is None:
			logo = PyIcon('splash.ppm').image()
			AboutPype._w = Toplevel()
			AboutPype._w.title('PypeAbout')
			AboutPype._w.iconname('PypeAbout')
			icon = Label(AboutPype._w,
						 relief=FLAT, image=logo, pady=10)
			icon.pack(expand=1, fill=BOTH)

			t = """
pype: python physiology environment
Copyright (c) 1999 Jamie Mazer
Version %s
Installed: %s""" % (PypeVersion, PypeInstallDate)
			text = Label(AboutPype._w, text=t)
			text.pack(expand=1, fill=BOTH)

			AboutPype._w.protocol("WM_DELETE_WINDOW", self._withdraw)
			b = Button(AboutPype._w, text='Close', command=self._withdraw)
			b.pack(expand=1, fill=X)
			undermouse(AboutPype._w)
		else:
			undermouse(AboutPype._w)
			AboutPype._w.deiconify()

	def _withdraw(self):
		AboutPype._w.withdraw()

def splash():
	"""
	Display a splash screen an destroy it after 10 secs.
	"""
	from pype import PyIcon
	from guitools import screencenter
	
	w = Toplevel()
	w.overrideredirect(1)
	w.withdraw()
	
	f = Frame(w, borderwidth=20, background='blue')
	f.pack(expand=1, fill=BOTH)
	logo = PyIcon('splash.ppm').image()
	icon = Label(f, relief=FLAT, image=logo)
	icon.pack(expand=1, fill=BOTH)
	w.update_idletasks()
	screencenter(w)
	w.deiconify()
	w.update_idletasks()
	w.after(3000, w.destroy)

