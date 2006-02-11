include ../../make.defs

P2MDIR = $(PYPEDIR)/../p2m

install:
	sed "s@%%P2MDIR%%@$(P2MDIR)@g"  \
	< pype_expander.template >pype_expander
	@mkdir -p $(P2MDIR)
	chmod +x pype_expander p2m p2m-ical p2m-fixes p2m-spotmap affinecal
	cp README p2m p2m-ical p2m-fixes p2m-spotmap \
		pype_expander pype_expander.py affinecal *.m $(P2MDIR)
	@date > $(P2MDIR)/LAST_UPDATE

build:
	@echo "p2m: Nothing to build."

tags:
	@echo "p2m: nothing to tagify."

clean:
	/bin/rm -f \#*~ pype_expander
