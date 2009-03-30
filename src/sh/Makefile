include ../../make.defs

SHFILES = pypesetup pypedocs pypeconfig pypekill pypenv-batch pype pypenv

install:
	for i in $(SHFILES); \
		do (cp $$i $(PYPEDIR)/bin; chmod +x $(PYPEDIR)/bin/$$i );\
		done


clean:
	@rm -f .*~

