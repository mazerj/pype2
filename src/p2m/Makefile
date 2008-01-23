include ../../make.defs

P2MDIR = $(PYPEDIR)/../p2m

install:
	@mkdir -p $(P2MDIR)
	sed "s@%%P2MDIR%%@$(P2MDIR)@g"  \
		< pype_expander.template >pype_expander
	chmod +x pype_expander p2m p2mupdate \
		p2m-ical p2m-fixes p2m-spotmap affinecal \
		plx2mat plx2asc.py tdtgetspikes
	cp README *.m \
		p2m p2mupdate \
		p2m-ical p2m-fixes p2m-spotmap \
		pype_expander pype_expander.py affinecal \
		plx2mat plx2asc.py tdtgetspikes \
			$(P2MDIR)
	@date > $(P2MDIR)/LAST_UPDATE

build:
	@echo "p2m: Nothing to build."

tags:
	@echo "p2m: nothing to tagify."

clean:
	/bin/rm -f \#*~ pype_expander
