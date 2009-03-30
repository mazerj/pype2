include ../../../make.defs

FILES = *.py

build:
	for i in *.gif; \
		do (python ../../tools/inline.py $$i `basename $$i .gif` \
				> im_`basename $$i .gif`.py) \
		done

install: build
	@cp *.py $(PYPEDIR)/pype

clean:
	@/bin/rm -f *.py

clobber: clean

