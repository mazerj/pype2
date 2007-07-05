/* title:   dummy_server.c

** author:  jamie mazer
** created: Mon Mar 13 19:31:14 2006 mazer 
** info:    dummy shm interface 
** history:
**
** Mon Mar 13 19:31:07 2006 mazer 
**   - derived from comedi_server.c
**   - provides stubs for a machine w/o a dacq card..
**   - servers must provide
*/

#include <sys/types.h>
#include <sys/time.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/mman.h>
#include <sys/io.h>
#include <signal.h>

#include "dacqinfo.h"
#include "sigs.h"
#include "psems.h"
#include "debug.h"

static char *progname = NULL;
static DACQINFO *dacq_data = NULL;
static int mem_locked = 0;

#include "das_common.h"

static int ad_in(int chan)
{
  return(0);
}

static void dig_in()
{
  int i, last;

  for (i = 0; i < 4; i++) {
    LOCK(semid);
    last = dacq_data->din[i];
    if (usbjs_dev < 0) {
      /* no joystick: use digital inputs */
      dacq_data->din[i] = 0;
    } else {
      /* joystick present: replaces digital inputs */
      dacq_data->din[i] = dacq_data->js[i];
    }
    if (dacq_data->din[i] != last) {
      dacq_data->din_changes[i] += 1;
      if (dacq_data->din_intmask[i]) {
	dacq_data->int_class = INT_DIN;
	dacq_data->int_arg = i;
	kill(getppid(), SIGUSR1);
      }
    }
    UNLOCK(semid);
  }

  /*
  LOCK(semid);
  dacq_data->din[0] = 0;
  dacq_data->din[2] = 0;
  dacq_data->din[3] = 0;
  UNLOCK(semid);
  */
}

static void dig_out()
{
  return;
}

static void halt(void)
{
  if (dacq_data != NULL) {
    shmdt(dacq_data);
  }
  if (mem_locked) {
    if (munlockall() != 0) {
      perror2("munlockall", __FILE__, __LINE__);
    } else {
      mem_locked = 0;
    }
  }
}

static int init()
{
  int shmid;

  if ((shmid = shmget((key_t)SHMKEY,
		      sizeof(DACQINFO), 0666 | IPC_CREAT)) < 0) {
    perror2("shmget", __FILE__, __LINE__);
    fprintf(stderr, "%s:init -- kernel compiled with SHM/IPC?\n", progname);
    exit(1);
  }

  if ((dacq_data = shmat(shmid, NULL, 0)) == NULL) {
    perror2("shmat", __FILE__, __LINE__);
    fprintf(stderr, "%s:init -- kernel compiled with SHM/IPC?\n", progname);
    exit(1);
  }

  if (mlockall(MCL_CURRENT) == 0) {
    mem_locked = 1;
  } else {
    perror2("mlockall", __FILE__, __LINE__);
    fprintf(stderr, "%s:init -- failed to lock memory\n", progname);
  }
  LOCK(semid);
  if (dacq_data->dacq_pri != 0) {
    if (nice(dacq_data->dacq_pri) == 0) {
      fprintf(stderr, "%s:init -- bumped priority %d\n",
	      progname, dacq_data->dacq_pri);
    } else {
      perror2("nice", __FILE__, __LINE__);
      fprintf(stderr, "%s:init -- failed to change priority\n", progname);
    }
  }
  UNLOCK(semid);

  atexit(halt);
  catch_signals(progname);

  /* ignore iscan exiting: */
  //signal(SIGCHLD, SIG_IGN);

  fprintf(stderr, "%s: dummy_server initialized.\n", progname);

  return(1);
}

#include "das_common.c"
