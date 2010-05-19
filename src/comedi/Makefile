include ../../make.defs

CC = gcc

EYELINK_LIB =  -lpthread -lm -lrt \
	./eyelinksoftware/`uname -m`/lib/libeyelink_core.a
EYELINK_INC = ./eyelinksoftware/`uname -m`/include

CFLAGS = -O6 -g -Wall -I$(EYELINK_INC) -I./include \
		$(GLOBAL_CFLAGS) $(PYTHONINC) -fPIC

SERVER_OBJS = sigs.o psems.o usbjs.o


all: build install

build: _dacqmodule.so comedi

comedi:
	if [ -f /usr/include/comedi.h -o -f /usr/local/include/comedi.h ]; then \
		$(MAKE) comedi_server; \
	fi;

sigs.o: sigs.c sigs.h
psems.o: psems.c psems.h
usbjs.o: usbjs.c usbjs.h


comedi_server: comedi_server.o $(SERVER_OBJS)
	$(CC) -o $@ $< $(SERVER_OBJS) $(EYELINK_LIB) -lcomedi -lm -lezV24

_dacqmodule.so: dacq.c dacq.h dacq.o psems.o
	cat _dacq.i dacq.h >dacq.i
	swig -python dacq.i
	$(CC) $(CFLAGS) $(PYTHONINC) -c dacq_wrap.c
	$(CC) -shared dacq_wrap.o dacq.o psems.o -o $@

install: _dacqmodule.so comedi
	cp dacq.py $(PYPEDIR)/pype
	cp _dacqmodule.so $(PYPEDIR)/pype
	if [ -x comedi_server ]; then cp comedi_server $(PYPEDIR)/bin; fi;

#############################################################


clean:
	@rm -f *.o _dacqmodule.so *.pyc _dacqmodule \
		*_server *_wrap.* .*~ dacq.py
	@rm -f dacq.i
	@rm -f comedi_server _dacqmodule.so 

