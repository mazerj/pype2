include ../../make.defs

SHFILES = pypesetup pypeconfig pypekill pypenv-batch pype pypenv

install:
	for i in $(SHFILES); \
		do (cp $$i $(PYPEDIR)/bin; chmod +x $(PYPEDIR)/bin/$$i );\
		done


clean:
	@rm -f .*~

