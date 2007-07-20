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
tar xfz $1
./Pmw/Pmw_1_2/bin/bundlepmw.py ./Pmw/Pmw_1_2/lib >/dev/null
mv ./Pmw.py $2
mv ./Pmw/Pmw_1_2/lib/PmwBlt.py $2
mv ./Pmw/Pmw_1_2/lib/PmwColor.py $2
cd $x
rm -rf /tmp/$$

