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
		do (cd $$i ; make install);\
		done
	(cd $(PYPEDIR); $(PYCOMPILE) -q lib || $(PYCOMPILE) lib)
	(cd $(PYPEDIR); $(PYCOMPILE) -q Tasks || $(PYCOMPILE) Tasks)

install-nodacq:
	@for i in $(SUBDIRS); \
		do (cd $$i ; make install-nodacq);\
		done
	(cd $(PYPEDIR); $(PYCOMPILE) -q lib || $(PYCOMPILE) lib)
	(cd $(PYPEDIR); $(PYCOMPILE) -q Tasks || $(PYCOMPILE) Tasks)

install-shared:
	@for i in $(SUBDIRS); \
		do (cd $$i ; make install-shared);\
		done
	(cd $(PYPEDIR); $(PYCOMPILE) -q lib || $(PYCOMPILE) lib)
	(cd $(PYPEDIR); $(PYCOMPILE) -q Tasks || $(PYCOMPILE) Tasks)

pycompile:
	(cd $(PYPEDIR); $(PYCOMPILE) -q lib || $(PYCOMPILE) lib)
	(cd $(PYPEDIR); $(PYCOMPILE) -q Tasks || $(PYCOMPILE) Tasks)

wrapper:
ifeq ($(WHO),root)
	(cd src/wrapper ; make install)
else
	@echo "Must be root to install wrapper."
endif

# clean: all the pype src directories
clean: 
	@find . -name core | xargs rm -f
	@find . -name \*.pyc | xargs rm -f
	for i in $(SUBDIRS); \
		do (cd $$i ; make clean);\
		done
	cd src/wrapper ; make clean

# clobber: pype srcs clean + external directories
clobber: clean x-clean

###############################################################
#      external programs/libraries
###############################################################

x-rig:
	cd External; make rig-install

x-workstation:
	cd External; make workstation-install

x-clean:
	cd External; make clean

###############################################################

uninstall: 
	rm -rf $(PYPEDIR)/bin
	rm -rf $(PYPEDIR)/lib
	rm -rf $(PYPEDIR)/Tasks
	rmdir $(PYPEDIR)

docs:
	# note: this requires happydoc to be installed!
	(cd src/pype; make happydoc)

.PHONY: install

###############################################################

# useful svn targets

unstable:
	@if [ -e RELEASE ]; then svn mv RELEASE UNSTABLE; fi
	@echo UNSTABLE

stable:
	@if [ -e UNSTABLE ]; then svn mv UNSTABLE RELEASE; fi
	@echo RELEASE

