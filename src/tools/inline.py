# this code fragment will convert a GIF to python source code
#
# python ./inline.py gif-file iconname >foo.py
#
# from foo import iconname
#

import base64, sys

file = sys.argv[1]
name = sys.argv[2]
data = base64.encodestring(open(file, "r").read())

print "import Tkinter"
print name + '=Tkinter.PhotoImage(data="""\n' + data + '""")'

