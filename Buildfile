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

all: install wrapper docs clobber

all-nodacq: install-nodacq wrapper

install:
	@for i in $(SUBDIRS); \
		do (cd $$i ; $(MAKE) install);\
		done
	(cd $(PYPEDIR); $(PYCOMPILE) -q pype || $(PYCOMPILE) pype)
	(cd $(PYPEDIR); $(PYCOMPILE) -q Tasks || $(PYCOMPILE) Tasks)

install-nodacq:
	@for i in $(SUBDIRS); \
		do (cd $$i ; $(MAKE) install-nodacq);\
		done
	(cd $(PYPEDIR); $(PYCOMPILE) -q pype || $(PYCOMPILE) pype)
	(cd $(PYPEDIR); $(PYCOMPILE) -q Tasks || $(PYCOMPILE) Tasks)

install-shared:
	@for i in $(SUBDIRS); \
		do (cd $$i ; $(MAKE) install-shared);\
		done
	(cd $(PYPEDIR); $(PYCOMPILE) -q pype || $(PYCOMPILE) pype)
	(cd $(PYPEDIR); $(PYCOMPILE) -q Tasks || $(PYCOMPILE) Tasks)

justbuild:
	@for i in $(SUBDIRS); \
		do (cd $$i ; $(MAKE) build);\
		done
	(cd $(PYPEDIR); $(PYCOMPILE) -q pype || $(PYCOMPILE) pype)
	(cd $(PYPEDIR); $(PYCOMPILE) -q Tasks || $(PYCOMPILE) Tasks)

p2m:
	(cd src; $(MAKE) install-p2m)

pycompile:
	(cd $(PYPEDIR); $(PYCOMPILE) -q pype || $(PYCOMPILE) pype)
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

clobber: clean

docs:
	ls ./src/pype/*.py | \
	    grep -v gracePlot.py | grep -v grace_np.py | grep -v blt | \
	        grep -v PlexHeaders.py | grep -v pstat.py | grep -v stats.py | \
		grep -v mplot.py | grep -v stimlib.py | \
		grep -v __init__.py | \
		xargs epydoc --docformat "restructuredtext en" --html \
		      --simple-term --parse-only -v --no-private \
		      -o $(PYPEDIR)/docs -n pype
	date > $(PYPEDIR)/docs/GENERATED



###############################################################

uninstall: 
	echo  "Uninstall must be done manually!"

.PHONY: install

###############################################################

# useful svn targets
#
#  these are not used, but probably should be...
#

unstable:
	@if [ -e RELEASE ]; then svn mv RELEASE UNSTABLE; fi
	@echo UNSTABLE

stable:
	@if [ -e UNSTABLE ]; then svn mv UNSTABLE RELEASE; fi
	@echo RELEASE

