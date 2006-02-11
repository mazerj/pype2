include ../../make.defs

all: clean install


install: pypeboot
	@echo "Using sudo to chmod/chown wrapper (pypeboot)..."
	@sudo cp -f pypeboot $(PYPEDIR)/bin
	@sudo chown root $(PYPEDIR)/bin/pypeboot
	@sudo chmod 4111 $(PYPEDIR)/bin/pypeboot

pypeboot: pypeboot.c
	$(CC) pypeboot.c -o pypeboot


clean:
	@/bin/rm -f *.o pypeboot \#*~ .*~


