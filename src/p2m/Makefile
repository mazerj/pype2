include ../../make.defs

P2MDIR = $(PYPEDIR)/../p2m

install:
	@mkdir -p $(P2MDIR)
	chmod +x pype_expander.py p2m p2mupdate \
		p2m-ical p2m-fixes p2m-spotmap affinecal \
		plx2mat plx2asc.py tdtgetspikes.py
	/bin/cp -f README *.m \
		p2m p2mupdate \
		p2m-ical p2m-fixes p2m-spotmap \
		pype_expander.py affinecal \
		plx2mat plx2asc.py tdtgetspikes.py \
			$(P2MDIR)
	@date > $(P2MDIR)/LAST_UPDATE

build:
	@echo "p2m: Nothing to build."

tags:
	@echo "p2m: nothing to tagify."

clean:
	/bin/rm -f \#*~
