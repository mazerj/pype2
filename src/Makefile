include ../make.defs

DACQDIR = dacq3
DUMMYDIR= dummy-dacq
PYDIR   = pype
SUBDIRS = sh icons sounds sample-tasks Plexon p2m tools

install: install-subdirs install-py install-dacq

install-nodacq: install-subdirs install-py install-dummydacq

install-shared: install-subdirs install-py-shared install-dummydacq

install-subdirs:
	@mkdir -p $(PYPEDIR)
	@mkdir -p $(PYPEDIR)/bin
	@mkdir -p $(PYPEDIR)/lib
	@mkdir -p $(PYPEDIR)/Tasks
	@mkdir -p $(PYPEDIR)/../p2m
	@for i in $(SUBDIRS); \
		do (cd $$i ; make install; cd ..);\
		done
	@rm -rf $(PYPEDIR)/lib/Pmw
	@(x=`pwd`; cd $(PYPEDIR)/lib; tar xfz $$x/Pmw.1.2.tar.gz)

install-py:
	@(cd $(PYDIR); make install; cd ..)

install-py-shared:
	@(cd $(PYDIR); make install-shared; cd ..)

install-dacq:
	@(cd $(DACQDIR); make install; cd ..)

install-dummydacq:
	@(cd $(DUMMYDIR); make install; cd ..)

build: build-dacq build-subdirs

build-nodacq: build-subdirs

build-subdirs:
	@for i in $(SUBDIRS); \
		do (cd $$i ; make; cd ..);\
		done

build-dacq:
	@(cd $(DACQDIR); make; cd ..)

clean:
	@for i in $(DACQDIR) $(DUMMYDIR) $(SUBDIRS); \
		do (cd $$i ; make clean; cd ..);\
		done

tags:
	rm -f TAGS */TAGS
	etags `pwd`/*/*.{c,h,py}
	for i in $(DACQDIR) $(DUMMYDIR) $(SUBDIRS); \
		do (cd $$i ; ln -s ../TAGS TAGS; cd ..);\
		done
