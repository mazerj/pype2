
from pype import *
from sprite import *

fb = quickinit(w=512, h=512)

fb.string(0, 0, '1', (255,255,255))
fb.flip()
keyboard()

fb.string(0, 10, '2', (255,255,255))
fb.flip()
keyboard()


