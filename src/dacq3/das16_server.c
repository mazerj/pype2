/* title:   das16_server.c

** author:  jamie mazer
** created: Tue Sep 19 20:35:27 2000 mazer 
** info:    shm interface to computerboards das1600 DA/AD card
** history:
**
** Tue Sep 19 15:52:36 2000 mazer 
**   - rewritten to use raw port i/o instead of loadable device driver..
**   - this now assumes that the iscan serial interface is handling
**     the eye info..
**
** Sun Dec  2 13:52:55 2001 mazer 
**   - changed name to das16_server
**
** Tue Feb 26 17:41:06 2002 mazer 
**   - merged iscan support directly into this module to eliminate
**     one more active process during recording.
**
** Mon Mar  4 17:24:41 2002 mazer 
**   - moved fixwin code here
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

#include "das16.h"

static char *progname = NULL;
static DACQINFO *dacq_data = NULL;
static int mem_locked = 0;
static int dbase = 0x260;
static int dummymode = 0;

#include "das_common.h"

static int ad_in(int chan)
{
  int lo, hi, i;

  if (dummymode) {
    return(0);
  } else {
    /* select desired channel */
    outb(chan + (chan << 4), dbase+Channel_Mux);
    
    /* trigger conversion */
    outb(0x00, dbase+ADC_Low);
    
    /* wait for converter to be free.. this is kludge */
    for (i = 0; i < 100; i++) {
      if ((inb(dbase+Status) & 0x80) == 0) {
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
    /* read digital input word from das1600 */
    b = inb(dbase+Digital_4_Bit);
    
    /* unpack inp word into the first 8 slots of the dacq struct's din array */
    for (i = 0; i < 8 && i < NDIGIN; i++) {
      LOCK(semid);
      last = dacq_data->din[i];
      dacq_data->din[i] = ((b & 1<<i) != 0);
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
  unsigned char b = 0;
  int i;

  if (dummymode) {
    return;
  } else {
    for (i = 0; i < 8 && i < NDIGOUT; i++) {
      LOCK(semid);
      b = b | (dacq_data->dout[i] << i);
      UNLOCK(semid);
    }
    outb(b, dbase+Digital_4_Bit);
  }
}

static void halt(void)
{
  fprintf(stderr, "%s: halt()\n", progname);
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
    outb(0x00, dbase+Pacer_Control);
    outb(0x00, dbase+Status);
    outb(0x00, dbase+Control);
    
    /* set max input gain..
       code	das1601/12	das1602/12
       0	+- 10v		+- 10v
       1	+- 1v		+- 5v
       2	+- 0.1v		+- 2.5v
       3	+- 0.01v	+- 1.25v
    */
    outb(0x00, dbase+Gain_Control);

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
  catch_signals(progname);

  /* ignore iscan exiting: */
  //signal(SIGCHLD, SIG_IGN);

  return(1);
}

#include "das_common.c"

