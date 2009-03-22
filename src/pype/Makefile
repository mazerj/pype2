include ../../make.defs

FILES = *.py

install: pypeversion install-pypelib install-pyperun install-pypebin

install-shared: pypeversion install-pypelib \
		install-pyperun-shared install-pypebin

install-pypelib:
	@for i in $(FILES); \
		do (cp $$i $(PYPEDIR)/lib);\
		done
	@echo ""
	@cp cour.ttf $(PYPEDIR)/lib
	@cp pypeversion.py $(PYPEDIR)/lib
	@rm pypeversion.py
	@(cd ./icons ; $(MAKE) install)

install-pyperun:
	@sed "s@%%PYPEDIR%%@$(PYPEDIR)@g" <pyperun.template | \
	 sed "s@%%PYTHONEXE%%@$(PYTHONEXE)@g" >pyperun
	@cp pyperun $(PYPEDIR)/bin
	@chmod +x $(PYPEDIR)/bin/pyperun
	@rm pyperun

install-pyperun-shared:
	@sed "s@%%PYPEDIR%%@$(PYPEDIR)@g" <pyperun.template | \
	 sed "s@%%PYTHONEXE%%@/usr/bin/env python@g" >pyperun
	@cp pyperun $(PYPEDIR)/bin
	@chmod +x $(PYPEDIR)/bin/pyperun
	@rm pyperun

install-pypebin:
	@cp pypedebug $(PYPEDIR)/bin
	@chmod +x $(PYPEDIR)/bin/pypedebug

	@chmod +x pypespike
	@cp pypespike $(PYPEDIR)/bin

#	@chmod +x pypeplex.py
#	@cp pypeplex.py $(PYPEDIR)/bin

pypeversion:
	@sed 's/%%INSTALLDATE%%/$(shell date)/' \
		<pypeversion.template >pypeversion.py
	@echo 'PypeBuildDir = "$(shell pwd)"' >>pypeversion.py
	@echo 'PypeBuildBy = "$(USER)"' >>pypeversion.py
	@echo 'PypeBuildDate = "$(shell date)"' >>pypeversion.py


build:
	@echo "nothing to do for build"

clean:
	(cd ./icons ; $(MAKE) clean)
	@rm -f *.pyc pypeversion.py .*~ prun .happydoc*py

