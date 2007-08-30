include ../../make.defs

#DEBUG = -DDEBUG=1
#DEBUG = -DDEBUG=0

# for beta/1st version of eyelink api tools:
#   LIBEYELINK = ./Eyelink/libeyelink.a -lpthread
#   INCEYELINK = 

# for new version (summer 2003):
LIBEYELINK = ./eyelinksoftware/lib/libeyelink_core.a -lpthread
INCEYELINK = ./eyelinksoftware/include

CFLAGS = -O6 -g -Wall -I$(INCEYELINK) -I./include \
		$(GLOBAL_CFLAGS) $(PYTHONINC) $(DEBUG)
CC = gcc

all: build install

build: das16_server das08_server _dacqmodule.so comedi 

sigs.o: sigs.c sigs.h
	$(CC) -c sigs.c

psems.o: psems.c psems.h
	$(CC) -c psems.c

usbjs.o: usbjs.c usbjs.h
	$(CC) -c usbjs.c

procname.o: procname.c procname.h
	$(CC) -c procname.c

comedi:
	if [ -f /usr/include/comedi.h -o -f /usr/local/include/comedi.h ]; then \
		$(MAKE) comedi_server; \
	fi;


SERVER_SRCS = das_common.c das_common.h procname.h procname.c
SERVER_OBJS = sigs.o psems.o procname.o usbjs.o libezV24-0.0.3/libezV24-0.a

dummy_server.o: dummy_server.c $(SERVER_SRCS)
comedi_server.o: comedi_server.c $(SERVER_SRCS)
das16_server.o: das16_server.c $(SAVER_SRCS)
das08_server.o: das08_server.c $(SERVER_SRCS)

dummy_server: dummy_server.o dacq.h $(SERVER_OBJS)
	$(CC) -o $@ $< $(SERVER_OBJS) $(LIBEYELINK)

das16_server: das16_server.o $(SERVER_OBJS)
	$(CC) -o $@ $< $(SERVER_OBJS) $(LIBEYELINK)

comedi_server: comedi_server.o $(SERVER_OBJS)
	$(CC) -o $@ $< $(SERVER_OBJS) $(LIBEYELINK) -lcomedi -lm

das08_server: das08_server.o $(SERVER_OBJS)
	$(CC) -o $@ $< $(SERVER_OBJS) $(LIBEYELINK)

libezV24-0.0.3/libezV24-0.a:
	(cd libezV24-0.0.3 ; $(MAKE) static)

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

install: dummy_server \
		das16_server das08_server _dacqmodule.so comedi
	cp dummy_server $(PYPEDIR)/bin
	cp das16_server $(PYPEDIR)/bin
	cp das08_server $(PYPEDIR)/bin
	cp dacq.py $(PYPEDIR)/lib
	cp _dacqmodule.so $(PYPEDIR)/lib
	#cp libeyelinkcore.so $(PYPEDIR)/lib
	if [ -x comedi_server ]; then cp comedi_server $(PYPEDIR)/bin; fi;

# test program for comedi drivers
comedi_test:
	cc -o comedi_test comedi_test.c -lcomedi

#############################################################


clean:
	@rm -f *.o _dacqmodule.so *.i *.pyc _dacqmodule \
		*_server *_wrap.* .*~ dacq.py
	(cd libezV24-0.0.3 ; $(MAKE) clean)
	@rm -f libezV24-0.0.3/libezV24-0.a
	@rm -f das16_server comedi_server das08_server _dacqmodule.so 

