#!/usr/bin/python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
#
# simpler, cleaner movie class w/ repeats
#

from sprite import *

class Movie:
    def __init__(self, dir, indexfile, fb=None):
        from string import split
        
        if not dir[-1] == '/':
            dir = dir + '/'

        self.dir = dir
        self.indexfile = indexfile
        self.__fb = fb
        self.__x = None
        self.__y = None
        
        # index file lines should be:
        # framefile frameinfo...
        f = open(self.dir + self.indexfile, 'r')
        index = f.readlines()
        f.close()

        self.header = []
        self.frames = []
        self.framesinfo = []
 
        for line in index:
            line = line[:-1]
            if line[0] == '#':
                self.header.append(line)
            else:
                l = split(line)

                self.frames.append(self.dir + l[0])
                self.framesinfo.append(line)
        self.__numframes = len(self.frames)
        self.__cache = {}
        
    def clear(self, list=None):
        if list is None:
            del self.__cache
            self.__cache = {}
        else:
            for n in list:
                n = n % self.__numframes
                file = self.frames[n]
                del self.__cache[file]

    def place(self, x, y):
        self.__x = x
        self.__y = y
        
    def len(self, nrepeats=1):
        return nrepeats * self.__numframes
        
    def frame(self, n, nrepeats=1):
        n = int(round(n / nrepeats)) % self.__numframes
        file = self.frames[n]
        if not self.__cache.has_key(file):
            self.__cache[file] = Sprite(fname=file, fb=self.__fb)
        s = self.__cache[file]
        if not self.__x is None:
            s.moveto(self.__x, self.__y)
        return s

