include make.defs

SUBDIRS = src

detect:
	@echo "Autodectected version info:"
	@echo " "PYTHONVER=$(PYTHONVER)
	@echo " "PYTHONEXE=$(PYTHONEXE)
	@echo " "PYPEDIR=$(PYPEDIR)

checkconfig:
	./configinfo

setenv:
	@echo "setenv PYTHONVER $(PYTHONVER)"
	@echo "setenv PYTHONEXE $(PYTHONEXE)"
	@echo "setenv PYPEDIR $(PYPEDIR)"

all: install wrapper

all-nodacq: install-nodacq wrapper

install:
	@for i in $(SUBDIRS); \
		do (cd $$i ; $(MAKE) install);\
		done
	(cd $(PYPEDIR); $(PYCOMPILE) -q lib || $(PYCOMPILE) lib)
	(cd $(PYPEDIR); $(PYCOMPILE) -q Tasks || $(PYCOMPILE) Tasks)

install-nodacq:
	@for i in $(SUBDIRS); \
		do (cd $$i ; $(MAKE) install-nodacq);\
		done
	(cd $(PYPEDIR); $(PYCOMPILE) -q lib || $(PYCOMPILE) lib)
	(cd $(PYPEDIR); $(PYCOMPILE) -q Tasks || $(PYCOMPILE) Tasks)

install-shared:
	@for i in $(SUBDIRS); \
		do (cd $$i ; $(MAKE) install-shared);\
		done
	(cd $(PYPEDIR); $(PYCOMPILE) -q lib || $(PYCOMPILE) lib)
	(cd $(PYPEDIR); $(PYCOMPILE) -q Tasks || $(PYCOMPILE) Tasks)

justbuild:
	@for i in $(SUBDIRS); \
		do (cd $$i ; $(MAKE) build);\
		done
	(cd $(PYPEDIR); $(PYCOMPILE) -q lib || $(PYCOMPILE) lib)
	(cd $(PYPEDIR); $(PYCOMPILE) -q Tasks || $(PYCOMPILE) Tasks)

p2m:
	(cd src; $(MAKE) install-p2m)

pycompile:
	(cd $(PYPEDIR); $(PYCOMPILE) -q lib || $(PYCOMPILE) lib)
	(cd $(PYPEDIR); $(PYCOMPILE) -q Tasks || $(PYCOMPILE) Tasks)

wrapper:
ifeq ($(WHO),root)
	(cd src/wrapper ; $(MAKE) install)
else
	@echo "Must be root to install wrapper."
endif

# clean: all the pype src directories
# the find command is slowest here..
clean: 
	@echo "Cleaning temp files..."
	@find . -name core -o -name music.raw -o -name \*.pyc | xargs rm -f
	@echo "Cleaning subdirs..."
	@for i in $(SUBDIRS); \
		do (cd $$i ; echo ...Cleaning $$i ; $(MAKE) clean);\
		done
	@cd src/wrapper ; $(MAKE) clean

clobber: clean x-clean


###############################################################
#      external programs/libraries
###############################################################

x-rig:
	cd External; $(MAKE) rig-install

x-workstation:
	cd External; $(MAKE) workstation-install

x-clean:
	cd External; $(MAKE) clean

###############################################################

# This is WAY to dangerous -- as Matt Krause can tell you. I'm
# taking it away..
#
#uninstall: 
#	rm -rf $(PYPEDIR)/bin
#	rm -rf $(PYPEDIR)/lib
#	rm -rf $(PYPEDIR)/Tasks
#	rmdir $(PYPEDIR)

uninstall: 
	echo  "Uninstall must be done manually!"

docs:
	# note: this requires happydoc to be installed!
	(cd src/pype; $(MAKE) happydoc)

.PHONY: install

###############################################################

# useful svn targets

unstable:
	@if [ -e RELEASE ]; then svn mv RELEASE UNSTABLE; fi
	@echo UNSTABLE

stable:
	@if [ -e UNSTABLE ]; then svn mv UNSTABLE RELEASE; fi
	@echo RELEASE

