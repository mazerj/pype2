include ../../make.defs

FILES = *.py

install: pypeversion install-pypelib install-pyperun install-pypebin

install-shared: pypeversion install-pypelib \
		install-pyperun-shared install-pypebin

install-pypelib:
	@for i in $(FILES); \
		do (cp $$i $(PYPEDIR)/pype);\
		done
	@echo ""
	@cp cour.ttf $(PYPEDIR)/lib
	@cp pypeversion.py $(PYPEDIR)/pype
	@rm pypeversion.py
	@(cd ./icons ; $(MAKE) install)
	@cp testpat.png $(PYPEDIR)/lib
	@rm $(PYPEDIR)/pype/__init__.py

install-pyperun:
	@sed "s@%%PYPEDIR%%@$(PYPEDIR)@g" <pyperun.py.template | \
	 sed "s@%%PYTHONEXE%%@$(PYTHONEXE)@g" >pyperun
	@cp pyperun $(PYPEDIR)/bin
	@chmod +x $(PYPEDIR)/bin/pyperun
	@rm pyperun

install-pyperun-shared:
	@sed "s@%%PYPEDIR%%@$(PYPEDIR)@g" <pyperun.py.template | \
	 sed "s@%%PYTHONEXE%%@/usr/bin/env python@g" >pyperun
	@cp pyperun $(PYPEDIR)/bin
	@chmod +x $(PYPEDIR)/bin/pyperun
	@rm pyperun

install-pypebin:
	@cp pypedebug $(PYPEDIR)/bin
	@chmod +x $(PYPEDIR)/bin/pypedebug

pypeversion:
	@sed 's/%%INSTALLDATE%%/$(shell date)/' \
		<pypeversion.py.template >pypeversion.py
	@echo 'PypeBuildDir = "$(shell pwd)"' >>pypeversion.py
	@echo 'PypeBuildBy = "$(shell logname)"' >>pypeversion.py
	@echo 'PypeBuildDate = "$(shell date)"' >>pypeversion.py
	@echo 'PypeBuildHost = "$(shell hostname)"' >>pypeversion.py


build:
	@echo "nothing to do for build"

clean:
	(cd ./icons ; $(MAKE) clean)
	@rm -f *.pyc pypeversion.py .*~ prun .happydoc*py

