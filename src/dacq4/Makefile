include ../../make.defs

#DEBUG = -DDEBUG=1
#DEBUG = -DDEBUG=0

# for beta/1st version of eyelink api tools:
#   LIBEYELINK = ./Eyelink/libeyelink.a -lpthread
#   INCEYELINK = 

# for new version (summer 2003):
LIBEYELINK =  -lpthread -lm -lrt \
	./eyelinksoftware/`uname -m`/lib/libeyelink_core.a
INCEYELINK = ./eyelinksoftware/`uname -m`/include

CFLAGS = -O6 -g -Wall -I$(INCEYELINK) -I./include \
		$(GLOBAL_CFLAGS) $(PYTHONINC) $(DEBUG) -fPIC
COMEDI_SERVER_OBJS = sigs.o psems.o usbjs.o

CC = gcc

all: build install

build: _dacqmodule.so comedi_server

sigs.o: sigs.c sigs.h
	$(CC) $(CFLAGS) -c sigs.c

psems.o: psems.c psems.h
	$(CC) $(CFLAGS) -c psems.c

usbjs.o: usbjs.c usbjs.h
	$(CC) $(CFLAGS) -c usbjs.c

comedi_server.o: comedi_server.c

comedi_server: comedi_server.o $(COMEDI_SERVER_OBJS)
	$(CC) -o $@ $< $(COMEDI_SERVER_OBJS) $(LIBEYELINK) -lcomedi -lm -lezV24

dacq.c: dacq.h

dacq.i: dacq.h
	@echo %module dacq >dacq.i
	@cat dacq.h >>dacq.i
	@echo "Made dacq.i"

dacq_wrap.c: dacq.i
	swig -python dacq.i

dacq_wrap.o: dacq_wrap.c
	$(CC) $(CFLAGS) $(PYTHONINC) -c dacq_wrap.c

_dacqmodule.so: dacq_wrap.o dacq.o psems.o
	$(CC) -shared dacq_wrap.o dacq.o psems.o -o $@

install: _dacqmodule.so comedi_server
	cp dacq.py $(PYPEDIR)/pype
	cp _dacqmodule.so $(PYPEDIR)/pype
	#cp libeyelinkcore.so $(PYPEDIR)/lib
	if [ -x comedi_server ]; then cp comedi_server $(PYPEDIR)/bin; fi;


#############################################################


clean:
	@rm -f *.o _dacqmodule.so *.i *.pyc _dacqmodule \
		*_server *_wrap.* .*~ dacq.py
	@rm -f comedi_server _dacqmodule.so 

