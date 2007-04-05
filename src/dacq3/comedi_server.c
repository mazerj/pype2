/* title:   comedi_server.c

** author:  jamie mazer
** created: Wed Jan  8 17:21:15 2003 mazer 
** info:    shm interface to COMEDI devices
** history:
**
** Wed Jan  8 17:20:18 2003 mazer 
**   - based on das16_server.c -- this is driver for the COMEDI
**     data acq. library/device-driver kit.  It's GENERIC, designed
**     to work with the ISA & PCI versions of the DAS-1602 card.
**
** Sun Mar  9 13:34:54 2003 mazer 
**   added support for din_changes[] to dig_in()
**
** Wed Nov  3 15:02:41 2004 mazer 
**   added support for the DAS08 board (no 8255!!)
**
** Tue Apr  3 08:37:59 2007 mazer 
**   cleaned up error messages for comedit to make it easier to track
**   down problems with non-DAS/ComputerBoards cards (like NI-6025E).
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
#include <comedilib.h>

#include "dacqinfo.h"
#include "sigs.h"
#include "psems.h"
#include "debug.h"

#include "das16.h"

static char *progname = NULL;
static DACQINFO *dacq_data = NULL;
static int mem_locked = 0;
static int dummymode = 0;

#include "das_common.h"

static int pci_das08 = 0;	/* board is pci-das08? */

static char *comedi_devname = "/dev/comedi0";
static comedi_t *comedi_dev;	/* main handle to comedi lib */
static int analog_in = -1;	/* subdevice for analog input */

static int use8255;		/* 0 for ISA, 1 for PCI */
static int dig_io = -1;		/* combined digital I/O subdevice */
static int dig_i = -1;		/* digital IN only subdevice (ISA) */
static int dig_o = -1;		/* digital OUT only subdevice (ISA)*/
static int analog_range;

// for the ISA cards, we have 4 bits of digital input and 4 of output
#define ISA_NOWRITEMASK	0
#define ISA_WRITEMASK	(1+2+4+8)

// NOTE: in case it's not clear -- these #defines are only for
//       cards with 8255-based dio, which are autodetected
//       below in the init function!!
//
// for cards with 8255 digital i/o, we have banks A,B and C
// we want bank A (0-7) for input, and B (8-15) for output:

#define BANK_A          0
#define BANK_B          8
#define PCI_NOWRITEMASK 0
#define PCI_READMASK    (1+2+4+8+16+32+64+128)
#define PCI_WRITEMASK   (1+2+4+8+16+32+64+128)<<BANK_B
	
static int comedi_init()
{
  char *devname;
  comedi_range *r;
  int n;

  // open comedi device... we're assuming it's at /dev/comedi0
  if (!(comedi_dev = comedi_open(comedi_devname))) {
    fprintf(stderr, "%s: can't find comedi board.\n", progname);
    return(0);
  }
  devname = comedi_get_driver_name(comedi_dev);
  
  fprintf(stderr, "%s: found DAQ device board=<%s> driver=<%s>\n",
	  progname, comedi_get_board_name(comedi_dev), devname);

  if (strncmp(devname, "das16", 5) == 0) {
    use8255 = 0;
    fprintf(stderr, "%s: 8255 disabled.\n", progname);
  } else if (strncmp(devname, "das08", 5) == 0) {
    use8255 = 0;
    fprintf(stderr, "%s: 8255 disabled.\n", progname);
  } else {
    use8255 = 1;
    fprintf(stderr, "%s: 8255 enabled.\n", progname);
  }

  if (strcmp(comedi_get_board_name(comedi_dev), "pci-das08") == 0) {
      pci_das08 = 1;
      fprintf(stderr, "%s: pci-das08 detected, delaying input\n", progname);
  }

  // find which comedi subdevices correspond the the facilities we need
  analog_in  = comedi_find_subdevice_by_type(comedi_dev,COMEDI_SUBD_AI,0);
  if (analog_in == -1) {
    comedi_perror("analog_in");
  } else {
    fprintf(stderr, "%s: analog input OK\n", progname);
  }


  n = comedi_get_n_channels(comedi_dev, analog_in);
  fprintf(stderr, "%s: %d analog inputs available.\n", progname, n);
  n = comedi_get_n_ranges(comedi_dev, analog_in, 0);
  fprintf(stderr, "%s: %d analog ranges available.\n", progname, n);
  if (n > 1) {
    // try to find the +/- 10V range.  the 4th parm means 'volts'.
    // BW: I THINK THIS ASSUMES ALL CHANNELS ARE THE SAME
    analog_range = comedi_find_range(comedi_dev,analog_in,0,0,-10,10);
    if (analog_range == -1) {
      comedi_perror("analog_range");
    }
  } else {
    /*
     * for DAS08, which doesn't have programmable ranges -- just use 0!
     */
    analog_range = 0;
  }
  r = comedi_get_range(comedi_dev, analog_in, 0, analog_range);
  fprintf(stderr, "%s: analog range (%.1f%s)-(%.1f%s)\n", progname,
	  r->min, (r->unit==UNIT_volt) ? "V" : "??",
	  r->max, (r->unit==UNIT_volt) ? "V" : "??");

  if (use8255) {
    dig_io = comedi_find_subdevice_by_type(comedi_dev,COMEDI_SUBD_DIO,0);
    if (dig_io == -1) {
      comedi_perror("dig_io");
    } else {
      fprintf(stderr, "%s: digitial IO OK\n", progname);
      dig_i = -1;
      dig_o = -1;
    }
  } else {
    dig_i  = comedi_find_subdevice_by_type(comedi_dev,COMEDI_SUBD_DI,0);
    if (dig_i == -1) {
      comedi_perror("dig_i");
    } else {
      fprintf(stderr, "%s: digitial input OK\n", progname);
    }
    dig_o = comedi_find_subdevice_by_type(comedi_dev,COMEDI_SUBD_DO,0);
    if (dig_o == -1) {
      comedi_perror("dig_o");
    } else {
      fprintf(stderr, "%s: digitial output OK\n", progname);
    }
  }

  if (use8255) {
    // configure digital I/O bank A as input, and bank B as output
    if (comedi_dio_config(comedi_dev,dig_io,BANK_A,COMEDI_INPUT) &&
	comedi_dio_config(comedi_dev,dig_io,BANK_B,COMEDI_OUTPUT)) {
      return(1);
    } else {
      return(0);
    }
  }
  return(1);
}


static int ad_in(int chan)
{
  lsampl_t sample;
  int success;

  if (dummymode) {
    return(0);
  } else {
    // need to set aref correctly
    // this could be either AREF_GROUND or AREF_COMMON
    if (pci_das08) {
      // das08 is screwy -- needs time for multiplexer to settle:
      success = comedi_data_read_delayed(comedi_dev,analog_in,
					 chan,analog_range,AREF_GROUND,
					 &sample, 0);
      if (success < 0) {
	comedi_perror("comedi_data_read_delayed");
      }
    } else {
      success = comedi_data_read(comedi_dev,analog_in,
				 chan,analog_range,AREF_GROUND,
				 &sample);
      if (success < 0) {
	comedi_perror("comedi_data_read");
      }
    }
    // NB lsampl is an unsigned int; we are casting to int. it won't
    // matter for 12 bit cards
    return((int)sample);
  }
}

static void dig_in()
{
  int i, success, bits, last;

  if (dummymode) {
    /* these are hardcoded for polarity of devices down in naf */
    LOCK(semid);
    dacq_data->din[0] = 0;	/* monkey bar NOT down */
    dacq_data->din[2] = 1;	/* user button 2 NOT down */
    dacq_data->din[3] = 1;	/* user button 1 NOT down */
    UNLOCK(semid);
    return;
  } else {
    if (use8255) {
      success = comedi_dio_bitfield(comedi_dev,dig_io,PCI_NOWRITEMASK,&bits);
      bits = bits & PCI_READMASK;
    } else {
      success = comedi_dio_bitfield(comedi_dev,dig_i,ISA_NOWRITEMASK,&bits);
    }
    /* unpack inp word into the first 8 slots of the dacq struct's din array */
    for (i = 0; i < 4; i++) {
      LOCK(semid);
      last = dacq_data->din[i];
      dacq_data->din[i] = ((bits & 1<<i) != 0);
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
  int bits = 0;
  int i, success;

  if (dummymode) {
    return;
  } else {
    for (i = 0; i < 8 && i < NDIGOUT; i++) {
      LOCK(semid);
      bits = bits | (dacq_data->dout[i] << i);
      UNLOCK(semid);
    }
    if (use8255) {
      bits = bits<<BANK_B;
      success = comedi_dio_bitfield(comedi_dev,dig_io,PCI_WRITEMASK,&bits);
    } else {
      success = comedi_dio_bitfield(comedi_dev,dig_o,ISA_WRITEMASK,&bits);
    }
  }
}

static void halt(void)
{
  fprintf(stderr, "%s: halt()\n", progname);

  comedi_close(comedi_dev);

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

  if (comedi_init()) {
    dummymode = 0;
  } else {
    fprintf(stderr, "%s: falling back to dummymode\n", progname);
    dummymode = 1;
  }
  fprintf(stderr, "%s: comedi initialized.\n", progname);
  if (dig_io >= 0) {
    fprintf(stderr, "%s: dig_io=subdev #%d\n", progname, dig_io);
  }
  if (dig_i >= 0) {
    fprintf(stderr, "%s: dig_i=subdev #%d\n", progname, dig_i);
  }
  if (dig_o >= 0) {
    fprintf(stderr, "%s: ddig_o=subdev #%d\n", progname, dig_o);
  }
  if (analog_in >= 0) {
    fprintf(stderr, "%s: analog_in=subdev #%d\n", progname, analog_in);
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
