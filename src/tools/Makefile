include ../../make.defs

FILES = pyaddwarn.py ntrials.py tally.py

install: 
	@for i in $(FILES); \
		do (chmod +x $$i; \
		    cp $$i $(PYPEDIR)/bin; \
		    echo installed tool $$i);\
		done

build:
	@echo "nothing to do for build"

clean:
	@rm -f *.pyc .*~
