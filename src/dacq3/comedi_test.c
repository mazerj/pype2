/* title:   comedi_test.c
**
** author:  jamie mazer
** created: Wed Jun  7 11:46:24 2006 mazer 
** info:    test program for comedi device
**
** compile with: cc -o comedi_test comedi_test.c -lcomedi
**
** requires running as root for access to /dev/comedi0
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

char *progname = NULL;

static char *comedi_devname = "/dev/comedi0";
static int pci_das08 = 0;	/* board is pci-das08? */
static comedi_t *comedi_dev;	/* main handle to comedi lib */
static int analog_in;		/* subdevice for analog input */
static int use8255;		/* 0 for ISA, 1 for PCI */
static int dig_io;		/* combined digital I/O subdevice */
static int dig_i;		/* digital IN only subdevice (ISA) */
static int dig_o;		/* digital OUT only subdevice (ISA)*/
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
    }
  } else {
    dig_i  = comedi_find_subdevice_by_type(comedi_dev,COMEDI_SUBD_DI,0);
    if (dig_i == -1) {
      comedi_perror("dig_i");
    }
    dig_o = comedi_find_subdevice_by_type(comedi_dev,COMEDI_SUBD_DO,0);
    if (dig_o == -1) {
      comedi_perror("dig_o");
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

static int dig_in()
{
  int i, success, bits, last;

  bits = 0;
  if (use8255) {
    success = comedi_dio_bitfield(comedi_dev,dig_io,PCI_NOWRITEMASK,&bits);
    bits = bits & PCI_READMASK;
  } else {
    success = comedi_dio_bitfield(comedi_dev,dig_i,ISA_NOWRITEMASK,&bits);
  }
  return(bits);

  /* unpack inp word into the first 8 slots of the dacq struct's din array */
  for (i = 0; i < 4; i++) {
    fprintf(stderr, "%d ", bits & 1<<i);
  }
}

static void halt(void)
{
  fprintf(stderr, "%s: halt()\n", progname);
  comedi_close(comedi_dev);
}

static int init()
{
  int shmid;

  if (!comedi_init()) {
    exit(1);
  }
  fprintf(stderr, "%s: comedi initialized.\n", progname);
  fprintf(stderr, "%s: d_io=%d\n", progname, dig_io);
  fprintf(stderr, "%s: d_i=%d\n", progname, dig_i);
  fprintf(stderr, "%s: d_o=%d\n", progname, dig_o);
  fprintf(stderr, "%s: analog_in=%d\n", progname, analog_in);

  atexit(halt);

  return(1);
}

int main(int ac, char **av)
{
  int i, j, k, nchan;

  progname = av[0];

  init();

  nchan = comedi_get_n_channels(comedi_dev, analog_in);

  for (i = 0; 1; i++) {
    j = dig_in();
    for (k = 0; k < nchan; k++) {
      fprintf(stdout, "%1d ", (j & 1<<k) == 1);
    }
    for (k = 0; k < 8; k++) {
      fprintf(stdout, "\t%05d", ad_in(k));
    }
    fprintf(stdout, "\n");
  }
}
