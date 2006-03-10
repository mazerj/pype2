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

build: das16_server das08_server _dacqmodule.so iscan_server comedi

sigs.o: sigs.c sigs.h
	$(CC) -c sigs.c

psems.o: psems.c psems.h
	$(CC) -c psems.c

usbjs.o: usbjs.c usbjs.h
	$(CC) -c usbjs.c

procname.o: procname.c procname.h
	$(CC) -c procname.c

psems: psems.c psems.h
	$(CC) -o psems -DTEST psems.c

cmdeyelink: cmdeyelink.o
	$(CC) -o $@ $< $(LIBEYELINK)

das16_server.o: das16_server.c das_common.c das_common.h \
	procname.h procname.c

das16_server: das16_server.o dacq.h sigs.o psems.o procname.o usbjs.o
	$(CC) -o $@ $< sigs.o psems.o procname.o usbjs.o $(LIBEYELINK)

comedi:
	if [ -f /usr/include/comedi.h -o -f /usr/local/include/comedi.h ]; then \
		make comedi_server; \
	fi;

comedi_server.o: comedi_server.c das_common.c das_common.h \
	procname.h procname.c

comedi_server: comedi_server.o dacq.h sigs.o psems.o procname.o usbjs.o
	$(CC) -o $@ $< sigs.o  psems.o procname.o usbjs.o $(LIBEYELINK) -lcomedi

das08_server.o: das08_server.c das_common.c das_common.h usbjs.o \
	procname.h procname.c

das08_server: das08_server.o dacq.h sigs.o psems.o procname.o usbjs.o
	$(CC) -o $@ $< sigs.o psems.o procname.o usbjs.o $(LIBEYELINK)

iscan_server: iscan_server.o dacq.h sigs.o  psems.o procname.o usbjs.o libez
	@echo "NOTE: can't tell if libez is fresh, will relink iscan_server"
	$(CC) -o $@ $< sigs.o psems.o procname.o libezV24-0.0.3/libezV24-0.a

libez:
	(cd libezV24-0.0.3 ; make static)


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

install: das16_server das08_server _dacqmodule.so iscan_server comedi
	cp das16_server $(PYPEDIR)/bin
	cp das08_server $(PYPEDIR)/bin
	cp iscan_server $(PYPEDIR)/bin
	cp dacq.py $(PYPEDIR)/lib
	cp _dacqmodule.so $(PYPEDIR)/lib
	#cp libeyelinkcore.so $(PYPEDIR)/lib
	if [ -x comedi_server ]; then cp comedi_server $(PYPEDIR)/bin; fi;

#############################################################

dastest_poll: dastest_poll.o
	$(CC) -o $@ $<

dastest_cont: dastest_cont.o
	$(CC) -o $@ $<

#############################################################


clean:
	@rm -f *.o _dacqmodule.so *.i *.pyc _dacqmodule \
		*_server *_wrap.* .*~ dacq.py
	(cd libezV24-0.0.3 ; make clean)
	@rm -f libezV24-0.0.3/libezV24-0.a
	@rm -f das16_server comedi_server das08_server _dacqmodule.so 

