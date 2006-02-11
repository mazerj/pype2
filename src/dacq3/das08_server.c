/* title:   das08_server.c

** author:  jamie mazer
** created: Sun Dec  2 13:22:15 2001 mazer 
** info:    shm interface to computerboards das08 DA/AD card
** history:
**
** Sun Dec  2 13:22:23 2001 mazer 
**   - derived from the das_server (das160x) driver code..
**
** Sun Mar  9 13:34:54 2003 mazer 
**   added support for din_changes[] to dig_in()
**
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

#include "das08.h"
#include "das_common.h"

static char *progname = NULL;
static DACQINFO *dacq_data = NULL;
static int mem_locked = 0;
static int dbase = 0x300;
static int dummymode = 0;
static unsigned char muxstate = 0x00;


static int ad_in(int chan)
{
  int lo, hi, i;

  if (dummymode) {
    return(0);
  } else {
    /* select desired channel */
    //wrong: muxstate = muxstate | chan;
    muxstate = (muxstate & 0xf8)  | (0x07 & chan);
    outb((unsigned char)muxstate, dbase+State);
    
    /* trigger conversion */
    outb(0x00, dbase+ADC_High);
    
    /* wait for converter to be free.. this is kludge */
    for (i = 0; i < 100; i++) {
      if ((inb(dbase+State) & 0x80) == 0) {
	break;
      }
    }
    
    /* get converted value */
    lo = inb(dbase+ADC_Low);
    hi = inb(dbase+ADC_High);
    
    /* converts 12bit unsigned # to 12bit signed */
    return((((lo&0xf0) >> 4) | (hi << 4)) - 2048);
  }
}

static void dig_in()
{
  int i, last;
  unsigned char b;

  if (dummymode) {
    /* these are hardcoded for polarity of devices down in naf */
    LOCK(semid);
    dacq_data->din[0] = 0;	/* monkey bar NOT down */
    dacq_data->din[2] = 1;	/* user button 2 NOT down */
    dacq_data->din[3] = 1;	/* user button 1 NOT down */
    UNLOCK(semid);
    return;
  } else {
    /* read digital input word from das08 */
    b = inb(dbase+State);
    
    /* unpack inp word into the first 3 slots of the dacq struct's din array */
    for (i = 0; i < 8 && i < 3; i++) {
      LOCK(semid);
      last = dacq_data->din[i];
      dacq_data->din[i] = ((b & 1<<(i+4)) != 0);
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
  }
}

static void dig_out()
{
  int i;

  if (dummymode) {
    return;
  } else {
    for (i = 0; i < 4; i++) {
      LOCK(semid);
      if (dacq_data->dout[i]) {
	muxstate = muxstate | (1 << (i+4));
      } else {
	muxstate = muxstate & ~(1 << (i+4));
      }
      UNLOCK(semid);
    }
    outb((unsigned char)muxstate, dbase+State);
  }
}

static void halt(void)
{
  // remember to clear the TTL lines before exiting..
  outb((unsigned char)0, dbase+State);

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

  /* first get access to IO ports -- this requires root perms */
  if (iopl(3) != 0) {
    perror2("iopl", __FILE__, __LINE__);
    fprintf(stderr, "%s: warning no port access -- using dummy mode\n",
	    progname);
    dummymode = 1;
  } else {
    /* setup for simple polling input on 4 channels */
    // outb(0x00, dbase+Pacer_Control);
    // outb(0x00, dbase+Status);
    // outb(0x00, dbase+Control);
    
    /* enable DAS usage */
    dummymode = 0;
  }

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
  //catch_signals(progname);

  /* ignore iscan exiting: */
  //signal(SIGCHLD, SIG_IGN);

  return(1);
}

#include "das_common.c"

