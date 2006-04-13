/* title:   iscan_server.c

** author:  jamie mazer
** created: Tue May 16 20:41:26 2000 mazer 
** info:    shm interface to iscan digital/serial output stream
** history:
**
** Tue May 16 20:41:36 2000 mazer 
**   started from das_server.c
**
** Mon Dec  4 11:44:56 2000 mazer 
**   added $(PYPE_ISCAN_PORT) support to set the name of the
**   iscan serial i/o port.
**
** Wed Jan 17 10:05:33 2001 mazer 
**   added alarm() calls to prevent blocking
**
** Fri Dec  7 12:10:45 2001 mazer 
**   added support for no_iscan opereration..
**
** Wed Dec 12 16:27:03 2001 mazer 
**   modified to use select for iscan polling instead of SIGALRM
**
** Mon Feb 25 16:24:30 2002 mazer 
**   added priority and moved PYPE_ISCAN_PORT to command line arg..
**
** Wed Apr  3 14:07:43 2002 mazer 
**  modified to use ezV24-0.0.3 serial unix i/o library
*/

#include <sys/types.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/errno.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <string.h>
#include <signal.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/mman.h>

#include <math.h>		/* for sqrt() */
#include "dacqinfo.h"
#include "sigs.h"
#include "debug.h"
#include "psems.h"

#include "libezV24-0.0.3/ezV24.h"

static char *progname = NULL;
static DACQINFO *dacq_data = NULL;
static int mem_locked = 0;
static v24_port_t *iscan_port = NULL;
static int semid = -1;

#define BYTE unsigned char

int iscan_read(v24_port_t *port, int *x, int *y)
{
  static BYTE buf[10];
  static int bp = -1;
  int c;
  int ex, ey;
  int crx, cry;
  int lsb, msb;
  short *ibuf;

  /* initialize the read buffer */
  if (bp < 0) {
    for (bp = 0; bp < sizeof(buf); bp++) {
      buf[bp] = 0;
    }
    bp = 0;
  }

  c = v24Getc(port);
  if (c < 0) {
    /* timeout or no data available, clear buffer and continue next call */
    for (bp = 0; bp < sizeof(buf); bp++) {
      buf[bp] = 0;
    }
    bp = 0;
    return(0);
  }

  buf[bp] = 0x00ff & c;
  bp = (bp + 1) % sizeof(buf);

  /* check to see if we've got a complete packet */
  if (buf[bp] != 'D' || buf[(bp + 1) % sizeof(buf)] != 'D') {
    /* packet is NOT complete */
    return(0);
  }

  ibuf = buf;
  ex = ibuf[1] - ibuf[3] + 4096;
  ey = ibuf[2] - ibuf[4] + 4096;
  if (ibuf[1] != 0 || ibuf[2] != 0 || ibuf[3] != 0 || ibuf[3] != 0) {
    // valid datapoint, return value
    *x = ex;
    *y = ey;
  } else {
    // invalid point or lost lock, use last value..
    ;
  }

  return(1);
}

static void halt(void)
{
  fprintf(stderr, "%s: halt()\n", progname);
  if (iscan_port) {
    v24ClosePort(iscan_port);
  }
  if (dacq_data != NULL) {
    shmdt(dacq_data);
  }
  if (mem_locked) {
    if (munlockall() != 0) {
      perror("munlockall");
    } else {
      mem_locked = 0;
    }
  }
}

static int init(char *dev)
{
  int shmid;

  if ((iscan_port = v24OpenPort(dev, V24_NO_DELAY | V24_NO_DELAY)) == NULL) {
    fprintf(stderr, "%s: can't open \"%s\"\n.", progname, dev);
    exit(1);
  }
  v24SetParameters(iscan_port, V24_B115200, V24_8BIT, V24_NONE);
  /* set timeout on port for 0.1s */
  v24SetTimeouts(iscan_port, 1);

  if ((shmid = shmget((key_t)SHMKEY,
		      sizeof(DACQINFO), 0666 | IPC_CREAT)) < 0) {
    perror("shmget");
    fprintf(stderr, "%s:init -- kernel compiled with SHM/IPC?\n", progname);
    exit(1);
  }

  if ((dacq_data = shmat(shmid, NULL, 0)) == NULL) {
    perror("shmat");
    fprintf(stderr, "%s:init -- kernel compiled with SHM/IPC?\n", progname);
    exit(1);
  }

  if (mlockall(MCL_CURRENT) == 0) {
    //fprintf(stderr, "%s:init -- locked memory\n", progname);
    mem_locked = 1;
  } else {
    perror("mlockall");
    fprintf(stderr, "%s:init -- failed to lock memory\n", progname);
  }

  if ((semid = psem_init(SEMKEY)) < 0) {
    perror("psem_init");
    fprintf(stderr, "%s: can't init semaphore\n", progname);
    exit(1);
  }

  fprintf(stderr, "iscan: attached to %s\n", dev);

  atexit(halt);
  catch_signals(progname);

  return(1);
}

static void mainloop(void)
{
  int x, y, i;
  int lastpri, setpri;

  errno = 0;
  LOCK(semid);
  i = dacq_data->iscan_pri;
  UNLOCK(semid);
  if (setpriority(PRIO_PROCESS, 0, i) == 0 && errno == 0) {
    fprintf(stderr, "%s:init -- bumped priority %d\n", progname, i);
    lastpri = i;
    setpri = 1;
  } else {
    fprintf(stderr, "%s:init -- failed to change priority\n", progname);
    lastpri = 0;
    setpri = 0;
  }


  fprintf(stderr, "%s: about to set ready flag\n", progname);
  LOCK(semid);
  dacq_data->iscan_x = dacq_data->iscan_x = x = y = 1;
  dacq_data->iscan_ready = 1;
  UNLOCK(semid);

  do {
    if (iscan_read(iscan_port, &x, &y)) {
      x -= 2048;
      y -= 2048;
      LOCK(semid);
      dacq_data->iscan_x = x;
      dacq_data->iscan_y = y;
      UNLOCK(semid);
    }

    /* possibly bump up or down priority on the fly */
    LOCK(semid);
    i = dacq_data->iscan_pri;
    UNLOCK(semid);
    if (setpri && lastpri != i) {
      lastpri = i;
      errno = 0;
      if (setpriority(PRIO_PROCESS, 0, i) == -1 && errno) {
	/* disable future priority changes */
	setpri = 0;
      }
    }
    LOCK(semid);
    i = dacq_data->iscan_terminate;
    UNLOCK(semid);
  } while (! i);

  if (dacq_data->iscan_terminate) {
    fprintf(stderr, "%s: exiting\n", progname);
  }
  dacq_data->iscan_ready = 0;
}

int main(int ac, char **av)
{
  char *p = rindex(av[0], '/');
  char *dev;

  if (p) {
    progname = p + 1;
  } else {
    progname = av[0];
  }

  fprintf(stderr, "%s: started up\n", progname);

  if (ac < 2) {
    fprintf(stderr, "usage: %s serialdev\n", progname);
    exit(1);
  }
  dev = av[1];

  init(dev);
  fprintf(stderr, "%s: entering mainloop\n", progname);
  mainloop();
  exit(0);
}
