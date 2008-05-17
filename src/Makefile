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
		do (cd $$i ; $(MAKE) install);\
		done
	@rm -rf $(PYPEDIR)/lib/Pmw*
	@sh pmw.sh $(PYPEDIR)/lib

install-p2m:
	@mkdir -p $(PYPEDIR)/../p2m
	(cd p2m ; $(MAKE) install)


install-py:
	@(cd $(PYDIR); $(MAKE) install)

install-py-shared:
	@(cd $(PYDIR); $(MAKE) install-shared)

install-dacq:
	@(cd $(DACQDIR); $(MAKE) install)

install-dummydacq:
	@(cd $(DUMMYDIR); $(MAKE) install)

build: build-dacq build-subdirs

build-nodacq: build-subdirs

build-subdirs:
	@for i in $(SUBDIRS); \
		do (cd $$i ; $(MAKE));\
		done

build-dacq:
	@(cd $(DACQDIR); $(MAKE))

clean:
	@for i in $(DACQDIR) $(DUMMYDIR) $(SUBDIRS) $(PYDIR); \
		do (cd $$i ; $(MAKE) clean);\
		done

tags:
	rm -f TAGS */TAGS
	etags `pwd`/*/*.{c,h,py}
	for i in $(DACQDIR) $(DUMMYDIR) $(SUBDIRS); \
		do (cd $$i ; ln -s ../TAGS TAGS);\
		done
