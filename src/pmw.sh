#!/bin/sh

# Create a bundle file for Pmw -- one importable file that contains
# all the Pmw stuff (+ PmwBlt.py and PmwColor.py) and copy it to the
# target directory
#
# usage: sh pmw.sh pwm.tgz dest-dir
#

x=`pwd`

mkdir /tmp/$$
cd /tmp/$$
tar xfz $x/Pmw.1.2.patched.tgz
./Pmw/Pmw_1_2/bin/bundlepmw.py ./Pmw/Pmw_1_2/lib >/dev/null
mv ./Pmw.py $1
mv ./Pmw/Pmw_1_2/lib/PmwBlt.py $1
mv ./Pmw/Pmw_1_2/lib/PmwColor.py $1
cd $x
rm -rf /tmp/$$

